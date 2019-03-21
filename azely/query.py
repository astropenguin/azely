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
from dateutil.tz import gettz, tzlocal
from timezonefinder import TimezoneFinder


# azely modules
import azely
import azely.utils as utils


# module exceptions
class AzelyQueryError(azely.AzelyError):
    pass


# main query functions
def get_object(query, **kwargs):
    try:
        return get_object_offline(query, **kwargs)
    except AzelyQueryError:
        return get_object_online(query, **kwargs)


def get_location(query=None, **kwargs):
    if query is None:
        return get_location_online('me', 'ip', **kwargs)

    try:
        return get_location_offline(query, **kwargs)
    except AzelyQueryError:
        return get_location_online(query, **kwargs)


def get_datetime(query=None, **kwargs):
    if query is None:
        query = str(pd.Timestamp('now').date())

    return get_datetime_from(query, **kwargs)


def get_timezone(query=None):
    if query is None:
        query = 'location'

    return get_timezone_from(query)


# validators
def is_valid_object(object_):
    if not isinstance(object_, dict):
        return False

    keys = object_.keys()
    name = object_.get('name', '')

    return (keys >= {'ra', 'dec'}
            or keys >= {'l', 'b'}
            or utils.is_solar(name))


def is_valid_location(location):
    if not isinstance(location, dict):
        return False

    keys = location.keys()

    return keys >= {'address', 'timezone',
                    'latitude', 'longitude'}


# subfunctions for object
@utils.set_defaults(**azely.config['object'])
def get_object_offline(query, searchfile='*.toml', searchdirs='.', **_):
    if utils.is_solar(query):
        return {'name': query}

    for object_ in utils.search_for(query, searchfile, searchdirs):
        if not is_valid_object(object_):
            continue

        object_.setdefault('name', query)
        return object_
    else:
        raise AzelyQueryError(query)


@utils.set_defaults(**azely.config['object'])
@utils.cache_to(azely.config['object']['cachefile'])
def get_object_online(query, frame='icrs', timeout=5, **_):
    # lazy import
    from astropy.coordinates import SkyCoord, name_resolve
    from astropy.utils.data import Conf

    try:
        with Conf.remote_timeout.set_temp(timeout):
            coord = SkyCoord.from_name(query, frame)
    except name_resolve.NameResolveError:
        raise AzelyQueryError(query)

    keys = list(coord.representation_component_units)
    values = coord.to_string('hmsdms').split()
    coords = dict(zip(keys, values))

    return {'name': query, 'frame': frame, **coords}


# subfunctions for location
@utils.set_defaults(**azely.config['location'])
def get_location_offline(query, searchfile='*.toml', searchdirs='.', **_):
    for location in utils.search_for(query, searchfile, searchdirs):
        if not is_valid_location(location):
            continue

        location.setdefault('name', query)
        return location
    else:
        raise AzelyQueryError(query)


@utils.set_defaults(**azely.config['location'])
@utils.cache_to(azely.config['location']['cachefile'], '^me$')
def get_location_online(query=None, provider='osm', key=None,
                        method='geocode', timeout=5, **_):
    func = getattr(geocoder, provider)
    geo = func(query, method=method, key=key, timeout=timeout)

    if not geo.ok:
        raise AzelyQueryError(query)

    name = getattr(geo, 'name', geo.address.split(',')[0])
    tz = TimezoneFinder().timezone_at(lng=geo.lng, lat=geo.lat)

    return {'name': name, 'address': geo.address, 'timezone': tz,
            'longitude': geo.lng, 'latitude': geo.lat}


# subfunctions for datetime
@utils.set_defaults(**azely.config['datetime'])
def get_datetime_from(query, frequency='10min', separator=',',
                      dayfirst=False, yearfirst=False, **_):
    items = query.split(separator)
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
        raise AzelyQueryError(query)

    return pd.date_range(start, end, None, frequency)


# subfunctions for timezone
def get_timezone_from(query):
    if query == 'location':
        return None

    if query == 'localtime':
        return tzlocal()

    timezone = gettz(query)

    if timezone is not None:
        return timezone
    else:
        raise AzelyQueryError(query)