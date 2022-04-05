import os
import pathlib
from functools import partial

from ..errors import Abort, Invalid, ParserNotFound
from ..template import Template, binary_suffixes
from .data_medium import dry_run, local, zipsource
from .parsers import cookiecutter_parser, ini_parser, json_parser


def setup(subparsers):
    parser = subparsers.add_parser("project", help="Create project from template")
    parser.add_argument("source", type=str, help="source dir")
    parser.add_argument("target", type=str, nargs="?", default=".", help="target dir")
    parser.add_argument("--dry-run", action="store_true", help="test run")
    parser.add_argument("-z", "--zip", action="store_true", help="source is a zip file")
    parser.add_argument(
        "-p", "--sub-path", type=str, default="", help="a sub path within a source"
    )
    # entrypoint for this subparser
    parser.set_defaults(func=make_project)


Parsers = {
    "ini_parser": ini_parser.get_vars,
    "json_parser": json_parser.get_vars,
    "cookiecutter_parser": cookiecutter_parser.get_vars,
}

Medium = {
    "local": local.Local,
    "dry_run": dry_run.DryRun,
    "zip": zipsource.LocalTargetAndZipSource,
}


def _render(kwargs, string):
    """
        Simple helperfunction to render a template.
        Plays nice with partial:

        .. code-block:: python

            render = partial(_render, variables)
            full_content = render(full_content)
    """
    return Template(string).render(kwargs)


def make_project(args):
    """
        * Fetches the source and target path.
        * Parses ``project.conf``
        * copy and transform files in source to target.
    """

    source_medium = get_source_medium(args)
    target_medium = get_target_medium(args)

    target_medium.acquire()
    target_medium.ensure_target_root()

    source_medium.acquire()
    source_medium.ensure_source_root()

    # run parser
    for parser in Parsers.values():
        try:
            variables = parser(source_medium=source_medium, dry_run=args.dry_run)
            if not variables is None:
                break
        except ParserNotFound:
            pass
    else:
        raise Abort("cannot parse source directory: {}".format(source_medium.root))

    create_files(source_medium, target_medium, variables)

    source_medium.release()
    target_medium.release()


def get_source_medium(args):
    is_zip = args.zip or zipsource.uri_is_zipfile(args.source)
    if is_zip:
        medium_class = Medium["zip"]
    else:
        medium_class = Medium["local"]

    if args.dry_run:

        class _dryrun(Medium["dry_run"], medium_class):
            pass  # override

        medium_class = _dryrun

    # To the user the source can be a path in local filesystem or the name
    # of a zipfile.
    # But to us the source is always a path, it is never a name of a file.
    # the source is a path in the local filesystem or a path inside a zipfile.
    # so we do this translation right here.

    if is_zip:
        medium = medium_class(args.source, args.sub_path)
    else:
        medium = medium_class(args.source)
    return medium


def get_target_medium(args):
    medium_class = Medium["local"]
    if args.dry_run:

        class _dryrun(Medium["dry_run"], medium_class):
            pass  # override

        medium_class = _dryrun
    return medium_class(args.target)


def create_files(source_medium, target_medium, variables):
    render = partial(_render, variables)
    source = source_medium.root
    target = target_medium.root
    for action, root, fn in source_medium.iter_filenames(source):
        is_tpl_dir = source_medium.is_template_dir(root)
        if action == 1:
            _root = render(root)
            if is_tpl_dir and _root and not target_medium.contains_blanks(_root):
                target_path = target_medium.joinpath(target, _root)
                target_medium.ensure_target(target_path)
                target_medium.mkdir(target_path)
        elif action == 2:
            _root = render(root)
            _fn = render(fn)
            # files in the root folder is ignored and files or folders with blank
            # name is also ignored
            if (
                is_tpl_dir
                and _fn
                and _root
                and not target_medium.contains_blanks(_root)
            ):
                source_path = source_medium.joinpath(source, root, fn)
                target_path = target_medium.joinpath(target, _root, _fn)
                target_medium.ensure_target(target_path)

                try:
                    if not source_path.suffix.lower() in binary_suffixes:
                        full_content = source_medium.read_text(source_path)
                        full_content = render(full_content)
                        target_medium.write_text(target_path, full_content)
                    else:
                        # medium.copy(source_path, target_path)
                        full_content = source_medium.read_bytes(source_path)
                        target_medium.write_bytes(target_path, full_content)

                except UnicodeDecodeError as err:
                    print(
                        "WARNING: {} can not be rendered with Jinja2. UnicodeDecodeError: {}".format(
                            source_path.name, str(err)
                        )
                    )
                    # medium.copy(source_path, target_path)
                    full_content = source_medium.read_bytes(source_path)
                    target_medium.write_bytes(target_path, full_content)
