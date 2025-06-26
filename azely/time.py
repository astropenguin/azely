__all__ = ["Time", "TimeDict", "get_time"]


# standard library
from dataclasses import dataclass
from datetime import timezone as tz
from functools import cached_property, partial
from re import split
from zoneinfo import ZoneInfo


# dependencies
import pandas as pd
from dateparser import parse
from dateparser.timezone_parser import StaticTzInfo
from typing_extensions import NotRequired, TypedDict
from .utils import AzelyError, StrPath, cache


# type hints
class TimeDict(TypedDict):
    """Dictionary of the time information attributes."""

    start: NotRequired[str]
    stop: NotRequired[str]
    step: NotRequired[str]
    timezone: NotRequired[str]


# constants
DEFAULT_START = "00:00 today"
DEFAULT_STOP = "00:00 tomorrow"
DEFAULT_STEP = "10min"
DEFAULT_TIMEZONE = ""
N_TIME_ARGS = 4


@dataclass(frozen=True)
class Time:
    """Time information.

    Args:
        start: Left bound of the time (inclusive).
        stop: Right bound of the time (inclusive).
        step: Step of the time (pandas offset alias).
        timezone: Timezone of the time (IANA timezone name).

    """

    start: str = DEFAULT_START
    """Left bound of the time (inclusive)."""

    stop: str = DEFAULT_STOP
    """Right bound of the time (exclusive)."""

    step: str = DEFAULT_STEP
    """Step of the time (pandas offset alias)."""

    timezone: str = DEFAULT_TIMEZONE
    """Timezone of the time (IANA timezone name)."""

    @cached_property
    def index(self) -> pd.DatetimeIndex:
        """Convert it to a pandas DatetimeIndex."""
        if (start := parse(self.start)) is None:
            raise AzelyError(f"Failed to parse: {self.start!s}")

        if (stop := parse(self.stop, settings={"RELATIVE_BASE": start})) is None:
            raise AzelyError(f"Failed to parse: {self.stop!s}")

        timezone = ZoneInfo(self.timezone) if self.timezone else None

        if (tzinfo := start.tzinfo or stop.tzinfo or timezone) is None:
            raise AzelyError("Failed to resolve timezone.")

        if isinstance(tzinfo, StaticTzInfo):
            tzname = tzinfo.tzname(None)
        else:
            tzname = str(tzinfo)

        if start.tzinfo is None and stop.tzinfo is None:
            start = start.replace(tzinfo=tzinfo)
            stop = stop.replace(tzinfo=tzinfo)
        elif start.tzinfo is None and stop.tzinfo is not None:
            start = start.replace(tzinfo=stop.tzinfo)
        elif start.tzinfo is not None and stop.tzinfo is None:
            stop = stop.replace(tzinfo=start.tzinfo)

        return pd.date_range(
            start=start.astimezone(tz.utc),
            end=stop.astimezone(tz.utc),
            freq=self.step,
            inclusive="left",
            name=tzname,
            tz=tz.utc,
        ).tz_convert(tzinfo)


@partial(cache, table="time")
def get_time(
    query: str,
    /,
    *,
    # options for query parse
    sep: str = r"\s*;\s*",
    # options for cache
    append: bool = True,
    overwrite: bool = False,
    source: StrPath | None = None,
) -> Time:
    """Parse given query to create time information.

    Args:
        query: Query string for the time information.
        sep: Separator string for splitting the query.
        append: Whether to append the time information
            to the source TOML file if it does not exist.
        overwrite: Whether to overwrite the time information
            to the source TOML file even if it already exists.
        source: Path of a source TOML file for the time information.

    Returns:
        Time information created from the parsed query.

    """
    if not query:
        return Time()
    else:
        args = (_ := split(sep, query)) + [""] * (N_TIME_ARGS - len(_))

        return Time(
            start=args[0] or DEFAULT_START,
            stop=args[1] or DEFAULT_STOP,
            step=args[2] or DEFAULT_STEP,
            timezone=args[3] or DEFAULT_TIMEZONE,
        )
