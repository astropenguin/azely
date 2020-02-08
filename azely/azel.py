

# standard library


# dependent packages
import pandas as pd
from astropy.coordinates import SkyCoord, get_body
from astropy.time import Time as ObsTime
from pandas import DataFrame
from . import HERE, NOW
from .location import Location, get_location
from .object import Object, get_object
from .time import Time, get_time


# data class


# main functions


# helper functions
def get_dataframe(skycoord: SkyCoord, time: Time) -> DataFrame:
    az = skycoord.altaz.az
    el = skycoord.altaz.alt
    lst = skycoord.obstime.sidereal_time("mean")
    lst = pd.to_timedelta(lst.value, unit="h")

    df = DataFrame({"az": az, "el": el, "lst": lst}, index=time)
    df.az.name = skycoord.info.name
    df.el.name = skycoord.info.name
    return df


def get_skycoord(object: Object, site: Location, time: Time) -> SkyCoord:
    obstime = ObsTime(time.as_utc, location=site.earthloc)

    if object.is_solar:
        skycoord = get_body(object.name, time=obstime)
    else:
        skycoord = SkyCoord(*object.coords, frame=object.frame, obstime=obstime)

        skycoord.location = obstime.location
    skycoord.info.name = object.name
    return skycoord
