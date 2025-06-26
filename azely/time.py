__all__ = ["Time", "get_time"]


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
from .utils import AzelyError, StrPath, cache


# constants
DEFAULT_QUERY = "00:00 today;00:00 tomorrow;10min;"


@dataclass(frozen=True)
class Time:
    """Time information.

    Args:
        start: Left bound of the time (inclusive).
        stop: Right bound of the time (inclusive).
        step: Step of the time (pandas offset alias).
        timezone: Timezone of the time (IANA timezone name).

    """

    start: str
    """Left bound of the time (inclusive)."""

    stop: str
    """Right bound of the time (exclusive)."""

    step: str
    """Step of the time (pandas offset alias)."""

    timezone: str
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
    sep: str = r"\s*;\s*",
    # consumed by decorators
    source: StrPath | None = None,
    update: bool = False,
) -> Time:
    """Parse given query to create time information.

    Args:
        query: Query string for the time information.
        sep: Separator string for splitting the query.
        source: Path of a source TOML file for reading from
            or writing to the time information.
        update: Whether to forcibly update the time information
            in the source TOML file even if it already exists.

    Returns:
        Time information created from the parsed query.

    """
    default_args = split(sep, DEFAULT_QUERY)
    parsed_args = (s := split(sep, query)) + [""] * (len(default_args) - len(s))

    if not query:
        return Time(*default_args)
    else:
        return Time(
            start=parsed_args[0] or default_args[0],
            stop=parsed_args[1] or default_args[1],
            step=parsed_args[2] or default_args[2],
            timezone=parsed_args[3] or default_args[3],
        )
