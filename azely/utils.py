"""Azely's utils module (low-level utilities).

This module provides series of utility related to exception and I/O:
(1) ``AzelyError`` class as Azely's base exception class
(2) ``set_defaults`` decorator which replaces default values of a function

"""
__all__ = ["AzelyError", "set_defaults"]


# standard library
from functools import wraps
from inspect import Signature, signature
from pathlib import Path
from typing import Any, Callable, Dict, Union


# dependent packages
from requests.utils import CaseInsensitiveDict
from toml import TomlDecodeError, dump, load


# type aliases
PathLike = Union[Path, str]
StrKeyDict = Dict[str, Any]


# main classes/functions
class AzelyError(Exception):
    """Azely's base exception class."""

    pass


class set_defaults:
    """Decorator which replaces default values of a function.

    The alternative default values are read from a TOML file.
    Suppose there is a function with some parameters
    and it is decorated by this function::

        >>> @azely.utils.set_defaults('defaults.toml')
        ... def func(a: int, b: int = 0) -> int:
        ...     return a + b

    Suppose the content of ``defaults.toml`` is like::

        # defaults.toml

        a = 1
        b = 2

    Then the following function calls results in::

        >>> func(0, 1) # -> 1
        >>> func(0) # -> 2
        >>> func() # -> 3

    This is because now the function is equivalent to::

        >>> def func(a: int = 1, b: int = 2) -> int:
        ...     return a + b

    """

    def __init__(self, path: PathLike, key: str = "") -> None:
        self.path = path
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
    def update(sig: Signature, defaults: StrKeyDict) -> Signature:
        params = []

        for param in sig.parameters.values():
            try:
                default = defaults[param.name]
                params.append(param.replace(default=default))
            except (KeyError, ValueError):
                params.append(param.replace())

        return sig.replace(parameters=params)


# helper classes/functions
class TOMLDict(CaseInsensitiveDict):
    """Open and update a TOML file as a dictionary."""

    def __init__(self, path: PathLike) -> None:
        self.path = Path(path)
        super().__init__(self.load_toml())

    def to_dict(self) -> StrKeyDict:
        return dict(self)

    def load_toml(self) -> StrKeyDict:
        with self.path.open("r") as f:
            try:
                return load(f)
            except TomlDecodeError:
                raise AzelyError(f"Failed to load: {self.path}")

    def update_toml(self) -> None:
        with self.path.open("w") as f:
            try:
                dump(self.to_dict(), f)
            except (TypeError, PermissionError):
                raise AzelyError(f"Failed to update: {self.path}")

    def close(self) -> None:
        self.update_toml()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
