__all__ = ["Object", "get_object"]


# standard library
from dataclasses import dataclass
from functools import partial
from re import split


# dependencies
from astropy.coordinates import SkyCoord, get_body
from astropy.time import Time as ObsTime
from astropy.utils.data import conf
from .consts import AZELY_CACHE, SOLAR_OBJECTS
from .utils import AzelyError, StrPath, cache, rename


# constants
DEFAULT_FRAME = "icrs"
SOLAR_FRAME = "solar"


@dataclass(frozen=True)
class Object:
    """Object information.

    Args:
        name: Name of the object.
        longitude: Longitude of the object (with units).
        latitude: Latitude of the object (with units).
        frame: Coordinate frame name of the object.

    """

    name: str
    """Name of the object."""

    longitude: str
    """Longitude of the object (with units)."""

    latitude: str
    """Latitude of the object (with units)."""

    frame: str
    """Coordinate frame name of the object. """

    @property
    def is_solar(self) -> bool:
        """Whether it is a solar object."""
        return self.frame == SOLAR_FRAME

    def to_skycoord(self, obstime: ObsTime, /) -> SkyCoord:
        """Convert it to an astropy's SkyCoord object."""
        if self.is_solar:
            skycoord = get_body(
                body=self.name,
                time=obstime,
            )
        else:
            skycoord = SkyCoord(
                self.longitude,
                self.latitude,
                frame=self.frame,
                obstime=obstime,
            )

        skycoord.location = obstime.location
        skycoord.info.name = self.name  # type: ignore
        return skycoord


@partial(rename, key="name")
@partial(cache, table="object")
def get_object(
    query: str,
    /,
    *,
    sep: str = r"\s*;\s*",
    timeout: float = 10.0,
    # consumed by decorators
    name: str | None = None,
    source: StrPath | None = AZELY_CACHE,
    update: bool = False,
) -> Object:
    """Parse given query to create object information.

    Args:
        query: Query string for the object information.
        sep: Separator string for splitting the query.
        timeout: Timeout length in units of seconds.
        name: Name of the object information (not cached).
        source: Path of a source TOML file for reading from
            or writing to the object information.
        update: Whether to forcibly update the object information
            in the source TOML file even if it already exists.

    Returns
        Object information created from the parsed query.

    """
    if len(args := split(sep, query)) == 1:
        if query.lower() in SOLAR_OBJECTS:
            return Object(
                name=query,
                longitude="NA",
                latitude="NA",
                frame=SOLAR_FRAME,
            )

        with conf.set_temp("remote_timeout", timeout):
            response = SkyCoord.from_name(
                name=query,
                frame=DEFAULT_FRAME,
                parse=False,
                cache=False,
            )

        # requiring double-str may be an astropy's issue
        return Object(
            name=query,
            longitude=str(str(response.data.lon)),  # type: ignore
            latitude=str(str(response.data.lat)),  # type: ignore
            frame=DEFAULT_FRAME,
        )

    if len(args) == 3:
        return Object(
            name=args[0],
            longitude=args[1],
            latitude=args[2],
            frame=DEFAULT_FRAME,
        )

    if len(args) == 4:
        return Object(
            name=args[0],
            longitude=args[1],
            latitude=args[2],
            frame=args[3],
        )

    raise AzelyError(f"Failed to parse: {query!s}")
