__all__ = ["AzelyError", "cache", "rename"]


# standard library
from contextlib import contextmanager
from dataclasses import asdict, replace
from functools import wraps
from inspect import Signature
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, TypeVar, Union


# dependencies
from tomlkit import TOMLDocument, dump, load, nl


# type hints
PathLike = Union[Path, str]
TCallable = TypeVar("TCallable", bound=Callable[..., Any])


class AzelyError(Exception):
    """Azely's base exception class."""

    pass


def cache(func: TCallable, table: str) -> TCallable:
    """Cache a dataclass object in a TOML file."""
    DataClass = func.__annotations__["return"]
    signature = Signature.from_callable(func)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        bargs = bound.arguments

        if (source := bargs["source"]) is None:
            return func(*args, **kwargs)

        with sync_toml(source) as doc:
            tab = doc.setdefault(table, {})

            if (query := bargs["query"]) in tab:
                if not bargs["update"]:
                    return DataClass(**tab[query].unwrap())

            tab[query] = asdict(func(*args, **kwargs))

            if tab is not doc.last_item():
                tab.add(nl())

            return DataClass(**tab[query].unwrap())

    return wrapper  # type: ignore


def rename(func: TCallable, key: str) -> TCallable:
    """Update the name field of a dataclass object."""
    signature = Signature.from_callable(func)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        bargs = bound.arguments

        if (name := bargs["name"]) is None:
            return func(*args, **kwargs)
        else:
            return replace(func(*args, **kwargs), **{key: name})

    return wrapper  # type: ignore


@contextmanager
def sync_toml(toml: PathLike) -> Iterator[TOMLDocument]:
    """Open a TOML file as an updatable tomlkit document."""
    with open(toml, "r") as file:
        yield (doc := load(file))

    with open(toml, "w") as file:
        dump(doc, file)
