# coding: utf-8

# public items
__all__ = ['AzEl',
           'Calculator']

# standard library
from collections import OrderedDict

# dependent packages
import azely
import numpy as np
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.coordinates import get_body
from astropy.time import Time

# module constants
UTC = ('UTC', 'COORDINATED UNIVERSAL TIME')
LST = ('LST', 'LOCAL SIDEREAL TIME')
LST_TO_UTC = 1 / 1.002_737_909


# classes
class AzEl(SkyCoord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def ra(self):
        return SkyCoord(self.transform_to('icrs')).ra

    @property
    def dec(self):
        return SkyCoord(self.transform_to('icrs')).dec

    @property
    def el(self):
        return self.alt

    def __repr__(self):
        return '<SkyCoord (AzEl)>'


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
            return azely.AzEl(skycoord.transform_to(self._frame))
        elif isinstance(skycoord, SkyCoord):
            skycoord.obstime = time_utc
            return azely.AzEl(skycoord.transform_to(self._frame))
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
