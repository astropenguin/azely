__all__ = ['get_location',
           'get_geometry',
           'get_timezone']


# standard library
from time import mktime
from pathlib import Path
from logging import getLogger
logger = getLogger(__name__)


# dependent packages
import azely
import googlemaps


def get_location(query=None, date=None, **kwargs):
    geo = get_geometry(query, **kwargs)

    try:
        tz = get_timezone(query, date, **kwargs)
        return {**geo, **tz}
    except:
        return geo


@azely.cache_to(azely.config['caches']['locations'])
@azely.default_kwargs(azely.config['locations'])
def get_geometry(query=None, **kwargs):
    client = googlemaps.Client(**kwargs)

    # coordinates
    if query is None:
        result = client.geolocate()

        name = 'Current location'
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


@azely.default_kwargs(azely.config['locations'])
def get_timezone(query=None, date=None, **kwargs):
    client = googlemaps.Client(**kwargs)

    geo = get_geometry(query, **kwargs)
    lat, lng = geo['latitude'], geo['longitude']

    ts = mktime(azely.parse_date(date).timetuple())
    result = client.timezone((lat, lng), ts)
    tz_name = result['timeZoneName']
    tz_hour = (result['rawOffset']+result['dstOffset']) / 3600

    return {'timezone_name': tz_name, 'timezone_hour': tz_hour}