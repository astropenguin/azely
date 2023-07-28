__all__ = ["Object", "get_object"]


# standard library
from dataclasses import dataclass


# dependent packages
from astropy.coordinates import Longitude, Latitude, SkyCoord, get_body
from astropy.time import Time as ObsTime
from astropy.utils.data import conf
from .cache import PathLike, cache
from .consts import AZELY_OBJECT, FRAME, SOLAR_FRAME, SOLAR_OBJECTS, TIMEOUT


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
    *,
    frame: str = FRAME,
    source: PathLike = AZELY_OBJECT,
    timeout: int = TIMEOUT,
    update: bool = False,
) -> Object:
    """Get object information."""
    if query.lower() in SOLAR_OBJECTS:
        return get_object_solar(
            query=query,
            source=source,
            update=update,
        )
    else:
        return get_object_by_name(
            query=query,
            frame=frame,
            timeout=timeout,
            source=source,
            update=update,
        )


@cache
def get_object_solar(
    query: str,
    *,
    source: PathLike,  # consumed by @cache
    update: bool,  # consumed by @cache
) -> Object:
    """Get object information in the solar system."""
    return Object(
        name=query,
        longitude="NA",
        latitude="NA",
        frame=SOLAR_FRAME,
    )


@cache
def get_object_by_name(
    query: str,
    *,
    frame: str,
    source: PathLike,  # consumed by @cache
    timeout: int,
    update: bool,  # consumed by @cache
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
