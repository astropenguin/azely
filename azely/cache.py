__all__ = ["cache"]


# standard library
from contextlib import contextmanager
from dataclasses import asdict
from functools import wraps
from inspect import Signature
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, TypeVar, Union, get_type_hints


# dependencies
from tomlkit import TOMLDocument, dump, load


# type hints
PathLike = Union[Path, str]
TCallable = TypeVar("TCallable", bound=Callable[..., Any])


def cache(func: TCallable) -> TCallable:
    """Cache dataclass objects in a TOML file."""
    dataclass = get_type_hints(func)["return"]
    signature = Signature.from_callable(func)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        cache: Optional[PathLike] = bound.arguments["cache"]
        query: str = bound.arguments["query"]
        update: bool = bound.arguments["update"]

        if cache is None:
            return func(*args, **kwargs)

        with open_toml(cache) as doc:
            if update or query not in doc:
                doc[query] = asdict(func(*args, **kwargs))

            return dataclass(**doc[query].unwrap())

    return wrapper  # type: ignore


@contextmanager
def open_toml(toml: PathLike) -> Iterator[TOMLDocument]:
    """Open a TOML file as an updatable tomlkit document."""
    with open(toml, "r") as file:
        yield (doc := load(file))

    with open(toml, "w") as file:
        dump(doc, file)
