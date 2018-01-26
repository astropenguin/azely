# public items
__all__ = ['AzEl',
           'Calculator']

# standard library
from collections import OrderedDict
from datetime import datetime
from logging import getLogger
logger = getLogger(__name__)

# dependent packages
import azely
import numpy as np
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.coordinates import get_body, solar_system_ephemeris
from astropy.time import Time

try:
    solar_system_ephemeris.set('jpl')
except ImportError:
    solar_system_ephemeris.set('builtin')

# module constants
UTC = ('UTC', 'COORDINATED UNIVERSAL TIME')
LST = ('LST', 'LOCAL SIDEREAL TIME')
LST_TO_UTC = 1 / 1.002_737_909


# classes
class AzEl(SkyCoord):
    """Az-el coordinate class as a subclass of Astropy's SkyCoord.

    In addition to the original attributes, the following ones are supported.


    Attributes:
        ra (Longitude): Right ascention (ICRS) of object.
        dec (Longitude): Declination (ICRS) of object.
        el (Latitude): Elevation of object (an alias of `alt`).

    """
    def __init__(self, *args, **kwargs):
        """Create (initialize) az-el coordinate instance.

        Args:
            args: Positional arguments. Same as SkyCoord's one.
            kwargs: Keyword arguments. Same as SkyCoord's one.

        """
        logger.debug(f'args = {args}')
        logger.debug(f'kwargs = {kwargs}')

        super().__init__(*args, **kwargs)

    @property
    def ra(self):
        """Right ascention (ICRS) of object."""
        return SkyCoord(self.transform_to('icrs')).ra

    @property
    def dec(self):
        """Declination (ICRS) of object."""
        return SkyCoord(self.transform_to('icrs')).dec

    @property
    def el(self):
        """Elevation of object (an alias of `alt`)."""
        return self.alt

    def __repr__(self):
        return '<SkyCoord (AzEl): (az, el) in deg>'


