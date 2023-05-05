"""Azely's location module (mid-level API).

This module mainly provides ``Location`` class for location information
and ``get_location`` function to search for location information as an
instance of ``Location`` class.

The ``Location`` class is defined as:
``Location(name: str, longitude: str, latitude: str, altitude: str = '0')``,
where units of lon/lat and altitude are deg and meter, respectively.

The ``get_location`` function acquires location information from:
(1) Guess by IP address (by default). Internet connection is required.
(2) Data from OpenStreetMap. Internet connection is required.
(3) User-defined location information written in a TOML file.

In the case of (1) and (2), obtained location information is cached
in a special TOML file (``~/.config/azely/locations.toml``) for an offline use.

In the case of (3), users can define location information in a TOML file
(e.g., ``user.toml``) which should be put in a current directory or in the
Azely's config directory (``~/.config/azely``). Location information must be
defined as a table in the TOML file like::

    # user.toml

    [ASTE]
    name = "ASTE Telescope"
    longitude = "-67.70317915"
    latitude = "-22.97163575"
    altitude = "0"

Then location information can be obtained by ``get_location(<query>)``.
Use ``get_location(<name>:<query>)`` for user-defined location information,
where ``<name>`` must be the name of a TOML file without suffix or the full
path of it. If it does not exist in a current directory, the function
will try to find it in the Azely's config directory (``~/.config/azely``).

Examples:
    To get location information by IP address::

        >>> loc = azely.location.get_location('here')

    To get location information from OpenStreetMap::

        >>> loc = azely.location.get_location('ALMA AOS')

    To get location information from ``user.toml``::

        >>> loc = azely.location.get_location('user:ASTE')

"""
__all__ = ["Location", "get_location"]


# standard library
from dataclasses import asdict, dataclass
from datetime import tzinfo
from typing import ClassVar


# dependent packages
from astropy.coordinates import EarthLocation, Latitude, Longitude
from astropy.coordinates.name_resolve import NameResolveError
from astropy.units import Quantity
from astropy.utils.data import conf
from pytz import timezone
from requests import ConnectionError, api
from timezonefinder import TimezoneFinder
from .cache import PathLike, cache
from .query import parse
from .utils import AzelyError


# constants
from .consts import (
    AZELY_DIR,
    AZELY_LOCATION,
    HERE,
    TIMEOUT,
)


IPINFO_URL = "https://ipinfo.io/json"


# data classes
@dataclass(frozen=True)
class Location:
    """Location information."""

    name: str
    """Name of the location."""

    longitude: str
    """Longitude of the location with units."""

    latitude: str
    """Latitude of the location with units."""

    altitude: str = "0.0 m"
    """Altitude of the location with units."""

    tf: ClassVar = TimezoneFinder()
    """TimezoneFinder instance."""

    def __post_init__(self) -> None:
        """Add or update units of location values."""
        setattr = object.__setattr__
        setattr(self, "longitude", str(Longitude(self.longitude, "deg")))
        setattr(self, "latitude", str(Latitude(self.latitude, "deg")))
        setattr(self, "altitude", str(Quantity(self.altitude, "m")))

    @property
    def timezone(self) -> tzinfo:
        """Timezone of the location."""
        return timezone(
            str(
                self.tf.timezone_at(
                    lng=Longitude(self.longitude).value,
                    lat=Latitude(self.latitude).value,
                )
            )
        )

    @property
    def earth_location(self) -> EarthLocation:
        """Location information in Astropy."""
        return EarthLocation(
            lon=Longitude(self.longitude),
            lat=Latitude(self.latitude),
            height=Quantity(self.altitude),
        )


# main functions
def get_location(query: str = HERE, timeout: int = TIMEOUT) -> Location:
    """Get location information by various ways.

    This function acquires location information by the following three ways:
    (1) Guess by IP address (by default). Internet connection is required.
    (2) Data from OpenStreetMap. Internet connection is required.
    (3) User-defined location information written in a TOML file.

    In the cases of (1) and (2), obtained location information is cached
    in a special TOML file (``~/.config/azely/locations.toml``) for an offline use.

    In the case of (3), users can define location information in a TOML file
    (e.g., ``user.toml``) which should be put in a current directory or in the
    Azely's config directory (``~/.config/azely``).

    Then location information can be obtained by ``get_location(<query>)``.
    Use ``get_location(<name>:<query>)`` for user-defined location information,
    where ``<name>`` must be the name of a TOML file without suffix or the full
    path of it. If it does not exist in a current directory, the function
    will try to find it in the Azely's config directory (``~/.config/azely``).

    Args:
        query: Query string (e.g., ``'ALMA AOS'`` or ``'user:ASTE'``).
            Default value, 'here', is a special one with which the function
            tries to guess location information by an IP address of a client.
        timeout: Query timeout expressed in units of seconds.

    Returns:
        Location information as an instance of ``Location`` class.

    Raises:
        AzelyError: Raised if the function fails to get location information.

    Examples:
        To get location information by IP address::

            >>> loc = azely.location.get_location('here')

        To get location information from OpenStreetMap::

            >>> loc = azely.location.get_location('ALMA AOS')

        To get location information from ``user.toml``::

            >>> loc = azely.location.get_location('user:ASTE')

    """
    parsed = parse(query)

    if parsed.query.lower() == HERE:
        return get_location_by_ip(
            query=parsed.query,
            cache=parsed.source or AZELY_LOCATION,
            update=parsed.update,
            timeout=timeout,
        )
    else:
        return get_location_by_name(
            query=parsed.query,
            cache=parsed.source or AZELY_LOCATION,
            update=parsed.update,
            timeout=timeout,
        )


@cache
def get_location_by_ip(
    query: str,
    cache: PathLike,
    update: bool,
    timeout: int,
) -> Location:
    """Get location information from a guess by IP address."""
    try:
        res = api.get(IPINFO_URL, timeout=timeout).json()
    except ConnectionError:
        raise AzelyError("Failed to get location by IP address")

    return Location(res["city"], *res["loc"].split(",")[::-1])


@cache
def get_location_by_name(
    query: str,
    cache: PathLike,
    update: bool,
    timeout: int,
) -> Location:
    """Get location information from OpenStreetMap."""
    original_remote_timeout = conf.remote_timeout

    try:
        conf.remote_timeout = timeout
        res = EarthLocation.of_address(query)  # type: ignore
    except NameResolveError:
        raise AzelyError(f"Failed to get location: {query}")
    finally:
        conf.remote_timeout = original_remote_timeout

    return Location(query, str(res.lon.value), str(res.lat.value))
