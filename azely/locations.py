# coding: utf-8

# imported items
__all__ = ['Locations']

# standard library
import webbrowser
from pprint import pformat
from urllib.error import URLError
from urllib.request import urlopen

# dependent packages
import azely
import yaml

# constants
URL_API = 'https://maps.googleapis.com/maps/api'
URL_GEOCODE = URL_API + '/geocode/json?address={0}'
URL_TIMEZONE = URL_API + '/timezone/json?location={0},{1}&timestamp={2}'
URL_MAPS = 'https://www.google.com/maps?q={0},{1}'


# classes
class Location(dict):
    def __init__(self, dict_like):
        super().__init__(dict_like)

    def googlemaps(self):
        url = URL_MAPS.format(self['latitude'], self['longitude'])
        webbrowser.open(url)


class Locations(dict):
    def __init__(self, date=None, encoding='utf-8', timeout=5):
        with open(azely.KNOWN_LOCS, 'r') as f:
            known_locs = yaml.load(f, yaml.loader.SafeLoader)
            super().__init__(known_locs)

        self.info = {
            'date': azely.parse_date(date),
            'encoding': encoding,
            'timeout': timeout,
        }

    def __getitem__(self, name):
        if name in self:
            item = dict.__getitem__(self, name)
            if 'query' in item:
                try:
                    query = item['query']
                    item = self.request_item(query) # updated
                    dict.__setitem__(self, name, item)
                    self.update_known_locations(name, item)
                except URLError:
                    if not self.info['date'] == item['timezone_date']:
                        print('warning!')
            else:
                print('warning!')
        else:
            try:
                query = azely.parse_location(name)
                item = self.request_item(query) # created
                dict.__setitem__(self, name, item)
                self.update_known_locations(name, item)
            except URLError:
                raise azely.AzelyError('error!')

        return Location(item)

    def request_item(self, query):
        # get geocode from google maps api
        url = URL_GEOCODE.format(query)
        with urlopen(url, timeout=self.info['timeout']) as f:
            string = f.read().decode(self.info['encoding'])
            geocode = yaml.load(string)['results'][0]

        item = {}
        item['name']      = geocode['address_components'][0]['long_name']
        item['address']   = geocode['formatted_address']
        item['latitude']  = geocode['geometry']['location']['lat']
        item['longitude'] = geocode['geometry']['location']['lng']
        item['query']     = query

        # get timezone from google maps api
        t = azely.get_unixtime(self.info['date'])
        url = URL_TIMEZONE.format(item['latitude'], item['longitude'], t)
        with urlopen(url, timeout=self.info['timeout']) as f:
            string = f.read().decode(self.info['encoding'])
            timezone = yaml.load(string)

        item['timezone_name'] = timezone['timeZoneName']
        item['timezone_date'] = self.info['date']
        item['timezone_hour'] = timezone['rawOffset'] / 3600
        item['timezone_hour'] += timezone['dstOffset'] / 3600

        return item

    def update_known_locations(self, name, item):
        with open(azely.KNOWN_LOCS, 'r') as f:
            known_locs = yaml.load(f, yaml.loader.SafeLoader)

        if name in known_locs:
            timezone = {key: item[key] for key in item if 'timezone' in key}
            known_locs[name].update(timezone)
        else:
            known_locs.update({name: item})

        with open(azely.KNOWN_LOCS, 'w') as f:
            f.write(yaml.dump(known_locs, default_flow_style=False))

    def __repr__(self):
        return pformat(dict(self))
