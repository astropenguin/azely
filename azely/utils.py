# coding: utf-8

# imported items
__all__ = [
    'AzelyError',
    'AzelyWarning',
    'get_unixtime',

# standard library
import time
from datetime import datetime


# classes
class AzelyError(Exception):
    """Error class of Azely."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class AzelyWarning(Warning):
    """Warning class of Azely."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


# functions
def get_unixtime(date_like=None):
    date = datetime.strptime(parse_date(date_like), DATE_FORMAT)
    return time.mktime(date.utctimetuple())


