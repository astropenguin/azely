__all__ = ["get_location"]


# standard library
from dataclasses import asdict, dataclass
from datetime import tzinfo
from typing import Tuple


# dependent packages
import pytz
import requests
from astropy.coordinates import EarthLocation
from geopy import Nominatim
from geopy.exc import GeocoderServiceError
from timezonefinder import TimezoneFinder
from . import AzelyError, AZELY_LOCATION
from .consts import HERE, TIMEOUT
from .utils import cache_to


# constants
IPINFO_URL = "https://ipinfo.io/json"


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
        return pytz.timezone(tf.timezone_at(lng=coords[0], lat=coords[1]))

    @property
    def earthloc(self) -> EarthLocation:
        coords = self.coords
        return EarthLocation(lon=coords[0], lat=coords[1], height=coords[2])


# main functions
def get_location(query: str = HERE, timeout: int = TIMEOUT) -> Location:
    if query.lower() == HERE:
        return Location(**get_location_by_ip(query, timeout))
    else:
        return Location(**get_location_by_query(query, timeout))


# helper functions
@cache_to(AZELY_LOCATION)
def get_location_by_query(query: str, timeout: int) -> dict:
    try:
        res = osm.geocode(query, timeout=timeout, namedetails=True).raw
    except (AttributeError, GeocoderServiceError):
        raise AzelyError(f"Failed to get location: {query}")

    return asdict(Location(res["namedetails"]["name"], res["lon"], res["lat"]))


@cache_to(AZELY_LOCATION)
def get_location_by_ip(query: str, timeout: int) -> dict:
    try:
        res = requests.get(IPINFO_URL, timeout=timeout).json()
    except requests.ConnectionError:
        raise AzelyError("Failed to get location by IP address")

    return asdict(Location(res["city"], *res["loc"].split(",")[::-1]))
