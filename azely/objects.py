# coding: utf-8

# public items
__all__ = ['Objects']

# standard library
import re
from collections import OrderedDict
from pathlib import Path
from pprint import pformat

# dependent packages
import azely
import yaml

yaml.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: OrderedDict(loader.construct_pairs(node))
)

# module constants
SEP = '+'

# classes
class Objects(dict):
    def __init__(self):
        super().__init__()

        # azely data directory
        for filepath in azely.DATA_DIR.glob('**/*.yaml'):
            with filepath.open() as f:
                self.update(yaml.load(f))

        # ~/.azely directory
        for filepath in azely.USER_DIR.glob('**/*.yaml'):
            if filepath.name == azely.KNOWN_LOCS.name:
                continue

            with filepath.open() as f:
                self.update(yaml.load(f))

        # current directory
        for filepath in Path('.').glob('*.yaml'):
            if filepath.name == azely.KNOWN_LOCS.name:
                continue

            with filepath.open() as f:
                self.update(yaml.load(f))

    def __getitem__(self, names_like):
        objects = OrderedDict()
        for name in self._parse_object_names(names_like):
            if name in self:
                value = super().__getitem__(name)
                if azely.isobject(value):
                    # name of an object
                    objects.update({name: value})
                elif isinstance(value, dict):
                    # name of group such as "Default"
                    objects.update(value)
                else:
                    continue
            else:
                # name of preset such as Sun, M82,
                # or name of an object in a group
                objects.update({name: name})
                for value in self.values():
                    if isinstance(value, dict) and name in value:
                        objects.update({name: value[name]})

        return objects

    def _parse_object_names(self, names_like):
        if isinstance(names_like, (list, tuple)):
            return names_like
        elif isinstance(names_like, str):
            return re.sub(azely.SEPARATORS, SEP, names_like).split(SEP)

    def __repr__(self):
        return pformat(dict(self))
