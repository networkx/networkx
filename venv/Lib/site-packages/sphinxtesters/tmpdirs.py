""" Utilities for running code in temporary directories
"""

from os import getcwd, chdir
from tempfile import mkdtemp
from functools import wraps
from contextlib import contextmanager
from shutil import rmtree


@contextmanager
def in_dtemp():
    """ Change into temporary directory for duration of context
    """
    tmpdir = mkdtemp()
    cwd = getcwd()
    try:
        chdir(tmpdir)
        yield tmpdir
    finally:
        chdir(cwd)
        rmtree(tmpdir)


def dtemporize(func):
    """ Decorate a function to run in a temporary directory """
    @wraps(func)
    def dfunc(*args, **kwargs):
        with in_dtemp():
            return func(*args, **kwargs)
    return dfunc
