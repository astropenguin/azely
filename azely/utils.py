# standard library
from functools import wraps
from inspect import Signature, signature
from pathlib import Path
from typing import Callable, Dict, Union


# dependent packages
import toml


# constants
PathLike = Union[Path, str]
TOMLDict = Dict[str, Union[str, int, float]]


# main classes
class cache_to:
    def __init__(self, path: PathLike, query: str = "query") -> None:
        self.path = Path(path)
        self.query = query

    def __call__(self, func: Callable) -> Callable:
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            query = bound.arguments[self.query]

            with LinkedDict(self.path) as cache:
                if query not in cache:
                    item = func(*args, **kwargs)
                    cache.update({query: item})

                return cache[query]

        return wrapper


class set_defaults:
    def __init__(self, path: PathLike, key: str = "") -> None:
        self.path = Path(path)
        self.key = key

    def __call__(self, func: Callable) -> Callable:
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            defaults = LinkedDict(self.path)

            if self.key:
                defaults = defaults.get(self.key, {})

            updated = self.update(sig, defaults)
            bound = updated.bind(*args, **kwargs)
            bound.apply_defaults()

            return func(*bound.args, **bound.kwargs)

        return wrapper

    @staticmethod
    def update(sig: Signature, defaults: TOMLDict) -> Signature:
        params = []

        for param in sig.parameters.values():
            try:
                default = defaults[param.name]
                params.append(param.replace(default=default))
            except (KeyError, ValueError):
                params.append(param.replace())

        return sig.replace(parameters=params)


# helper classes
class LinkedDict(dict):
    def __init__(self, path: PathLike) -> None:
        self.path = Path(path)
        super().__init__(self.load_toml())

    def load_toml(self) -> TOMLDict:
        with self.path.open("r") as f:
            return toml.load(f)

    def update_toml(self) -> None:
        with self.path.open("w") as f:
            f.write(toml.dumps(dict(self)))

    def close(self) -> None:
        self.update_toml()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
