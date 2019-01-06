__all__ = ['get_location',
           'get_object',
           'get_time',
           'get_timezone']


# standard library
from functools import partial
from logging import getLogger
logger = getLogger(__name__)


# dependent packages
import googlemaps
import pytz
import pandas as pd
from astropy.coordinates import SkyCoord, name_resolve
from astropy.coordinates import solar_system_ephemeris
from astropy.utils.data import Conf
from dateutil.parser import parse


# azely submodules
import azely
import azely.utils as utils


# module constants
CONFIG = azely.config
LOCATION_KEYS = {'address', 'timezone',
                 'latitude', 'longitude', 'altitude'}


# main query functions
@utils.default_kwargs(**CONFIG['location'])
def get_location(query=None, **kwargs):
    if query is None:
        return location_here(**kwargs)

    try:
        return location_offline(query, **kwargs)
    except ValueError:
        return location_online(query, **kwargs)


@utils.default_kwargs(**CONFIG['object'])
def get_object(query, **kwargs):
    if is_solar(query):
        return {'name': query}

    try:
        return object_offline(query, **kwargs)
    except ValueError:
        return object_online(query, **kwargs)


@utils.default_kwargs(**CONFIG['time'])
def get_time(query=None, **kwargs):
    if query is None:
        return parse_time()

    return parse_time(*query.split(','), **kwargs)


@utils.default_kwargs(**CONFIG['timezone'])
def get_timezone(query, **kwargs):
    if query is None:
        return None

    try:
        return parse_number(query)
    except ValueError:
        return pytz.timezone(query)


# subfunctions for location
def is_solar(query):
    return query.lower() in solar_system_ephemeris.bodies


def location_here(key, timeout=5, **kwargs):
    client = googlemaps.Client(key, timeout=timeout)

    # coordinates
    result = client.geolocate()
    name = 'Current Location'
    addr = ''
    lat = result['location']['lat']
    lng = result['location']['lng']

    # altitude
    result = client.elevation((lat, lng))[0]
    alt = result['elevation']

    # timezone
    result = client.timezone((lat, lng))
    tz = result['timeZoneId']

    return {'name': name, 'address': addr, 'timezone': tz,
            'latitude': lat, 'longitude': lng, 'altitude': alt}


@utils.cache_to(CONFIG['cache']['location'], CONFIG['cache']['enable'])
def location_online(query, key, timeout=5, **kwargs):
    client = googlemaps.Client(key, timeout=timeout)

    # coordinates
    result = client.places(query)['results'][0]
    name = result['name']
    addr = result['formatted_address']
    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']

    # altitude
    result = client.elevation((lat, lng))[0]
    alt = result['elevation']

    # timezon
    result = client.timezone((lat, lng))
    tz = result['timeZoneId']

    return {'name': name, 'address': addr, 'timezone': tz,
            'latitude': lat, 'longitude': lng, 'altitude': alt}


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


# subfunctions for object
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


# subfunctions for time
def parse_time(start=None, end=None, freq='10min', periods=None,
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
def parse_number(number):
    try:
        zone = f'Etc/GMT{int(number):+d}'
        return pytz.timezone(zone)
    except pytz.UnknownTimeZoneError:
        raise ValueError(number)