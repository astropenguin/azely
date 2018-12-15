__all__ = ['get_location',
           'get_object']


# standard library
from copy import deepcopy
from time import mktime
from pathlib import Path
from logging import getLogger
logger = getLogger(__name__)


# dependent packages
import azely
import googlemaps


# main query functions
@azely.default_kwargs(azely.config['location'])
def get_location(query=None, date=None, **kwargs):
    geo = get_geometry(query, **kwargs)

    try:
        tz = get_timezone(query, date, **kwargs)
        return {**geo, **tz}
    except:
        return geo


@azely.default_kwargs(azely.config['object'])
def get_object(query, **kwargs):
    if azely.is_solar(query):
        return {'name': query, 'solar': True}

    try:
        return get_local(query, **kwargs)
    except ValueError:
        return get_remote(query, **kwargs)


# sub query functions
@azely.cache_to(azely.config['cache']['location'],
                azely.config['cache']['enable'])
def get_geometry(query=None, **kwargs):
    client = googlemaps.Client(**kwargs)

    # coordinates
    if query is None:
        result = client.geolocate()

        name = 'Current Location'
        addr = ''
        pid  = ''
        lat  = result['location']['lat']
        lng  = result['location']['lng']
    else:
        result = client.places(query)['results'][0]

        name = result['name']
        addr = result['formatted_address']
        pid  = result['place_id']
        lat  = result['geometry']['location']['lat']
        lng  = result['geometry']['location']['lng']

    # altitude
    result = client.elevation((lat, lng))[0]
    alt = result['elevation']

    # timezone (DST is not considered)
    ts = mktime(azely.parse_date().timetuple())

    result = client.timezone((lat, lng), ts)
    tz_name = result['timeZoneId']
    tz_hour = result['rawOffset'] / 3600

    return {'name': name, 'address': addr, 'place_id': pid,
            'latitude': lat, 'longitude': lng, 'altitude': alt,
            'timezone_name': tz_name, 'timezone_hour': tz_hour}


def get_timezone(query=None, date=None, **kwargs):
    client = googlemaps.Client(**kwargs)

    geo = get_geometry(query, **kwargs)
    lat, lng = geo['latitude'], geo['longitude']

    ts = mktime(azely.parse_date(date).timetuple())
    result = client.timezone((lat, lng), ts)
    tz_name = result['timeZoneName']
    tz_hour = (result['rawOffset']+result['dstOffset']) / 3600

    return {'timezone_name': tz_name, 'timezone_hour': tz_hour}


@azely.cache_to(azely.config['cache']['object'],
                azely.config['cache']['enable'])
def get_remote(query, frame='icrs', timeout=5, **kwargs):
    from astropy.utils.data import Conf
    from astropy.coordinates import SkyCoord
    from astropy.coordinates.name_resolve import NameResolveError

    try:
        with Conf.remote_timeout.set_temp(timeout):
            coord = SkyCoord.from_name(query, frame)
            ra, dec = coord.to_string('hmsdms').split()
    except NameResolveError:
        raise ValueError(query)

    return {'name': query, 'solar': False,
            'ra': ra, 'dec': dec, 'frame': frame}


def get_local(query, pattern='*.toml', searchdirs=['.'], **kwargs):
    from astropy.coordinates import SkyCoord

    for searchdir in (Path(d).expanduser() for d in searchdirs):
        for path in searchdir.glob(pattern):
            data = azely.read_toml(path)

            if query not in data:
                continue

            try:
                obj = deepcopy(data[query])
                obj.pop('name', None)
                obj.pop('solar', None)
                SkyCoord(**obj)
            except:
                continue

            return data[query]

    raise ValueError(query)