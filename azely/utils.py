__all__ = ['cache_to',
           'default_kwargs',
           'read_toml',
           'write_toml',
           'parse_date']


# standard library
from datetime import date
from datetime import datetime
from functools import wraps
from inspect import signature
from pathlib import Path
from logging import getLogger
logger = getLogger(__name__)


# dependent packages
import toml
import azely
from dateutil.parser import parse
from requests.utils import CaseInsensitiveDict


class cache_to:
    def __init__(self, path, enable=True, key='query'):
        self.path = Path(path).expanduser()
        self.enable = enable
        self.key = key

    def __call__(self, func):
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enable:
                return func(*args, **kwargs)

            if not self.path.exists():
                self.path.touch()

            bound = sig.bind(*args, **kwargs)
            query = str(bound.arguments[self.key])
            config = azely.read_toml(self.path)

            if query not in config:
                result = func(*args, **kwargs)
                config.update({query: result})
                azely.write_toml(self.path, config)

            return config[query]

        return wrapper


class default_kwargs:
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs_ = self.kwargs.copy()
            kwargs_.update(kwargs)

            return func(*args, **kwargs_)

        return wrapper


def read_toml(path, *, mode='r', encoding='utf-8'):
    with Path(path).open(mode, encoding=encoding) as f:
        try:
            return CaseInsensitiveDict(toml.load(f))
        except:
            logger.warning(f'fail to load {path}')
            logger.warning('empty dict is returned instead')
            return CaseInsensitiveDict()


def write_toml(path, data, *, mode='w', encoding='utf-8'):
    try:
        string = toml.dumps(dict(data))
    except:
        logger.warning('fail to convert data to TOML')
        logger.warning(f'fail to write data to {path}')
        return

    with Path(path).open(mode, encoding=encoding) as f:
        try:
            f.write(string)
        except:
            logger.warning(f'fail to write data to {path}')


def parse_date(date_like=None):
    if date_like is None:
        return date.today()

    try:
        dt = parse(str(date_like), yearfirst=True)
        return date.fromtimestamp(dt.timestamp())
    except (ValueError, TypeError):
        logger.warning(f'Invalid format: {date_like}')
        logger.warning('Today is returned instead')
        return date.today()

