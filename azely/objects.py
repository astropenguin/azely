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
class Objects(dict):
    def __init__(self, reload=True):
        super().__init__()
        self._load_object_yamls()
        self._load_known_objects()
        self.reload = reload

    @property
    def params(self):
        return {'reload': self.reload}

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
        if self.reload:
            self._load_object_yamls()

        objects = OrderedDict()

        for name in self._parse_names(names_like):
            self._add_object(objects, name)

        for name in objects:
            self._parse_object(objects, name)

        self._update_known_objects()
        return objects

    def _add_object(self, objects, name):
        if name in self.groups:
            objects.update(self.groups[name])
        elif name in self.flatitems:
            objects.update({name: self.flatitems[name]})
        else:
            objects.update({name: name})

    def _parse_object(self, objects, name):
        if not objects[name]:
            objects.update({name: name})

        object_like = objects[name]

        if isinstance(object_like, dict):
            try:
                coord = SkyCoord(**object_like)
                objects.update({name: coord})
            except ValueError:
                print('logging later!')
        elif isinstance(object_like, str):
            if object_like.lower() in EPHEMS:
                return

            if name in self._known_objects:
                coord = SkyCoord(**self._known_objects[name])
                objects.update({name: coord})
                return

            try:
                frame = 'icrs'
                coord = SkyCoord.from_name(object_like, frame)
                ra, dec = coord.to_string('hmsdms').split()
                dict_coord = {'ra': ra, 'dec': dec, 'frame': frame}

                objects.update({name: coord})
                self._known_objects.update({name: dict_coord})
            except NameResolveError:
                print('logging later!')
        else:
            print('logging later!')

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
        self._known_objects = {}

        with azely.KNOWN_OBJS.open('r') as f:
            known_objects = yaml.load(f, yaml.loader.SafeLoader)

        if known_objects is not None:
            self._known_objects.update(known_objects)

    def _update_known_objects(self):
        with azely.KNOWN_OBJS.open('w') as f:
            f.write(yaml.dump(self._known_objects, default_flow_style=False))

    def _parse_names(self, names_like):
        if isinstance(names_like, (list, tuple)):
            return names_like
        elif isinstance(names_like, str):
            pattern = f'[{azely.SEPARATORS}]+'
            return re.sub(pattern, ' ', names_like).split()

    def __repr__(self):
        if self.reload:
            self._load_object_yamls()

        return pformat(dict(self))
