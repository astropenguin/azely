# coding: utf-8

# public items
__all__ = ['AzEl',
           'Calculator',]

# standard library
from collections import OrderedDict

# dependent packages
import azely
import ephem
import numpy as np
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.coordinates import get_body
from astropy.time import Time

# module constants
UTC = ('UTC', 'COORDINATED UNIVERSAL TIME')
LST = ('LST', 'LOCAL SIDEREAL TIME')
LST_TO_UTC = 1 / 1.002_737_909
UTC_TO_LST = 1.002_737_909


# classes
class Calculator(object):
    def __init__(self, location, timezone=None, date=None,
                 *, reload=True, timeout=5, encoding='utf-8'):
        self._locations = azely.Locations(reload=reload,
                                          timeout=timeout,
                                          encoding=encoding)
        self._objects = azely.Objects(reload=reload,
                                      timeout=timeout,
                                      encoding=encoding)

        self.date = azely.parse_date(date)
        self.location = self._locations[location, date]
        if timezone:
            self.timezone = self._parse_timezone(timezone)
        else:
            self.timezone = self.location.copy()

    def __call__(self, object_names, hours=None):
        """Calculate azimuth and elevation of objects at given hour(angle)s."""
        skycoords = self._objects[object_names]
        time_utc = self._get_time_utc(hours)

        azels = OrderedDict()
        for name, skycoord in skycoords.items():
            if skycoord == azely.PASS_FLAG:
                continue

            azels.update({name: self._get_azel(skycoord, time_utc)})

        return azels

    def _get_azel(self, skycoord, time_utc):
        """Get azimuth and elevation of given skycoord and time in UTC."""
        if isinstance(skycoord, str):
            skycoord = get_body(skycoord, time=time_utc)
            return skycoord.transform_to(self._frame)
        elif isinstance(skycoord, SkyCoord):
            skycoord.obstime = time_utc
            return skycoord.transform_to(self._frame)
        else:
            raise ValueError(skycoord)

    def _get_time_utc(self, hours=None):
        """Get time in UTC from hour(angle)s of given timezone."""
        if hours is None:
            return Time.now()

        hours = np.asarray(hours)
        if self._islst(self.timezone['name']):
            # time in UTC corresponding timezone's 0:00 am
            # if timezone = LST, timezone of location is used
            utc_at_tz0am = self._date - self.location['timezone_hour']*u.hr
            lst_at_tz0am = utc_at_tz0am.sidereal_time('mean').value
            return utc_at_tz0am + LST_TO_UTC*(hours-lst_at_tz0am)*u.hr
        else:
            utc_at_tz0am = self._date - self.timezone['timezone_hour']*u.hr
            return utc_at_tz0am + hours*u.hr

    def _parse_timezone(self, timezone):
        """Parse timezone string and return location-like dict."""
        if self._islst(timezone):
            # timezone = 'LST' or related string
            return {'name': 'LST',
                    'timezone_hour': None,
                    'timezone_name': 'Local Sidereal Time'}
        elif self._isutc(timezone):
            # timezone = 'UTC' or related string
            return {'name': 'UTC',
                    'timezone_hour': 0.0,
                    'timezone_name': 'UTC'}
        elif self._isnumber(timezone):
            # timezone = 9.0 or '9.0', for example
            return {'name': f'UTC{float(timezone):+.1f}',
                    'timezone_hour': float(timezone),
                    'timezone_name': f'UTC{float(timezone):+.1f}'}
        elif isinstance(timezone, str):
            # timezone = 'japan', for example
            return self._locations[timezone]
        else:
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

    @property
    def _date(self):
        """Get date as an Astropy's time object (midnight in UTC)."""
        earthloc = EarthLocation(lon=self.location['longitude']*u.deg,
                                 lat=self.location['latitude']*u.deg)

        return Time(self.date, location=earthloc)

    @property
    def _frame(self):
        """Get az-el frame of location as an Astropy's AltAz object."""
        earthloc = EarthLocation(lon=self.location['longitude']*u.deg,
                                 lat=self.location['latitude']*u.deg)

        return AltAz(location=earthloc)

    def __repr__(self):
        loc, axis = self.location['name'], self.timezone['name']
        return f'AzEl(location:{loc}, timezone:{axis}, date:{self.date})'


class AzEl(object):
    def __init__(self, location, timezone=None, date=None):
        # location
        locs = azely.Locations(date)
        location = locs[location]

        # timezone
        if timezone is None or timezone == '':
            timezone = location
        elif self._isnumber(timezone):
            timezone = {
                'name': 'UTC{0:+.1f}'.format(float(timezone)),
                'timezone_hour': float(timezone),
                'timezone_name': 'UTC{0:+.1f}'.format(float(timezone)),
            }
        elif type(timezone) == str:
            if timezone.upper() == 'LST':
                timezone = {
                    'name': 'LST',
                    'timezone_hour': None,
                    'timezone_name': 'Local Sidereal Time',
                }
            else:
                timezone = locs[timezone]
        else:
            raise ValueError(timezone)

        # store params
        self.params = {
            'date': azely.parse_date(date),
            'location': location,
            'timezone': timezone,
        }

    def __call__(self, obj, hr=None):
        # body
        body = self._get_body(obj)

        # observer
        observer = ephem.Observer()
        observer.lat = str(self.location['latitude'])
        observer.lon = str(self.location['longitude'])

        if hr is None:
            observer.date = ephem.now()
        else:
            observer.date = ephem.Date(self.date)

            if self.timezone['name'] == 'LST':
                st = observer.sidereal_time()
                offset_hr = st / (2*np.pi) * 24 / UTC_TO_LST
            else:
                offset_hr = self.timezone['timezone_hour'] % 24

            observer.date -= offset_hr * ephem.hour

        # compute
        coords = []
        names = ['az', 'el', 'ra', 'dec', 'lst']
        hrs = [hr] if not hasattr(hr, '__iter__') else hr
        for hr in hrs:
            coords.append(self._compute(body, observer, hr))

        return np.rec.fromarrays(np.array(coords).T, names=names)

    def _compute(self, body, observer, hr=None):
        observer = observer.copy()

        if hr is not None:
            if self.timezone['name'] == 'LST':
                observer.date += hr * ephem.hour / UTC_TO_LST
            else:
                observer.date += hr * ephem.hour

        body.compute(observer)
        az, el  = np.rad2deg([body.az, body.alt])
        ra, dec = np.rad2deg([body.ra, body.dec])
        lst = observer.sidereal_time() / (2*np.pi) * 24
        return az, el, ra, dec, lst

    def _isnumber(self, timezone):
        """Whether timezone can be converted to number or not."""
        try:
            float(timezone)
            return True
        except ValueError:
            return False

    @staticmethod
    def _get_body(object_like):
        if isinstance(object_like, str):
            try:
                return getattr(ephem, object_like)()
            except AttributeError:
                return ephem.star(object_like)
        elif isinstance(object_like, dict):
            body = ephem.FixedBody()
            body._ra = ephem.hours(str(object_like['ra']))
            body._dec = ephem.degrees(str(object_like['dec']))
            if 'epoch' in object_like:
                body._epoch = getattr(ephem, object_like['epoch'])
                return body
            else:
                body._epoch = ephem.J2000
                return body
        else:
            raise ValueError(object_like)

    def __getattr__(self, name):
        return self.params[name]

    def __repr__(self):
        return str.format(
            'AzEl(location={0}, timezone={1}, date={2})',
            self.location['name'], self.timezone['name'], self.date,
        )
