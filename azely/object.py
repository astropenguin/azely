__all__ = ["Object", "get_object"]

# standard library
from dataclasses import dataclass

# dependent packages
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
    # lazy import
    from astropy.coordinates import solar_system_ephemeris

    return query.lower() in solar_system_ephemeris.bodies


def get_object_of_solar(query: str) -> dict:
    return {
        "name": query.capitalize(),
        "frame": "n/a",
        "longitude": "n/a",
        "latitude": "n/a",
    }


@cache_to(AZELY_OBJECT)
def get_object_by_query(query: str, frame: str = "icrs", timeout: int = 5) -> dict:
    # lazy import
    from astropy.coordinates import SkyCoord, name_resolve
    from astropy.utils.data import Conf

    try:
        with Conf.remote_timeout.set_temp(timeout):
            coord = SkyCoord.from_name(query, frame)
    except name_resolve.NameResolveError:
        raise AzelyError(f"Failed to get object: {query}")

    longitude, latitude = coord.to_string("hmsdms").split()

    return {
        "name": query,
        "frame": frame,
        "longitude": longitude,
        "latitude": latitude,
    }
