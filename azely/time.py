"""Azely's time module (mid-level API).

This module mainly provides `Time` class for date and time information at a
given location (time information, hereafter) and `get_time` function to obtain
time information as an instance of `Time` class.

The `Time` class is subclass of `pandas.DatetimeIndex` and expressed like:
`Time(['2020-02-18'], dtype='datetime64[ns, Asia/Tokyo]', name='Asia/Tokyo', freq='D')`.

The `get_time` function computes time information in several cases:
(1) Current time (e.g., [2020-01-01 22:32:58+09:00]).
(2) Time range today (e.g., [2020-01-01 00:00, ..., 2020-01-02 00:00])
(3) Time range of given date and length (by query)

In the cases of (1) and (2), special queries, `'now'` and `'today'`, must be
specified, respectively. The `view` option specifies a timezone where
time (range) is considered (timezone or location name can be accepted).

In the case of (3), formatted query (e.g., `'2020-01-01 to 2020-01-05'`)
or natural language-like query can be used (e.g., `'Jan. 1st to Jan. 5th'`),
where start and end must be separated by `'to'`. The `view` option also works.

Examples:
    To get current time in Tokyo (by default)::

        >>> time = azely.time.get_time('now', view="Tokyo")

    To get current time in UTC::

        >>> time = azely.time.get_time('now', view="UTC")

    To get time range today at ALMA AOS::

        >>> time = azely.time.get_time('today', view="ALMA AOS")

    To get time range from Jan. 1 to Jan. 5 in 2020 in UTC::

        >>> time = azely.time.get_time('2020-01-01 to 2020-01-05', view='UTC')

"""
__all__ = ["Time", "get_time"]


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
    """Azely's time information class."""

    def to_obstime(self, earthloc: EarthLocation) -> ObsTime:
        """Convert it to an astropy's time (obstime)."""
        utc_naive = self.tz_convert(utc).tz_localize(None)
        return ObsTime(utc_naive, location=earthloc)

    def to_index(self) -> DatetimeIndex:
        """Convert it to a pandas DatetimeIndex."""
        return DatetimeIndex(self)

    @property
    def _constructor(self):
        """Constructor of class."""
        return Time


# main functions
def get_time(
    query: str = NOW,
    view: str = HERE,
    freq: str = FREQ,
    dayfirst: bool = DAYFIRST,
    yearfirst: bool = YEARFIRST,
    timeout: int = TIMEOUT,
) -> Time:
    """Get time information by various ways.

    Args:
        query: Query string (e.g., `'2020-01-01 to 2020-01-05'`). If `'now'`
            (by default) or `'today'` is specified, then current time
            or time range today is computed, respectively.
        view: Name of timezone (e.g., `'Asia/Tokyo'` or `'UTC'`) or location
            with which timezone can be identified (e.g., `'Tokyo'`).
        freq: Frequency of time samples as the same format of pandas offset aliases
            (e.g., `'1D'` -> 1 day, `'3H'` -> 3 hours, `'10T'` -> 10 minutes).
        dayfirst: Whether to interpret the first value in an ambiguous 3-integer
            date (e.g., `'01-02-03'`) as the day. If True, for example,
            `'01-02-03'` is treated as Feb. 1st 2003.
        yearfirst: Whether to interpret the first value in an ambiguous 3-integer
            date (e.g., `'01-02-03'`) as the year. If True, for example,
            `'01-02-03'` is treated as Feb. 3rd 2001. If `dayfirst` is also `True`,
            then it will be Mar. 2nd 2001.
        timeout: Query timeout expressed in units of seconds (see notes).

    Returns:
        Time information as an instance of `Time` class.

    Raises:
        AzelyError: Raised if the function fails to parse query or timezone.

    The `get_time` function computes time information in several cases:
    (1) Current time (e.g., [2020-01-01 22:32:58+09:00]).
    (2) Time range of today (e.g., [2020-01-01 00:00, ..., 2020-01-02 00:00])
    (3) Time range of given date and length (by query)

    In the cases of (1) and (2), special queries, `'now'` and `'today'`, must be
    specified, respectively. The `view` option specifies a timezone where
    time (range) is considered (timezone or location name can be accepted).

    In the case of (3), formatted query (e.g., `'2020-01-01 to 2020-01-05'`)
    or natural language-like query can be used (e.g., `'Jan. 1st to Jan. 5th'`),
    where start and end must be separated by `'to'`. The `view` option also works.

    Notes:
        If location is specified as `view`, then `azely.location.get_location`
        function is used inside the function, which requires internet connection
        if the location is queried for the first time.

    Examples:
        To get current time in Tokyo (by default)::

            >>> time = azely.time.get_time('now', view="Tokyo")

        To get current time in UTC::

            >>> time = azely.time.get_time('now', view="UTC")

        To get time range of today at ALMA AOS::

            >>> time = azely.time.get_time('today', view="ALMA AOS")

        To get time range from Jan. 1 to Jan. 5 in 2020 in UTC::

            >>> time = azely.time.get_time('2020-01-01 to 2020-01-05', view='UTC')

    """
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
    """Get current time at given timezone."""
    start = end = datetime.now(tzinfo)
    return date_range(start, end, tz=tzinfo, name=tzinfo.zone)


def get_time_today(freq: str, tzinfo: tzinfo) -> DatetimeIndex:
    """Get time range of today at given timezone."""
    start = datetime.now(tzinfo).date()
    end = start + timedelta(days=1)
    return date_range(start, end, None, freq, tz=tzinfo, name=tzinfo.zone)


def get_time_period(
    query: str, freq: str, tzinfo: tzinfo, parser: Callable
) -> DatetimeIndex:
    """Get time range of given date and length at given timezone."""
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
