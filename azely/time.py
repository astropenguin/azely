__all__ = ["get_time"]


# standard library
from datetime import datetime, timedelta, tzinfo


# dependent packages
import pytz
from dateutil import parser
from pandas import DatetimeIndex, date_range
from pytz import UnknownTimeZoneError
from . import AzelyError
from .consts import DAYFIRST, HERE, NOW, TODAY, FREQ, TIMEOUT, YEARFIRST
from .location import get_location

try:
    from dateutil.parser import ParserError
except ImportError:
    ParserError = ValueError


# constants
DELIMITER = "to"


# main functions
def get_time(
    query: str = NOW,
    view: str = HERE,
    freq: str = FREQ,
    dayfirst: bool = DAYFIRST,
    yearfirst: bool = YEARFIRST,
    timeout: int = TIMEOUT,
) -> DatetimeIndex:
    tzinfo = get_tzinfo(view, timeout)
    name = tzinfo.zone

    if query == NOW:
        start = end = datetime.now(tzinfo)
    elif query == TODAY:
        start = datetime.now(tzinfo).date()
        end = start + timedelta(days=1)
    elif DELIMITER in query:
        queries = query.split(DELIMITER)
        start = get_datetime(queries[0], dayfirst, yearfirst)
        end = get_datetime(queries[1], dayfirst, yearfirst)
    else:
        start = get_datetime(query, dayfirst, yearfirst)
        end = start + timedelta(days=1)

    return date_range(start, end, None, freq, tzinfo, name=name)


# helper functions
def get_tzinfo(query: str, timeout: int) -> tzinfo:
    try:
        return pytz.timezone(query)
    except UnknownTimeZoneError:
        return get_location(query, timeout).tzinfo


def get_datetime(query: str, dayfirst: bool, yearfirst: bool) -> datetime:
    try:
        return parser.parse(query, dayfirst=dayfirst, yearfirst=yearfirst)
    except ParserError:
        raise AzelyError(f"Failed to parse: {query}")
