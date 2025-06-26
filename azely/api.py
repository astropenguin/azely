__all__ = ["AzEl", "calc"]


# standard library
from dataclasses import replace
from typing import ClassVar


# dependent packages
import pandas as pd
from astropy.time import Time as ObsTime
from typing_extensions import NotRequired, Self, TypedDict
from .consts import AZELY_CACHE
from .location import Location, LocationDict, get_location
from .object import Object, ObjectDict, get_object
from .time import Time, TimeDict, get_time
from .utils import StrPath


# type hints
class AppendDict(TypedDict):
    """Dictionary of the append options for each information."""

    location: NotRequired[bool]
    object: NotRequired[bool]
    time: NotRequired[bool]


class OverwriteDict(TypedDict):
    """Dictionary of the overwrite options for each information."""

    location: NotRequired[bool]
    object: NotRequired[bool]
    time: NotRequired[bool]


class SourceDict(TypedDict):
    """Dictionary of the source options for each information."""

    location: NotRequired[StrPath | None]
    object: NotRequired[StrPath | None]
    time: NotRequired[StrPath | None]


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
        time = ObsTime(
            self.index.tz_convert(None),  # type: ignore
            location=self.location.earthlocation,
        )
        lst = pd.to_timedelta(time.sidereal_time("mean").value, "hr")
        dt = pd.TimedeltaIndex(self.index - self.index[0], freq=None)  # type: ignore
        dlst = dt * SOLAR_TO_SIDEREAL
        return self.set_index((lst + (lst[0] + dlst).floor("D")).rename("LST"))

    @property
    def in_utc(self) -> Self:
        """Convert its index to UTC."""
        utc = self.index.tz_convert("UTC")  # type: ignore
        return self.set_index(pd.DatetimeIndex(utc, name="UTC"))


def calc(
    object: Object | ObjectDict | str,
    location: Location | LocationDict | str = "",
    time: Time | TimeDict | str = "",
    *,
    # options for query parse
    google_api: str | None = None,
    ipinfo_api: str | None = None,
    sep: str = r"\s*;\s*",
    timeout: float = 10.0,
    # options for cache
    append: AppendDict | bool = True,
    overwrite: OverwriteDict | bool = False,
    source: SourceDict | StrPath | None = AZELY_CACHE,
) -> AzEl:
    """Calculate azimuth/elevation of given object in given location at give time.

    Args:
        object: Object information, or query dictionary or string for it.
        location: Location information, or query dictionary or string for it.
        time: Time information, or query dictionary or string for it.
        google_api: Optional Google API key.
        ipinfo_api: Optional IPinfo API key.
        sep: Separator string for splitting the query.
        timeout: Timeout length in units of seconds.
        append: Whether to append the location/object/time information
            to the source TOML file if it does not exist.
            An option dictionary for each information is also accepted.
        overwrite: Whether to overwrite the location/object/time information
            to the source TOML file even if it already exists.
            An option dictionary for each information is also accepted.
        source: Path of a source TOML file for the location/object/time information.
            An option dictionary for each information is also accepted.

    Returns:
        DataFrame of the calculated azimuth/elevation.

    """
    if not isinstance(append, dict):
        append = {"location": append, "object": append, "time": append}

    if not isinstance(overwrite, dict):
        overwrite = {"location": overwrite, "object": overwrite, "time": overwrite}

    if not isinstance(source, dict):
        source = {"location": source, "object": source, "time": source}

    if isinstance(location, dict):
        location = Location(**location)
    elif isinstance(location, str):
        location = get_location(
            location,
            google_api=google_api,
            ipinfo_api=ipinfo_api,
            sep=sep,
            timeout=timeout,
            append=append.get("location", True),
            overwrite=overwrite.get("location", False),
            source=source.get("location", AZELY_CACHE),
        )

    if isinstance(object, dict):
        object = Object(**object)
    elif isinstance(object, str):
        object = get_object(
            object,
            sep=sep,
            timeout=timeout,
            append=append.get("object", True),
            overwrite=overwrite.get("object", False),
            source=source.get("object", AZELY_CACHE),
        )

    if isinstance(time, dict):
        time = Time(**time)
    elif isinstance(time, str):
        time = get_time(
            time,
            sep=sep,
            append=append.get("time", True),
            overwrite=overwrite.get("time", False),
            source=source.get("time", AZELY_CACHE),
        )

    time = replace(time, timezone=str(location.timezone))
    obstime = ObsTime(
        time.index.tz_convert(None),
        location=location.earthlocation,
    )
    skycoord = object.skycoord(obstime).altaz

    azel = AzEl(
        index=time.index,
        data={
            "az": skycoord.az,  # type: ignore
            "el": skycoord.alt,  # type: ignore
        },
    )
    azel.location = location
    azel.object = object
    azel.time = time
    return azel