class Calculator(object):
    """Function-like azimuth/elevation calculator class.

    This is Azely's highest-level class. Most of operations are executed
    through the class (its instance) including requesting location and
    objects' information via internet and calculating azimuth/elevation
    of objects. To create an instance, user can use ambiguous strings
    about location, timezone, and date when and where azimuth/elevation
    of objects should be calculated.

    Attributes:
        date (Time): Astropy's time of date.
        location (dict): Dictionary of location information.
        timezone (dict): Dictionary of timezone information.

    """
    def __init__(self, location, timezone=None, date=None,
                 *, reload=False, timeout=5, encoding='utf-8'):
        """Create (initialize) azimuth/elevation calculator instance.

        Args:
            location (str): Location's name (address) such as 'tokyo',
                'san pedro de atacama', or '2-21-1 osawa mitaka'.
            timezone (str, optional): Timezone's name. There are three types
                of timezone-like names are supported: (1) 'UTC', 'UTC+9.0',
                or '9.0', (2) 'LST', 'local sidereal time' (although it is
                not timezone), and (3) 'tokyo' (same as `location`). If not
                spacified, timezone of `location` at given `date` will be used.
            date (str, optional): Date (YYYY-mm-dd) used for calculating
                azimuth/elevation of objects and requesting timezone.
            reload (bool, optional, keyword-only): If True, YAML files of
                astronomical objects (*.yaml) and ~/known_locations.yaml are
                automatically reloaded every time before calculation.
                Default is False.
            timeout (int, optional, keyword-only): Time to wait for remote
                data queries in units of second. Default is 5.
            encoding (str, optional, keyword-only): File encoding used for
                loading and updating YAML files. Default is 'utf-8'.

        """
        logger.debug(f'location = {location}')
        logger.debug(f'timezone = {timezone}')
        logger.debug(f'date = {date}')
        logger.debug(f'reload = {reload}')
        logger.debug(f'timeout = {timeout}')
        logger.debug(f'encoding = {encoding}')

        self._location = location
        self._timezone = timezone
        self._date = azely.parse_date(date)

        self._locations = azely.Locations(reload=reload,
                                          timeout=timeout,
                                          encoding=encoding)
        self._objects = azely.Objects(reload=reload,
                                      timeout=timeout,
                                      encoding=encoding)

    @property
    def date(self):
        """Astropy's time object of date."""
        earthloc = EarthLocation(lon=self.location['longitude']*u.deg,
                                 lat=self.location['latitude']*u.deg)

        return Time(self._date, location=earthloc, out_subfmt='date')

    @property
    def location(self):
        """Dictionary of location information."""
        return self._locations[self._location, self._date]

    @property
    def timezone(self):
        """Dictionary of timezone information."""
        if not self._timezone:
            return self._parse_timezone(self._location)
        else:
            return self._parse_timezone(self._timezone)

    def __call__(self, object_names, hours=None, squeeze=True):
        """Calculate azimuth/elevation of objects at given hour(angle)s."""
        objects = self._objects[object_names]
        time_utc = self._get_time_utc(hours)

        azels = OrderedDict()

        for item in objects.items():
            azels.update(self._calc_azel(*item, time_utc))

        if squeeze and len(azels) == 1:
            return azels.popitem()[1]
        else:
            return azels

    def _calc_azel(self, name, obj, time_utc):
        """Calculate azimuth/elevation of given object and time in UTC."""
        if obj == azely.PASS_FLAG:
            return dict()

        if isinstance(obj, SkyCoord):
            obj.obstime = time_utc
        elif isinstance(obj, str):
            obj = get_body(obj, time=time_utc)

        altaz = AltAz(location=time_utc.location)
        return {name: azely.AzEl(obj.transform_to(altaz))}

    def _get_time_utc(self, hours=None):
        """Get time in UTC from hour(angle)s of given timezone."""
        if hours is None:
            return Time(datetime.utcnow(), location=self.date.location)

        hours = np.asarray(hours) * u.hr

        # time in UTC corresponding timezone's 0:00 am
        # if timezone = LST, timezone of location is used
        utc_at_tz0am = self.date - self.timezone['hour']*u.hr

        if self._islst(self.timezone['name']):
            lst_at_tz0am = utc_at_tz0am.sidereal_time('mean').value * u.hr
            return utc_at_tz0am + LST_TO_UTC * (hours - lst_at_tz0am)
        else:
            return utc_at_tz0am + hours

    def _parse_timezone(self, timezone):
        """Parse timezone string and return location-like dict."""
        if self._islst(timezone):
            # timezone = 'LST' or related string
            return {'name': 'Local Sidereal Time',
                    'hour': self.location['timezone_hour']}
        elif self._isutc(timezone):
            # timezone = 'UTC' or related string
            return {'name': 'UTC+0.0', 'hour': 0.0}
        elif self._isnumber(timezone):
            # timezone = 9.0 or '9.0', for example
            hour = float(timezone)
            return {'name': f'UTC{hour:+.1f}', 'hour': hour}
        elif isinstance(timezone, str):
            # timezone = 'japan', for example
            location = self._locations[timezone]
            return {'name': location['timezone_name'],
                    'hour': location['timezone_hour']}
        else:
            logger.error(f'invalid timezone: {timezone}')
            logger.error('calculator object cannot be created')
            raise ValueError(timezone)

    def _islst(self, string):
        """Whether string can be interpreted as local sideral time."""
        if not isinstance(string, str):
            return False

        return ' '.join(azely.parse_name(string)).upper() in LST

    def _isutc(self, string):
        """Whether string can be interpreted as coordinated universal time."""
        if not isinstance(string, str):
            return False

        return ' '.join(azely.parse_name(string)).upper() in UTC

    def _isnumber(self, string):
        """Whether string can be converted to number or not."""
        try:
            float(string)
            return True
        except ValueError:
            return False

    def __repr__(self):
        loc, tz = self.location['name'], self.timezone['name']
        return f'Calculator(location:{loc}, timezone:{tz}, date:{self._date})'
