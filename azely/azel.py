__all__ = ["compute"]


# standard library


# dependent packages
from pandas import DataFrame, Series, Timestamp, to_timedelta
from pandas.api.extensions import register_dataframe_accessor
from .utils import set_defaults
from .location import Location, get_location
from .object import Object, get_object
from .time import Time, get_time


# constants
from .consts import (
    AZELY_CONFIG,
    DAYFIRST,
    HERE,
    NOW,
    FRAME,
    FREQ,
    TIMEOUT,
    YEARFIRST,
)

SOLAR_TO_SIDEREAL = 1.002_737_909


# data accessor
@register_dataframe_accessor("as_lst")
class AsLSTAccessor:
    def __init__(self, accessed: DataFrame) -> None:
        self.accessed = accessed

    @property
    def az(self) -> Series:
        return self.accessed.set_index(self.index).az

    @property
    def el(self) -> Series:
        return self.accessed.set_index(self.index).el

    @property
    def index(self) -> Time:
        df = self.accessed
        td_solar = df.index - df.index[0]
        td_sidereal = td_solar * SOLAR_TO_SIDEREAL + df.lst[0]
        index = Timestamp(0) + td_sidereal.floor("1D") + df.lst

        return Time(index, name="Local Sidereal Time")


# main functions
@set_defaults(AZELY_CONFIG, "compute")
def compute(
    object: str,
    site: str = HERE,
    time: str = NOW,
    view: str = "",
    frame: str = FRAME,
    freq: str = FREQ,
    dayfirst: bool = DAYFIRST,
    yearfirst: bool = YEARFIRST,
    timeout: int = TIMEOUT,
) -> DataFrame:
    object_ = get_object(object, frame, timeout)
    site_ = get_location(site, timeout)
    time_ = get_time(time, view or site, freq, dayfirst, yearfirst, timeout)

    return compute_from(object_, site_, time_)


# helper functions
def compute_from(object: Object, site: Location, time: Time) -> DataFrame:
    obstime = time.to_obstime(site.to_earthloc())
    skycoord = object.to_skycoord(obstime)

    az = skycoord.altaz.az
    el = skycoord.altaz.alt
    lst = skycoord.obstime.sidereal_time("mean")
    lst = to_timedelta(lst.value, unit="h")

    return DataFrame(dict(az=az, el=el, lst=lst), index=time.to_index())
