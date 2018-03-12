"""Azely Command Line Interface.

This script is independent from the Azely package and
intended to be executed as `azely` command in a shell::

    $ azely -o sun -l mitaka -d 2018-01-01

"""

# standard library
import argparse
import logging

# dependent packages
import azely
import yaml


# functions
def create_parser(config=None):
    """Create an argument parser based on config."""
    if config is None:
        config = azely.read_yaml(azely.CLI_PARSER)

    # main commands
    main = config.pop('main')
    desc = main['description']
    prog = main['prog']

    parser = argparse.ArgumentParser(prog=prog, description=desc)
    subparsers = parser.add_subparsers(dest='subcommand')

    for arg in main['args']:
        flags = arg.pop('flags')
        parser.add_argument(*flags, **arg)

    # subcommands
    for sub in config.values():
        name = sub['name']
        help = sub['help']
        desc = sub['description']

        subparser = subparsers.add_parser(name, help=help,
                                          description=desc)
        for arg in sub['args']:
            flags = arg.pop('flags')
            subparser.add_argument(*flags, **arg)

        func = getattr(azely, f'{name}_azel')
        subparser.set_defaults(func=func)

    return parser


def main():
    """Main function."""
    parser = create_parser()
    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)


# main program
if __name__ == '__main__':
    main()
