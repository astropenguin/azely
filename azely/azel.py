__all__ = ["compute"]


# standard library


# dependent packages
import pytz
from astropy.coordinates import SkyCoord, get_body
from astropy.time import Time
from pandas import DataFrame, DatetimeIndex, Series, to_timedelta
from pandas.api.extensions import register_dataframe_accessor
from . import config
from .consts import HERE, NOW, FRAME, FREQ, SEP, TIMEOUT
from .utils import set_defaults
from .location import Location, get_location
from .object import Object, get_object
from .time import get_time


# constants
SOLAR_TO_SIDEREAL = 1.002_737_909


# data accessor
class AsAccessor:
    def __init__(self, accessed: DataFrame) -> None:
        self.accessed = accessed

    @property
    def az(self) -> Series:
        return self.accessed.set_index(self.index).az

    @property
    def el(self) -> Series:
        return self.accessed.set_index(self.index).el


@register_dataframe_accessor("as_lst")
class AsLSTAccessor(AsAccessor):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def index(self) -> DatetimeIndex:
        df = self.accessed
        td_solar = df.index - df.index[0]
        td_sidereal = td_solar * SOLAR_TO_SIDEREAL + df.lst[0]
        td_sidereal = td_sidereal.floor("1D") + df.lst

        index = df.index[0].floor("1D").tz_localize(None) + td_sidereal
        return DatetimeIndex(index, name="Local Sidereal Time")


@register_dataframe_accessor("as_utc")
class AsUTCAccessor(AsAccessor):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def index(self) -> DatetimeIndex:
        index = self.accessed.index.tz_convert(pytz.UTC)
        return DatetimeIndex(index, name=index.tzinfo.zone)


# main functions
@set_defaults(**config["compute"])
def compute(
    object: str,
    site: str = HERE,
    time: str = NOW,
    view: str = "",
    frame: str = FRAME,
    freq: str = FREQ,
    sep: str = SEP,
    timeout: int = TIMEOUT,
) -> DataFrame:
    object_ = get_object(object, frame, timeout)
    site_ = get_location(site, timeout)
    time_ = get_time(time, view or site, freq, sep, timeout)

    skycoord = get_skycoord(object_, site_, time_)
    return get_dataframe(skycoord, time_)


# helper functions
def get_dataframe(skycoord: SkyCoord, time: DatetimeIndex) -> DataFrame:
    az = skycoord.altaz.az
    el = skycoord.altaz.alt
    lst = skycoord.obstime.sidereal_time("mean")
    lst = to_timedelta(lst.value, unit="h")

    return DataFrame(dict(az=az, el=el, lst=lst), index=time)


def get_skycoord(object: Object, site: Location, time: DatetimeIndex) -> SkyCoord:
    time_utc_naive = time.tz_convert(pytz.UTC).tz_localize(None)
    obstime = Time(time_utc_naive, location=site.earthloc)

    if object.is_solar:
        skycoord = get_body(object.name, time=obstime)
    else:
        skycoord = SkyCoord(*object.coords, frame=object.frame, obstime=obstime)

    skycoord.location = obstime.location
    skycoord.info.name = object.name
    return skycoord
