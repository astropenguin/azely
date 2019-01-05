__all__ = ['AzEl',
           'compute_azel']


# standard library
from logging import getLogger
logger = getLogger(__name__)

# dependent packages
import pandas as pd
from astropy.coordinates import get_body
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.time import Time


# azely submodules
import azely.query as query


# Azely's azel class
class AzEl(SkyCoord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def at(self, time=None, timezone=None):
        object_ = self.info.meta['object']
        location = self.info.meta['location']

        return compute_azel(object_, location, time, timezone)

    @property
    def az(self):
        return self._df(SkyCoord(self.altaz).az)

    @property
    def el(self):
        return self._df(SkyCoord(self.altaz).alt)

    @property
    def ra(self):
        return self._df(SkyCoord(self.icrs).ra)

    @property
    def dec(self):
        return self._df(SkyCoord(self.icrs).dec)

    @property
    def l(self):
        return self._df(SkyCoord(self.galactic).l)

    @property
    def b(self):
        return self._df(SkyCoord(self.galactic).b)

    @property
    def utc(self):
        return self._df(self.obstime.utc)

    @property
    def lst(self):
        return self._df(self.obstime.sidereal_time('mean'))

    def _df(self, data):
        name = self.info.meta['object']['name']
        return pd.DataFrame({name: data}, self._df_index())

    def _df_index(self):
        utc = self.obstime.to_datetime()
        timezone = self.info.meta['timezone']

        index = pd.Index(utc, name=timezone.zone)
        return index.tz_localize('UTC').tz_convert(timezone)

    def __repr__(self):
        object_ = self.info.meta['object']['name']
        location = self.info.meta['location']['name']

        return f'AzEl({object_} / {location})'


# functions for azel computation
def compute_azel(object_, location=None, time=None, timezone=None):
    if isinstance(object_, str):
        object_ = query.get_object(object_)

    if isinstance(location, str) or (location is None):
        location = query.get_location(location)

    if isinstance(time, str) or (time is None):
        time = query.get_time(time)

    if isinstance(timezone, (str, int, float)):
        timezone = query.get_timezone(timezone)

    # create astropy's time
    obstime = create_obstime(location, time, timezone)

    # create astropy's skycoord
    coord = create_skycoord(object_, obstime)

    # update skycoord's information
    coord.info.meta = {'object': object_,
                       'location': location,
                       'timezone': timezone}

    return AzEl(coord)


# subfunctions for azel computation
def create_obstime(location, time, timezone):
    if timezone is None:
        timezone = location['timezone']

    if time.tzinfo is None:
        time = time.tz_localize(timezone).tz_convert('UTC')

    location = EarthLocation(lat=location['latitude'],
                             lon=location['longitude'],
                             height=location['altitude'])

    return Time(time, location=location)


def create_skycoord(object_, obstime):
    object_ = object_.copy()
    name = object_.pop('name')

    try:
        coord = get_body(name, time=obstime)
    except:
        coord = SkyCoord(**object_, obstime=obstime)
    finally:
        coord.location = obstime.location

    return coord