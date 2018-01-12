# coding: utf-8

# public items
__all__ = ['get_body',
           'isnumber',
           'isobject',
           'open_googlemaps',
           'parse_date']

# standard library
import re
import webbrowser
from datetime import datetime
from urllib.parse import urlencode

# dependent packages
import azely
import ephem
from astropy.coordinates import SkyCoord

# module constants
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


def isnumber(obj):
    """Whether an object can be converted to number or not."""
    try:
        float(obj)
        return True
    except ValueError:
        return False


def isobject(obj):
    """Whether an object is astronomical object-like or not.

    """
    if isinstance(obj, str):
        return True
    elif isinstance(obj, dict):
        try:
            SkyCoord(**obj)
            return True
        except ValueError:
            return False
    else:
        return False


def open_googlemaps(location):
    """Open Google Maps of given location by a web browser."""
    query = azely.parse_location(location)
    item = azely.Locations()._request_item(query)
    params = {'q': f'{item["latitude"]}, {item["longitude"]}'}
    webbrowser.open(f'{URL_GOOGLEMAPS}?{urlencode(params)}')


def parse_date(date_like=None):
    """Parse date-like object and return format string."""
    if date_like is None:
        return datetime.now().strftime(azely.DATE_FORMAT)
    elif isinstance(date_like, datetime):
        return date_like.strftime(azely.DATE_FORMAT)
    elif isinstance(date_like, str):
        date_like = re.sub(azely.SEPARATORS, '', date_like)
        try:
            dt = datetime.strptime(date_like, '%y%m%d')
            return dt.strftime(azely.DATE_FORMAT)
        except ValueError:
            dt = datetime.strptime(date_like, '%Y%m%d')
            return dt.strftime(azely.DATE_FORMAT)
    else:
        raise ValueError(date_like)
