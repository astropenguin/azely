__all__ = ["compute"]


# standard library


# dependent packages
import pytz
from astropy.coordinates import SkyCoord, get_body
from astropy.time import Time as ObsTime
from pandas import DataFrame, to_timedelta
from . import HERE, NOW
from .location import Location, get_location
from .object import Object, get_object
from .time import Time, get_time


# constants
SOLAR_TO_SIDEREAL = 1.002_737_909


# data class
class AzEl(DataFrame):
    """Data class of azel (pandas.DataFrame with properties)."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def as_utc(self):
        new_index = self.index.tz_convert(pytz.UTC)
        new_index.name = new_index.tzinfo.zone
        return AzEl(self.set_index(new_index))

    @property
    def as_lst(self):
        dt_solar = self.index - self.index[0]
        dt_sidereal = dt_solar * SOLAR_TO_SIDEREAL + self.lst[0]
        dt_sidereal = dt_sidereal.floor("1D") + self.lst

        new_index = self.index[0].floor("1D") + dt_sidereal
        new_index.name = "Local Sidereal Time"
        return AzEl(self.set_index(new_index))


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
) -> AzEl:
    object_ = get_object(object, frame, timeout)
    site_ = get_location(site, timeout)
    time_ = get_time(time, view or site, freq, sep, timeout)

    skycoord = get_skycoord(object_, site_, time_)
    return AzEl(get_dataframe(skycoord, time_))


# helper functions
def get_dataframe(skycoord: SkyCoord, time: Time) -> DataFrame:
    az = skycoord.altaz.az
    el = skycoord.altaz.alt
    lst = skycoord.obstime.sidereal_time("mean")
    lst = to_timedelta(lst.value, unit="h")

    return AzEl(DataFrame({"az": az, "el": el, "lst": lst}, index=time))


def get_skycoord(object: Object, site: Location, time: Time) -> SkyCoord:
    obstime = ObsTime(time.tz_convert(pytz.UTC), location=site.earthloc)

    if object.is_solar:
        skycoord = get_body(object.name, time=obstime)
    else:
        skycoord = SkyCoord(*object.coords, frame=object.frame, obstime=obstime)

    skycoord.location = obstime.location
    skycoord.info.name = object.name
    return skycoord
