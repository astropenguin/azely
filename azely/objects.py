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
remote_timeout = Conf.remote_timeout

# module constants
EPHEMS = solar_system_ephemeris.bodies
NONOBJ_YAMLS = [azely.KNOWN_LOCS.name,
                azely.KNOWN_OBJS.name,
                azely.CLI_PARSER.name,
                azely.USER_CONFIG.name]

# classes
class Objects(dict):
    """Dictionary-like astronomical objects class.

    Its instance is a dictionary equivalent to YAML files of astronomical
    objects. YAML files are detected and loaded from (1) package's data
    directory (`azely.DATA_DIR`), (2) ~/.azely directory (`azely.USER_DIR`),
    and (3) current directory with this order. If objects of same name are
    found in latter YAML files, the former ones are overwritten by them.
    For the first time user create its intance, dictionary should be like::

        >>> objects = azely.Objects()
        >>> objects
        {'Galactic center': OrderedDict([('l', '23h59m46.6222s'),
                                         ('b', '-00d02m46.1843s'),
                                         ('frame', 'galactic')]),
         'NGC 1068': OrderedDict([('ra', '02h42m40.711s'),
                                  ('dec', '-00d00m47.8116s'),
                                  ('frame', 'icrs')]),
         'default': OrderedDict([('Sun', None)]),
         'solar': OrderedDict([('Sun', None),
                               ('Mercury', None),
                               ('Venus', None),
                               ('Mars', None),
                               ('Jupiter', None),
                               ('Saturn', None),
                               ('Uranus', None),
                               ('Neptune', None)])}

    where Galactic center and NGC 1068 are single objects, and default and
    solar are grouped objects. User can spacify both names of groups and/or
    single objects when you select objects::

        >>> objects['solar'] # group
        OrderedDict([('Sun', 'sun'),
                     ('Mercury', 'mercury'),
                     ('Venus', 'venus'),
                     ('Mars', 'mars'),
                     ('Jupiter', 'jupiter'),
                     ('Saturn', 'saturn'),
                     ('Uranus', 'uranus'),
                     ('Neptune', 'neptune')])

        >>> objects['default, NGC 1068'] # group and single object
        OrderedDict([('Sun', 'sun'),
                     ('NGC 1068', <SkyCoord (ICRS): (ra, dec) ...>)])

    The returned ordered dictionary contains Astropy's skycoords or names of
    solar system emphemeris which are converted inside the instance. When you
    spacify object names which are not listed in the instance, then it will
    try to obtain coordinates of them from web database. Internet connection
    is thus necessary for the first time user requests a new object name.
    This will also update ~/.azely/known_objects.yaml with the obtained
    coordinate as a cached known object.

    Attributes:
        groups (OrderedDict): Ordered dictionary that has only object groups.
            It is intended to be used inside an instance.
        flatitems (OrderedDict): Ordered dictionary of all objects with groups
            flattened. It is intended to be used inside an instance.

    Notes:
        For the convenience, Azely provides its instance, by default, as
        `azely.objects` (not `azely.Objects`) with enabling `reload` option.

    References:
        http://docs.astropy.org/en/stable/coordinates/skycoord.html

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
        self._reload_yamls()

    def __getitem__(self, names):
        """Return azimuth/elevation coordinate objects of given names."""

        objects = OrderedDict()

        for name in azely.parse_keyword(names):
            objects.update(self._select_objects(name))

        for item in objects.items():
            objects.update(self._parse_object(*item))
        self._reload_yamls()

        self._update_known_objects(objects)
        return objects

    def _select_objects(self, name):
        """Return {name: object_like, ...} from name of object or group."""
        if name in self.groups:
            return self.groups[name]
        elif name in self.flatitems:
            return {name: self.flatitems[name]}
        else:
            return {name: name}

    def _parse_object(self, name, object_like):
        """Parse {name: object_like} and return {name: skycoord}."""
        # pre-processing
        object_like = object_like or name

        if not isinstance(object_like, (dict, str)):
            logger.warning(f'invalid object: {object_like}')
            logger.warning('this will be not plotted')
            return {name: azely.PASS_FLAG}

        if name in self.known_objects:
            object_like = self.known_objects[name]
            return {name: SkyCoord(**object_like)}

        # dict of skycoord information
        if isinstance(object_like, dict):
            try:
                return {name: SkyCoord(**object_like)}
            except ValueError:
                logger.warning(f'invalid object: {object_like}')
                logger.warning('this will be not plotted')
                return {name: azely.PASS_FLAG}

        # solar objects (sun and planets)
        if object_like.lower() in EPHEMS:
            return {name: object_like.lower()}

        # otherwise: try to get information from catalogue
        try:
            with remote_timeout.set_temp(self.timeout):
                return {name: SkyCoord.from_name(object_like)}
        except NameResolveError:
            logger.warning(f'cannot resolve name: {object_like}')
            logger.warning('this will be not plotted')
            return {name: azely.PASS_FLAG}
        except Exception:
            logger.warning(f'invalid object: {object_like}')
            logger.warning('this will be not plotted')
            return {name: azely.PASS_FLAG}

    def _reload_yamls(self, force=False):
        """(Re)load YAML file(s) if reload option is activated."""
        if self.reload or force:
            self._load_objects()

        self.groups = OrderedDict()

        for name, object_like in self.items():
            if not isinstance(object_like, dict):
                continue

            try:
                SkyCoord(**object_like)
            except:
                self.groups.update({name: object_like})

        self.flatitems = OrderedDict()

        for name, object_like in self.items():
            if name in self.groups:
                self.flatitems.update(object_like)
            else:
                self.flatitems.update({name: object_like})

    def _load_objects(self):
        """Load YAML files (*.yaml) of astronomical objects."""
        # azely data directory
        for path in azely.DATA_DIR.glob('*.yaml'):
            if path.name in NONOBJ_YAMLS:
                continue

            self.update(azely.read_yaml(path, True, encoding=self.encoding))

        # ~/.azely directory (search in subdirectories)
        for path in azely.USER_DIR.glob('**/*.yaml'):
            if path.name in NONOBJ_YAMLS:
                continue

            self.update(azely.read_yaml(path, True, encoding=self.encoding))

        # current directory (do not search in subdirectories)
        for path in Path('.').glob('*.yaml'):
            if path.name in NONOBJ_YAMLS:
                continue

            self.update(azely.read_yaml(path, True, encoding=self.encoding))

    def _load_known_objects(self):
        """Load ~/.azely/known_objects.yaml (`azely.KNOWN_OBJS`)."""
        self.known_objects = azely.read_yaml(azely.KNOWN_OBJS,
                                             encoding=self.encoding)

    def _update_known_objects(self, objects):
        """Update ~/.azely/known_objects.yaml (`azely.KNOWN_OBJS`)."""
        for name, obj in objects.items():
            if isinstance(obj, SkyCoord):
                ra, dec = obj.to_string('hmsdms').split()
                coords = {'ra': ra, 'dec': dec, 'frame': 'icrs'}
                self.known_objects.update({name: coords})

        azely.write_yaml(azely.KNOWN_OBJS, self.known_objects,
                                           encoding=self.encoding)

    def __repr__(self):
        self._reload_yamls()
        return pformat(dict(self))


class KnownObjects(OrderedDict):
    def __init__(self, *, reload=False, timeout=5, encoding='utf-8'):
        logger.debug(f'reload = {reload}')
        logger.debug(f'timeout = {timeout}')
        logger.debug(f'encoding = {encoding}')

        super().__init__()
        self.reload = reload
        self.timeout = timeout
        self.encoding = encoding

        # initial loading
        self._reload_yamls(force=True)

    def __getitem__(self, name):
        self._reload_yamls()

        if name not in self:
            self._add_object(name, 'icrs')
            self._update_known_objects()

        return super().__getitem__(name)

    def _add_object(self, name, frame='icrs'):
        with remote_timeout.set_temp(self.timeout):
            skycoord = SkyCoord.from_name(name, frame)
            ra, dec = skycoord.to_string('hmsdms').split()

        super().__setitem__(name, {'name': name,
                                   'ra': ra,
                                   'dec': dec,
                                   'frame': frame})

    def _reload_yamls(self, *, force=False):
        """(Re)load YAML file(s) if reload option is activated."""
        if self.reload or force:
            self._load_known_objects()

    def _load_known_objects(self):
        """Load known_objects.yaml (`azely.KNOWN_OBJS`)."""
        self.update(azely.read_yaml(azely.KNOWN_OBJS, encoding=self.encoding))

    def _update_known_objects(self):
        """Update known_objects.yaml (`azely.KNOWN_OBJS`)."""
        azely.write_yaml(azely.KNOWN_OBJS, dict(self), encoding=self.encoding)

    def __repr__(self):
        self._reload_yamls()
        return pformat(dict(self))
