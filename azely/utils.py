__all__ = ['open_toml',
           'cache_to',
           'override_defaults',
           'abspath',
           'open_googlemaps']


# standard library
import webbrowser
from functools import wraps
from inspect import signature
from logging import getLogger
from pathlib import Path
from urllib.parse import urlencode
logger = getLogger(__name__)


# dependent packages
import toml
from requests.utils import CaseInsensitiveDict


class open_toml(CaseInsensitiveDict):
    def __init__(self, path, update_when_exit=True):
        self.path = Path(path)
        self.update_when_exit = update_when_exit
        super().__init__(self.load_toml())

    def load_toml(self):
        with self.path.open('r') as f:
            return toml.load(f)

    def update_toml(self):
        data = toml.dumps(dict(self))

        with self.path.open('w') as f:
                f.write(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.update_when_exit:
            self.update_toml()


class cache_to:
    def __init__(self, path=None, arg_query='query'):
        if path is not None:
            self.path = Path(path).expanduser()
            self.arg_query = arg_query

    def __call__(self, func):
        if not hasattr(self, 'path'):
            return func

        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # read cache
            if not self.path.exists():
                logger.info(f'creating {self.path}')
                self.path.touch()

            logger.debug(f'loading {self.path}')
            cache = read_toml(self.path)

            # get query
            bound = sig.bind(*args, **kwargs)
            query = bound.arguments[self.arg_query]

            # return cached data if it exists
            if query in cache:
                logger.debug(f'{query} exists in {self.path}')
                logger.debug('cached data is then returned')
                return cache[query]

            logger.debug(f'{query} does not exist in {self.path}')
            logger.debug('trying to get data and cache it')
            data = func(*args, **kwargs)

            cache.update({query: data})
            write_toml(self.path, cache)
            return data

        return wrapper


class override_defaults:
    def __init__(self, **defaults):
        self.defaults = defaults

    def __call__(self, func):
        sig = signature(func)
        sig_new = self.modify_signature(sig)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig_new.bind(*args, **kwargs)
            bound.apply_defaults()
            return func(*bound.args, **bound.kwargs)

        return wrapper

    def modify_signature(self, sig):
        params = []

        for p in sig.parameters.values():
            if (p.kind == p.VAR_POSITIONAL) or (p.kind==p.VAR_KEYWORD):
                params.append(p.replace())
                continue

            if not p.name in self.defaults:
                params.append(p.replace())
                continue

            params.append(p.replace(default=self.defaults[p.name]))

        return sig.replace(parameters=params)


def abspath(*paths):
    return (Path(p).expanduser() for p in paths)


def open_googlemaps(latitude, longitude, **_):
    query = urlencode({'q': f'{latitude}, {longitude}'})
    webbrowser.open(f'https://google.com/maps?{query}')
