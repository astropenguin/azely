# coding: utf-8

# public items
__all__ = [
    'Objects'
]

# standard library
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

    def __getitem__(self, name):
        item = OrderedDict()
        for obj in azely.parse_objects(name):
            if obj in self:
                value = super().__getitem__(obj)
                if (isinstance(value, dict)
                    and not set(value) & {'ra', 'dec'}):
                    # name of group such as "Default"
                    item.update(value)
                else:
                    # name of an object defined as (RA, Dec)
                    item.update({obj: value})
            else:
                # name of preset such as Sun, M82,
                # or name of an object in a group
                item.update({obj: obj})
                for value in self.values():
                    if isinstance(value, dict) and obj in value:
                        item.update({obj: value[obj]})

        return item

    def __repr__(self):
        return pformat(dict(self))
