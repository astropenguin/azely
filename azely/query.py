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
import azely.config as config
import azely.utils as utils


# main query functions
@utils.default_kwargs(**config['location'])
def get_location(query=None, **kwargs):
    if query is None:
        return geolocate(**kwargs)
    else:
        return find_place(query, **kwargs)


@utils.default_kwargs(**config['object'])
def get_object(query, **kwargs):
    if is_solar(query):
        return {'name': query}

    try:
        return from_local(query, **kwargs)
    except ValueError:
        return from_remote(query, **kwargs)


@utils.default_kwargs(**config['time'])
def get_time(query=None, **kwargs):
    if query is None:
        return parse_time()

    return parse_time(*query.split(','), **kwargs)


@utils.default_kwargs(**config['timezone'])
def get_timezone(query, **kwargs):
    try:
        return from_number(query)
    except ValueError:
        return pytz.timezone(query)


# subfunctions for location
def is_solar(query):
    return query.lower() in solar_system_ephemeris.bodies


def geolocate(**kwargs):
    client = googlemaps.Client(**kwargs)

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


@utils.cache_to(config['cache']['location'], config['cache']['enable'])
def find_place(query, **kwargs):
    client = googlemaps.Client(**kwargs)

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


# subfunctions for object
@utils.cache_to(config['cache']['object'], config['cache']['enable'])
def from_remote(query, frame='icrs', timeout=5, **kwargs):
    try:
        with Conf.remote_timeout.set_temp(timeout):
            coord = SkyCoord.from_name(query, frame)
            ra, dec = coord.to_string('hmsdms').split()
    except name_resolve.NameResolveError:
        raise ValueError(query)

    return {'name': query, 'ra': ra, 'dec': dec, 'frame': frame}


def from_local(query, pattern='*.toml', searchdirs=('.',), **kwargs):
    for searchdir in utils.to_abspath(*searchdirs):
        for path in searchdir.glob(pattern):
            data = utils.read_toml(path)

            if query not in data:
                continue

            try:
                obj = data[query].copy()
                obj.pop('name', None)
                SkyCoord(**obj)
            except:
                continue

            obj = data[query].copy()
            obj.setdefault('name', query)
            return obj
    else:
        raise ValueError(query)


# subfunctions for time
def parse_time(start=None, end=None, periods=None, freq='1h',
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
def from_number(number):
    try:
        zone = f'Etc/GMT{int(number):+d}'
        return pytz.timezone(zone)
    except pytz.UnknownTimeZoneError:
        raise ValueError(number)