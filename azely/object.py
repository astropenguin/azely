__all__ = ["Object", "get_object"]

# standard library
from dataclasses import dataclass

# dependent packages
from astropy.coordinates import SkyCoord, solar_system_ephemeris
from astropy.coordinates.name_resolve import NameResolveError
from astropy.utils.data import Conf
from . import AzelyError, AZELY_OBJECT, config
from .utils import cache_to, set_defaults


# data classes
@dataclass
class Object:
    name: str
    frame: str
    longitude: str
    latitude: str


# main functions
@set_defaults(**config["object"])
def get_object(query: str, frame: str = "icrs", timeout: int = 5) -> Object:
    if is_solar(query):
        return Object(**get_object_of_solar(query))
    else:
        return Object(**get_object_by_query(query, frame, timeout))


# helper functions
def is_solar(query: str) -> bool:
    return query.lower() in solar_system_ephemeris.bodies


@cache_to(AZELY_OBJECT)
def get_object_of_solar(query: str) -> dict:
    return {
        "name": query,
        "frame": "solar",
        "longitude": "n/a",
        "latitude": "n/a",
    }


@cache_to(AZELY_OBJECT)
def get_object_by_query(query: str, frame: str, timeout: int) -> dict:
    try:
        with Conf.remote_timeout.set_temp(timeout):
            coord = SkyCoord.from_name(query, frame)
    except NameResolveError:
        raise AzelyError(f"Failed to get object: {query}")

    longitude, latitude = coord.to_string("hmsdms").split()

    return {
        "name": query,
        "frame": frame,
        "longitude": longitude,
        "latitude": latitude,
    }
