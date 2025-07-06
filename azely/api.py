__all__ = ["AzEl", "calc"]


# standard library
from dataclasses import replace
from typing import ClassVar


# dependent packages
import pandas as pd
from astropy.coordinates import SkyCoord
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
    """Calculated azimuth and elevation of the object in degrees."""

    az: pd.Series
    """Azimuth of the object in degrees."""

    el: pd.Series
    """Elevation of the object in degrees."""

    index: pd.DatetimeIndex
    """Timezone-aware time index (timezone-naive for local sidereal time)."""

    location: Location
    """Location information used for the azimuth/elevation calculation."""

    object: Object
    """Object information used for the azimuth/elevation calculation."""

    time: Time
    """Time information used for the azimuth/elevation calculation."""

    _metadata: ClassVar = ["location", "object", "time"]
    """Ensure the location/object/time information as normal properties."""

    def in_lst(self) -> Self:
        """Convert its time index to the local sidereal time (LST)."""
        lst_0days = pd.to_timedelta(
            ObsTime(
                self.index.tz_convert(None),
                location=self.location.earthlocation,
            )
            .sidereal_time("mean")
            .value,
            unit="hr",
        )
        lst_ndays = lst_0days + (
            lst_0days[0]
            + pd.TimedeltaIndex(
                self.index - self.index[0],
                freq=None,  # type: ignore
            )
            * SOLAR_TO_SIDEREAL
        ).floor("D")

        origin = self.index[0].normalize().tz_localize(None)
        return self.set_index((origin + lst_ndays).rename("LST"))

    def in_utc(self) -> Self:
        """Convert its time index to the coordinated universal time (UTC)."""
        return self.set_index(self.index.tz_convert("UTC").rename("UTC"))

    def separation(self, other: Self, /) -> pd.Series:
        """Calculate the separation angle with other object in degrees."""
        joined = self.join(other, how="outer", lsuffix="_l", rsuffix="_r")
        left = SkyCoord(joined.az_l, joined.el_l, unit="deg", frame="altaz")
        right = SkyCoord(joined.az_r, joined.el_r, unit="deg", frame="altaz")

        return pd.Series(
            left.separation(right).value,
            index=joined.index.tz_convert(self.index.tz),
            name="separation",
        )

    @property
    def _constructor(self) -> type[Self]:
        """Ensure an AzEl DataFrame as the result of DataFrame manipulation."""
        return type(self)


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
    source: SourceDict | (StrPath | None) = AZELY_CACHE,
) -> AzEl:
    """Calculate azimuth/elevation of given object in given location at give time.

    Args:
        object: Object information, or query dictionary or string for it.
        location: Location information, or query dictionary or string for it.
        time: Time information, or query dictionary or string for it.
        google_api: Optional Google API key for the location information.
        ipinfo_api: Optional IPinfo API key for the location information.
        sep: Separator string for splitting the location/object/time queries.
        timeout: Timeout length in seconds for the location/object information.
        append: Whether to append the location/object/time information
            to the source TOML file if it does not exist.
            An option dictionary for each information is also accepted.
        overwrite: Whether to overwrite the location/object/time information
            to the source TOML file even if it already exists.
            An option dictionary for each information is also accepted.
        source: Path of a source TOML file for the location/object/time information.
            An option dictionary for each information is also accepted.

    Returns:
        Calculated azimuth and elevation of the object in degrees.

    """
    if not isinstance(append, dict):
        append = {"location": append, "object": append, "time": append}

    if not isinstance(overwrite, dict):
        overwrite = {"location": overwrite, "object": overwrite, "time": overwrite}

    if not isinstance(source, dict):
        source = {"location": source, "object": source, "time": source}

    if isinstance(location, dict):
        location_ = Location(**location)
    elif isinstance(location, str):
        location_ = get_location(
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
        object_ = Object(**object)
    elif isinstance(object, str):
        object_ = get_object(
            object,
            sep=sep,
            timeout=timeout,
            append=append.get("object", True),
            overwrite=overwrite.get("object", False),
            source=source.get("object", AZELY_CACHE),
        )

    if isinstance(time, dict):
        time_ = Time(**time)
    elif isinstance(time, str):
        time_ = get_time(
            time,
            sep=sep,
            append=append.get("time", True),
            overwrite=overwrite.get("time", False),
            source=source.get("time", AZELY_CACHE),
        )
    time_ = replace(time_, timezone=str(location_.timezone))

    skycoord = object_.skycoord(
        ObsTime(
            time_.index.tz_convert(None),
            location=location_.earthlocation,
        )
    ).altaz

    azel = AzEl(
        index=time_.index,
        data={
            "az": skycoord.az,  # type: ignore
            "el": skycoord.alt,  # type: ignore
        },
    )
    azel.location = location_
    azel.object = object_
    azel.time = time_
    return azel
