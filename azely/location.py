__all__ = ["Location", "get_location"]


# standard library
from dataclasses import dataclass
from functools import partial
from re import split
from typing import ClassVar
from zoneinfo import ZoneInfo


# dependencies
from astropy.coordinates import EarthLocation, Latitude, Longitude
from astropy.units import Quantity
from astropy.utils.data import conf
from ipinfo import getHandler
from timezonefinder import TimezoneFinder
from .utils import AzelyError, StrPath, cache, rename


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

    altitude: str
    """Altitude of the location (with units)."""

    _timezone_finder: ClassVar = TimezoneFinder()

    @property
    def timezone(self) -> ZoneInfo:
        """IANA timezone of the location."""
        response = self._timezone_finder.timezone_at(
            lng=Longitude(self.longitude, wrap_angle="180d").value,
            lat=Latitude(self.latitude).value,
        )

        return ZoneInfo(str(response))

    def to_earthlocation(self) -> EarthLocation:
        """Convert it to an astropy's EarthLocation object."""
        return EarthLocation(
            lon=Longitude(self.longitude),
            lat=Latitude(self.latitude),
            height=Quantity(self.altitude),
        )


@partial(rename, key="name")
@partial(cache, table="location")
def get_location(
    query: str,
    /,
    *,
    google_api: str | None = None,
    ipinfo_api: str | None = None,
    sep: str = r"\s*;\s*",
    timeout: float = 10.0,
    # consumed by decorators
    name: str | None = None,
    source: StrPath | None = None,
    update: bool = False,
) -> Location:
    """Parse given query to create location information.

    Args:
        query: Query string for the location information.
        google_api: Optional Google API key.
        ipinfo_api: Optional IPinfo API key.
        sep: Separator string for splitting the query.
        timeout: Timeout length in units of seconds.
        name: Name of the location information (not cached).
        source: Path of a source TOML file for reading from
            or writing to the location information.
        update: Whether to forcibly update the location information
            in the source TOML file even if it already exists.

    Returns
        Location information created from the parsed query.

    """
    if not query:
        handler = getHandler(ipinfo_api)
        response = handler.getDetails(timeout=timeout)

        return Location(
            name=response.city,
            longitude=response.longitude,
            latitude=response.latitude,
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

    if len(args) == 3:
        return Location(
            name=args[0],
            longitude=args[1],
            latitude=args[2],
            altitude=DEFAULT_ALTITUDE,
        )

    if len(args) == 4:
        return Location(
            name=args[0],
            longitude=args[1],
            latitude=args[2],
            altitude=args[3],
        )

    raise AzelyError(f"Failed to parse: {query!s}")
