"""Azely's utils module (low-level utilities).

This module provides series of utility related to exception and I/O:
(1) `AzelyError` class as Azely's base exception class
(2) `open_toml` function to open (and update if any) a TOML file
(3) `cache_to` decorator which caches returns of a function to a TOML file
(4) `set_defaults` decorator which replaces default values of a function

"""
__all__ = ["AzelyError", "open_toml", "cache_to", "set_defaults"]


# standard library
from functools import wraps
from inspect import Signature, signature
from pathlib import Path
from typing import Any, Callable, Dict, Union


# dependent packages
from toml import TomlDecodeError, dump, load


# constants
TOML_SUFFIX = ".toml"


# type aliases
PathLike = Union[Path, str]
StrKeyDict = Dict[str, Any]


# main classes/functions
class AzelyError(Exception):
    """Azely's base exception class."""

    pass


def open_toml(path: PathLike, alt_dir: PathLike = "."):
    """Open a TOML file and get contents as a dictionary.

    If this function is used in a `with` context management,
    any updates to the dictionary is also reflected on the TOML file.

    Args:
        path: Path or filename (without suffix) of a TOML file.
            If the latter is specified and if it does not exist in a current
            directory, then the function tries to find it in `alt_dir`.
        alt_dir: Path of a directory where the function tries to find
            the TOML file if it does not exist in a current directory.

    Returns:
        toml_dict: Dictionary equivalent to the contents of the TOML file.

    Raises:
        AzelyError: Raised if the TOML file is not found anywhere.

    Examples:
        To simply open a TOML file (for example, `./user.toml`)::

            >>> dic = azely.utils.open_toml('user.toml')

        or::

            >>> dic = azely.utils.open_toml('user')

        To open and update a TOML file::

            >>> with azely.utils.open_toml('user.toml') as dic:
            ...     dic['new_key'] = new_value

    """
    path = Path(path).with_suffix(TOML_SUFFIX).expanduser()

    if not path.exists():
        path = Path(alt_dir) / path

    if not path.exists():
        raise AzelyError(f"Failed to find path: {path}")

    return TOMLDict(path)


class cache_to:
    """Decorator which cache returns of a function to a TOML file.

    Suppose there is a function which takes a long time to get
    a result and it is decorated by this function::

        >>> import time
        >>> @azely.utils.cache_to('cache.toml')
        ... def func(query: str) -> str:
        ...     # simulates a long-time processing
        ...     time.sleep(10)
        ...     return query + '!'

    Then the following function calls::

        >>> func('aaa')
        >>> func('bbb')
        >>> func('ccc')

    would take ~30 seconds to finish. But at the same time,
    the results are cached to `cache.toml` like::

        aaa = "aaa!"
        bbb = "bbb!"
        ccc = "ccc!"

    Then the second calls would take much shorter time because
    cached values are simply read and returned by the decorator.

    """

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
    """Decorator which replaces default values of a function.

    The alternative defualt values are read from a TOML file.
    Suppose there is a function with some parameters
    and it is decorated by this function::

        >>> @azely.utils.set_defaults('defaults.toml')
        ... def func(a: int, b: int = 0) -> int:
        ...     return a + b

    Suppose the contents of `defaults.toml` is like::

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
def ensure_existance(path: PathLike) -> Path:
    """Make path of file exist."""
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()

    return path


class TOMLDict(dict):
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
