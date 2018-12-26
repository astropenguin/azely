__all__ = ['get_location',
           'get_object']


# standard library
from pathlib import Path
from logging import getLogger
logger = getLogger(__name__)


# dependent packages
import azely
import googlemaps
from astropy.utils.data import Conf
from astropy.coordinates import SkyCoord
from astropy.coordinates import name_resolve


# main query functions
@azely.default_kwargs(azely.config['location'])
def get_location(query=None, **kwargs):
    if query is None:
        return geolocate(**kwargs)
    else:
        return find_place(query, **kwargs)


@azely.default_kwargs(azely.config['object'])
def get_object(query, **kwargs):
    if azely.is_solar(query):
        return {'name': query}

    try:
        return from_local(query, **kwargs)
    except ValueError:
        return from_remote(query, **kwargs)


# sub query functions
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


@azely.cache_to(azely.config['cache']['location'],
                azely.config['cache']['enable'])
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


@azely.cache_to(azely.config['cache']['object'],
                azely.config['cache']['enable'])
def from_remote(query, frame='icrs', timeout=5, **kwargs):
    try:
        with Conf.remote_timeout.set_temp(timeout):
            coord = SkyCoord.from_name(query, frame)
            ra, dec = coord.to_string('hmsdms').split()
    except name_resolve.NameResolveError:
        raise ValueError(query)

    return {'name': query, 'ra': ra, 'dec': dec, 'frame': frame}


def from_local(query, pattern='*.toml', searchdirs=('.',), **kwargs):
    for searchdir in (Path(d).expanduser() for d in searchdirs):
        for path in searchdir.glob(pattern):
            data = azely.read_toml(path)

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