__all__ = ['cache_to',
           'default_kwargs',
           'freeze',
           'read_toml',
           'write_toml']


# standard library
from functools import wraps
from inspect import signature, getmodule
from logging import getLogger
from pathlib import Path
logger = getLogger(__name__)


# dependent packages
import toml
from requests.utils import CaseInsensitiveDict


class cache_to:
    def __init__(self, path, enable=True, query_arg='query'):
        self.path = Path(path).expanduser()
        self.enable = enable
        self.query_arg = query_arg

    def __call__(self, func):
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enable:
                return func(*args, **kwargs)

            # read config
            if not self.path.exists():
                self.path.touch()

            config = read_toml(self.path)

            # query check and update
            bound = sig.bind(*args, **kwargs)
            query = bound.arguments[self.query_arg]

            if query not in config:
                result = func(*args, **kwargs)
                config.update({query: result})
                write_toml(self.path, config)

            return config[query]

        return wrapper


class default_kwargs:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _kwargs = self.kwargs.copy()
            _kwargs.update(kwargs)

            return func(*args, **_kwargs)

        return wrapper


class freeze:
    def __init__(self, func, module=None):
        self.func = func
        self.module = module or getmodule(func)

    def frozen(self, *args, **kwargs):
        if hasattr(self, 'cache'):
            return self.cache

        self.cache = self.func(*args, **kwargs)
        return self.cache

    def __enter__(self):
        setattr(self.module, self.func.__name__, self.frozen)

    def __exit__(self, exc_type, exc_value, traceback):
        setattr(self.module, self.func.__name__, self.func)


def read_toml(path, Class=CaseInsensitiveDict, encoding='utf-8'):
    with Path(path).open('r', encoding=encoding) as f:
        try:
            return Class(toml.load(f))
        except:
            logger.warning(f'fail to load {path}')
            logger.warning('empty dict is returned instead')
            return Class()


def write_toml(path, data, encoding='utf-8'):
    try:
        string = toml.dumps(dict(data))
    except:
        logger.warning('fail to convert data to TOML')
        logger.warning(f'fail to write data to {path}')
        return None

    with Path(path).open('w', encoding=encoding) as f:
        try:
            f.write(string)
        except:
            logger.warning(f'fail to write data to {path}')