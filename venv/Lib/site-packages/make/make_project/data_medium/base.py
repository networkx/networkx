import os
import pathlib


class DataMediumBase:
    os_sep = os.path.sep
    os_sep_dbl = os.path.sep + os.path.sep

    @classmethod
    def contains_blanks(cls, pth):
        return (cls.os_sep_dbl in pth) or pth.endswith(cls.os_sep)

    @staticmethod
    def get_absolute_as_Path(path_str):
        return pathlib.Path(path_str).absolute()

    @staticmethod
    def is_template_dir(path_str):
        start = path_str.find("{{")
        if start >= 0:
            if path_str.find("}}") > start:
                return True
        return False

    @staticmethod
    def exists(target):
        raise NotImplementedError

    @staticmethod
    def joinpath(path1, *pathN):
        raise NotImplementedError

    @staticmethod
    def mkdir(target):
        raise NotImplementedError

    @staticmethod
    def write_text(target, content):
        raise NotImplementedError

    @staticmethod
    def write_bytes(target, content):
        raise NotImplementedError

    @staticmethod
    def read_text(source):
        raise NotImplementedError

    @staticmethod
    def read_bytes(source):
        raise NotImplementedError

    @staticmethod
    def copy(source, target):
        raise NotImplementedError

    def ensure_source_root(self):
        raise NotImplementedError

    def ensure_target_root(self):
        raise NotImplementedError

    def ensure_target(self, target):
        raise NotImplementedError

    @staticmethod
    def iter_filenames(source):
        raise NotImplementedError

    @staticmethod
    def acquire():
        raise NotImplementedError

    @staticmethod
    def release():
        raise NotImplementedError
