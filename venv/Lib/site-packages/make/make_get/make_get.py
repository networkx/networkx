from pathlib import Path
from urllib import parse, request

from ..errors import Abort

opener = request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
request.install_opener(opener)


def make_get(args):
    """
        Download ``source`` and store it to disk as ``target``
    """
    retrive_from_url(str(args.source), str(args.target), "")


def can_retrieve(uri):
    if isinstance(uri, str):
        uri = parse.urlsplit(uri)
    return not uri.scheme in ("file", "")


def uri_is_zipfile(uri):
    if isinstance(uri, str):
        uri = parse.urlsplit(uri)
    uri, _ = expand_uri(uri, "")
    return uri.path.endswith("zip")


def expand_uri(uri, subpath):
    if uri.scheme == "gh":
        # https://github.com/fholmer/make/archive/master.zip
        path_parts = uri.path.split("/")
        master = "{0[1]}-master".format(path_parts)

        if not subpath:
            subpath = master
            if len(path_parts) > 2:
                subpath = "/".join([subpath] + path_parts[2:])

        uri = parse.SplitResult(
            "https", "github.com", "{}/archive/master.zip".format(uri.path), "", ""
        )

    elif uri.scheme == "gl":
        # https://gitlab.com/fholmer/make/-/archive/master/make-master.zip
        # https://gitlab.com/fholmer/make/-/archive/master/make-master.zip?path=tests%2Fmake%2Fmake_project
        # make-master-tests-make-make_project
        path_parts = uri.path.split("/")
        master = "{0[1]}-master".format(path_parts)
        if subpath:
            qs = parse.urlencode({"path": subpath})
        elif len(path_parts) > 2:
            qs = parse.urlencode({"path": "/".join(path_parts[2:])})
            subpath_root = "-".join([master] + path_parts[2:])
            subpath = "/".join([subpath_root] + path_parts[2:])
        else:
            qs = ""
            subpath = master
        uri = parse.SplitResult(
            "https",
            "gitlab.com",
            "/{0[0]}/{0[1]}/-/archive/master/{1}.zip".format(path_parts, master),
            qs,
            "",
        )
    return uri, subpath


def retrive_from_url(source, target, subpath):
    """
        Download ``source`` and store it to disk as ``target``
    """
    uri = parse.urlsplit(source)

    if not can_retrieve(uri):
        raise Abort("URI not supported: {}".format(source))

    uri, subpath = expand_uri(uri, subpath)
    source = uri.geturl()

    target_path = abs_from_url(uri, target)
    target = str(target_path)

    if target_path.exists():
        names = "\n".join(["1) Use existing", "2) Overwrite", "3) Cancel"])
        question = "target file: {} already exists".format(target_path.name)
        reply = input(
            "{}\nOptions:\n{}\nChoose an option ([1], 2, 3): ".format(question, names)
        )

        if reply == "1" or reply == "":
            return target, subpath
        elif reply == "2":
            pass
        else:
            raise Abort("Aborted by user")

    print("Download: ", source)
    print("Into    : ", target)
    request.urlretrieve(source, target)
    return target, subpath


def abs_from_url(uri, target):
    if isinstance(uri, str):
        uri = parse.urlsplit(uri)
    if target:
        target = Path(target).absolute()
    else:
        target = Path(Path(uri.path).name).absolute()
    return target


def setup(subparsers):
    parser = subparsers.add_parser("get", help="Download source and store as target")
    parser.add_argument("source", type=str, help="source URL")
    parser.add_argument("target", type=str, nargs="?", default="", help="target dir")
    parser.set_defaults(func=make_get)
