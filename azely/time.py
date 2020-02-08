from __future__ import annotations


__all__ = ["Time", "get_time"]


# standard library
from datetime import datetime, timedelta, tzinfo


# dependent packages
import pytz
from dateutil.parser import ParserError, parse
from pandas import DatetimeIndex, date_range
from pytz import UnknownTimeZoneError
from . import AzelyError, HERE, NOW, TODAY, config
from .location import get_location
from .utils import set_defaults


# data class
class Time(DatetimeIndex):
    """Data class of time (pandas.DatetimeIndex with properties)."""

    def __new__(cls, *args, **kwargs) -> Time:
        return super().__new__(cls, *args, **kwargs)

    @property
    def as_utc(self) -> Time:
        return Time(self.tz_convert(pytz.UTC))


# main functions
@set_defaults(**config["time"])
def get_time(
    query: str = NOW,
    view: str = HERE,
    freq: str = "10T",
    sep: str = "to",
    timeout: int = 5,
) -> Time:
    tzinfo = get_tzinfo(view, timeout)

    if query == NOW:
        start = end = datetime.now(tzinfo)
    elif query == TODAY:
        start = datetime.now(tzinfo).date()
        end = start + timedelta(days=1)
    elif sep in query:
        queries = query.split(sep)
        start, end = map(get_datetime, queries)
    else:
        start = get_datetime(query)
        end = start + timedelta(days=1)

    return Time(date_range(start, end, None, freq, tzinfo))


# helper functions
def get_tzinfo(query: str, timeout: int) -> tzinfo:
    try:
        return pytz.timezone(query)
    except UnknownTimeZoneError:
        return get_location(query, timeout).tzinfo


def get_datetime(query: str) -> datetime:
    try:
        return parse(query)
    except ParserError:
        raise AzelyError(f"Failed to parse: {query}")
