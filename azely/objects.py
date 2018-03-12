# public items
__all__ = ['Objects']

# standard library
from collections import OrderedDict
from copy import copy
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
SOLAR_SYSTEM_OBJECTS = solar_system_ephemeris.bodies
NONOBJ_YAMLS = [azely.KNOWN_LOCS.name,
                azely.KNOWN_OBJS.name,
                azely.CLI_PARSER.name,
                azely.USER_CONFIG.name]

# classes
class Objects(OrderedDict):
    """Dictionary-like astronomical objects class.

    Its instance is a dictionary equivalent to YAML files of astronomical
    objects. YAML files are detected and loaded from (1) package's data
    directory (`azely.DATA_DIR`), (2) ~/.azely directory (`azely.USER_DIR`),
    and (3) current directory with this order. If objects of same name are
    found in latter YAML files, the former ones are overwritten by them.
    For the first time user create its intance, dictionary should be like::

        >>> objects = azely.Objects()
        >>> objects
        Objects([('default', OrderedDict([('Sun', None)])),
                 ('solar',
                  OrderedDict([('Sun', None),
                               ('Mercury', None),
                               ('Venus', None),
                               ('Mars', None),
                               ('Jupiter', None),
                               ('Saturn', None),
                               ('Uranus', None),
                               ('Neptune', None)])),
                 ('NGC 1068',
                  OrderedDict([('name', 'NGC 1068'),
                               ('ra', '02h42m40.711s'),
                               ('dec', '-00d00m47.8116s'),
                               ('frame', 'icrs')])),
                 ('GC',
                  OrderedDict([('name', 'Galactic center'),
                               ('l', '23h59m46.6222s'),
                               ('b', '-00d02m46.1843s'),
                               ('frame', 'galactic')]))])

    where Galactic center and NGC 1068 are single objects, and default and
    solar are grouped objects. User can spacify both names of groups and/or
    single objects when you select objects::

        >>> objects['solar'] # group
        [{'name': 'sun'},
         {'name': 'mercury'},
         {'name': 'venus'},
         {'name': 'mars'},
         {'name': 'jupiter'},
         {'name': 'saturn'},
         {'name': 'uranus'},
         {'name': 'neptune'}]

        >>> objects['default, NGC 1068'] # group and single object
        [{'name': 'sun'},
         OrderedDict([('name', 'NGC 1068'),
                      ('ra', '02h42m40.711s'),
                      ('dec', '-00d00m47.8116s'),
                      ('frame', 'icrs')])]

    The returned list contains coordinates of objects. When you spacify object
    names which are not listed in the instance, then it will try to obtain
    coordinates of them from web database. Internet connection is thus necessary
    for the first time user requests a new object name. This will also update
    ~/.azely/known_objects.yaml with the obtained coordinate as a cached object.

    Attributes:
        groups (OrderedDict): Ordered dictionary that has only object groups.
            It is intended to be used inside an instance.
        flattened (OrderedDict): Ordered dictionary of all objects with groups
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
        self.known = KnownObjects(reload=reload,
                                  timeout=timeout,
                                  encoding=encoding)

        # initial loading of YAMLs
        # groups and flattened are created herein
        self._reload_yamls(force=True)

    def __getitem__(self, keyword_like):
        """Return azimuth/elevation coordinate objects of given names."""
        self._reload_yamls()

        keywords = azely.parse_keyword(keyword_like, seps=',')
        values = azely.flatten(self._values_from(kwd) for kwd in keywords)
        objects = (self._object_from(val) for val in values)
        return list(filter(None, objects))

    def _values_from(self, keyword):
        """Parse keyword and return values."""
        if keyword in self.groups:
            group = self.groups[keyword]
            return (val or key for key, val in group.items())

        return self.flattened.get(keyword) or keyword

    def _object_from(self, value):
        """Convert value to coordinate object (if necessary)."""
        if isinstance(value, dict):
            return dict(value)

        if value.lower() in SOLAR_SYSTEM_OBJECTS:
            return {'name': value}

        try:
            return self.known[value]
        except NameResolveError as error:
            logger.warning(error)
            return None

    def _reload_yamls(self, *, force=False):
        """(Re)load YAML file(s) if reload option is activated."""
        if not (self.reload or force):
            return None

        self._load_objects()
        self.groups = OrderedDict()
        self.flattened = OrderedDict()

        # update dict of groups
        for name, obj in self.items():
            try:
                _obj = copy(obj)
                _obj.pop('name')
                SkyCoord(**_obj)
            except Exception:
                self.groups.update({name: obj})

        # update dict of flattened
        for name, obj in self.items():
            if name in self.groups:
                self.flattened.update(obj)
            else:
                self.flattened.update({name: obj})

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

    def __repr__(self):
        self._reload_yamls()
        return pformat(dict(self))


class KnownObjects(dict):
    def __init__(self, *, reload=False, timeout=5, encoding='utf-8'):
        logger.debug(f'reload = {reload}')
        logger.debug(f'timeout = {timeout}')
        logger.debug(f'encoding = {encoding}')

        super().__init__()
        self.reload = reload
        self.timeout = timeout
        self.encoding = encoding

        # initial loading of YAMLs
        self._reload_yamls(force=True)

    def __getitem__(self, name):
        self._reload_yamls()

        if name not in self:
            self._add_object(name, frame='icrs')
            self._update_known_objects()

        return super().__getitem__(name)

    def _add_object(self, name, *, frame='icrs'):
        with remote_timeout.set_temp(self.timeout):
            skycoord = SkyCoord.from_name(name, frame)
            ra, dec = skycoord.to_string('hmsdms').split()

        super().__setitem__(name, {'name': name, 'ra': ra,
                                   'dec': dec, 'frame': frame})

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
