__all__ = ['get_object',
           'get_location',
           'get_datetime',
           'get_timezone']


# standard library
from functools import partial
from logging import getLogger
logger = getLogger(__name__)


# dependent packages
import geocoder
import pandas as pd
from dateutil.parser import parse
from dateutil.tz import gettz, UTC
from timezonefinder import TimezoneFinder


# azely modules
import azely
import azely.utils as utils


# module constants
LOCATION_KEYS = {'address', 'timezone', 'latitude', 'longitude'}


# main query functions
def get_object(query, **kwargs):
    try:
        return get_object_local(query, **kwargs)
    except ValueError:
        return get_object_server(query, **kwargs)


def get_location(query=None, **kwargs):
    try:
        return get_location_local(query, **kwargs)
    except ValueError:
        return get_location_server(query, **kwargs)


def get_datetime(query=None, **kwargs):
    if query is None:
        return get_datetime_now()
    else:
        return get_datetime_period(query, **kwargs)


def get_timezone(query=None, **kwargs):
    if query is None:
        return get_timezone_default(**kwargs)
    else:
        return get_timezone_name(query)


# subfunctions for object
def is_valid_object(object_):
    # lazy import
    from astropy.coordinates import SkyCoord

    if not isinstance(object_, dict):
        return False

    object_ = object_.copy()
    object_.pop('name', None)

    try:
        SkyCoord(**object_)
        return True
    except:
        return False


@utils.override_defaults(**azely.config['object'])
def get_object_local(query, pattern='*.toml', searchdirs='.', **_):
    # lazy import
    from astropy.coordinates import solar_system_ephemeris

    if query.lower() in solar_system_ephemeris.bodies:
        return {'name': query}

    for object_ in utils.find_in(query, pattern, searchdirs):
        if not is_valid_object(object_):
            continue

        object_.setdefault('name', query)
        return object_
    else:
        raise ValueError(query)


@utils.cache_to(azely.config['object']['cache'])
@utils.override_defaults(**azely.config['object'])
def get_object_server(query, frame='icrs', timeout=5, **_):
    # lazy import
    from astropy.coordinates import SkyCoord, name_resolve
    from astropy.utils.data import Conf

    try:
        with Conf.remote_timeout.set_temp(timeout):
            coord = SkyCoord.from_name(query, frame)
    except name_resolve.NameResolveError:
        raise ValueError(query)

    keys = list(coord.representation_component_units)
    values = coord.to_string('hmsdms').split()
    coords = dict(zip(keys, values))
    return {'name': query, 'frame': frame, **coords}


# subfunctions for location
def is_valid_location(location):
    if not isinstance(location, dict):
        return False

    return location.keys() >= LOCATION_KEYS


@utils.override_defaults(**azely.config['location'])
def get_location_local(query, pattern='*.toml', searchdirs='.', **_):
    for location in utils.find_in(query, pattern, searchdirs):
        if not is_valid_location(location):
            continue

        location.setdefault('name', query)
        return location
    else:
        raise ValueError(query)


@utils.cache_to(azely.config['location']['cache'])
@utils.override_defaults(**azely.config['location'])
def get_location_server(query=None, provider='osm', key=None,
                        method='geocode', timeout=5, **_):
    if query is None:
        geo = geocoder.ip('me', timeout=timeout)
    else:
        func = getattr(geocoder, provider)
        geo = func(query, method=method, key=key, timeout=timeout)

    if not geo.ok:
        raise RuntimeError('could not find location'
                           'or not connected to a network')

    name = getattr(geo, 'name', geo.address.split(',')[0])
    tz = TimezoneFinder().timezone_at(lng=geo.lng, lat=geo.lat)

    return {'name': name, 'address': geo.address, 'timezone': tz,
            'longitude': geo.lng, 'latitude': geo.lat}


# subfunctions for datetime
def get_datetime_now():
    start = end = pd.Timestamp('now', tz=UTC)
    return pd.date_range(start, end)


@utils.override_defaults(**azely.config['datetime'])
def get_datetime_period(query, frequency='10min',
                        dayfirst=False, yearfirst=False, **_):
    items = query.split(',')
    func = partial(parse, dayfirst=dayfirst, yearfirst=yearfirst)

    if len(items) == 1:
        start = func(items[0])
        end = start + pd.offsets.Day()
    elif len(items) == 2:
        start, end = map(func, items)
    elif len(items) == 3:
        start, end = map(func, items[:2])
        frequency = items[2]
    else:
        raise ValueError(query)

    return pd.date_range(start, end, None, frequency)


# subfunctions for timezone
@utils.override_defaults(**azely.config['timezone'])
def get_timezone_default(default='location', **_):
    if default == 'location':
        return gettz('location')
    elif default == 'localtime':
        return gettz('/etc/localtime')
    else:
        raise ValueError(default)


def get_timezone_name(query):
    tz = gettz(query)

    if tz is not None:
        return tz
    else:
        raise ValueError(query)