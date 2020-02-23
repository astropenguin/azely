"""Azely's location module (mid-level API).

This module mainly provides `Location` class for location information
and `get_location` function to search for location information as an
instance of `Location` class.

The `Location` class is defined as:
`Location(name: str, longitude: str, latitude: str, altitude: str = '0')`,
where units of lon/lat and altitude are deg and meter, respectively.

The `get_location` function acquires location information from:
(1) Guess by IP address (by default). Internet connection is required.
(2) Data from OpenStreetMap. Internet connection is required.
(3) User-defined location information written in a TOML file.

In the case of (1) and (2), obtained location information is cached
in a special TOML file (`~/.config/azely/locations.toml`) for an offline use.

In the case of (3), users can define location information in a TOML file
(e.g., `user.toml`) which should be put in a current directory or in the
Azely's config directory (`~/.config/azely`). Location information must be
defined as a table in the TOML file like::

    # user.toml

    [ASTE]
    name = "ASTE Telescope"
    longitude = "-67.70317915"
    latitude = "-22.97163575"
    altitude = "0"

Then location information can be obtained by `get_location(<query>)`.
Use `get_location(<name>:<query>)` for user-defined location information,
where `<name>` must be the name of a TOML file without suffix or the full
path of it. If it does not exist in a current directory, the function
will try to find it in the Azely's config directory (`~/.config/azely`).

Examples:
    To get location information by IP address::

        >>> loc = azely.location.get_location('here')

    To get location information from OpenStreetMap::

        >>> loc = azely.location.get_location('ALMA AOS')

    To get location information from `user.toml`::

        >>> loc = azely.location.get_location('user:ASTE')

"""
__all__ = ["Location", "get_location"]


# standard library
from dataclasses import asdict, dataclass
from datetime import tzinfo
from typing import Dict


# dependent packages
from astropy.coordinates import EarthLocation
from geopy import Nominatim
from geopy.exc import GeocoderServiceError
from pytz import timezone
from requests import ConnectionError, api
from timezonefinder import TimezoneFinder
from .utils import AzelyError, cache_to, open_toml


# constants
from .consts import (
    AZELY_DIR,
    AZELY_LOCATION,
    HERE,
    TIMEOUT,
)

DELIMITER = ":"
IPINFO_URL = "https://ipinfo.io/json"
USER_TOML = "user.toml"


# type aliases
LocationDict = Dict[str, str]


# query instances
tf = TimezoneFinder()
osm = Nominatim(user_agent="azely")


# data classes
@dataclass(frozen=True)
class Location:
    """Azely's location information class."""

    name: str  #: Location's name.
    longitude: str  #: Longitude expressed in units of degrees.
    latitude: str  #: Latitude expressed in units of degrees.
    altitude: str = "0"  #: Altitude expressed in units of meters.

    @property
    def tzinfo(self) -> tzinfo:
        """Return a location's tzinfo."""
        lon, lat = map(float, (self.longitude, self.latitude))
        return timezone(tf.timezone_at(lng=lon, lat=lat))

    def to_dict(self) -> LocationDict:
        """Convert it to a Python's dictionary."""
        return asdict(self)

    def to_earthloc(self) -> EarthLocation:
        """Convert it to an astropy's earth location."""
        lon, lat, alt = map(float, (self.longitude, self.latitude, self.altitude))
        return EarthLocation(lon=lon, lat=lat, height=alt)


# main functions
def get_location(query: str = HERE, timeout: int = TIMEOUT) -> Location:
    """Get location information by various ways.

    Args:
        query: Query string (e.g., `'ALMA AOS'` or `'user:ASTE'`). Default value,
            'here', is a special one with which the function tries to guess
            location information by an IP address of a client.
        timeout: Query timeout expressed in units of seconds.

    Returns:
        Location information as an instance of `Location` class.

    Raises:
        AzelyError: Raised if the function fails to get location information.

    This function acquires location information by the following three ways:
    (1) Guess by IP address (by default). Internet connection is required.
    (2) Data from OpenStreetMap. Internet connection is required.
    (3) User-defined location information written in a TOML file.

    In the cases of (1) and (2), obtained location information is cached
    in a special TOML file (`~/.config/azely/locations.toml`) for an offline use.

    In the case of (3), users can define location information in a TOML file
    (e.g., `user.toml`) which should be put in a current directory or in the
    Azely's config directory (`~/.config/azely`).

    Then location information can be obtained by `get_location(<query>)`.
    Use `get_location(<name>:<query>)` for user-defined location information,
    where `<name>` must be the name of a TOML file without suffix or the full
    path of it. If it does not exist in a current directory, the function
    will try to find it in the Azely's config directory (`~/.config/azely`).

    Examples:
        To get location information by IP address::

            >>> loc = azely.location.get_location('here')

        To get location information from OpenStreetMap::

            >>> loc = azely.location.get_location('ALMA AOS')

        To get location information from `user.toml`::

            >>> loc = azely.location.get_location('user:ASTE')

    """

    if DELIMITER in query:
        return Location(**get_location_by_user(query))
    elif query.lower().lstrip("! ") == HERE:
        return Location(**get_location_by_ip(query, timeout))
    else:
        return Location(**get_location_by_query(query, timeout))


# helper functions
def get_location_by_user(query: str) -> LocationDict:
    """Get location information from a user-defined TOML file."""
    path, query = query.split(DELIMITER)

    try:
        return open_toml(path or USER_TOML, AZELY_DIR)[query]
    except KeyError:
        raise AzelyError(f"Failed to get location: {query}")


@cache_to(AZELY_LOCATION)
def get_location_by_query(query: str, timeout: int) -> LocationDict:
    """Get location information from OpenStreetMap."""
    try:
        res = osm.geocode(query, timeout=timeout, namedetails=True).raw
    except (AttributeError, GeocoderServiceError):
        raise AzelyError(f"Failed to get location: {query}")

    return Location(res["namedetails"]["name"], res["lon"], res["lat"]).to_dict()


@cache_to(AZELY_LOCATION)
def get_location_by_ip(query: str, timeout: int) -> LocationDict:
    """Get location information from a guess by IP address."""
    try:
        res = api.get(IPINFO_URL, timeout=timeout).json()
    except ConnectionError:
        raise AzelyError("Failed to get location by IP address")

    return Location(res["city"], *res["loc"].split(",")[::-1]).to_dict()
