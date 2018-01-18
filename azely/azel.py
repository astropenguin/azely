# coding: utf-8

# public items
__all__ = [
    'AzEl'
]

# dependent packages
import azely
import ephem
import numpy as np

# module constants
UTC_TO_LST = 1.0027379


# classes
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
