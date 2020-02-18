"""Azely's object module.

This module mainly provides (1) `Object` class for information of an astronomical
object (object information, hereafter) and (2) `get_object` function to search for
object information and get it as an instance of `Object` class.

Object information is defiend as
`Object(name: str, frame: str, longitude: str, latitude: str)`,
where frame is a name of equatorial coordinates (e.g., icrs) and lon/lat are values
of coordinates which must be written with units like 02h42m40.771s/-00d00m47.84s.

Object info can be retrieved by the following two ways:
(1) Data from CDS (by default). Internet connection is required.
(2) User-defined object information written in a TOML file.

In the case of (1), obtained object information is cached in a special
TOML file (`~/.config/azely/object.toml`) for an offline use.

Examples:
    To get object info from CDS::

        >>> obj = azely.object.get_object('NGC1068')

    To get object info from a user-defined TOML file::

        >>> obj = azely.object.get_object('user:GC')

The second example assumes that a TOML file, `user.toml`, exists in a
current directory or in the Azely's config directory (`~/.config/azely`)
and the following TOML text is written in it::

    [GC]
    name = "Galactic center"
    frame = "galactic"
    longitude = "0deg"
    latitude = "0deg"

"""


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
