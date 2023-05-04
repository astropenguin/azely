__all__ = ["parse"]


# standard library
from dataclasses import dataclass
from re import compile
from typing import Optional


# constants
QUERY = compile(r"^\s*((.+):)?([^!]+)(!)?\s*$")


@dataclass(frozen=True)
class Parsed:
    query: str
    """Final query to be passed."""

    source: Optional[str] = None
    """Path of the query source."""

    update: bool = False
    """Whether to update the query source."""


def parse(string: str) -> Parsed:
    """Parse a string and return a parsed object."""
    if (match := QUERY.search(string)) is None:
        raise ValueError(f"{string} is not valid.")

    return Parsed(
        query=match.group(3),
        source=match.group(2),
        update=bool(match.group(4)),
    )
