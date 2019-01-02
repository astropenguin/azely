__all__ = ['AzEl',
           'compute_azel']


# standard library
from logging import getLogger
logger = getLogger(__name__)

# dependent packages
import azely
import pandas as pd
from astropy.coordinates import get_body
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.time import Time


# Azely's azel class
class AzEl(SkyCoord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def at(self, time=None, timezone=None):
        object_ = self.info.meta['object']
        location = self.info.meta['location']

        return compute_azel(object_, location, time, timezone)

    @property
    def time_index(self):
        utc = self.obstime.to_datetime()
        timezone = self.info.meta['timezone']

        index = pd.Index(utc, name=timezone.zone)
        return index.tz_localize('UTC').tz_convert(timezone)

    @property
    def az(self):
        data = {'Az (deg)': SkyCoord(self).az}
        return pd.DataFrame(data, self.time_index)

    @property
    def el(self):
        data = {'El (deg)': SkyCoord(self).alt}
        return pd.DataFrame(data, self.time_index)

    @property
    def ra(self):
        data = {'R.A. (deg)': SkyCoord(self.icrs).ra}
        return pd.DataFrame(data, self.time_index)

    @property
    def dec(self):
        data = {'Dec. (deg)': SkyCoord(self.icrs).dec}
        return pd.DataFrame(data, self.time_index)

    @property
    def l(self):
        data = {'l (deg)': SkyCoord(self.galactic).l}
        return pd.DataFrame(data, self.time_index)

    @property
    def b(self):
        data = {'l (deg)': SkyCoord(self.galactic).b}
        return pd.DataFrame(data, self.time_index)

    @property
    def lst(self):
        data = {'LST (hourangle)': self.obstime.sidereal_time('mean')}
        return pd.DataFrame(data, self.time_index)

    @property
    def utc(self):
        data = {'UTC': self.obstime.utc}
        return pd.DataFrame(data, self.time_index)

    def __repr__(self):
        obj = self.info.meta['object']['name']
        loc = self.info.meta['location']['name']
        tz  = self.info.meta['timezone'].zone

        return f'AzEl({obj} / {loc} / {tz})'


# function for azel computation
def compute_azel(object_, location=None, time=None, timezone=None):
    if isinstance(object_, str):
        object_ = azely.get_object(object_)

    if isinstance(location, str) or (location is None):
        location = azely.get_location(location)

    if isinstance(time, str) or (time is None):
        time = azely.get_time(time)

    if isinstance(timezone, (str, int, float)):
        timezone = azely.get_timezone(timezone)

    if timezone is None:
        timezone = azely.get_timezone(location['timezone'])

    # create astropy's time
    obstime = create_obstime(location, time, timezone)

    # create astropy's skycoord
    altaz = create_altaz(object_, obstime)

    # update skycoord's information
    altaz.info.meta = {'object': object_,
                       'location': location,
                       'timezone': timezone}

    return AzEl(altaz)


# subfunctions for azel computation
def create_obstime(location, time, timezone):
    if time.tzinfo is None:
        time = time.tz_localize(timezone).tz_convert('UTC')

    location = EarthLocation(lat=location['latitude'],
                             lon=location['longitude'],
                             height=location['altitude'])

    return Time(time, location=location)


def create_altaz(object_, obstime):
    object_ = object_.copy()
    name = object_.pop('name')

    try:
        coord = get_body(name, time=obstime)
    except:
        coord = SkyCoord(**object_, obstime=obstime)
    finally:
        coord.location = obstime.location

    return coord.altaz