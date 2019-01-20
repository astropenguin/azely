__all__ = ['get_object',
           'get_location',
           'get_datetime',
           'get_timezone']


# standard library
import re
from datetime import timedelta, timezone
from functools import partial
from logging import getLogger
logger = getLogger(__name__)


# dependent packages
import geocoder
import pytz
import pandas as pd
from astropy.coordinates import SkyCoord, name_resolve
from astropy.coordinates import solar_system_ephemeris
from astropy.utils.data import Conf
from dateutil.parser import parse
from timezonefinder import TimezoneFinder


# azely modules
import azely
import azely.utils as utils


# module constants
CONFIG = azely.config
LOCATION_KEYS = {'address', 'timezone', 'latitude', 'longitude'}


# main query functions
@utils.default_kwargs(**CONFIG['object'])
def get_object(query, **kwargs):
    if is_solar(query):
        return {'name': query}

    try:
        return object_offline(query, **kwargs)
    except ValueError:
        return object_online(query, **kwargs)


@utils.default_kwargs(**CONFIG['location'])
def get_location(query=None, **kwargs):
    if query is None:
        return location_here(**kwargs)

    try:
        return location_offline(query, **kwargs)
    except ValueError:
        return location_online(query, **kwargs)


@utils.default_kwargs(**CONFIG['datetime'])
def get_datetime(query=None, **kwargs):
    if query is None:
        return parse_datetime()

    return parse_datetime(*query.split(','), **kwargs)


@utils.default_kwargs(**CONFIG['timezone'])
def get_timezone(query, **kwargs):
    if query is None:
        return None

    try:
        return timezone_utcoffset(query)
    except ValueError:
        return pytz.timezone(query)


# subfunctions for object
def is_solar(query):
    return query.lower() in solar_system_ephemeris.bodies


@utils.cache_to(CONFIG['cache']['object'], CONFIG['cache']['enable'])
def object_online(query, frame='icrs', timeout=5, **kwargs):
    try:
        with Conf.remote_timeout.set_temp(timeout):
            coord = SkyCoord.from_name(query, frame)
    except name_resolve.NameResolveError:
        raise ValueError(query)

    keys = list(coord.get_representation_component_names())[:2]
    values = coord.to_string('hmsdms').split()

    return dict(name=query, frame=frame, **dict(zip(keys, values)))


def object_offline(query, pattern='*.toml', searchdirs=('.',), **kwargs):
    for searchdir in utils.abspath(*searchdirs):
        for path in searchdir.glob(pattern):
            data = utils.read_toml(path)

            if query not in data:
                continue

            object_ = data[query].copy()
            object_.pop('name', None)

            try:
                SkyCoord(**object_)
            except:
                continue

            object_ = data[query]
            object_.setdefault('name', query)
            return object_
    else:
        raise ValueError(query)


# subfunctions for location
def location_here(timeout=5, **ignored_kwargs):
    geo = geocoder.ip('me', timeout=timeout)

    if not geo.ok:
        raise RuntimeError('not connected to a network')

    name = geo.address.split(',')[0]
    tz = TimezoneFinder().timezone_at(lng=geo.lng, lat=geo.lat)

    return {'name': name, 'address': geo.address, 'timezone': tz,
            'longitude': geo.lng, 'latitude': geo.lat}


@utils.cache_to(CONFIG['cache']['location'], CONFIG['cache']['enable'])
def location_online(query, provider='osm', method='geocode',
                    key=None, timeout=5, **ignored_kwargs):
    func = getattr(geocoder, provider)
    geo = func(query, method=method, key=key, timeout=timeout)

    if not geo.ok:
        raise RuntimeError(f'could not find {query}'
                           ' (or not connected to a network)')

    name = getattr(geo, 'name', geo.address.split(',')[0])
    tz = TimezoneFinder().timezone_at(lng=geo.lng, lat=geo.lat)

    return {'name': name, 'address': geo.address, 'timezone': tz,
            'longitude': geo.lng, 'latitude': geo.lat}


def location_offline(query, pattern='*.toml', searchdirs=('.',), **kwargs):
    for searchdir in utils.abspath(*searchdirs):
        for path in searchdir.glob(pattern):
            data = utils.read_toml(path)

            if query not in data:
                continue

            location = data[query].copy()
            location.pop('name', None)

            if location.keys() < LOCATION_KEYS:
                continue

            location = data[query]
            location.setdefault('name', query)
            return location
    else:
        raise ValueError(query)


# subfunctions for datetime
def parse_datetime(start=None, end=None, freq='10min', periods=None,
                   dayfirst=False, yearfirst=False, **kwargs):
    f = partial(parse, dayfirst=dayfirst, yearfirst=yearfirst)

    if (start is None) and (end is None):
        start = end = pd.Timestamp('now', tz=pytz.UTC)
    elif (start is not None) and (end is None):
        start = f(start).date()
        end = start + pd.offsets.Day()
    else:
        start, end = f(start), f(end)

    return pd.date_range(start, end, periods, freq)


# subfunctions for timezone
def timezone_utcoffset(query):
    m = re.search('^(UTC)?([+\-])?([0-9.]+):?([0-9]+)?', query)

    if m is None:
        raise ValueError(query)

    sign, hh, mm = m.groups()[1:]

    sign = +1 if sign != '-' else -1
    mm = 0 if mm is None else mm
    hh, mm = sign*float(hh), sign*float(mm)

    return timezone(timedelta(hours=hh, minutes=mm))