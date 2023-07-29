__all__ = ["cache"]


# standard library
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from functools import wraps
from inspect import Signature
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar, Union


# dependencies
from tomlkit import TOMLDocument, dump, load
from .consts import AZELY_DIR


# type hints
PathLike = Union[Path, str]
TCallable = TypeVar("TCallable", bound=Callable[..., Any])


def cache(func: TCallable) -> TCallable:
    """Cache a dataclass object in a TOML file."""
    DataClass = func.__annotations__["return"]
    signature = Signature.from_callable(func)

    if not is_dataclass(DataClass):
        raise TypeError("Return type must be a dataclass.")

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        query: str = bound.arguments["query"]
        source: PathLike = bound.arguments["source"]
        update: bool = bound.arguments["update"]

        with sync_toml(resolve(source)) as doc:
            if update or query not in doc:
                doc[query] = asdict(func(*args, **kwargs))

            return DataClass(**doc[query].unwrap())

    return wrapper  # type: ignore


def resolve(toml: PathLike) -> Path:
    """Resolve the path of a TOML file."""
    if (toml := Path(toml).expanduser().resolve()).exists():
        return toml

    if (toml := toml.with_suffix(".toml")).exists():
        return toml

    if (toml := AZELY_DIR / toml.name).exists():
        return toml

    raise FileNotFoundError(f"{toml} could not be found.")


@contextmanager
def sync_toml(toml: PathLike) -> Iterator[TOMLDocument]:
    """Open a TOML file as an updatable tomlkit document."""
    with open(toml, "r") as file:
        yield (doc := load(file))

    with open(toml, "w") as file:
        dump(doc, file)
