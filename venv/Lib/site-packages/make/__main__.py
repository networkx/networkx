from argparse import ArgumentParser

from .errors import Abort, Invalid
from .make_get import make_get
from .make_project import make_project

SetupFunctions = [make_project.setup, make_get.setup]


def main():
    """
        Main entrypoint.

        .. code-block:: console

            usage: python -m make [-h] [--dry-run] conf_type source [target]

            positional arguments:
            conf_type   configuration type
            source      source dir
            target      target dir

            optional arguments:
            -h, --help  show this help message and exit
            --dry-run   test run
    """

    global_parser = ArgumentParser(add_help=True)
    global_parser.set_defaults(func=None)
    subparsers = global_parser.add_subparsers(
        title="Commands", description="Additional help for commands: {command} --help"
    )

    for setup in SetupFunctions:
        setup(subparsers)

    args = global_parser.parse_args()

    if args.func:
        try:
            args.func(args=args)
        except Invalid as error:
            print("{}".format(error))
        except Abort as error:
            print("{}".format(error))
            global_parser.print_usage()
        except KeyboardInterrupt:
            print("Aborted by user")
    else:
        global_parser.print_help()


if __name__ == "__main__":
    main()
