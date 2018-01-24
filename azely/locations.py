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
    """Dictionary-like locations class."""
    def __init__(self, *, reload=False, timeout=5, encoding='utf-8'):
        """Create (initialize) locations instance.

        The following three keyword-only arguments are supported.

        Args:
            reload (bool, optional, keyword-only): If True,
                ~/known_locations.yaml (`azely.KNOWN_LOCS`) is automatically
                reloaded every time before trying to get location from self.
                Default is False.
            timeout (int, optional, keyword-only): Time to wait for remote
                data queries in units of second. Default is 5.
            encoding (str, optional, keyword-only): File encoding used for
                loading and updating ~/known_locations.yaml. Default is 'utf-8'.

        """
        logger.debug(f'reload = {reload}')
        logger.debug(f'timeout = {timeout}')
        logger.debug(f'encoding = {encoding}')

        super().__init__()
        self.reload = reload
        self.timeout = timeout
        self.encoding = encoding

        # initial loading
        self._load_known_locations()

    def __getitem__(self, name):
        if self.reload:
            self._load_known_locations()

        if isinstance(name, tuple):
            name, date = name
        elif isinstance(name, str):
            name, date = name, None
        else:
            logger.error(f'ValueError: {name}')
            raise ValueError(name)

        date = azely.parse_date(date)
        self._update_location(name, date)
        self._update_known_locations()
        return super().__getitem__(name)

    def _update_location(self, name, date):
        if name in self:
            # update only information of timezone on given date
            try:
                query = super().__getitem__(name)['query']
                location = self._request_location(query, date)
                tz_info = {k:v for k,v in location.items() if TZ in k}
                super().__getitem__(name).update(tz_info)
            except KeyError:
                # manually defined location
                pass
            except URLError:
                # no internet connection
                print('logging later!')
            except ValueError:
                # result with some error
                print('logging later!')
        else:
            # request whole information of location on given date
            query = ' '.join(azely.parse_name(name))
            location = self._request_location(query, date)
            super().__setitem__(query, location) # OK?

    def _request_location(self, query, date):
        # get geocode from google maps api
        params = {'address': query}
        result = self._request_api(URL_GEOCODE, params)['results'][0]

        name = result['address_components'][0]['long_name']
        address = result['formatted_address']
        lat = result['geometry']['location']['lat']
        lon = result['geometry']['location']['lng']

        # get timezone from google maps api
        unixtime = self._get_unixtime(date)
        params = {'location': f'{lat}, {lon}', 'timestamp': unixtime}
        result = self._request_api(URL_TIMEZONE, params)

        tz_name = result['timeZoneName']
        tz_hour = (result['rawOffset'] + result['dstOffset']) / 3600

        return {'name': name, 'query': query, 'address': address,
                'latitude': lat, 'longitude': lon, f'{TZ}_date': date,
                f'{TZ}_name': tz_name, f'{TZ}_hour': tz_hour}

    def _request_api(self, url, params):
        url_with_params = f'{url}?{urlencode(params)}'
        with urlopen(url_with_params, timeout=self.timeout) as f:
            result = json.loads(f.read().decode(self.encoding))
            status = result['status']

        if status == 'OK':
            return result
        else:
            message = result['error_message']
            logger.error(f'ValueError: {message}')
            raise ValueError(message)

    def _get_unixtime(self, date):
        """Get unix time of given date (midnight) in units of second."""
        date = datetime.strptime(date, azely.DATE_FORMAT)
        return time.mktime(date.utctimetuple())

    def _load_known_locations(self):
        """Load ~/known_locations.yaml (`azely.KNOWN_LOCS`)."""
        self.update(azely.read_yaml(azely.KNOWN_LOCS, encoding=self.encoding))

    def _update_known_locations(self):
        """Update ~/known_locations.yaml (`azely.KNOWN_LOCS`)."""
        azely.write_yaml(azely.KNOWN_LOCS, dict(self), encoding=self.encoding)

    def __repr__(self):
        if self.reload:
            self._load_known_locations()

        return pformat(dict(self))
