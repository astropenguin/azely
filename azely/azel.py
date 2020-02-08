__all__ = ["compute"]


# standard library


# dependent packages
import pytz
from astropy.coordinates import SkyCoord, get_body
from astropy.time import Time
from pandas import DataFrame, DatetimeIndex, Series, to_timedelta
from pandas.api.extensions import register_dataframe_accessor
from . import HERE, NOW
from .location import Location, get_location
from .object import Object, get_object
from .time import get_time


# constants
SOLAR_TO_SIDEREAL = 1.002_737_909


# data accessor
class AsAccessor:
    def __init__(self, df: DataFrame) -> None:
        self._df = df

    @property
    def az(self) -> Series:
        return self._df.set_index(self.index).az

    @property
    def el(self) -> Series:
        return self._df.set_index(self.index).el


@register_dataframe_accessor("as_lst")
class AsLSTAccessor(AsAccessor):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def index(self) -> DatetimeIndex:
        dt_solar = self._df.index - self._df.index[0]
        dt_sidereal = dt_solar * SOLAR_TO_SIDEREAL + self._df.lst[0]
        dt_sidereal = dt_sidereal.floor("1D") + self._df.lst

        index = self._df.index[0].floor("1D") + dt_sidereal
        return DatetimeIndex(index, name="Local Sidereal Time")


@register_dataframe_accessor("as_utc")
class AsUTCAccessor(AsAccessor):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def index(self) -> DatetimeIndex:
        index = self._df.index.tz_convert(pytz.UTC)
        return DatetimeIndex(index, name=index.tzinfo.zone)


# main functions
def compute(
    object: str,
    site: str = HERE,
    time: str = NOW,
    view: str = "",
    frame: str = "icrs",
    freq: str = "10T",
    sep: str = "to",
    timeout: int = 5,
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
    obstime = Time(time.tz_convert(pytz.UTC), location=site.earthloc)

    if object.is_solar:
        skycoord = get_body(object.name, time=obstime)
    else:
        skycoord = SkyCoord(*object.coords, frame=object.frame, obstime=obstime)

    skycoord.location = obstime.location
    skycoord.info.name = object.name
    return skycoord
