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
from astropy.coordinates import SkyCoord
from astropy.coordinates import solar_system_ephemeris
from astropy.coordinates.name_resolve import NameResolveError

# module constants
EPHEMS = solar_system_ephemeris.bodies


# classes
class Objects(dict):
    def __init__(self, *, reload=True, timeout=5, encoding='utf-8'):
        super().__init__()
        self._load_objects()
        self._load_known_objects()
        self.reload = reload
        self.timeout = timeout # not implemented yet
        self.encoding = encoding

    @property
    def groups(self):
        if hasattr(self, '_groups') and not self.reload:
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
        if hasattr(self, '_flatitems') and not self.reload:
            return self._flatitems

        self._flatitems = OrderedDict()
        for name, object_like in self.items():
            if name in self.groups:
                self._flatitems.update(object_like)
            else:
                self._flatitems.update({name: object_like})

        return self._flatitems

    def __getitem__(self, names):
        if self.reload:
            self._load_objects()
            self._load_known_objects()

        objects = OrderedDict()

        for name in azely.parse_name(names):
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
        # pre-processing
        if not objects[name]:
            objects.update({name: name})

        object_like = objects[name]

        if isinstance(object_like, dict):
            # if object_like is a group of objects
            try:
                coord = SkyCoord(**object_like)
                objects.update({name: coord})
            except ValueError:
                print('logging later!')
                objects.update({name: azely.PASS_FLAG})
        elif isinstance(object_like, str):
            # if object_like is a name of object
            if object_like.lower() in EPHEMS:
                # solar objects are not processed here
                # they need date and time for calculation
                return None

            if name in self.known_objects:
                # if name exists in known_objects.yaml
                coord = SkyCoord(**self.known_objects[name])
                objects.update({name: coord})
                return None

            # otherwise: try to get information from catalogue
            # and update known_objects.yaml with the result
            try:
                frame = 'icrs'
                coord = SkyCoord.from_name(object_like, frame)
                ra, dec = coord.to_string('hmsdms').split()
                dict_coord = {'ra': ra, 'dec': dec, 'frame': frame}

                objects.update({name: coord})
                self.known_objects.update({name: dict_coord})
            except NameResolveError:
                print('logging later!')
                objects.update({name: azely.PASS_FLAG})
        else:
            # if object_like has invalid type
            print('logging later!')
            objects.update({name: azely.PASS_FLAG})

    def _load_objects(self):
        # azely data directory
        for filepath in azely.DATA_DIR.glob('*.yaml'):
            if filepath.name == azely.CLI_CONFIG.name:
                continue

            self.update(azely.read_yaml(filepath, True, encoding=self.encoding))

        # ~/.azely directory (search in subdirectories)
        for filepath in azely.USER_DIR.glob('**/*.yaml'):
            if (filepath.name == azely.KNOWN_LOCS.name
                or filepath.name == azely.KNOWN_OBJS.name):
                # ignore these files
                continue

            self.update(azely.read_yaml(filepath, True, encoding=self.encoding))

        # current directory (do not search in subdirectories)
        for filepath in Path('.').glob('*.yaml'):
            if (filepath.name == azely.KNOWN_LOCS.name
                or filepath.name == azely.KNOWN_OBJS.name):
                # ignore these files
                continue

            self.update(azely.read_yaml(filepath, True, encoding=self.encoding))

    def _load_known_objects(self):
        self.known_objects = azely.read_yaml(azely.KNOWN_OBJS, encoding=self.encoding)

    def _update_known_objects(self):
        azely.write_yaml(azely.KNOWN_OBJS, self.known_objects, encoding=self.encoding)

    def __repr__(self):
        if self.reload:
            self._load_objects()
            self._load_known_objects()

        return pformat(dict(self))
