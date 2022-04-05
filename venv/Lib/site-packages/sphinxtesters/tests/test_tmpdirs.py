""" Test tmpdirs module """
from __future__ import division, print_function, absolute_import

from os import unlink
from os.path import isfile, isdir

from ..tmpdirs import in_dtemp, dtemporize


def test_in_dtemp():
    # Test working in temporary directory
    with in_dtemp() as tmpdir:
        with open('test.txt', 'wt') as fobj:
            fobj.write('Some text')
    assert not isdir(tmpdir)


def test_dtmeporize():
    # Test decorator to work in temporary directory

    def func1():
        with open('test.txt', 'wt') as fobj:
            fobj.write('Some text')

    @dtemporize
    def func2():
        with open('test.txt', 'wt') as fobj:
            fobj.write('Some text')

    with in_dtemp():
        func1()
        assert isfile('test.txt')
        unlink('test.txt')
        # Next one should be in a temporary directory, not here
        func2()
        assert not isfile('test.txt')
