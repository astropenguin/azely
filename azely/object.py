# standard library
from dataclasses import asdict, dataclass
from typing import Dict


# dependent packages
from astropy.coordinates import SkyCoord, get_body, solar_system_ephemeris
from astropy.time import Time as ObsTime
from astropy.coordinates.name_resolve import NameResolveError
from astropy.utils.data import Conf
from .utils import AzelyError, cache_to, open_toml


# constants
from .consts import (
    AZELY_DIR,
    AZELY_OBJECT,
    FRAME,
    TIMEOUT,
)

DELIMITER = ":"
SOLAR = "solar"
USER_TOML = "user.toml"


# type aliases
ObjectDict = Dict[str, str]


# data classes
@dataclass(frozen=True)
class Object:
    name: str
    frame: str
    longitude: str
    latitude: str

    def is_solar(self) -> bool:
        return self.frame == SOLAR

    def to_dict(self) -> ObjectDict:
        return asdict(self)

    def to_skycoord(self, obstime: ObsTime) -> SkyCoord:
        if self.is_solar():
            skycoord = get_body(self.name, time=obstime)
        else:
            coords = self.longitude, self.latitude
            skycoord = SkyCoord(*coords, frame=self.frame, obstime=obstime)

        skycoord.location = obstime.location
        skycoord.info.name = self.name
        return skycoord


# main functions
def get_object(query: str, frame: str = FRAME, timeout: int = TIMEOUT) -> Object:
    if DELIMITER in query:
        return Object(**get_object_by_user(query))
    elif query.lower() in solar_system_ephemeris.bodies:
        return Object(**get_object_of_solar(query))
    else:
        return Object(**get_object_by_query(query, frame, timeout))


# helper functions
def get_object_by_user(query: str) -> ObjectDict:
    path, query = query.split(DELIMITER)

    try:
        return open_toml(path or USER_TOML, AZELY_DIR)[query]
    except KeyError:
        raise AzelyError(f"Failed to get object: {query}")


@cache_to(AZELY_OBJECT)
def get_object_of_solar(query: str) -> ObjectDict:
    return Object(query, SOLAR, "NaN", "NaN").to_dict()


@cache_to(AZELY_OBJECT)
def get_object_by_query(query: str, frame: str, timeout: int) -> ObjectDict:
    with Conf.remote_timeout.set_temp(timeout):
        try:
            res = SkyCoord.from_name(query, frame)
        except NameResolveError:
            raise AzelyError(f"Failed to get object: {query}")
        except ValueError:
            raise AzelyError(f"Failed to parse frame: {frame}")

    return Object(query, frame, *res.to_string("hmsdms").split()).to_dict()
