# standard library
from functools import wraps
from inspect import Signature, signature
from pathlib import Path
from typing import Any, Callable, Dict, Union


# dependent packages
import toml


# constants
TOML_SUFFIX = ".toml"


# type aliases
PathLike = Union[Path, str]


# main classes/functions
class AzelyError(Exception):
    pass


def open_toml(path: PathLike, alt_dir: PathLike = "."):
    path = Path(path).with_suffix(TOML_SUFFIX).expanduser()

    if not path.exists():
        path = Path(alt_dir) / path

    if not path.exists():
        raise AzelyError(f"Failed to find path: {path}")

    return TOMLDict(path)


class cache_to:
    def __init__(self, path: PathLike, query: str = "query") -> None:
        self.path = ensure_existance(path)
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
    def __init__(self, path: PathLike, key: str = "") -> None:
        self.path = ensure_existance(path)
        self.key = key

    def __call__(self, func: Callable) -> Callable:
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            defaults = TOMLDict(self.path)

            if self.key:
                defaults = defaults.get(self.key, {})

            updated = self.update(sig, defaults)
            bound = updated.bind(*args, **kwargs)
            bound.apply_defaults()

            return func(*bound.args, **bound.kwargs)

        return wrapper

    @staticmethod
    def update(sig: Signature, defaults: Dict[str, Any]) -> Signature:
        params = []

        for param in sig.parameters.values():
            try:
                default = defaults[param.name]
                params.append(param.replace(default=default))
            except (KeyError, ValueError):
                params.append(param.replace())

        return sig.replace(parameters=params)


# helper classes/functions
def ensure_existance(path: PathLike) -> Path:
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()

    return path


class TOMLDict(dict):
    def __init__(self, path: PathLike) -> None:
        self.path = Path(path)
        super().__init__(self.load_toml())

    def load_toml(self) -> Dict[str, Any]:
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
