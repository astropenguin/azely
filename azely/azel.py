# coding: utf-8

# public items
__all__ = ['AzEl']

# dependent packages
import azely
import ephem
import numpy as np

# local constants
UT_TO_LST = 1.0027379


# classes
class AzEl(object):
    def __init__(self, location, timezone=None, date=None):
        # location
        locs = azely.Locations(date)
        location = locs[location]

        # timezone
        if timezone is None:
            timezone = location
        elif type(timezone) in (int, float):
            timezone = {
                'name': 'UTC{0:+.1f}'.format(timezone),
                'timezone_hour': float(timezone),
                'timezone_name': 'UTC{0:+.1f}'.format(timezone),
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
        body = azely.get_body(obj)

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
                offset_hr = st / (2*np.pi) * 24 / UT_TO_LST
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
                observer.date += hr * ephem.hour / UT_TO_LST
            else:
                observer.date += hr * ephem.hour

        body.compute(observer)
        az, el  = np.rad2deg([body.az, body.alt])
        ra, dec = np.rad2deg([body.ra, body.dec])
        lst = observer.sidereal_time() / (2*np.pi) * 24
        return az, el, ra, dec, lst

    def __getattr__(self, name):
        return self.params[name]

    def __repr__(self):
        return str.format(
            'AzEl(location={0}, timezone={1}, date={2})',
            self.location['name'], self.timezone['name'], self.date,
        )
