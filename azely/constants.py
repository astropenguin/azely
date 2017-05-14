# coding: utf-8

# imported items
__all__ = [
    'AZELY_DIR',
    'DATA_DIR',
    'KNOWN_LOCS',
]

# standard library
import os

# dependent packages
import azely

# constants
HOME_DIR = os.environ['HOME']
AZELY_DIR = os.path.join(HOME_DIR, '.azely')
DATA_DIR = os.path.join(azely.__path__[0], 'data')
KNOWN_LOCS = os.path.join(AZELY_DIR, 'known_locations.yaml')
