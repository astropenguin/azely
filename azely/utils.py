__all__ = ["AzelyError", "cache"]


# standard library
from contextlib import contextmanager
from dataclasses import asdict, replace
from functools import wraps
from inspect import Signature
from os import PathLike
from typing import Any, Callable, Iterator, TypeVar, Union


# dependencies
from tomlkit import TOMLDocument, dump, load, nl


# type hints
StrPath = Union[PathLike[str], str]
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

        append = bound.arguments.get("append", True)
        overwrite = bound.arguments.get("overwrite", False)
        source = bound.arguments.get("source", None)
        query = bound.arguments.get("query", None)

        if source is None:
            return func(*args, **kwargs)

        with sync_toml(source) as doc:
            table_ = doc.setdefault(table, {})

            if query not in table_ and not append and not overwrite:
                return func(*args, **kwargs)

            if query in table_ and not overwrite:
                return DataClass(**table_[query].unwrap())

            table_[query] = asdict(obj := func(*args, **kwargs))

            if table_ is not doc.last_item():
                table_.add(nl())

            return obj

    return wrapper  # type: ignore


@contextmanager
def sync_toml(toml: StrPath) -> Iterator[TOMLDocument]:
    """Open a TOML file as an updatable tomlkit document."""
    with open(toml, "r") as file:
        yield (doc := load(file))

    with open(toml, "w") as file:
        dump(doc, file)
