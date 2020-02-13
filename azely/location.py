__all__ = ["get_location"]


# standard library
from dataclasses import asdict, dataclass
from datetime import tzinfo
from pathlib import Path
from typing import Dict, Tuple


# dependent packages
import requests
from astropy.coordinates import EarthLocation
from geopy import Nominatim
from geopy.exc import GeocoderServiceError
from pytz import timezone
from timezonefinder import TimezoneFinder
from .utils import AzelyError, TOMLDict, cache_to


# constants
from .consts import (
    AZELY_DIR,
    AZELY_LOCATION,
    HERE,
    TIMEOUT,
)

DELIMITER = ":"
IPINFO_URL = "https://ipinfo.io/json"
TOML_SUFFIX = ".toml"


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
    def coords(self) -> Tuple[float]:
        return float(self.longitude), float(self.latitude), float(self.altitude)

    @property
    def tzinfo(self) -> tzinfo:
        coords = self.coords
        return timezone(tf.timezone_at(lng=coords[0], lat=coords[1]))

    @property
    def earthloc(self) -> EarthLocation:
        coords = self.coords
        return EarthLocation(lon=coords[0], lat=coords[1], height=coords[2])


# main functions
def get_location(query: str = HERE, timeout: int = TIMEOUT) -> Location:
    if DELIMITER in query:
        return Location(**get_location_by_user(query))
    elif query.lower() == HERE:
        return Location(**get_location_by_ip(query, timeout))
    else:
        return Location(**get_location_by_query(query, timeout))


# helper functions
def get_location_by_user(query: str) -> LocationDict:
    path, query = query.split(DELIMITER)
    path = Path(path).with_suffix(TOML_SUFFIX).expanduser()

    if not path.exists():
        path = AZELY_DIR / path

    if not path.exists():
        raise AzelyError(f"Failed to find path: {path}")

    try:
        return TOMLDict(path)[query]
    except KeyError:
        raise AzelyError(f"Failed to get location: {query}")


@cache_to(AZELY_LOCATION)
def get_location_by_query(query: str, timeout: int) -> LocationDict:
    try:
        res = osm.geocode(query, timeout=timeout, namedetails=True).raw
    except (AttributeError, GeocoderServiceError):
        raise AzelyError(f"Failed to get location: {query}")

    return asdict(Location(res["namedetails"]["name"], res["lon"], res["lat"]))


@cache_to(AZELY_LOCATION)
def get_location_by_ip(query: str, timeout: int) -> LocationDict:
    try:
        res = requests.get(IPINFO_URL, timeout=timeout).json()
    except requests.ConnectionError:
        raise AzelyError("Failed to get location by IP address")

    return asdict(Location(res["city"], *res["loc"].split(",")[::-1]))
