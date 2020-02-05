__all__ = ["get_location"]

# standard library
from dataclasses import dataclass

# dependent packages
import requests
from geopy import Nominatim
from geopy.exc import GeocoderServiceError
from timezonefinder import TimezoneFinder
from . import AzelyError, AZELY_LOCATIONS, config
from .utils import cache_to, set_defaults

# constants
IPINFO_URL = "https://ipinfo.io/json"

# query instances
tf = TimezoneFinder()
osm = Nominatim(user_agent="azely")


# data classes
@dataclass
class Location:
    name: str
    longitude: str
    latitude: str
    timezone: str


# main functions
@set_defaults(**config["location"])
def get_location(query: str = "here", timeout: int = 5) -> Location:
    if query == "here":
        return Location(**get_location_by_ip(timeout))
    else:
        return Location(**get_location_by_query(query, timeout))


# helper functions
def get_timezone(longitude: float, latitude: float) -> str:
    return tf.timezone_at(lng=longitude, lat=latitude)


@cache_to(AZELY_LOCATIONS)
def get_location_by_query(query: str, timeout: int = 5) -> dict:
    try:
        res = osm.geocode(query, timeout=timeout)
    except GeocoderServiceError:
        raise AzelyError(f"Failed to get location: {query}")

    if res is None:
        raise AzelyError(f"Failed to get location: {query}")

    return {
        "name": res.address.split(",")[0],
        "longitude": res.raw["lon"],
        "latitude": res.raw["lat"],
        "timezone": get_timezone(res.longitude, res.latitude),
    }


def get_location_by_ip(timeout: int = 5) -> dict:
    try:
        res = requests.get(IPINFO_URL, timeout=timeout).json()
    except requests.ConnectionError:
        raise AzelyError("Failed to get location by IP address")

    latitude, longitude = res["loc"].split(",")

    return {
        "name": res["city"],
        "longitude": longitude,
        "latitude": latitude,
        "timezone": get_timezone(float(longitude), float(latitude)),
    }
