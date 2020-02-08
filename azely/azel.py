

# standard library


# dependent packages
from astropy.coordinates import SkyCoord, get_body
from astropy.time import Time as ObsTime
from . import HERE, TODAY
from .location import Location, get_location
from .object import Object, get_object
from .time import Time, get_time


# data class


# main functions


# helper functions
def get_skycoord(object_: Object, site: Location, time: Time) -> SkyCoord:
    obstime = ObsTime(time.as_utc, location=site.earthloc)

    if object_.is_solar:
        skycoord = get_body(object_.name, time=obstime)
        skycoord.location = obstime.location
    else:
        skycoord = SkyCoord(*object_.coords, frame=object_.frame, obstime=obstime)
        skycoord.location = obstime.location

    return skycoord
