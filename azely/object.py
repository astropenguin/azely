"""Azely's object module (mid-level API).

This module mainly provides `Object` class for information of an astronomical
object (object information, hereafter) and `get_object` function to search for
object information as an instance of `Object` class.

The `Object` class is defiend as
`Object(name: str, frame: str, longitude: str, latitude: str)`,
where frame is a name of equatorial coordinates (e.g., icrs) and lon/lat are values
of coordinates which must be written with units like 02h42m40.771s/-00d00m47.84s.


The `get_object` function retrieves object information from:
(1) Data from CDS (by default). Internet connection is required.
(2) User-defined object information written in a TOML file.

In the case of (1), obtained object information is cached in a special
TOML file (`~/.config/azely/object.toml`) for an offline use.

In the case of (2), users can define object information in a TOML file
(e.g., `user.toml`) which should be put in a current directory or in the
Azely's config directory (`~/.config/azely`). Object information must be
defined as a table in the TOML file like::

    [GC]
    name = "Galactic center"
    frame = "galactic"
    longitude = "0deg"
    latitude = "0deg"

Then object information can be obtained by `get_object(<query>)`.
Use `get_object(<name>:<query>)` for user-defined object information,
where `<name>` must be the name of a TOML file without suffix or the full
path of it. If it does not exist in a current directory, the function
will try to find it in the Azely's config directory (`~/.config/azely`).

Examples:
    To get object info from CDS::

        >>> obj = azely.object.get_object('NGC1068')

    To get object info from `user.toml`::

        >>> obj = azely.object.get_object('user:GC')

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
    """Azely's object information class."""

    name: str
    frame: str
    longitude: str
    latitude: str

    def is_solar(self) -> bool:
        """Return True if it is an solar object."""
        return self.frame == SOLAR

    def to_dict(self) -> ObjectDict:
        """Convert it to a Python's dictionary."""
        return asdict(self)

    def to_skycoord(self, obstime: ObsTime) -> SkyCoord:
        """Convert it to an astropy's skycoord with given obstime."""
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
    """Get object information by various ways.

    Args:
        query: Query string (e.g., `'NGC1068'` or `'user:GC'`).
        frame: Name of equatorial coordinates used in astropy's SkyCoord.
        timeout: Query timeout expressed in units of seconds.

    Returns:
        object: Object information as an instance of `Object` class.

    Raises:
        AzelyError: Raised if the function fails to get object information.

    This function retrieves object information by the following two ways:
    (1) Data from CDS (by default). Internet connection is required.
    (2) User-defined object information written in a TOML file.

    In the case of (1), obtained object information is cached in a special
    TOML file (`~/.config/azely/object.toml`) for an offline use.

    In the case of (2), users can define object information in a TOML file
    (e.g., `user.toml`) which should be put in a current directory or in the
    Azely's config directory (`~/.config/azely`).

    Then object information can be obtained by `get_object(<query>)`.
    Use `get_object(<name>:<query>)` for user-defined object information,
    where `<name>` must be the name of a TOML file without suffix or the full
    path of it. If it does not exist in a current directory, the function
    will try to find it in the Azely's config directory (`~/.config/azely`).

    Notes:
        As `object` is the Python's builtin base class, it might be better
        to use an alternative variable name (e.g., 'object_' or 'obj')
        for object information which this function returns.

    Examples:
        To get object info from CDS::

            >>> obj = azely.object.get_object('NGC1068')

        To get object info from `user.toml`::

            >>> obj = azely.object.get_object('user:GC')

    """
    if DELIMITER in query:
        return Object(**get_object_by_user(query))
    elif query.lower() in solar_system_ephemeris.bodies:
        return Object(**get_object_of_solar(query))
    else:
        return Object(**get_object_by_query(query, frame, timeout))


# helper functions
def get_object_by_user(query: str) -> ObjectDict:
    """Get object information from a user-defined TOML file."""
    path, query = query.split(DELIMITER)

    try:
        return open_toml(path or USER_TOML, AZELY_DIR)[query]
    except KeyError:
        raise AzelyError(f"Failed to get object: {query}")


@cache_to(AZELY_OBJECT)
def get_object_of_solar(query: str) -> ObjectDict:
    """Get object information of the solar system."""
    return Object(query, SOLAR, "NaN", "NaN").to_dict()


@cache_to(AZELY_OBJECT)
def get_object_by_query(query: str, frame: str, timeout: int) -> ObjectDict:
    """Get object information from CDS."""
    with Conf.remote_timeout.set_temp(timeout):
        try:
            res = SkyCoord.from_name(query, frame)
        except NameResolveError:
            raise AzelyError(f"Failed to get object: {query}")
        except ValueError:
            raise AzelyError(f"Failed to parse frame: {frame}")

    return Object(query, frame, *res.to_string("hmsdms").split()).to_dict()
