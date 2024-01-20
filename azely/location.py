__all__ = ["Location", "get_location"]


# standard library
from dataclasses import dataclass
from datetime import tzinfo
from functools import partial
from typing import ClassVar, Optional


# dependencies
from astropy.coordinates import Angle, EarthLocation, Latitude, Longitude
from astropy.units import Quantity
from astropy.utils.data import conf
from ipinfo import getHandler
from pytz import timezone
from timezonefinder import TimezoneFinder
from .consts import AZELY_CACHE, GOOGLE_API, HERE, IPINFO_API, TIMEOUT
from .utils import PathLike, cache, rename


@dataclass
class Location:
    """Location information."""

    name: str
    """Name of the location."""

    longitude: str
    """Longitude of the location with units."""

    latitude: str
    """Latitude of the location with units."""

    altitude: str = "0m"
    """Altitude of the location with units."""

    tf: ClassVar = TimezoneFinder()
    """TimezoneFinder instance."""

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
    google_api: Optional[str] = GOOGLE_API,
    ipinfo_api: Optional[str] = IPINFO_API,
    name: Optional[str] = None,
    source: Optional[PathLike] = AZELY_CACHE,
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
    ipinfo_api: Optional[str],
    timeout: float,
    # consumed by decorators
    name: Optional[str],  # @rename
    source: Optional[PathLike],  # @cache
    update: bool,  # @cache
) -> Location:
    """Get location information by ipinfo.io."""
    handler = getHandler(ipinfo_api)
    response = handler.getDetails(timeout=timeout)

    return Location(
        name=response.city,
        longitude=str(Angle(response.longitude, "deg")),
        latitude=str(Angle(response.latitude, "deg")),
    )


@partial(rename, key="name")
@partial(cache, table="location")
def get_location_by_map(
    query: str,
    /,
    *,
    google_api: Optional[str],
    timeout: float,
    # consumed by decorators
    name: Optional[str],  # @rename
    source: Optional[PathLike],  # @cache
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
