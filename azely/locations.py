# coding: utf-8

# public items
__all__ = ['Locations']

# standard library
import re
import time
from datetime import datetime
from pprint import pformat
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

# dependent packages
import azely
import json

# module constants
URL_API = 'https://maps.googleapis.com/maps/api'
URL_GEOCODE  = f'{URL_API}/geocode/json'
URL_TIMEZONE = f'{URL_API}/timezone/json'


# classes
class Locations(dict):
    def __init__(self, date=None, *, reload=True, timeout=5, encoding='utf-8'):
        super().__init__()
        self._load_known_locations()

        self.date = azely.parse_date(date) # for old AzEl (temporary)
        self.reload = reload
        self.timeout = timeout
        self.encoding = encoding

    def __getitem__(self, name):
        if self.reload:
            self._load_known_locations()

        if isinstance(name, tuple):
            name, date = name
        elif isinstance(name, str):
            # name, date = name, None (uncomment soon!)
            date = self.date # for old AzEl (temporary)
        else:
            raise ValueError(name)

        self._update_location(name, date)
        self._update_known_locations()
        return super().__getitem__(name)

    def _update_location(self, name, date=None):
        if name in self:
            # update only information of timezone on given date
            try:
                query = super().__getitem__(name)['query']
                location = self._request_location(query, date)
                tz_info = {k:v for k,v in location.items() if 'timezone' in k}
                super().__getitem__(name).update(tz_info)
            except KeyError:
                # manually defined location
                # not necessary to be updated
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
            super().__setitem__(query, location)

    def _request_location(self, query, date=None):
        location = {}

        # get geocode from google maps api
        params = {'address': query}
        result = self._request_api(URL_GEOCODE, params)['results'][0]
        location['name']      = result['address_components'][0]['long_name']
        location['address']   = result['formatted_address']
        location['latitude']  = result['geometry']['location']['lat']
        location['longitude'] = result['geometry']['location']['lng']
        location['query']     = query

        # get timezone from google maps api
        date = azely.parse_date(date)
        dateobj = datetime.strptime(date, azely.DATE_FORMAT)
        params = {'timestamp': time.mktime(dateobj.utctimetuple()), # unix time
                  'location': f'{location["latitude"]}, {location["longitude"]}'}
        result = self._request_api(URL_TIMEZONE, params)
        location['timezone_name'] = result['timeZoneName']
        location['timezone_date'] = date
        location['timezone_hour'] = result['rawOffset'] / 3600
        location['timezone_hour'] += result['dstOffset'] / 3600

        return location

    def _request_api(self, url, params):
        url_with_params = f'{url}?{urlencode(params)}'
        with urlopen(url_with_params, timeout=self.timeout) as f:
            result = json.loads(f.read().decode(self.encoding))
            status = result['status']

        if status == 'OK':
            return result
        else:
            message = result['error_message']
            raise ValueError(message)

    def _load_known_locations(self):
        self.update(azely.read_yaml(azely.KNOWN_LOCS, encoding=self.encoding))

    def _update_known_locations(self):
        azely.write_yaml(azely.KNOWN_LOCS, dict(self), encoding=self.encoding)

    def __repr__(self):
        if self.reload:
            self._load_known_locations()

        return pformat(dict(self))
