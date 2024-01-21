__all__ = ["Object", "get_object"]


# standard library
from dataclasses import dataclass
from functools import partial
from typing import Optional


# dependencies
from astropy.coordinates import SkyCoord, get_body
from astropy.time import Time as ObsTime
from astropy.utils.data import conf
from .consts import AZELY_CACHE, FRAME, SOLAR_FRAME, SOLAR_OBJECTS, TIMEOUT
from .utils import PathLike, cache, rename


@dataclass
class Object:
    """Object information."""

    name: str
    """Name of the object."""

    longitude: str
    """Longitude of the object with units."""

    latitude: str
    """Latitude of the object with units."""

    frame: str
    """Equatorial coordinates of the object."""

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
    source: Optional[PathLike] = AZELY_CACHE,
    timeout: float = TIMEOUT,
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
        return get_object_by_cds(
            query,
            frame=frame,
            timeout=timeout,
            name=name,
            source=source,
            update=update,
        )


@partial(rename, key="name")
@partial(cache, table="object")
def get_object_solar(
    query: str,
    /,
    *,
    # consumed by decorators
    name: Optional[str],  # @rename
    source: Optional[PathLike],  # @cache
    update: bool,  # @cache
) -> Object:
    """Get object information in the solar system."""
    return Object(
        name=query,
        longitude="NA",
        latitude="NA",
        frame=SOLAR_FRAME,
    )


@partial(rename, key="name")
@partial(cache, table="object")
def get_object_by_cds(
    query: str,
    /,
    *,
    frame: str,
    timeout: float,
    # consumed by decorators
    name: Optional[str],  # @rename
    source: Optional[PathLike],  # @cache
    update: bool,  # @cache
) -> Object:
    """Get object information by the CDS name resolver."""
    with conf.set_temp("remote_timeout", timeout):
        response = SkyCoord.from_name(
            name=query,
            frame=frame,
            parse=False,
            cache=False,
        )
        lonlat = response.to_string("hmsdms")

    return Object(
        name=query,
        longitude=lonlat.split()[0],  # type: ignore
        latitude=lonlat.split()[1],  # type: ignore
        frame=frame,
    )
