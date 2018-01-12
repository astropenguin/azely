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
import yaml

# module constants
URL_API = 'https://maps.googleapis.com/maps/api'
URL_GEOCODE  = f'{URL_API}/geocode/json'
URL_TIMEZONE = f'{URL_API}/timezone/json'


# classes
class Locations(dict):
    def __init__(self, date=None, encoding='utf-8', timeout=5):
        with azely.KNOWN_LOCS.open() as f:
            known_locs = yaml.load(f, yaml.loader.SafeLoader)
            super().__init__(known_locs)

        date = azely.parse_date(date)
        self.params = {'date': date,
                       'encoding': encoding,
                       'timeout': timeout}

    def __getitem__(self, name_like):
        self._update_location(name_like)
        self._update_known_locations()
        return super().__getitem__(name_like)

    def _update_location(self, name_like):
        if name_like in self:
            # update only information of timezone on given date
            try:
                query = super().__getitem__(name_like)['query']
                location = self._request_location(query)
                tz_info = {k:v for k,v in location.items() if 'timezone' in k}
                super().__getitem__(name_like).update(tz_info)
            except KeyError:
                # manually defined location
                # not necessary to be updated
                pass
            except URLError:
                # no internet connection
                print('URLError!')
            except ValueError:
                # result with some error
                print('ValueError!')
        else:
            # request whole information of location on given date
            query = self._parse_location_name(name_like)
            location = self._request_location(query)
            super().__setitem__(name_like, location)

    def _update_known_locations(self):
        with azely.KNOWN_LOCS.open('w') as f:
            f.write(yaml.dump(dict(self), default_flow_style=False))

    def _request_location(self, query):
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
        params = {'location': f'{location["latitude"]}, {location["longitude"]}',
                 'timestamp': self._get_unixtime()}
        result = self._request_api(URL_TIMEZONE, params)
        location['timezone_name'] = result['timeZoneName']
        location['timezone_date'] = self.date
        location['timezone_hour'] = result['rawOffset'] / 3600
        location['timezone_hour'] += result['dstOffset'] / 3600

        return location

    def _request_api(self, url, params):
        with urlopen(f'{url}?{urlencode(params)}', timeout=self.timeout) as f:
            result = yaml.load(f.read().decode(self.encoding))
            status = result['status']

        if status == 'OK':
            return result
        else:
            message = result['error_message']
            raise ValueError(message)

    def _get_unixtime(self):
        date = datetime.strptime(self.date, azely.DATE_FORMAT)
        return time.mktime(date.utctimetuple())

    def _parse_location_name(self, name_like):
        if isinstance(name_like, (list, tuple)):
            return SEP.join(name_like)
        elif isinstance(name_like, str):
            pattern = f'[{azely.SEPARATORS}]+'
            return re.sub(pattern, '+', name_like)
        else:
            raise ValueError(name_like)

    def __getattr__(self, name):
        return self.params[name]

    def __repr__(self):
        return pformat(dict(self))
