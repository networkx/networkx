from .base import DataMediumBase


class DryRun(DataMediumBase):
    @staticmethod
    def mkdir(target):
        print("Create path:", target)

    @staticmethod
    def write_text(target, content):
        print("Create file:", str(target))

    @staticmethod
    def write_bytes(target, content):
        print("Create file:", str(target))

    @staticmethod
    def copy(source, target):
        print("copy from", source, " to ", target)
