__all__ = ["AZELY_CACHE", "AZELY_DIR"]


# standard library
from os import getenv
from pathlib import Path


# constants
AZELY_CACHE: Path
"""Azely's default cache TOML file."""

AZELY_DIR: Path
"""Azely's directory for the cache TOML file."""


if (env := getenv("AZELY_DIR")) is not None:
    AZELY_DIR = Path(env).resolve()
elif (env := getenv("XDG_CONFIG_HOME")) is not None:
    AZELY_DIR = Path(env).resolve() / "azely"
else:
    AZELY_DIR = Path.home() / ".config" / "azely"


if not (AZELY_CACHE := AZELY_DIR / "cache.toml").exists():
    AZELY_CACHE.parent.mkdir(parents=True, exist_ok=True)
    AZELY_CACHE.touch()
