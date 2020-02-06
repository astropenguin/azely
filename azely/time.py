__all__ = ["get_time", "get_sidereal_time"]

# standard library

# dependent packages
import pandas as pd
from astropy.time import Time
from dateutil.parser import parse
from pandas import DataFrame
from . import AzelyError, config
from .location import get_location, get_tzinfo, get_earthloc
from .utils import set_defaults

# constants
NOW = "now"
HERE = "here"
UTC = "utc"
PERIOD_SEP = ":"


# main functions
@set_defaults(**config["time"])
def get_time(query: str = NOW, at: str = HERE, freq: str = "10T") -> DataFrame:
    tzinfo = get_tzinfo(at)

    if query == NOW:
        start = end = pd.Timestamp.now(tzinfo)
    elif PERIOD_SEP in query:
        start, end = map(parse, query.split(PERIOD_SEP))
    else:
        start, end = parse(query), parse(query) + pd.offsets.Day()

    time = pd.date_range(start, end, None, freq, tz=tzinfo)
    return DataFrame({tzinfo.zone: time}, index=time.tz_convert(UTC))


def get_sidereal_time(query: str = NOW, at: str = HERE, freq: str = "10T") -> DataFrame:
    pass


