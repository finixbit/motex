import sys
import argparse
from pathlib import Path
from importlib.machinery import SourceFileLoader
from motex import __version__, Motex, MotexExtractor, MotexHelpers


def command_load(arguments):
    motex_instance = Motex(arguments.config)
    extractor = MotexExtractor(motex_instance.motex_config, motex_instance.storage)
    extractor.extract(motex_instance.extract_config)


def command_run(arguments):
    motex_instance = Motex(arguments.config)
    helpers = MotexHelpers(motex_instance.storage)

    full_module_name = arguments.script
    if not Path(full_module_name).is_file():
        logger.error("Invalid script path")
        sys.exit(1)

    foo = SourceFileLoader("motex.script", arguments.script).load_module()
    foo.main(helpers)

def main():
    parser = argparse.ArgumentParser()

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version=f"motex version {__version__}")

    subparsers = parser.add_subparsers()
    subparsers.required = True

    load_parser = subparsers.add_parser('load')
    load_parser.add_argument('config', help="Path to toml config file")
    load_parser.set_defaults(func=command_load)

    run_parser = subparsers.add_parser('run')
    run_parser.add_argument('config', help="Path to toml config file")
    run_parser.add_argument('script', help="Path to script file")
    run_parser.set_defaults(func=command_run)

    args = parser.parse_args()
    if not callable(args.func):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    pass
