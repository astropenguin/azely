# standard library
from datetime import datetime, timedelta, tzinfo
from functools import partial
from typing import Callable


# dependent packages
from astropy.coordinates import EarthLocation
from astropy.time import Time as ObsTime
from dateutil.parser import parse
from pandas import DatetimeIndex, date_range
from pytz import UnknownTimeZoneError, timezone, utc
from .utils import AzelyError
from .location import get_location

# constants
from .consts import (
    DAYFIRST,
    HERE,
    NOW,
    TODAY,
    FREQ,
    TIMEOUT,
    YEARFIRST,
)

DELIMITER = "to"


# data classes
class Time(DatetimeIndex):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def to_obstime(self, earthloc: EarthLocation) -> ObsTime:
        utc_naive = self.tz_convert(utc).tz_localize(None)
        return ObsTime(utc_naive, location=earthloc)

    def to_index(self) -> DatetimeIndex:
        return DatetimeIndex(self)


# main functions
def get_time(
    query: str = NOW,
    view: str = HERE,
    freq: str = FREQ,
    dayfirst: bool = DAYFIRST,
    yearfirst: bool = YEARFIRST,
    timeout: int = TIMEOUT,
) -> Time:
    try:
        tzinfo = timezone(view)
    except UnknownTimeZoneError:
        tzinfo = get_location(view, timeout).tzinfo

    if query == NOW:
        return Time(get_time_now(tzinfo))
    elif query == TODAY:
        return Time(get_time_today(freq, tzinfo))
    else:
        parser = partial(parse, dayfirst=dayfirst, yearfirst=yearfirst)
        return Time(get_time_period(query, freq, tzinfo, parser))


# helper functions
def get_time_now(tzinfo: tzinfo) -> DatetimeIndex:
    start = end = datetime.now(tzinfo)
    return date_range(start, end, tz=tzinfo, name=tzinfo.zone)


def get_time_today(freq: str, tzinfo: tzinfo) -> DatetimeIndex:
    start = datetime.now(tzinfo).date()
    end = start + timedelta(days=1)
    return date_range(start, end, None, freq, tz=tzinfo, name=tzinfo.zone)


def get_time_period(
    query: str, freq: str, tzinfo: tzinfo, parser: Callable
) -> DatetimeIndex:
    period = query.split(DELIMITER)

    try:
        if len(period) == 1:
            start = parser(period[0])
            end = start + timedelta(days=1)
        else:
            start, end = map(parser, period)
    except ValueError:
        raise AzelyError(f"Failed to parse: {query}")

    return date_range(start, end, None, freq, tz=tzinfo, name=tzinfo.zone)
