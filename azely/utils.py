# coding: utf-8

# public items
__all__ = [
    'get_body',
    'get_googlemaps',
    'get_unixtime',
    'isnum',
    'parse_date',
    'parse_location',
    'parse_objects',
]

# standard library
import re
import time
import webbrowser
from datetime import datetime
from urllib.parse import urlencode

# dependent packages
import azely
import ephem

# local constants
DATE_FORMAT = '%Y-%m-%d'
SEPARATORS = '[+\-_&,./|:; ]+'
URL_GOOGLEMAPS = 'https://www.google.com/maps'


# functions
def get_body(object_like):
    if isinstance(object_like, str):
        try:
            return getattr(ephem, object_like)()
        except AttributeError:
            return ephem.star(object_like)
    elif issubclass(type(object_like), dict):
        body = ephem.FixedBody()
        body._ra = ephem.hours(str(object_like['ra']))
        body._dec = ephem.degrees(str(object_like['dec']))
        if 'epoch' in object_like:
            body._epoch = getattr(ephem, object_like['epoch'])
            return body
        else:
            body._epoch = ephem.J2000
            return body
    else:
        raise ValueError(object_like)


def get_googlemaps(name):
    locs = azely.Locations()
    query = azely.parse_location(name)
    item = locs._request_item(query)
    params = {'q': f'{item["latitude"]}, {item["longitude"]}'}
    webbrowser.open(f'{URL_GOOGLEMAPS}?{urlencode(params)}')


def get_unixtime(date_like=None):
    date = datetime.strptime(parse_date(date_like), DATE_FORMAT)
    return time.mktime(date.utctimetuple())


def isnum(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def parse_date(date_like=None):
    if date_like is None:
        return datetime.now().strftime(DATE_FORMAT)
    elif isinstance(date_like, datetime):
        return date_like.strftime(DATE_FORMAT)
    elif type(date_like) == str:
        date_like = re.sub(SEPARATORS, '', date_like)
        try:
            dt = datetime.strptime(date_like, '%y%m%d')
            return dt.strftime(DATE_FORMAT)
        except ValueError:
            dt = datetime.strptime(date_like, '%Y%m%d')
            return dt.strftime(DATE_FORMAT)
    else:
        raise ValueError(date_like)


def parse_location(location_like):
    if type(location_like) in (list, tuple):
        return '+'.join(location_like)
    elif type(location_like) == str:
        return re.sub(SEPARATORS, '+', location_like)
    else:
        raise ValueError(location_like)


def parse_objects(objects_like):
    if type(objects_like) in (list, tuple):
        return objects_like
    elif type(objects_like) == str:
        return re.sub(SEPARATORS, ' ', objects_like).split()
