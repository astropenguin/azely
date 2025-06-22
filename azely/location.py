__all__ = ["Location", "get_location"]


# standard library
from dataclasses import dataclass
from functools import partial
from typing import ClassVar
from zoneinfo import ZoneInfo


# dependencies
from astropy.coordinates import EarthLocation, Latitude, Longitude
from astropy.units import Quantity
from astropy.utils.data import conf
from ipinfo import getHandler
from timezonefinder import TimezoneFinder
from .consts import AZELY_CACHE, GOOGLE_API, HERE, IPINFO_API, TIMEOUT
from .utils import StrPath, cache, rename


@dataclass
class Location:
    """Location information."""

    name: str
    """Name of the location."""

    longitude: str
    """Longitude of the location."""

    latitude: str
    """Latitude of the location."""

    altitude: str = "0.0 m"
    """Altitude of the location."""

    tf: ClassVar = TimezoneFinder()
    """TimezoneFinder instance."""

    def __post_init__(self) -> None:
        """Add or update units of location values."""
        self.longitude = str(Longitude(self.longitude, "deg"))
        self.latitude = str(Latitude(self.latitude, "deg"))
        self.altitude = str(Quantity(self.altitude, "m"))

    @property
    def timezone(self) -> ZoneInfo:
        """Timezone of the location."""
        response = self.tf.timezone_at(
            lng=Longitude(self.longitude, wrap_angle="180 deg").value,
            lat=Latitude(self.latitude).value,
        )

        return ZoneInfo(str(response))

    def to_earthlocation(self) -> EarthLocation:
        """Convert it to an EarthLocation object."""
        return EarthLocation(
            lon=Longitude(self.longitude),
            lat=Latitude(self.latitude),
            height=Quantity(self.altitude),
        )


def get_location(
    query: str,
    /,
    *,
    google_api: str | None = GOOGLE_API,
    ipinfo_api: str | None = IPINFO_API,
    name: str | None = None,
    source: StrPath | None = AZELY_CACHE,
    timeout: float = TIMEOUT,
    update: bool = False,
) -> Location:
    """Get location information."""
    if query.lower() == HERE:
        return get_location_by_ip(
            query,
            ipinfo_api=ipinfo_api,
            timeout=timeout,
            name=name,
            source=source,
            update=update,
        )
    else:
        return get_location_by_map(
            query,
            google_api=google_api,
            timeout=timeout,
            name=name,
            source=source,
            update=update,
        )


@partial(rename, key="name")
@partial(cache, table="location")
def get_location_by_ip(
    query: str,
    /,
    *,
    ipinfo_api: str | None,
    timeout: float,
    # consumed by decorators
    name: str | None,  # @rename
    source: StrPath | None,  # @cache
    update: bool,  # @cache
) -> Location:
    """Get location information by ipinfo.io."""
    handler = getHandler(ipinfo_api)
    response = handler.getDetails(timeout=timeout)

    return Location(
        name=response.city,
        longitude=response.longitude,
        latitude=response.latitude,
    )


@partial(rename, key="name")
@partial(cache, table="location")
def get_location_by_map(
    query: str,
    /,
    *,
    google_api: str | None,
    timeout: float,
    # consumed by decorators
    name: str | None,  # @rename
    source: StrPath | None,  # @cache
    update: bool,  # @cache
) -> Location:
    """Get location information by online maps."""
    with conf.set_temp("remote_timeout", timeout):
        response = EarthLocation.of_address(
            address=query,
            get_height=bool(google_api),
            google_api_key=google_api,
        )

    return Location(
        name=query,
        longitude=str(response.lon),
        latitude=str(response.lat),
    )
