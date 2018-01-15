# coding: utf-8

# public items
__all__ = ['get_body',
           'islst',
           'isnumber',
           'read_yaml',
           'write_yaml',
           'open_googlemaps',
           'parse_date']

# standard library
import re
import webbrowser
from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode

# dependent packages
import azely
import ephem
import yaml
from astropy.coordinates import SkyCoord

# module constants
URL_GOOGLEMAPS = 'https://www.google.com/maps'

# use OrderedDict in PyYAML by default
yaml.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: OrderedDict(loader.construct_pairs(node))
)

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


def islst(string):
    """Whether a string can be interpreted as local sideral time."""
    if not isinstance(string, str):
        return False

    pattern = f'[{azely.SEPARATORS}]+'
    string = re.sub(pattern, ' ', string).upper()
    return string == 'LST' or string == 'LOCAL SIDEREAL TIME'


def isnumber(obj):
    """Whether an object can be converted to number or not."""
    try:
        float(obj)
        return True
    except ValueError:
        return False


def read_yaml(filepath, keep_order=False):
    with filepath.open('r') as f:
        try:
            if keep_order:
                result = yaml.load(f)
            else:
                Loader = yaml.loader.SafeLoader
                result = yaml.load(f, Loader)
        except:
            # fail to load yaml
            print('logging later!')
            return {}

    if not result:
        # empty file
        return {}
    else:
        # valid yaml
        return result


def write_yaml(filepath, data, flow_style=False):
    with filepath.open('w') as f:
        try:
            if flow_style:
                f.write(yaml.dump(data))
            else:
                f.write(yaml.dump(data, default_flow_style=False))
        except:
            # fail to write yaml
            print('logging later!')


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
        pattern = f'[{azely.SEPARATORS}]+'
        date_like = re.sub(pattern, '', date_like)
        try:
            dt = datetime.strptime(date_like, '%y%m%d')
            return dt.strftime(azely.DATE_FORMAT)
        except ValueError:
            dt = datetime.strptime(date_like, '%Y%m%d')
            return dt.strftime(azely.DATE_FORMAT)
    else:
        raise ValueError(date_like)
