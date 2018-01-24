# public items
__all__ = ['Objects']

# standard library
import re
from collections import OrderedDict
from logging import getLogger
from pathlib import Path
from pprint import pformat
logger = getLogger(__name__)

# dependent packages
import azely
from astropy.coordinates import SkyCoord
from astropy.coordinates import solar_system_ephemeris
from astropy.coordinates.name_resolve import NameResolveError
from astropy.utils.data import Conf

# module constants
EPHEMS = solar_system_ephemeris.bodies


# classes
class Objects(dict):
    """Dictionary-like astronomical objects class.

    YAML files are detected and loaded from (1) package's data directory
    (`azely.DATA_DIR`), (2) ~/.azely directory (`azely.USER_DIR`), and
    (3) current directory with this order. If objects of same name are
    found in later YAML files, the former ones are overwritten by them.

    Attributes:
        groups (OrderedDict):
        flatitems (OrderedDict):

    """
    def __init__(self, *, reload=False, timeout=5, encoding='utf-8'):
        """Create (initialize) astronomical objects instance.

        The following three keyword-only arguments are supported.

        Args:
            reload (bool, optional, keyword-only): If True, YAML files of
                astronomical objects are automatically reloaded every time
                before trying to get objects from self. Default is False.
            timeout (int, optional, keyword-only): Time to wait for remote
                data queries in units of second. Default is 5.
            encoding (str, optional, keyword-only): File encoding used for
                loading and updating YAML files. Default is 'utf-8'.

        """
        logger.debug(f'reload = {reload}')
        logger.debug(f'timeout = {timeout}')
        logger.debug(f'encoding = {encoding}')

        super().__init__()
        self.reload = reload
        self.timeout = timeout
        self.encoding = encoding

        # initial loading
        self._load_objects()
        self._load_known_objects()

    @property
    def groups(self):
        """Ordered dict that has only object groups."""
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
        """Ordered dict of all objects with groups flattened."""
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
        """This may be a bad implementation ..."""
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
                Conf.remote_timeout.set(self.timeout)
                coord = SkyCoord.from_name(object_like, 'icrs')
                ra, dec = coord.to_string('hmsdms').split()
                dict_coord = {'ra': ra, 'dec': dec, 'frame': 'icrs'}

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
        """Load YAML files (*.yaml) of astronomical objects."""
        # azely data directory
        for path in azely.DATA_DIR.glob('*.yaml'):
            if path.name in (azely.CLI_CONFIG.name,):
                continue

            self.update(azely.read_yaml(path, True, encoding=self.encoding))

        # ~/.azely directory (search in subdirectories)
        for path in azely.USER_DIR.glob('**/*.yaml'):
            if path.name in (azely.KNOWN_LOCS.name, azely.KNOWN_OBJS.name):
                continue

            self.update(azely.read_yaml(path, True, encoding=self.encoding))

        # current directory (do not search in subdirectories)
        for path in Path('.').glob('*.yaml'):
            if path.name in (azely.KNOWN_LOCS.name, azely.KNOWN_OBJS.name):
                continue

            self.update(azely.read_yaml(path, True, encoding=self.encoding))

    def _load_known_objects(self):
        """Load ~/known_objects.yaml (`azely.KNOWN_OBJS`)."""
        self.known_objects = azely.read_yaml(azely.KNOWN_OBJS,
                                             encoding=self.encoding)

    def _update_known_objects(self):
        """Update ~/known_objects.yaml (`azely.KNOWN_OBJS`)."""
        azely.write_yaml(azely.KNOWN_OBJS, self.known_objects,
                                           encoding=self.encoding)

    def __repr__(self):
        if self.reload:
            self._load_objects()
            self._load_known_objects()

        return pformat(dict(self))
