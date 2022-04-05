import io
import pathlib
import zipfile

from ...errors import Abort
from ...make_get.make_get import can_retrieve, retrive_from_url, uri_is_zipfile
from ...template import root_exclude
from .local import Local


def make_zipobj(source, zip_sub_path):
    content = io.BytesIO(open(source, "rb").read())
    zipobj = zipfile.ZipFile(content)

    if zip_sub_path:
        path = zip_sub_path
    else:
        path = ""

    return pathlib.PurePosixPath(path), zipobj

def _z_is_dir(path):
        """Return True if this archive member is a directory."""
        return path.filename[-1] == '/'

class LocalTargetAndZipSource(Local):
    os_sep = "/"
    os_sep_dbl = "//"

    def __init__(self, zip_source, zip_sub_path):
        self.zip_source = zip_source
        self.zip_sub_path = zip_sub_path

    def exists(self, path):
        path_str = "/".join(path.parts)
        foundfile = path_str in self.zip.namelist()
        if foundfile:
            return foundfile
        founddir = path_str + "/" in self.zip.namelist()
        return founddir

    def read_text(self, source):
        zippath = "/".join(source.parts)
        return self.zip.read(zippath).decode()

    def read_bytes(self, source):
        zippath = "/".join(source.parts)
        return self.zip.read(zippath)

    def copy(self, source, target):
        zippath = "/".join(source.parts)
        self.zip.extract(zippath, str(target))

    def acquire(self):
        # TODO: make sure filesystem is mounted
        if can_retrieve(self.zip_source):
            local_path, sub_path = retrive_from_url(
                self.zip_source, "", self.zip_sub_path
            )
        else:
            local_path = self.zip_source
            sub_path = self.zip_sub_path

        self.root, self.zip = make_zipobj(local_path, sub_path)

    def release(self):
        pass  # TODO:
        # make sure filesystem is unmounted if it was not already
        # mounted

    def ensure_source_root(self):
        source = "/".join(self.root.parts)
        if not source.endswith("/"):
            source += "/"
        if not source in self.zip.namelist() and not source == "/":
            raise Abort("Error: Source %s does not exists" % source)

    def ensure_target_root(self):
        target = "/".join(self.root.parts)
        if not target.endswith("/"):
            target += "/"
        if target in self.zip.namelist():
            raise Abort("Error: Target %s already exists" % self.root)

    def ensure_target(self, target):
        if self.exists(target):
            raise Abort("Error: Target %s already exists" % target)

    def iter_filenames(self, source):
        """
            Walk through all files and yield one of the following:

            * (1, rootdir, dirname, None)
            * (2, rootdir, dirname, filename)

        """
        zipobject = self.zip

        source_str = "/".join(source.parts)
        if source_str == "":
            root_index = 0
        else:
            root_index = len(source_str) + 1

        exclude = []
        # for exc in root_exclude:
        #    exclude.extend(glob.glob(str(source.joinpath(exc))))

        for path in zipobject.filelist:

            full_root = path.filename
            if not full_root.startswith(source_str):
                continue

            root = full_root[root_index:]

            skip = False
            for exc in exclude:
                if full_root.startswith(exc):
                    skip = True

            if skip:
                continue

            if _z_is_dir(path):
                yield 1, root.strip("/"), None
            else:
                parent, _sep, fn = root.rpartition("/")
                yield 2, parent, fn
