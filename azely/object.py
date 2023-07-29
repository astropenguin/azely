__all__ = ["Object", "get_object"]


# standard library
from dataclasses import dataclass
from typing import Optional


# dependent packages
from astropy.coordinates import Longitude, Latitude, SkyCoord, get_body
from astropy.time import Time as ObsTime
from astropy.utils.data import conf
from .consts import AZELY_OBJECTS, FRAME, SOLAR_FRAME, SOLAR_OBJECTS, TIMEOUT
from .utils import PathLike, cache, rename


@dataclass
class Object:
    """Object information."""

    name: str
    """Name of the object."""

    longitude: str
    """Longitude (e.g. R.A. or l) of the object."""

    latitude: str
    """Latitude (e.g. Dec. or b) of the object."""

    frame: str
    """Equatorial coordinates of the object."""

    def __post_init__(self) -> None:
        """Add or update units of object coordinates."""
        if not self.is_solar:
            self.longitude = str(Longitude(self.longitude, "hr"))
            self.latitude = str(Latitude(self.latitude, "deg"))

    @property
    def is_solar(self) -> bool:
        """Whether it is a solar object."""
        return self.frame == SOLAR_FRAME

    def to_skycoord(self, obstime: ObsTime) -> SkyCoord:
        """Convert it to a SkyCoord object."""
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


def get_object(
    query: str,
    /,
    *,
    frame: str = FRAME,
    name: Optional[str] = None,
    source: PathLike = AZELY_OBJECTS,
    timeout: int = TIMEOUT,
    update: bool = False,
) -> Object:
    """Get object information."""
    if query.lower() in SOLAR_OBJECTS:
        return get_object_solar(
            query,
            name=name,
            source=source,
            update=update,
        )
    else:
        return get_object_by_name(
            query,
            frame=frame,
            timeout=timeout,
            name=name,
            source=source,
            update=update,
        )


@rename
@cache
def get_object_solar(
    query: str,
    /,
    *,
    # consumed by decorators
    name: Optional[str],  # @rename
    source: PathLike,  # @cache
    update: bool,  # @cache
) -> Object:
    """Get object information in the solar system."""
    return Object(
        name=query,
        longitude="NA",
        latitude="NA",
        frame=SOLAR_FRAME,
    )


@rename
@cache
def get_object_by_name(
    query: str,
    /,
    *,
    frame: str,
    timeout: int,
    # consumed by decorators
    name: Optional[str],  # @rename
    source: PathLike,  # @cache
    update: bool,  # @cache
) -> Object:
    """Get object information by an object name."""
    with conf.set_temp("remote_timeout", timeout):
        response = SkyCoord.from_name(
            name=query,
            frame=frame,
            parse=False,
            cache=False,
        )

    return Object(
        name=query,
        longitude=str(response.data.lon),  # type: ignore
        latitude=str(response.data.lat),  # type: ignore
        frame=frame,
    )
