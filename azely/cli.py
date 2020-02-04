# standard library
from argparse import ArgumentParser
from pathlib import Path


# azely modules
import azely
import azely.plot as plot
import azely.utils as utils


def create_parser():
    """Create an argument parser."""
    # read toml
    path = Path(azely.__path__[0]) / "data" / "cli.toml"
    config = utils.read_toml(path)

    main = config["main"]
    cmds = config["cmds"]

    # main commands
    args = main.pop("args", [])
    parser = ArgumentParser(**main)

    for arg in args:
        if "name" in arg:
            parser.add_argument(arg.pop("name"), **arg)
        elif "flags" in arg:
            parser.add_argument(*arg.pop("flags"), **arg)

    # subcommands
    subparsers = parser.add_subparsers(dest="cmds")

    for cmd in cmds.values():
        args = cmd.pop("args", [])
        subparser = subparsers.add_parser(**cmd)

        for arg in args:
            if "name" in arg:
                subparser.add_argument(arg.pop("name"), **arg)
            elif "flags" in arg:
                subparser.add_argument(*arg.pop("flags"), **arg)

    return parser


def main():
    """Main function."""
    parser = create_parser()
    args = vars(parser.parse_args())
    cmd = args.pop("cmds")

    if cmd is not None:
        getattr(plot, cmd)(**args)
    else:
        parser.print_help()


# main program
if __name__ == "__main__":
    main()
