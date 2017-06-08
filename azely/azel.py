# coding: utf-8

# imported items
__all__ = ['AzEl']

# dependent packages
import azely
import ephem
import numpy as np

# constants
UT_TO_LST = 1.0027379


# classes
class AzEl(object):
    def __init__(self, observer, timezone=None, date=None):
        self.info = {
            'observer': observer,
            'timezone': timezone,
            'date': azely.parse_date(date),
        }

    def __call__(self, obj, hr=None):
        # body
        body = azely.parse_object(obj)

        # observer
        observer = ephem.Observer()
        observer.lat = str(self.info['observer']['latitude'])
        observer.lon = str(self.info['observer']['longitude'])

        if hr is None:
            observer.date = ephem.now()
        else:
            observer.date = ephem.Date(self.info['date'])

            if self.info['timezone'] is None:
                offset_hr = self.info['observer']['timezone_hour'] % 24
            elif issubclass(type(self.info['timezone']), dict):
                offset_hr = self.info['timezone']['timezone_hour'] % 24
            elif type(self.info['timezone']) in (int, float):
                offset_hr = self.info['timezone'] % 24
            elif self.info['timezone'] == 'LST':
                st = observer.sidereal_time()
                offset_hr = st / (2*np.pi) * 24 / UT_TO_LST
            else:
                raise ValueError(self.info['timezone'])

            observer.date -= offset_hr * ephem.hour

        # compute
        coords = []
        names = ['Az', 'El', 'RA', 'Dec', 'LST']
        hrs = [hr] if not hasattr(hr, '__iter__') else hr
        for hr in hrs:
            coords.append(self._compute(body, observer, hr))

        return np.rec.fromarrays(np.array(coords).T, names=names)

    def _compute(self, body, observer, hr=None):
        observer = observer.copy()

        if hr is not None:
            if self.info['timezone'] == 'LST':
                observer.date += hr * ephem.hour / UT_TO_LST
            else:
                observer.date += hr * ephem.hour

        body.compute(observer)
        az, el  = np.rad2deg([body.az, body.alt])
        ra, dec = np.rad2deg([body.ra, body.dec])
        lst = observer.sidereal_time() / (2*np.pi) * 24
        return az, el, ra, dec, lst
