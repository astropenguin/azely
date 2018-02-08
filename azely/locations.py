# public items
__all__ = ['Locations']

# standard library
import re
import time
from datetime import datetime
from logging import getLogger
from pprint import pformat
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen
logger = getLogger(__name__)

# dependent packages
import azely
import json

# module constants
TZ = 'timezone'
URL_API = 'https://maps.googleapis.com/maps/api'
URL_GEOCODE  = f'{URL_API}/geocode/json'
URL_TIMEZONE = f'{URL_API}/timezone/json'


# classes
class Locations(dict):
    """Dictionary-like locations class.

    Its instance is a dictionary equivalent to ~/.azely/known_locations.yaml.
    For the first time user create its intance, dictionary should be empty::

        >>> locations = azely.Locations()
        >>> locations
        {}

    Now user can get and add location information from Google Maps::

        >>> locations['alma observatory'] # like normal dictionary
        {'address': 'San Pedro de Atacama, Antofagasta Region, Chile',
         'latitude': -23.0234342,
         'longitude': -67.7538335,
         'name': 'San Pedro de Atacama',
         'query': 'alma observatory',
         'timezone_date': '2018-01-01',
         'timezone_hour': -3.0,
         'timezone_name': 'Chile Summer Time'}

    Internet connection is necessary for the first time user requests a new
    location information. By default, today's timezone information will be
    requested and obtained. This will also update ~/.azely/known_locations.yaml
    with the obtained information as a cached known information. User can also
    spacify date for requesting timezone information on it::

        >>> locations['alma observatory', '2018-08-01']
        {'address': 'San Pedro de Atacama, Antofagasta Region, Chile',
         'latitude': -23.0234342,
         'longitude': -67.7538335,
         'name': 'San Pedro de Atacama',
         'query': 'alma observatory',
         'timezone_date': '2018-08-01',          # changed
         'timezone_hour': -4.0,                  # changed
         'timezone_name': 'Chile Standard Time'} # changed

    This means that an instance will try to update timezone information if the
    spacified date is different from that in the cached information. If no
    internet connection at that time, then the instance will return the cached
    information, whose timezone information is possible be incorrect, though.

    Notes:
        For the convenience, Azely provides its instance, by default, as
        `azely.locations` (not `azely.Locations`) with enabling `reload` option.

    References:
        https://developers.google.com/maps/documentation/geocoding/start
        https://developers.google.com/maps/documentation/timezone/start

    """
    def __init__(self, *, reload=False, timeout=5, encoding='utf-8'):
        """Create (initialize) locations instance.

        The following three keyword-only arguments are supported.

        Args:
            reload (bool, optional, keyword-only): If True,
                ~/.azely/known_locations.yaml is automatically reloaded
                every time before trying to get location from self.
                Default is False.
            timeout (int, optional, keyword-only): Time to wait for remote
                data queries in units of second. Default is 5.
            encoding (str, optional, keyword-only): File encoding used for
                loading and updating ~/.azely/known_locations.yaml.
                Default is 'utf-8'.

        """
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
        """Return location information of given name."""
        self._reload_yamls()

        if isinstance(name, tuple):
            name, date = name
        elif isinstance(name, str):
            name, date = name, None
        else:
            logger.error(f'ValueError: {name}')
            raise ValueError(name)

        if name in self:
            self._update_location(name, date)
        else:
            self._add_location(name, date)

        self._update_known_locations()
        return super().__getitem__(name)

    def _add_location(self, name, date):
        """Request whole information of location on given date."""
        try:
            query = ' '.join(azely.parse_keyword(name))
            date = azely.parse_date(date)
            location = self._request_location(query, date)
            super().__setitem__(name, location)
        except URLError as err:
            logger.error('no internet connection')
            logger.error('location imformation could not be obtained')
            raise err
        except ValueError as err:
            logger.error('exceeded daily request quota for Google Maps API')
            logger.error('location imformation could not be obtained')
            raise err
        except Exception as err:
            logger.error(err)
            logger.error('location imformation could not be obtained')
            raise err

    def _update_location(self, name, date):
        """Update only information of timezone on given date."""
        location_old = super().__getitem__(name)
        date = azely.parse_date(date)

        if location_old[f'{TZ}_date'] == date:
            # timezone name/hour should be unchanged
            return None

        if 'query' not in location_old:
            # manually defined location (probably)
            return None

        try:
            query = location_old['query']
            location_new = self._request_location(query, date)
            tz_info = {k:v for k,v in location_new.items() if TZ in k}
            location_old.update(tz_info)
        except URLError:
            logger.warning('no internet connection')
            logger.warning('timezone information was not updated')
        except ValueError:
            logger.warning('exceeded daily request quota for Google Maps API')
            logger.warning('timezone information was not updated')
        except Exception as err:
            logger.warning(err)
            logger.warning('timezone information was not updated')

    def _request_location(self, query, date):
        """Request result for Google Maps API with parameters"""
        # get geocode from google maps api
        params = {'address': query}
        result = self._request_api(URL_GEOCODE, params)['results'][0]

        name = result['address_components'][0]['long_name']
        address = result['formatted_address']
        lat = result['geometry']['location']['lat']
        lon = result['geometry']['location']['lng']

        # get timezone from google maps api
        dt = datetime.strptime(date, azely.DATE_FORMAT)
        unixtime = time.mktime(dt.utctimetuple())
        params = {'location': f'{lat}, {lon}', 'timestamp': unixtime}
        result = self._request_api(URL_TIMEZONE, params)

        tz_name = result['timeZoneName']
        tz_hour = (result['rawOffset'] + result['dstOffset']) / 3600

        return {'name': name, 'query': query, 'address': address,
                'latitude': lat, 'longitude': lon, f'{TZ}_date': date,
                f'{TZ}_name': tz_name, f'{TZ}_hour': tz_hour}

    def _request_api(self, url, params):
        """Request result for Google Maps API with parameters"""
        url_with_params = f'{url}?{urlencode(params)}'
        with urlopen(url_with_params, timeout=self.timeout) as f:
            result = json.loads(f.read().decode(self.encoding))

        if result['status'] == 'OK':
            return result
        else:
            raise ValueError(result['error_message'])

    def _reload_yamls(self, *, force=False):
        """(Re)load YAML file(s) if reload option is activated."""
        if self.reload or force:
            self._load_known_locations()

    def _load_known_locations(self):
        """Load ~/.azely/known_locations.yaml (`azely.KNOWN_LOCS`)."""
        self.update(azely.read_yaml(azely.KNOWN_LOCS, encoding=self.encoding))

    def _update_known_locations(self):
        """Update ~/.azely/known_locations.yaml (`azely.KNOWN_LOCS`)."""
        azely.write_yaml(azely.KNOWN_LOCS, dict(self), encoding=self.encoding)

    def __repr__(self):
        self._reload_yamls()
        return pformat(dict(self))
