# public items
__all__ = ['read_yaml',
           'write_yaml',
           'parse_date',
           'parse_name',
           'open_googlemaps']

# standard library
import re
import webbrowser
from collections import OrderedDict
from datetime import datetime
from logging import getLogger
from urllib.parse import urlencode
logger = getLogger(__name__)

# dependent packages
import azely
import yaml

# module constants
URL_GOOGLEMAPS = 'https://www.google.com/maps'

# use OrderedDict in PyYAML by default
yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                     lambda loader, node: OrderedDict(loader.construct_pairs(node)))

# functions
def read_yaml(path, keep_order=False, *, mode='r', encoding='utf-8'):
    """Read YAML file safely and return (ordered) dictionary.

    User can choose whether keeping order of items in mappings
    when loading a YAML file (see `keep_order` argument).
    If a YAML file is invalid (i.e. syntax error or empty),
    this function will return an empty (ordered) dict.

    Args:
        path (str or path object): File path of YAML.
        keep_order (bool, optional): If True, a YAML is loaded with keeping
            order of items in mappings (i.e. OrderedDict). Default is False.
        mode (str, optional, keyword-only): Mode for file open. Default is 'r'.
        encoding (str, optional, keyword-only): File encoding. Default is 'utf-8'.

    Returns:
        data (dict or OrderedDict): Loaded YAML.
            OrderedDict is returned if `keep_order` is True.

    """
    logger.debug(f'path = {path}')
    logger.debug(f'keep_order = {keep_order}')
    logger.debug(f'mode = {mode}')
    logger.debug(f'encoding = {encoding}')

    with path.open(mode=mode, encoding=encoding) as f:
        try:
            if keep_order:
                return yaml.load(f) or dict()
            else:
                Loader = yaml.loader.SafeLoader
                return yaml.load(f, Loader) or OrderedDict()
        except Exception:
            logger.warning(f'fail to load {path}')
            return dict()


def write_yaml(path, data, flow_style=False, *, mode='w', encoding='utf-8'):
    """Write dictionary data safely to YAML file.

    User can choose style of YAML (flow or block style).
    If data is invalid (e.g. incompatible with YAML format),
    this function does not open a file for protecting existing data.

    Args:
        path (str or path object): File path of YAML.
        data (dict or OrderedDict): Data to be converted to YAML.
        flow_style (bool, optional): If True, data will be written
            with flow style of YAML. Default is False (block style).
        mode (str, optional, keyword-only): Mode for file open. Default is 'w'.
        encoding (str, optional, keyword-only): File encoding. Default is 'utf-8'.

    Returns:
        This function returns nothing.

    """
    logger.debug(f'path = {path}')
    logger.debug(f'flow_style = {flow_style}')
    logger.debug(f'mode = {mode}')
    logger.debug(f'encoding = {encoding}')

    try:
        if flow_style:
            stream = yaml.dump(data, default_flow_style=True)
        else:
            stream = yaml.dump(data, default_flow_style=False)
    except Exception:
        logger.warning('fail to convert data to YAML')
        return None

    with path.open(mode=mode, encoding=encoding) as f:
        try:
            f.write(stream)
        except Exception:
            logger.warning(f'fail to write data to {path}')


def parse_name(name_like, seps=','):
    """Parse name-like object and return tuple of names.

    For example, a string 'NGC 1068, M82, Sun' will be converted
    to a tuple of strings, ('NGC 1068', 'M82', 'Sun') if `seps=','`.

    Args:
        name_like (string or tuple/list of string): Name-like object.
            If type is string, it is split into several strings by `seps`.
        seps (str, optional): Separators for `name_like`. Default is comma (,).

    Returns:
        names (tuple of string): Parsed strings of names.
            If `name_like` is tuple of string, the same object is returned.

    """
    logger.debug(f'name_like = {name_like}')
    logger.debug(f'seps = {seps}')

    if isinstance(name_like, (list, tuple)):
        return tuple(name_like)
    elif isinstance(name_like, str):
        replaced = re.sub(f'[{seps}]+', seps[0], name_like)
        return tuple(s.strip() for s in replaced.split(seps[0]))
    else:
        logger.error(f'ValueError: {name_like}')
        raise ValueError(name_like)


def parse_date(date_like=None, seps='/\.\-'):
    """Parse date-like object and return formatted string.

    Args:
        date_like (str or datetime object): Date-like object such as
            '2018-01-23', '180123', '1/23', or datetime.datetime.now().
            If `date_like` has no year info, then current year is used.
            If not spacified, then current local date is used.
        seps (str, optional): Separators for `date_like`.
            Default is either hyphen (-), slash (/), or dot (.).

    Returns:
        date (str): Formatted date string (YYYY-mm-dd).

    """
    logger.debug(f'date_like = {date_like}')
    logger.debug(f'seps = {seps}')

    dt_now = datetime.now()

    if date_like is None:
        return dt_now.strftime(azely.DATE_FORMAT)
    elif isinstance(date_like, datetime):
        return date_like.strftime(azely.DATE_FORMAT)
    elif isinstance(date_like, str):
        string = ''.join(azely.parse_name(date_like, seps))
        try:
            dt = datetime.strptime(string, '%m%d')
            dt = dt.replace(year=dt_now.year)
            return dt.strftime(azely.DATE_FORMAT)
        except ValueError:
            pass

        try:
            dt = datetime.strptime(string, '%y%m%d')
            return dt.strftime(azely.DATE_FORMAT)
        except ValueError:
            pass

        try:
            dt = datetime.strptime(string, '%Y%m%d')
            return dt.strftime(azely.DATE_FORMAT)
        except ValueError:
            logger.error(f'ValueError: {date_like}')
            raise ValueError(string)
    else:
        logger.error(f'ValueError: {date_like}')
        raise ValueError(date_like)


def open_googlemaps(name):
    """Open Google Maps of given location by a web browser.

    Args:
        name (str): Location name (address) such as `tokyo`,
            `san pedro de atacama`, or `2-21-1 osawa mitaka`.

    Returns:
        This function returns nothing.

    """
    logger.debug(f'name = {name}')

    query = ' '.join(azely.parse_name(name))
    location = azely.Locations()._request_location(query)
    params = {'q': f'{location["latitude"]}, {location["longitude"]}'}
    webbrowser.open(f'{URL_GOOGLEMAPS}?{urlencode(params)}')
