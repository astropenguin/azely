__all__ = ["Location", "get_location"]


# standard library
from dataclasses import dataclass
from datetime import tzinfo
from typing import ClassVar, Optional


# dependencies
from astropy.coordinates import EarthLocation, Latitude, Longitude
from astropy.units import Quantity
from astropy.utils.data import conf
from ipinfo import getHandler
from pytz import timezone
from timezonefinder import TimezoneFinder
from .cache import PathLike, cache
from .consts import AZELY_LOCATIONS, GOOGLE_API, HERE, IPINFO_API, TIMEOUT


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
    def timezone(self) -> tzinfo:
        """Timezone of the location."""
        response = self.tf.timezone_at(
            lng=Longitude(self.longitude).value,
            lat=Latitude(self.latitude).value,
        )

        return timezone(str(response))

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
    google_api: str = GOOGLE_API,
    ipinfo_api: str = IPINFO_API,
    name: Optional[str] = None,
    source: PathLike = AZELY_LOCATIONS,
    timeout: int = TIMEOUT,
    update: bool = False,
) -> Location:
    """Get location information."""
    if query.lower() == HERE:
        return get_location_by_ip(
            query,
            ipinfo_api=ipinfo_api,
            name=name,
            timeout=timeout,
            source=source,
            update=update,
        )
    else:
        return get_location_by_name(
            query,
            google_api=google_api,
            name=name,
            timeout=timeout,
            source=source,
            update=update,
        )


@cache
def get_location_by_ip(
    query: str,
    /,
    *,
    ipinfo_api: str,
    name: Optional[str],
    source: PathLike,  # consumed by @cache
    timeout: int,
    update: bool,  # consumed by @cache
) -> Location:
    """Get location information by current IP address."""
    handler = getHandler(ipinfo_api or None)
    response = handler.getDetails(timeout=timeout)

    return Location(
        name=response.city,
        longitude=response.longitude,
        latitude=response.latitude,
    )


@cache
def get_location_by_name(
    query: str,
    /,
    *,
    google_api: str,
    name: Optional[str],
    source: PathLike,  # consumed by @cache
    timeout: int,
    update: bool,  # consumed by @cache
) -> Location:
    """Get location information by a location name."""
    with conf.set_temp("remote_timeout", timeout):
        response = EarthLocation.of_address(
            address=query,
            get_height=bool(google_api),
            google_api_key=google_api or None,
        )

    return Location(
        name=name or query,
        longitude=str(response.lon),
        latitude=str(response.lat),
    )
