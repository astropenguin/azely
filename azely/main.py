# coding: utf-8

"""Azely: plot azimuth and elevation of astronomical objects.

Usage:
    azely show [-d <keyword>] [-l <keyword>] [-o <keyword>] [-t <keyword>]
    azely save [-d <keyword>] [-l <keyword>] [-o <keyword>] [-t <keyword>] [-e <keyword>]
    azely (-h | --help)
    azely (-v | --version)

Options:
    -h --help                 Show the help and exit.
    -v --version              Show the version and exit.
    -d --date <keyword>       Keyword of date [default: {date}].
    -l --location <keyword>   Keyword of location [default: {location}].
    -o --objects <keyword>    Keyword of objects [default: {objects}].
    -t --timezone <keyword>   Keyword of timezone [default: {timezone}].
    -e --extension <keyword>  Keyword of file extension [default: {extension}].

Details:
    Lorem ipsum dolor sit amet, consectetur adipisicing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

"""

# dependent packages
import azely
from docopt import docopt

# local constants
DEFAULTS = {
    'date': azely.parse_date(),
    'location': 'Mitaka',
    'objects': 'Solar',
    'timezone': '',
    'extension': 'pdf',
}


# functions
def main():
    args = docopt(__doc__.format(**DEFAULTS), version=azely.__version__)
    kwargs = {k.lstrip('-'): v for k, v in args.items()}

    if kwargs['show'] or kwargs['save']:
        azely.plot_azel(**kwargs)


# main
if __name__ == '__main__':
    main()
