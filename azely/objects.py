# coding: utf-8

# public items
__all__ = ['Objects']

# standard library
from collections import OrderedDict
from glob import glob
from os.path import join
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

        # azely data directorVy
        for fname in glob(join(azely.DATA_DIR, '**', '*.yaml'), recursive=True):
            with open(fname, 'r') as f:
                self.update(yaml.load(f))

        # ~/.azely directory
        for fname in glob(join(azely.AZELY_DIR, '**', '*.yaml'), recursive=True):
            if fname == azely.KNOWN_LOCS:
                continue

            with open(fname, 'r') as f:
                self.update(yaml.load(f))

        # current directory
        for fname in glob(join('**', '*.yaml'), recursive=True):
            with open(fname, 'r') as f:
                self.update(yaml.load(f))

    def __getitem__(self, name):
        item = OrderedDict()
        for obj in azely.parse_objects(name):
            if obj in self:
                value = super().__getitem__(obj)
                if issubclass(type(value), dict):
                    if not any(['ra' in value, 'dec' in value]):
                        item.update(value)
                        continue

                item.update({obj: value})
            else:
                item.update({obj: obj})
                for value in self.values():
                    if issubclass(type(value), dict):
                        item.update({obj: value.get(obj, obj)})

        return item

    def __repr__(self):
        return pformat(dict(self))
