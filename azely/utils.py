# standard library
from functools import wraps
from inspect import Signature, signature
from pathlib import Path
from typing import Callable, Union


# dependent packages
import toml


# constants
PathLike = Union[Path, str]


# main classes
class cache_to:
    def __init__(self, path: PathLike, query: str = "query") -> None:
        self.path = Path(path).expanduser()
        self.query = query

    def __call__(self, func: Callable) -> Callable:
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            query = bound.arguments[self.query]

            with TOMLDict(self.path) as cache:
                if query not in cache:
                    item = func(*args, **kwargs)
                    cache.update({query: item})

                return cache[query]

        return wrapper


class set_defaults:
    def __init__(self, **defaults: dict) -> None:
        self.defaults = defaults

    def __call__(self, func: Callable) -> Callable:
        sig = self.get_signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            return func(*bound.args, **bound.kwargs)

        return wrapper

    def get_signature(self, func: Callable) -> Signature:
        sig = signature(func)
        params = []

        for param in sig.parameters.values():
            if param.kind == param.VAR_POSITIONAL:
                params.append(param.replace())
            elif param.kind == param.VAR_POSITIONAL:
                params.append(param.replace())
            elif param.name not in self.defaults:
                params.append(param.replace())
            else:
                default = self.defaults[param.name]
                params.append(param.replace(default=default))

        return sig.replace(parameters=params)


# helper classes
class TOMLDict(dict):
    def __init__(self, path: PathLike, create_if_not_exists: bool = True) -> None:
        self.path = Path(path).expanduser()

        if create_if_not_exists:
            self.path.touch()

        super().__init__(self.load_toml())

    def load_toml(self) -> dict:
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
