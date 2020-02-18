"""Azely's location module.

This module mainly provides (1) `Location` class for location information
and (2) `get_location` function to search for location information and get
it as an instance of `Location` class.

Location information is defined as:
`Location(name: str, longitude: str, latitude: str, altitude: str = '0')`,
where units of lon/lat and altitude are deg and meter, respectively.

Location information can be retrieved by the following three ways:
(1) Guess by IP address (by default). Internet connection is required.
(2) Data from OpenStreetMap. Internet connection is required.
(3) User-defined location information written in a TOML file.

In the case of (1) and (2), obtained location information is cached
in a special TOML file (`~/.config/azely/location.toml`) for an offline use.

Examples:
    To get location info by IP address::

        >>> loc = azely.location.get_location()

    To get location info from OpenStreetMap::

        >>> loc = azely.location.get_location('ALMA AOS')

    To get location info from a user-defined TOML file::

        >>> loc = azely.location.get_location('user:ASTE')

The third example assumes that a TOML file, `user.toml`, exists in a
current directory or in the Azely's config directory (`~/.config/azely`)
and the following TOML text is written in it::

    [ASTE]
    name = "ASTE Telescope"
    longitude = "-67.70317915"
    latitude = "-22.97163575"
    altitude = "0"

"""


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
    name: str
    longitude: str
    latitude: str
    altitude: str = "0"

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
    """Get location's information by various ways.

    Args:
        query: Query string.
        timeout:

    Returns:
        location:

    """

    if DELIMITER in query:
        return Location(**get_location_by_user(query))
    elif query.lower() == HERE:
        return Location(**get_location_by_ip(query, timeout))
    else:
        return Location(**get_location_by_query(query, timeout))


# helper functions
def get_location_by_user(query: str) -> LocationDict:
    path, query = query.split(DELIMITER)

    try:
        return open_toml(path or USER_TOML, AZELY_DIR)[query]
    except KeyError:
        raise AzelyError(f"Failed to get location: {query}")


@cache_to(AZELY_LOCATION)
def get_location_by_query(query: str, timeout: int) -> LocationDict:
    try:
        res = osm.geocode(query, timeout=timeout, namedetails=True).raw
    except (AttributeError, GeocoderServiceError):
        raise AzelyError(f"Failed to get location: {query}")

    return Location(res["namedetails"]["name"], res["lon"], res["lat"]).to_dict()


@cache_to(AZELY_LOCATION)
def get_location_by_ip(query: str, timeout: int) -> LocationDict:
    try:
        res = api.get(IPINFO_URL, timeout=timeout).json()
    except ConnectionError:
        raise AzelyError("Failed to get location by IP address")

    return Location(res["city"], *res["loc"].split(",")[::-1]).to_dict()
