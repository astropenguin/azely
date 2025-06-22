__all__ = ["Time", "get_time"]


# standard library
from dataclasses import dataclass
from datetime import timezone as tz
from re import split
from zoneinfo import ZoneInfo


# dependencies
import pandas as pd
from astropy.coordinates import EarthLocation
from astropy.time import Time as ObsTime
from dateparser import parse
from .utils import AzelyError


# constants
DEFAULT_ARGS = "00:00 today", "tomorrow", "10min", ""
DEFAULT_SEP = r"\s*;\s*"


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

    def to_index(self) -> pd.DatetimeIndex:
        """Convert it to a pandas' DatetimeIndex object."""
        if (start := parse(self.start)) is None:
            raise AzelyError(f"Failed to parse: {self.start!s}")

        if (stop := parse(self.stop, settings={"RELATIVE_BASE": start})) is None:
            raise AzelyError(f"Failed to parse: {self.stop!s}")

        timezone = ZoneInfo(self.timezone) if self.timezone else None

        if (tzinfo := start.tzinfo or stop.tzinfo or timezone) is None:
            raise AzelyError("Failed to resolve timezone.")

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
            tz=tz.utc,
            inclusive="left",
        ).tz_convert(tzinfo)

    def to_obstime(self, earthloc: EarthLocation, /) -> ObsTime:
        """Convert it to an astropy's Time object."""
        return ObsTime(self.to_index().tz_convert(None), location=earthloc)


def get_time(query: str, /, *, sep: str = DEFAULT_SEP) -> Time:
    """Parse given query to create time information.

    Args:
        query: Query string for the time information.
        sep: Separator string for splitting the query.

    Returns:
        Time information created from the parsed query.

    """
    args = (s := split(sep, query)) + [""] * (len(DEFAULT_ARGS) - len(s))

    if not query:
        return Time(*DEFAULT_ARGS)
    else:
        return Time(
            start=args[0] or DEFAULT_ARGS[0],
            stop=args[1] or DEFAULT_ARGS[1],
            step=args[2] or DEFAULT_ARGS[2],
            timezone=args[3] or DEFAULT_ARGS[3],
        )
