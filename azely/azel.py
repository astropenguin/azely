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
LST_TO_UTC = 1 / 1.002_737_909


# classes
class AzEl(SkyCoord):
    """Azimuth/elevation coordinate class as a subclass of astropy's skycoord.

    Its instance is a default object created by azimuth/elevation calculation.
    In addition to the original attributes, the following ones are supported.

    Attributes:
        ra (Longitude): Right ascention (ICRS) of object.
        dec (Longitude): Declination (ICRS) of object.
        el (Latitude): Elevation of object (an alias of `alt`).

    References:
        http://docs.astropy.org/en/stable/coordinates/

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

    Examples:
        To calculate Sun's azimuth/elevation at Mitaka today::

            >>> import azely
            >>> import numpy as np
            >>> c = azely.Calculator('Mitaka')
            >>> hr = np.arange(24+1) # [0, 24] hr in JST
            >>> azel = c('Sun', hr, unpack_one=True)
            >>> azel.az
            <Longitude [ 15.54934246,  57.27383585,  75.91460181,  87.02248378,
                         95.56647071, 103.28094924, 111.01491654, 119.3533959 ,
                        128.8178452 , 139.90588154, 152.97878391, 167.95714675,
                        183.99626059, 199.66878059, 213.76196278, 225.83142911,
                        236.06364539, 244.91350713, 252.89454982, 260.54782882,
                        268.55139407, 278.06678007, 291.90835609, 319.17703863,
                         15.0002828 ] deg>
            >>> azel.el
            <Latitude [-76.94837869,-69.39652495,-58.18051618,-46.14260649,
                       -33.97655493,-21.96976874,-10.33686226,  0.68394112,
                        10.77580478, 19.49556842, 26.24707722, 30.33815355,
                        31.20023124, 28.69493286, 23.20542918, 15.39936451,
                         5.93769249, -4.65899071,-16.01515708,-27.85870914,
                       -39.97035455,-52.11635814,-63.8824217 ,-73.92269689,
                       -76.89451916] deg>

    Notes:
        Lower-level classes used in it are `azely.Locations`, `azely.Objects`,
        and `azely.AzEl`. See these docstrings for detailed information.

    References:
        http://docs.astropy.org/en/stable/generated/examples
        (Determining and plotting the altitude/azimuth of a celestial object)

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

        self.location = location
        self.timezone = timezone
        self.date = date

        self._locations = azely.Locations(reload=reload,
                                          timeout=timeout,
                                          encoding=encoding)
        self._objects = azely.Objects(reload=reload,
                                      timeout=timeout,
                                      encoding=encoding)

    @property
    def _date(self):
        """Astropy's time object of date."""
        return Time(azely.parse_date(self.date),
                    location=self._earthlocation, out_subfmt='date')

    @property
    def _location(self):
        """Dictionary of location information."""
        with azely.set_date(self.date):
            return self._locations[self.location]

    @property
    def _timezone(self):
        """Dictionary of timezone information."""
        if not self.timezone:
            return self._parse_timezone(self.location)
        else:
            return self._parse_timezone(self.timezone)

    @property
    def _earthlocation(self):
        """Astropy's earth location object."""
        return EarthLocation(lon=self._location['longitude']*u.deg,
                             lat=self._location['latitude']*u.deg)


    def __call__(self, object_names, hours=None, unpack_one=True):
        """Calculate azimuth/elevation of objects at given hour(angle)s.

        Args:
            object_names (str or tuple of str): Names of astronomical objects.
            hours (array_like, optional): Hour(angle)s at given timezone or LST.
            unpack_one (bool, optional): If True and only one object is
                detected from `object_names`, this method will directly return
                azimuth/elevation coordinate instance of the object instead of
                ordered dictionary for reducing redundancy.

        Returns:
            azels (OrderedDict or AzEl): Ordered dictionary that contains
                azimuth/elevation coordinate instances (i.e. {name: azel}).
                If `unpack_one` is True and only one object is detected,
                its instance will be returned instead of ordered dictionary.

        """
        objects = self._objects[object_names]
        time_utc = self._get_time_utc(hours)

        azels = OrderedDict()

        for item in objects.items():
            azels.update(self._calc_azel(*item, time_utc))

        if unpack_one and len(azels) == 1:
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
            return Time(datetime.utcnow(), location=self._earthlocation)

        hours = np.asarray(hours) * u.hr

        # time in UTC corresponding timezone's 0:00 am
        # if timezone = LST, timezone of location is used
        utc_at_tz0am = self._date - self._timezone['hour']*u.hr

        if self._islst(self._timezone['name']):
            lst_at_tz0am = utc_at_tz0am.sidereal_time('mean').value * u.hr
            return utc_at_tz0am + LST_TO_UTC * (hours - lst_at_tz0am)
        else:
            return utc_at_tz0am + hours

    def _parse_timezone(self, timezone):
        """Parse timezone string and return location-like dict."""
        if self._islst(timezone):
            # timezone = 'LST' or related string
            return {'name': 'Local Sidereal Time',
                    'hour': self._location['timezone_hour']}
        elif self._isutc(timezone):
            # timezone = 'UTC' or related string
            return {'name': 'UTC+0.0', 'hour': 0.0}
        elif self._isnumber(timezone):
            # timezone = 9.0 or '9.0', for example
            hour = float(timezone)
            return {'name': f'UTC{hour:+.1f}', 'hour': hour}
        elif isinstance(timezone, str):
            # timezone = 'japan', for example
            with azely.set_date(self.date):
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

        string = ' '.join(azely.parse_keyword(string))
        return string.upper() in ('LST', 'LOCAL SIDEREAL TIME')

    def _isutc(self, string):
        """Whether string can be interpreted as coordinated universal time."""
        if not isinstance(string, str):
            return False

        string = ' '.join(azely.parse_keyword(string))
        return string.upper() in ('UTC', 'UNIVERSAL COORDINATED TIME')

    def _isnumber(self, string):
        """Whether string can be converted to number or not."""
        try:
            float(string)
            return True
        except ValueError:
            return False

    def __repr__(self):
        date = azely.parse_date(self.date)
        loc, tz = self._location['name'], self._timezone['name']
        return f'Calculator(location:{loc}, timezone:{tz}, date:{date})'
