# coding: utf-8

# imported items
__all__ = [
    'AzelyError',
    'AzelyWarning',


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


