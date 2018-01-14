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
from astropy.coordinates import SkyCoord
from astropy.coordinates import solar_system_ephemeris
from astropy.coordinates.name_resolve import NameResolveError

# module constants
EPHEMS = solar_system_ephemeris.bodies

# use OrderedDict in PyYAML
yaml.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: OrderedDict(loader.construct_pairs(node))
)


# classes
class Objects(OrderedDict):
    def __init__(self):
        super().__init__()
        self._load_object_yamls()
        self._load_known_objects()

    @property
    def groups(self):
        if hasattr(self, '_groups'):
            return self._groups

        self._groups = OrderedDict()
        for name, object_like in self.items():
            if not isinstance(object_like, dict):
                continue

            try:
                SkyCoord(**object_like)
            except:
                self._groups.update({name: object_like})

        return self._groups

    @property
    def flatitems(self):
        if hasattr(self, '_flatitems'):
            return self._flatitems

        self._flatitems = OrderedDict()
        for name, object_like in self.items():
            if name in self.groups:
                self._flatitems.update(object_like)
            else:
                self._flatitems.update({name: object_like})

        return self._flatitems

    def __getitem__(self, names_like):
        objects = self._select_objects(names_like)
        skycoords = self._parse_objects(objects)
        return skycoords

    def _select_objects(self, names_like):
        objects = OrderedDict()

        for name in self._parse_object_names(names_like):
            if name in self.groups:
                objects.update(self.groups[name])
            elif name in self.flatitems:
                objects.update({name: self.flatitems[name]})
            else:
                objects.update({name: name})

        for name, object_like in objects.items():
            if not object_like:
                objects.update({name: name})

        return objects

    def _parse_objects(self, objects):
        skycoords = OrderedDict()

        for name, object_like in objects.items():
            if isinstance(object_like, dict):
                try:
                    coord = SkyCoord(**object_like)
                    skycoords.update({name: coord})
                except ValueError:
                    print('logging later!')
            elif isinstance(object_like, str):
                if object_like.lower() in EPHEMS:
                    skycoords.update({name: object_like})
                    continue

                if name in self._known_objects:
                    coord = SkyCoord(**self._known_objects[name])
                    skycoords.update({name: coord})
                    continue

                try:
                    coord = SkyCoord.from_name(name)
                    radec = {'ra': str(coord.ra), 'dec': str(coord.dec)}
                    skycoords.update({name: coord})
                    self._known_objects.update({name: radec})
                except NameResolveError:
                    print('logging later!')
            else:
                print('logging later!')

        self._update_known_objects()
        return skycoords

    def _load_object_yamls(self):
        # azely data directory
        for filepath in azely.DATA_DIR.glob('*.yaml'):
            if filepath.name == azely.CLI_CONFIG.name:
                continue

            with filepath.open('r') as f:
                self.update(yaml.load(f))

        # ~/.azely directory (search in subdirectories)
        for filepath in azely.USER_DIR.glob('**/*.yaml'):
            if filepath.name == azely.KNOWN_LOCS.name:
                continue

            if filepath.name == azely.KNOWN_OBJS.name:
                continue

            with filepath.open('r') as f:
                try:
                    self.update(yaml.load(f))
                except:
                    print('logging later!')

        # current directory (do not search in subdirectories)
        for filepath in Path('.').glob('*.yaml'):
            if filepath.name == azely.KNOWN_LOCS.name:
                continue

            if filepath.name == azely.KNOWN_OBJS.name:
                continue

            with filepath.open('r') as f:
                try:
                    self.update(yaml.load(f))
                except:
                    print('logging later!')

    def _load_known_objects(self):
        if not hasattr(self, '_known_objects'):
            self._known_objects = {}

        with azely.KNOWN_OBJS.open('r') as f:
            self._known_objects.update(yaml.load(f, yaml.loader.SafeLoader))

    def _update_known_objects(self):
        with azely.KNOWN_OBJS.open('w') as f:
            f.write(yaml.dump(self._known_objects, default_flow_style=False))

    def _parse_object_names(self, names_like):
        if isinstance(names_like, (list, tuple)):
            return names_like
        elif isinstance(names_like, str):
            pattern = f'[{azely.SEPARATORS}]+'
            return re.sub(pattern, ' ', names_like).split()

    def __repr__(self):
        return pformat(dict(self))
