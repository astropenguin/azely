__all__ = ["AzEl", "calc", "compute"]


# standard library
from dataclasses import replace
from typing import ClassVar


# dependent packages
import pandas as pd
from typing_extensions import Self
from .consts import AZELY_CACHE
from .location import Location, get_location
from .object import Object, get_object
from .time import Time, get_time
from .utils import StrPath


# constants
SOLAR_TO_SIDEREAL = 1.002_737_909


class AzEl(pd.DataFrame):
    """Azely's custom DataFrame."""

    alt: pd.Series
    az: pd.Series
    el: pd.Series
    location: Location
    object: Object
    time: Time
    _metadata: ClassVar = ["location", "object", "time"]

    @property
    def _constructor(self) -> type[Self]:
        return type(self)

    @property
    def in_lst(self) -> Self:
        """Convert its index to LST."""
        td = self.index - self.index[0]
        td_lst = td * SOLAR_TO_SIDEREAL + self.lst.iloc[0]
        td_lst = td_lst.floor("1D") + self.lst

        lst = pd.Timestamp(0) + td_lst
        return self.set_index(pd.DatetimeIndex(lst, name="LST"))

    @property
    def in_utc(self) -> Self:
        """Convert timezone of its index to UTC."""
        utc = self.index.tz_convert("UTC")  # type: ignore
        return self.set_index(pd.DatetimeIndex(utc, name="UTC"))


def calc(
    object: Object | str,
    location: Location | str = "",
    time: Time | str = "",
    # options for location, object, time
    google_api: str | None = None,
    ipinfo_api: str | None = None,
    sep: str = r"\s*;\s*",
    timeout: float = 10.0,
    # options for information cache
    source: StrPath | None = AZELY_CACHE,
    update: bool = False,
) -> AzEl:
    """Calculate azimuth/elevation of given object in given location at give time.

    Args:
        object: Object information or query string for it.
        location: Location information or query string for it.
        time: Time information or query string for it.
        google_api: Optional Google API key.
        ipinfo_api: Optional IPinfo API key.
        sep: Separator string for splitting the query.
        timeout: Timeout length in units of seconds.
        source: Path of a source TOML file for reading from
            or writing to the object/location/time information.
        update: Whether to forcibly update the object/location/time
            information in the source TOML file even if it already exists.

    Returns:
        DataFrame of the calculated azimuth/elevation.

    """
    if isinstance(object, str):
        object = get_object(
            object,
            sep=sep,
            timeout=timeout,
            source=source,
            update=update,
        )

    if isinstance(location, str):
        location = get_location(
            location,
            google_api=google_api,
            ipinfo_api=ipinfo_api,
            sep=sep,
            timeout=timeout,
            source=source,
            update=update,
        )

    if isinstance(time, str):
        time = get_time(
            time,
            sep=sep,
            source=source,
            update=update,
        )

    time = replace(time, timezone=str(location.timezone))
    obstime = time.to_obstime(location.to_earthlocation())
    skycoord = object.to_skycoord(obstime)
    sidereal_time = obstime.sidereal_time("mean").value

    azel = AzEl(
        index=time.to_index(),
        data={
            "az": skycoord.altaz.az,  # type: ignore
            "el": skycoord.altaz.alt,  # type: ignore
            "lst": pd.to_timedelta(sidereal_time, unit="hr"),
        },
    )
    azel.location = location
    azel.object = object
    azel.time = time
    return azel


def compute(
    object: Object | str,
    location: Location | str = "",
    time: Time | str = "",
    # options for location, object, time
    google_api: str | None = None,
    ipinfo_api: str | None = None,
    sep: str = r"\s*;\s*",
    timeout: float = 10.0,
    # options for cache
    source: StrPath | None = AZELY_CACHE,
    update: bool = False,
) -> AzEl:
    """Calculate azimuth/elevation of given object in given location at give time.

    Args:
        object: Object information or query string for it.
        location: Location information or query string for it.
        time: Time information or query string for it.
        google_api: Optional Google API key.
        ipinfo_api: Optional IPinfo API key.
        sep: Separator string for splitting the query.
        timeout: Timeout length in units of seconds.
        source: Path of a source TOML file for reading from
            or writing to the object/location/time information.
        update: Whether to forcibly update the object/location/time
            information in the source TOML file even if it already exists.

    Returns:
        DataFrame of the calculated azimuth/elevation.

    Important:
        This function will be deprecated in a future release.
        Please use the ``azely.calc`` function instead.

    """
    return calc(**locals())
