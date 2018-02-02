"""Azely Command Line Interface"""

# standard library
import argparse

# dependent packages
import azely
import yaml


# functions
def create_parser(config=None):
    """Create an argument parser based on config."""
    if config is None:
        config = azely.read_yaml(azely.CLI_PARSER)

    # main commands
    main = conf.pop('common')
    desc = main['description']
    prog = main['prog']

    parser = argparse.ArgumentParser(prog=prog, description=desc)
    subparsers = parser.add_subparsers()

    for arg in main['args']:
        flags = arg.pop('flags')
        parser.add_argument(*flags, **arg)

    # subcommands
    for sub in conf.values():
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
    args.func(args)


if __name__ == '__main__':
    main()
