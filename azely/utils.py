# coding: utf-8

# imported items
__all__ = [
    'AzelyError',
    'AzelyWarning',
    'create_body',
    'get_unixtime',
    'googlemaps',
    'parse_date',
    'parse_location',
    'parse_objects',
]

# standard library
import re
import time
import webbrowser
from datetime import datetime

# dependent packages
import azely
import ephem

# constants
DATE_FORMAT = '%Y-%m-%d'
URL_MAPS = 'https://www.google.com/maps?q={0},{1}'


# classes
class AzelyError(Exception):
    """Error class of Azely."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class AzelyWarning(Warning):
    """Warning class of Azely."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


# functions
def create_body(object_like):
    if isinstance(object_like, str):
        return getattr(ephem, str(object_like))()
    elif issubclass(type(object_like), dict):
        body = ephem.FixedBody()
        body._ra = ephem.hours(str(object_like['ra']))
        body._dec = ephem.degrees(str(object_like['dec']))
        if 'epoch' in object_like:
            body._epoch = getattr(ephem, object_like['epoch'])
        else:
            body._epoch = ephem.J2000

        return body
    else:
        raise ValueError(object_like)


def get_unixtime(date_like=None):
    date = datetime.strptime(parse_date(date_like), DATE_FORMAT)
    return time.mktime(date.utctimetuple())


def googlemaps(name):
    locs = azely.Locations()
    query = azely.parse_location(name)
    item = locs._request_item(query)
    url = URL_MAPS.format(item['latitude'], item['longitude'])
    webbrowser.open(url)


def parse_date(date_like=None):
    if date_like is None:
        return datetime.now().strftime(DATE_FORMAT)
    elif isinstance(date_like, datetime):
        return date_like.strftime(DATE_FORMAT)
    elif type(date_like) == str:
        date_like = re.sub('[+\-_&,./|:; ]+', '', date_like)
        for fmt in ('%y%m%d', '%Y%m%d'):
            try:
                dt = datetime.strptime(date_like, fmt)
                return dt.strftime(DATE_FORMAT)
            except ValueError:
                continue

        raise ValueError(date_like)
    else:
        raise ValueError(date_like)


def parse_location(location_like):
    if type(location_like) in (list, tuple):
        return '+'.join(location_like)
    elif type(location_like) == str:
        return re.sub('[+\-_&,./|:; ]+', '+', location_like)
    else:
        raise ValueError(location_like)


def parse_objects(objects_like):
    if type(objects_like) in (list, tuple):
        return objects_like
    elif type(objects_like) == str:
        return re.sub('[+\-_&,./|:; ]+', ' ', objects_like).split()
