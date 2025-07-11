__all__ = ["Location", "LocationDict", "get_location"]


# standard library
from dataclasses import dataclass
from functools import cached_property, partial
from re import split
from typing import ClassVar
from zoneinfo import ZoneInfo


# dependencies
from astropy.coordinates import EarthLocation, Latitude, Longitude
from astropy.units import Quantity
from astropy.utils.data import conf
from ipinfo import getHandler
from timezonefinder import TimezoneFinder
from typing_extensions import NotRequired, Required, TypedDict
from .utils import AzelyError, StrPath, cache


# type hints
class LocationDict(TypedDict):
    """Dictionary of the location information attributes."""

    name: Required[str]
    longitude: Required[str]
    latitude: Required[str]
    altitude: NotRequired[str]


# constants
DEFAULT_ALTITUDE = "0 m"


@dataclass(frozen=True)
class Location:
    """Location information.

    Args:
        name: Name of the location.
        longitude: Longitude of the location (with units).
        latitude: Latitude of the location (with units).
        altitude: Altitude of the location (with units).

    """

    name: str
    """Name of the location."""

    longitude: str
    """Longitude of the location (with units)."""

    latitude: str
    """Latitude of the location (with units)."""

    altitude: str = DEFAULT_ALTITUDE
    """Altitude of the location (with units)."""

    _timezone_finder: ClassVar = TimezoneFinder()

    @cached_property
    def timezone(self) -> ZoneInfo:
        """Convert it to an IANA ZoneInfo."""
        response = self._timezone_finder.timezone_at(
            lng=Longitude(self.longitude, wrap_angle="180d").value,
            lat=Latitude(self.latitude).value,
        )

        return ZoneInfo(str(response))

    @cached_property
    def earthlocation(self) -> EarthLocation:
        """Convert it to an astropy EarthLocation."""
        return EarthLocation(
            lon=Longitude(self.longitude),
            lat=Latitude(self.latitude),
            height=Quantity(self.altitude),
        )


@partial(cache, table="location")
def get_location(
    query: str,
    /,
    *,
    # options for query parse
    google_api: str | None = None,
    ipinfo_api: str | None = None,
    sep: str = r"\s*;\s*",
    timeout: float = 10.0,
    # options for cache
    append: bool = True,
    overwrite: bool = False,
    source: StrPath | None = None,
) -> Location:
    """Parse given query to create location information.

    Args:
        query: Query string for the location information.
        google_api: Optional Google API key.
        ipinfo_api: Optional IPinfo API key.
        sep: Separator string for splitting the query.
        timeout: Timeout length in seconds.
        append: Whether to append the location information
            to the source TOML file if it does not exist.
        overwrite: Whether to overwrite the location information
            to the source TOML file even if it already exists.
        source: Path of a source TOML file for the location information.

    Returns
        Location information created from the parsed query.

    """
    if not query:
        handler = getHandler(ipinfo_api)
        response = handler.getDetails(timeout=timeout)

        # requiring double-str may be an astropy's issue
        return Location(
            name=response.city,
            longitude=str(str(Longitude(response.longitude, "deg"))),
            latitude=str(str(Latitude(response.latitude, "deg"))),
            altitude=DEFAULT_ALTITUDE,
        )

    if len(args := split(sep, query)) == 1:
        with conf.set_temp("remote_timeout", timeout):
            response = EarthLocation.of_address(
                address=query,
                get_height=bool(google_api),
                google_api_key=google_api,
            )

        # requiring double-str may be an astropy's issue
        return Location(
            name=query,
            longitude=str(str(response.lon)),
            latitude=str(str(response.lat)),
            altitude=str(response.height),
        )

    if 3 <= len(args) <= 4:
        return Location(*args)

    raise AzelyError(f"Failed to parse: {query!s}")
