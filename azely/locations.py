# coding: utf-8

# imported items
__all__ = [
    'get_location',
    'request_location',
]

# standard library
from datetime import datetime
from urllib.error import URLError
from urllib.request import urlopen

# dependent packages
import azely
import yaml

# constants
URL_API = 'https://maps.googleapis.com/maps/api'
URL_GEOCODE = URL_API + '/geocode/json?address={0}'
URL_TIMEZONE = URL_API + '/timezone/json?location={0},{1}&timestamp={2}'


# functions
def get_location(name, date):
    with open(azely.KNOWN_LOCS, 'r') as f:
        locations = yaml.load(f)

    if name in locations:
        loc = locations[name]
        if 'query' in loc:
            try:
                loc = request_location(loc['query'], date)
                update_known_locations(name, loc)
            except URLError:
                if not loc['timezone_day'] == date.strftime('%Y-%m-%d'):
                    print('AzelyWarning: timezone hour might be different')
        else:
            print('AzelyWarning: location is not updated (no place_id)')
    else:
        try:
            loc = request_location(name, date)
            update_known_locations(name, loc)
        except URLError:
            raise azely.AzelyError('error!')

    return loc


def request_location(name, date, encoding='utf-8', timeout=5):
    # get geocode from google maps api
    url = URL_GEOCODE.format(name)
    with urlopen(url, timeout=timeout) as f:
        geocode = yaml.load(f.read().decode(encoding))['results'][0]

    loc = {}
    loc['name']      = geocode['address_components'][0]['long_name']
    loc['address']   = geocode['formatted_address']
    loc['latitude']  = geocode['geometry']['location']['lat']
    loc['longitude'] = geocode['geometry']['location']['lng']
    loc['query']     = name

    # get timezone from google maps api
    t = (date-datetime(1970, 1, 1)).total_seconds() # UNIX time
    url = URL_TIMEZONE.format(loc['latitude'], loc['longitude'], t)
    with urlopen(url, timeout=timeout) as f:
        timezone = yaml.load(f.read().decode(encoding))

    loc['timezone_name'] = timezone['timeZoneName']
    loc['timezone_hour'] = (timezone['rawOffset']+timezone['dstOffset']) / 3600
    loc['timezone_date'] = date.strftime('%Y-%m-%d')

    return loc


def update_known_locations(name, loc):
    with open(azely.KNOWN_LOCS, 'r') as f:
        locations = yaml.load(f)

    if name in locations:
        locations[name]['timezone_name'] = loc['timezone_name']
        locations[name]['timezone_hour'] = loc['timezone_hour']
        locations[name]['timezone_date'] = loc['timezone_date']
    else:
        locations[name] = loc

    with open(azely.KNOWN_LOCS, 'w') as f:
        f.write(yaml.dump(locations, default_flow_style=False))
