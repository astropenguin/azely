__all__ = ['open_toml',
           'cache_to',
           'set_defaults',
           'findin_toml',
           'open_googlemaps']


# standard library
import webbrowser
from copy import deepcopy
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
            if not self.path.exists():
                self.path.touch()

            bound = sig.bind(*args, **kwargs)
            query = bound.arguments[self.arg_query]

            if query is None:
                return func(*args, **kwargs)

            with open_toml(self.path) as cache:
                if query not in cache:
                    item = func(*args, **kwargs)
                    cache.update({query: item})

                return cache[query]

        return wrapper


class set_defaults:
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
            if (p.kind==p.VAR_POSITIONAL) or (p.kind==p.VAR_KEYWORD):
                params.append(p.replace())
                continue

            if not p.name in self.defaults:
                params.append(p.replace())
                continue

            default = self.defaults[p.name]
            params.append(p.replace(default=default))

        return sig.replace(parameters=params)


def findin_toml(query, pattern='*.toml', searchdirs='.'):
    if query is None:
        return iter([])

    for dirpath in (Path(p).expanduser() for p in searchdirs):
        if not dirpath.is_dir():
            continue

        for path in dirpath.glob(pattern):
            data = open_toml(path)

            if not query in data:
                continue

            yield deepcopy(data[query])


def open_googlemaps(latitude, longitude, **_):
    query = urlencode({'q': f'{latitude}, {longitude}'})
    webbrowser.open(f'https://google.com/maps?{query}')
