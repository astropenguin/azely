__all__ = ['Observer']


# standard library
from logging import getLogger
logger = getLogger(__name__)

# dependent packages
import azely


class Observer:
    def __init__(self, query=None, date=None, **kwargs):
        self.date = azely.parse_date(date)
        self.location = azely.get_location(query, date, **kwargs)

    def observe(self, query, **kwargs):
        obj = azely.get_object(query, **kwargs)
        return azely.AzEl.from_observer(obj, self.location, self.date)

    def __repr__(self):
        name = self.location['name']
        date = self.date.strftime('%Y-%m-%d')
        return f'Observer({name} / {date})'
