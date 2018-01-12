# coding: utf-8

# public items
__all__ = [
    'Locations'
]

# standard library
from pprint import pformat
from urllib.error import URLError
from urllib.request import urlopen

# dependent packages
import azely
import yaml

# local constants
URL_API = 'https://maps.googleapis.com/maps/api'
URL_GEOCODE   = URL_API + '/geocode/json?address={0}'
URL_ELEVATION = URL_API + '/elevation/json?locations={0},{1}'
URL_TIMEZONE  = URL_API + '/timezone/json?location={0},{1}&timestamp={2}'


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

    def _update_known_locations(self):
        with azely.KNOWN_LOCS.open('w') as f:
            f.write(yaml.dump(dict(self), default_flow_style=False))

    def _update_item(self, name):
        if name in self:
            try:
                query = super().__getitem__(name)['query']
                item = self._request_item(query) # updated
                timezone = {key: item[key] for key in item if 'timezone' in key}
                super().__getitem__(name).update(timezone)
            except KeyError:
                print('warning!')
            except URLError:
                print('warning!')
        else:
            try:
                query = azely.parse_location(name)
                item = self._request_item(query) # created
                super().__setitem__(name, item)
            except URLError:
                raise ConnectionError('error!')

    def _request_item(self, query):
        # get geocode from google maps api
        url = URL_GEOCODE.format(query)
        with urlopen(url, timeout=self.timeout) as f:
            string = f.read().decode(self.encoding)
            result = yaml.load(string)['results'][0]

        item = {}
        item['name']      = result['address_components'][0]['long_name']
        item['address']   = result['formatted_address']
        item['latitude']  = result['geometry']['location']['lat']
        item['longitude'] = result['geometry']['location']['lng']
        item['query']     = query

        # get elevation from google maps api
        url = URL_ELEVATION.format(item['latitude'], item['longitude'])
        with urlopen(url, timeout=self.timeout) as f:
            string = f.read().decode(self.encoding)
            result = yaml.load(string)['results'][0]

        item['elevation'] = result['elevation']

        # get timezone from google maps api
        ut = azely.get_unixtime(self.date)
        url = URL_TIMEZONE.format(item['latitude'], item['longitude'], ut)
        with urlopen(url, timeout=self.timeout) as f:
            string = f.read().decode(self.encoding)
            result = yaml.load(string)

        item['timezone_name'] = result['timeZoneName']
        item['timezone_date'] = self.date
        item['timezone_hour'] = result['rawOffset'] / 3600
        item['timezone_hour'] += result['dstOffset'] / 3600

        return item

    def __getitem__(self, name):
        self._update_item(name)
        self._update_known_locations()
        return super().__getitem__(name)

    def __getattr__(self, name):
        return self.params[name]

    def __repr__(self):
        return pformat(dict(self))
