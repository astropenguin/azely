__all__ = ["get_time"]

# standard library

# dependent packages
import pandas as pd
from astropy.time import Time
from dateutil.parser import ParserError, parse
from pandas import DatetimeIndex, Series
from . import AzelyError, config
from .location import get_earthloc, get_location, get_tzinfo
from .utils import set_defaults

# constants
NOW = "now"
TODAY = "today"
HERE = "here"
UTC = "utc"
LST = "local sidereal time"
PERIOD_SEP = ":"


# main functions
@set_defaults(**config["time"])
def get_time(query: str = NOW, at: str = HERE, freq: str = "10T") -> Series:
    index = get_time_index(query, at, freq)
    time = Time(index.tz_convert(UTC), location=get_earthloc(at))

    lst = pd.to_timedelta(time.sidereal_time("mean").value, unit="h")
    return Series(lst, index, name=LST)


# helper functions
def get_time_index(query: str, at: str, freq: str) -> DatetimeIndex:
    tzinfo = get_tzinfo(at)
    name = get_location(at).name

    if query == NOW:
        start = end = pd.Timestamp.now(tzinfo)
    elif query == TODAY:
        start = pd.Timestamp.now(tzinfo).date()
        end = start + pd.offsets.Day()
    elif PERIOD_SEP in query:
        try:
            start, end = map(parse, query.split(PERIOD_SEP))
        except ParserError:
            raise AzelyError(f"Failed to parse: {query}")
    else:
        try:
            start = parse(query)
            end = start + pd.offsets.Day()
        except ParserError:
            raise AzelyError(f"Failed to parse: {query}")

    return pd.date_range(start, end, None, freq, tzinfo, name=name)
