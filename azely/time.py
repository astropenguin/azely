__all__ = ["Time", "get_time"]


# standard library
from datetime import datetime, timedelta, tzinfo


# dependent packages
from dateutil.parser import ParserError, parse
from pandas import DatetimeIndex, date_range
from pytz import UnknownTimeZoneError, timezone
from . import AzelyError, HERE, NOW, TODAY, config
from .location import get_location
from .utils import set_defaults


# constants
PERIOD_SEP = ":"


# data class
class Time(DatetimeIndex):
    """Data class of time (equivalent to pandas.DatetimeIndex)."""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


# main functions
@set_defaults(**config["time"])
def get_time(query: str = NOW, view: str = HERE, freq: str = "10T") -> Time:
    tzinfo = get_tzinfo(view)

    if query == NOW:
        start = end = datetime.now(tzinfo)
    elif query == TODAY:
        start = datetime.now(tzinfo).date()
        end = start + timedelta(days=1)
    elif PERIOD_SEP in query:
        queries = query.split(PERIOD_SEP)
        start, end = map(get_datetime, queries)
    else:
        start = get_datetime(query)
        end = start + timedelta(days=1)

    return Time(date_range(start, end, None, freq, tzinfo))


# helper functions
def get_tzinfo(query: str) -> tzinfo:
    try:
        return timezone(query)
    except UnknownTimeZoneError:
        return timezone(get_location(query).timezone)


def get_datetime(query: str) -> datetime:
    try:
        return parse(query)
    except ParserError:
        raise AzelyError(f"Failed to parse: {query}")
