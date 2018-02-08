# public items
__all__ = ['read_yaml',
           'write_yaml',
           'parse_date',
           'parse_keyword',
           'open_googlemaps']

# standard library
import re
import webbrowser
from collections import OrderedDict
from datetime import datetime
from itertools import chain
from logging import getLogger
from pathlib import Path
from urllib.parse import urlencode
logger = getLogger(__name__)

# dependent packages
import azely
import yaml

# module constants
DATE_FORMAT = '%Y-%m-%d'
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
    this function will return an empty (ordered) dictionary.

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

    with Path(path).open(mode=mode, encoding=encoding) as f:
        try:
            if keep_order:
                return yaml.load(f) or OrderedDict()
            else:
                Loader = yaml.loader.SafeLoader
                return yaml.load(f, Loader) or dict()
        except Exception:
            logger.warning(f'fail to load {path}')
            return OrderedDict() if keep_order else dict()


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

    with Path(path).open(mode=mode, encoding=encoding) as f:
        try:
            f.write(stream)
        except Exception:
            logger.warning(f'fail to write data to {path}')


def parse_keyword(keyword_like, seps=','):
    """Parse keyword-like object and return iterator that yields keywords.

    For example, the following objects will be interpreted as
    iter(['a', 'b', 'c']) by this function if `seps` is comma::

        >>> parse_keyword('a, b, c')
        >>> parse_keyword(['a, b, c'])
        >>> parse_keyword(['a', 'b, c'])
        >>> parse_keyword(['a', 'b', 'c'])

    Args:
        keyword_like (str or sequence of str): Keyword-like object.
        seps (str, optional): Separators for `keyword_like`. Default is ','.

    Returns:
        keywords (iterator): Iterator that yields keywords.

    """
    logger.debug(f'keyword_like = {keyword_like}')
    logger.debug(f'seps = {seps}')

    if isinstance(keyword_like, (list, tuple)):
        return chain(*(parse_keyword(kwd) for kwd in keyword_like))
    elif isinstance(keyword_like, str):
        replaced = re.sub(f'[{seps}]+', seps[0], keyword_like)
        splitted = replaced.split(seps[0])
        return (s.strip() for s in splitted if s.strip())
    else:
        logger.error(f'ValueError: {keyword_like}')
        raise ValueError(keyword_like)


def parse_date(date_like=None, *, return_datetime=False):
    """Parse date-like object and return formatted string.

    Args:
        date_like (str or datetime object): Date-like object such as
            '2018-01-23', '18.01.23', '1/23', or datetime.datetime.now().
            If `date_like` has no year info, then current year is used.
            If not spacified, then current local date is used. supported
            separators for `date_like` are hyphen (-), slash (/), or dot (.).
        return_datetime (bool, optional, keyword-only): If True, this function
            will return datetime object (datetime.datetime) instead of
            formatted string. Default is False.

    Returns:
        date (str): Formatted date string (YYYY-mm-dd). If `return_datetime`
            is True, datetime object (midnight of given date) will be returned.

    """
    logger.debug(f'date_like = {date_like}')
    logger.debug(f'return_datetime = {return_datetime}')

    now = datetime.now()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)

    def postproc(dt):
        return dt if return_datetime else dt.strftime(DATE_FORMAT)

    if not date_like:
        return postproc(now)
    elif isinstance(date_like, datetime):
        return postproc(date_like)
    elif isinstance(date_like, str):
        date = ''.join(azely.parse_keyword(date_like, '/\.\-'))

        try:
            dt = datetime.strptime(date, '%m%d')
            return postproc(dt.replace(year=now.year))
        except ValueError:
            for fmt in ('%y%m%d', '%Y%m%d'):
                try:
                    return postproc(datetime.strptime(date, fmt))
                except ValueError:
                    pass
            else:
                logger.error(f'ValueError: {date_like}')
                raise ValueError(date_like)
    else:
        logger.error(f'ValueError: {date_like}')
        raise ValueError(date_like)


def open_googlemaps(name):
    """Open Google Maps of given location by a web browser.

    Args:
        name (str): Location's name (address) such as 'tokyo',
            'san pedro de atacama', or '2-21-1 osawa mitaka'.

    Returns:
        This function returns nothing.

    """
    logger.debug(f'name = {name}')

    query = ' '.join(azely.parse_name(name))
    location = azely.Locations()._request_location(query)
    params = {'q': f'{location["latitude"]}, {location["longitude"]}'}
    webbrowser.open(f'{URL_GOOGLEMAPS}?{urlencode(params)}')
