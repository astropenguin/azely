# coding: utf-8

# imported items
__all__ = [
    'request_location_info',
    'get_location_info',
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
def request_location_info(location, date, timeout=5, encoding='utf-8'):
    # get geocode info from google maps
    url = URL_GEOCODE.format(location)
    with urlopen(url, timeout=timeout) as f:
        geocode = yaml.load(f.read().decode(encoding))['results'][0]

    info = {}
    info['name']      = geocode['address_components'][0]['long_name']
    info['address']   = geocode['formatted_address']
    info['place_id']  = geocode['place_id']
    info['latitude']  = geocode['geometry']['location']['lat']
    info['longitude'] = geocode['geometry']['location']['lng']

    # get timezone info from google maps
    t = (date-datetime(1970, 1, 1)).total_seconds() # UNIX time
    url = URL_TIMEZONE.format(info['latitude'], info['longitude'], t)
    with urlopen(url, timeout=timeout) as f:
        timezone = yaml.load(f.read().decode(encoding))

    info['timezone_name'] = timezone['timeZoneName']
    info['timezone_hour'] = (timezone['rawOffset']+timezone['dstOffset']) / 3600
    info['timezone_day']  = date.strftime('%Y-%m-%d')
    return info


def get_location_info(location, date):
    try:
        info = request_location_info(location, date)
        with open(azely.KNOWN_LOCS, 'r') as f:
            dinfo = yaml.load(f)
            dinfo.update({location: info})

        with open(azely.KNOWN_LOCS, 'w') as f:
            f.write(yaml.dump(dinfo, default_flow_style=False))

    except URLError:
        with open(azely.KNOWN_LOCS, 'r') as f:
            dinfo = yaml.load(f)

        if location in dinfo:
            info = dinfo[location]
            if info['timezone_day'] != date.strftime('%Y-%m-%d'):
                print('AzelyWarning: timezone hour might be different')
        else:
            raise azely.AzelyError('error!')

    return info
