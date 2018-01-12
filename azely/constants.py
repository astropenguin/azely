# coding: utf-8

# public items
__all__ = ['DATA_DIR',
           'USER_DIR',
           'AZELY_CONF',
           'KNOWN_LOCS',
           'SEPARATORS',
           'DATE_FORMAT']

# standard library
from shutil import copy
from pathlib import Path

# dependent packages
import azely
import yaml

# module constants
HOME = Path('~').expanduser()
CONF = 'azely_config.yaml'
OBJS = 'sample_objects.yaml'
LOCS = 'known_locations.yaml'


# package constants
DATA_DIR = Path(azely.__path__[0]) / 'data'
USER_DIR = HOME / '.azely'
AZELY_CONF = USER_DIR / CONF
KNOWN_LOCS = USER_DIR / LOCS
SEPARATORS = '-+_,./ '
DATE_FORMAT = '%Y-%m-%d'


# create directory and file (if not existing)
if not USER_DIR.exists():
    USER_DIR.mkdir()

if not AZELY_CONF.exists():
    copy(DATA_DIR / CONF, USER_DIR)

if not (USER_DIR / OBJS).exists():
    copy(DATA_DIR / OBJS, USER_DIR)

if not KNOWN_LOCS.exists():
    with KNOWN_LOCS.open('w') as f:
        f.write(yaml.dump({}, default_flow_style=False))
