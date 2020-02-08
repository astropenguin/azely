__all__ = ["get_object"]


# standard library
from dataclasses import asdict, dataclass
from typing import Tuple


# dependent packages
from astropy.coordinates import SkyCoord, solar_system_ephemeris
from astropy.coordinates.name_resolve import NameResolveError
from astropy.utils.data import Conf
from . import AzelyError, AZELY_OBJECT
from .consts import FRAME, TIMEOUT
from .utils import cache_to


# constants
SOLAR = "solar"


# data classes
@dataclass(frozen=True)
class Object:
    name: str
    frame: str
    longitude: str
    latitude: str

    @property
    def is_solar(self) -> bool:
        return self.frame == SOLAR

    @property
    def coords(self) -> Tuple[str]:
        return self.longitude, self.latitude


# main functions
def get_object(query: str, frame: str = FRAME, timeout: int = TIMEOUT) -> Object:
    if query.lower() in solar_system_ephemeris.bodies:
        return Object(**get_object_of_solar(query))
    else:
        return Object(**get_object_by_query(query, frame, timeout))


# helper functions
@cache_to(AZELY_OBJECT)
def get_object_of_solar(query: str) -> dict:
    return asdict(Object(query, SOLAR, "NaN", "NaN"))


@cache_to(AZELY_OBJECT)
def get_object_by_query(query: str, frame: str, timeout: int) -> dict:
    with Conf.remote_timeout.set_temp(timeout):
        try:
            res = SkyCoord.from_name(query, frame)
        except NameResolveError:
            raise AzelyError(f"Failed to get object: {query}")
        except ValueError:
            raise AzelyError(f"Failed to parse frame: {frame}")

    return asdict(Object(query, frame, *res.to_string("hmsdms").split()))
