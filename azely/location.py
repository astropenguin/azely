__all__ = ["get_location"]


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
        lon, lat = map(float, (self.longitude, self.latitude))
        return timezone(tf.timezone_at(lng=lon, lat=lat))

    def to_earthloc(self) -> EarthLocation:
        lon, lat, alt = map(float, (self.longitude, self.latitude, self.altitude))
        return EarthLocation(lon=lon, lat=lat, height=alt)


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

    try:
        return open_toml(path, AZELY_DIR)[query]
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
        res = api.get(IPINFO_URL, timeout=timeout).json()
    except ConnectionError:
        raise AzelyError("Failed to get location by IP address")

    return asdict(Location(res["city"], *res["loc"].split(",")[::-1]))
