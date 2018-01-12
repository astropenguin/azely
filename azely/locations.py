# coding: utf-8

# public items
__all__ = [
    'Locations'
]

# standard library
from pprint import pformat
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

# dependent packages
import azely
import yaml

# local constants
URL_API = 'https://maps.googleapis.com/maps/api'
URL_GEOCODE  = f'{URL_API}/geocode/json'
URL_TIMEZONE = f'{URL_API}/timezone/json'


# classes
class Locations(dict):
    def __init__(self, date=None, encoding='utf-8', timeout=5):
        with azely.KNOWN_LOCS.open() as f:
            known_locs = yaml.load(f, yaml.loader.SafeLoader)
            super().__init__(known_locs)

        self.params = {
            'date': azely.parse_date(date),
            'encoding': encoding,
            'timeout': timeout,
        }

    def __getitem__(self, name):
        self._update_item(name)
        self._update_known_locations()
        return super().__getitem__(name)

    def _update_item(self, name):
        if name in self:
            # update only information of timezone on given date
            try:
                query = super().__getitem__(name)['query']
                item = self._request_item(query)
                tz_info = {key: item[key] for key in item if 'timezone' in key}
                super().__getitem__(name).update(tz_info)
            except KeyError:
                # manually defined location
                pass
            except URLError:
                # no internet connection
                print('URLError!')
            except ValueError:
                # result with some error
                print('ValueError!')
        else:
            # request whole information of location on given date
            query = azely.parse_location(name)
            item = self._request_item(query)
            super().__setitem__(name, item)

    def _update_known_locations(self):
        with azely.KNOWN_LOCS.open('w') as f:
            f.write(yaml.dump(dict(self), default_flow_style=False))

    def _request_item(self, query):
        item = {}

        # get geocode from google maps api
        params = {'address': query}
        result = self._request_api(URL_GEOCODE, params)['results'][0]
        item['name']      = result['address_components'][0]['long_name']
        item['address']   = result['formatted_address']
        item['latitude']  = result['geometry']['location']['lat']
        item['longitude'] = result['geometry']['location']['lng']
        item['query']     = query

        # get timezone from google maps api
        params = {
            'location': f'{item["latitude"]}, {item["longitude"]}',
            'timestamp': azely.get_unixtime(self.date)
        }
        result = self._request_api(URL_TIMEZONE, params)
        item['timezone_name'] = result['timeZoneName']
        item['timezone_date'] = self.date
        item['timezone_hour'] = result['rawOffset'] / 3600
        item['timezone_hour'] += result['dstOffset'] / 3600

        return item

    def _request_api(self, url, query):
        with urlopen(f'{url}?{urlencode(query)}', timeout=self.timeout) as f:
            result = yaml.load(f.read().decode(self.encoding))
            status = result['status']

        if status == 'OK':
            return result
        else:
            raise ValueError

    def __getattr__(self, name):
        return self.params[name]

    def __repr__(self):
        return pformat(dict(self))
