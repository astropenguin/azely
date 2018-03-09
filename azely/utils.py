# public items
__all__ = ['set_date',
           'read_yaml',
           'write_yaml',
           'flatten',
           'parse_date',
           'parse_keyword',
           'open_googlemaps']

# standard library
import re
import sys
import webbrowser
from contextlib import contextmanager
from collections import OrderedDict
from copy import copy
from datetime import datetime
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


# classes
class OrderedLoader(yaml.Loader):
    """Util: YAML loader for keeping order of items.

    This class is intended to be used internally.
    Its instance is only used in `azely.read_yaml`.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

        def constructor(loader, node):
            return OrderedDict(loader.construct_pairs(node))

        self.add_constructor(tag, constructor)


class DateManager(object):
    """Util: context manager class for global date, `azely.DATE`.

    This class is intended to be used internally.
    Its instance is only used in `azely.set_date`.

    """
    def __init__(self, date_like=None):
        """Create (initialize) date manager instance.

        Its instance immediately changes `azely.DATE` with given date
        with this initialization. If it is used as context manager,
        `azely.DATE` reverts to old value outside a with block.

        Args:
            date_like (str or datetime object): Date-like object. Acceptable
                values are same as those for `azely.parse_date` (see its help).

        """
        logger.debug(f'date_like = {date_like}')

        self.date_old = copy(azely.DATE)
        self.date_new = azely.parse_date(date_like)

        logger.debug(f'{self.date_old} -> {self.date_new}')
        azely.DATE = self.date_new

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug(f'{self.date_new} -> {self.date_old}')
        azely.DATE = self.date_old


# functions
def set_date(date_like=None):
    """Util: set global date used for Azely's calculations.

    This function changes `azely.DATE` with given date, whose value is used
    for calulating azimuth/elevation of astronomical objects as well as
    requesting timezone information of a location::

        >>> azely.set_date('2018-01-01')
        >>> print(azely.DATE)
        2018-01-01

    It also works as context manager for a temporal change of `azely.DATE`::

        >>> print(azely.DATE)
        2018-01-01

        >>> with azely.set_date('2018-07-31'):
        ...     print(azely.DATE)
        2018-07-31

        >>> print(azely.DATE)
        2018-01-01

    Args:
        date_like (str or datetime object): Date-like object. Acceptable
            values are same as those for `azely.parse_date` (see its help).

    Returns:
        This function returns nothing.

    """
    logger.debug(f'date_like = {date_like}')
    return DateManager(date_like)


def read_yaml(path, keep_order=False, *, mode='r', encoding='utf-8'):
    """Util: read YAML file safely and return (ordered) dictionary.

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

    emptydict = OrderedDict() if keep_order else dict()
    Loader = OrderedLoader if keep_order else yaml.Loader

    with Path(path).open(mode=mode, encoding=encoding) as f:
        try:
            return yaml.load(f, Loader) or emptydict
        except Exception:
            logger.warning(f'fail to load {path}')
            return emptydict


def write_yaml(path, data, flow_style=False, *, mode='w', encoding='utf-8'):
    """Util: write dictionary data safely to YAML file.

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
        stream = yaml.dump(data, default_flow_style=flow_style)
    except Exception:
        logger.warning('fail to convert data to YAML')
        return None

    with Path(path).open(mode=mode, encoding=encoding) as f:
        try:
            f.write(stream)
        except Exception:
            logger.warning(f'fail to write data to {path}')


def flatten(sequence, depth=None, *, exclude_classes=(str, dict)):
    """Util: flatten a sequence object of specific type.

    For example, [1,2,3, [4,5,[6]]] will be interpreted as
    iter([1, 2, 3, 4, 5, 6]) with defualt optional arguments.

    Args:
        sequence (sequence): Sequence object to be flattened.
        depth (int, optional): Maximum depth of flattening.
            Default is None (recursively flatten with unlimited depth).
        exclude_classes (class or tuple of class, optional, keyword-only):
            Classes whose instances are not flattened. Default is (dict, str).

    Returns:
        flattened (iterator): Iterator that yields flattened elements.

    """
    logger.debug(f'sequence = {sequence}')
    logger.debug(f'depth = {depth}')
    logger.debug(f'exclude_classes = {exclude_classes}')

    if depth is None:
        depth = sys.getrecursionlimit()

    if (depth+1
        and hasattr(sequence, '__iter__')
        and not isinstance(sequence, exclude_classes)):
        # recursively flatten each element
        for element in sequence:
            yield from flatten(element, depth-1,
                               exclude_classes=exclude_classes)
    else:
        yield sequence


def parse_keyword(keyword_like, *, seps=','):
    """Util: parse keyword-like object and return iterator that yields keywords.

    For example, the following objects will be interpreted as
    iter(['a', 'b', 'c']) by this function if `seps` is comma::

        >>> parse_keyword('a, b, c')
        >>> parse_keyword(['a, b, c'])
        >>> parse_keyword(['a', 'b, c'])
        >>> parse_keyword(['a', 'b', 'c'])

    Args:
        keyword_like (str or sequence of str): Keyword-like object.
        seps (str, optional, keyword-only): Separator(s) for `keyword_like`.
            Default is ',' (comma). Note that `seps` is used as a reqular
            expression patterns like '[seps]+'.

    Returns:
        keywords (iterator): Iterator that yields keywords.

    """
    logger.debug(f'keyword_like = {keyword_like}')
    logger.debug(f'seps = {seps}')

    if not isinstance(keyword_like, (list, tuple, str)):
        logger.error(f'ValueError: {keyword_like}')
        raise ValueError(keyword_like)

    joined = seps[0].join(azely.flatten(keyword_like))
    replaced = re.sub(f'[{seps}]+', seps[0], joined)
    splitted = replaced.split(seps[0])
    return (s.strip() for s in splitted if s.strip())


def parse_date(date_like=None, *, return_datetime=False):
    """Util: parse date-like object and return formatted string.

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

    def convert(dt):
        return dt if return_datetime else dt.strftime(DATE_FORMAT)

    def parse(date, formats):
        for fmt in formats:
            try:
                return datetime.strptime(date, fmt)
            except ValueError:
                continue

        raise ValueError(date_like)

    now = datetime.now()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if date_like is None:
        return convert(now)

    if isinstance(date_like, datetime):
        return convert(date_like)

    if isinstance(date_like, str):
        seps = '/\.\-' # slash or dot or hyphen
        date = '-'.join(azely.parse_keyword(date_like, seps=seps))
        try:
            # if year is not spacified
            dt = parse(date, ('%m%d', '%m-%d'))
            return convert(dt.replace(year=now.year))
        except ValueError:
            dt = parse(date, ('%y%m%d', '%Y%m%d',
                              '%y-%m-%d', '%Y-%m-%d'))
            return convert(dt)

    logger.error(f'ValueError: {date_like}')
    raise ValueError(date_like)


def open_googlemaps(name):
    """Util: open Google Maps of given location by a web browser.

    Args:
        name (str): Location's name (address) such as 'tokyo',
            'san pedro de atacama', or '2-21-1 osawa mitaka'.

    Returns:
        This function returns nothing.

    """
    logger.debug(f'name = {name}')

    query = ' '.join(azely.parse_keyword(name))
    location = azely.Locations()._request_location(query)
    params = {'q': f'{location["latitude"]}, {location["longitude"]}'}
    webbrowser.open(f'{URL_GOOGLEMAPS}?{urlencode(params)}')
