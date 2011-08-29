import tempfile
import os

from nose.tools import *

import networkx as nx
from networkx.utils.decorators import open_file,require

def test_require_decorator1():
    @require('os','sys')
    def test1():
        import os
        import sys
    test1()

def test_require_decorator2():
    @require('blahhh')
    def test2():
        import blahhh
    assert_raises(nx.NetworkXError, test2)

class TestOpenFileDecorator(object):
    def setUp(self):
        self.text = ['Blah... ', 'BLAH ', 'BLAH!!!!']
        self.fobj = tempfile.NamedTemporaryFile('wb+', delete=False)
        self.name = self.fobj.name

    def write(self, path):
        for text in self.text:
            path.write(text.encode('ascii'))

    @open_file(1, 'r')
    def read(self, path):
        return path.readlines()[0]

    @staticmethod
    @open_file(0, 'wb')
    def writer_arg0(path):
        path.write('demo'.encode('ascii'))

    @open_file(1, 'wb+')
    def writer_arg1(self, path):
        self.write(path)

    @open_file(2, 'wb')
    def writer_arg2default(self, x, path=None):
        if path is None:
            fh = tempfile.NamedTemporaryFile('wb+', delete=False)
            close_fh = True
        else:
            fh = path
            close_fh = False

        try:
            self.write(fh)
        finally:
            if close_fh:
                fh.close()

    @open_file(4, 'wb')
    def writer_arg4default(self, x, y, other='hello', path=None, **kwargs):
        if path is None:
            fh = tempfile.NamedTemporaryFile('wb+', delete=False)
            close_fh = True
        else:
            fh = path
            close_fh = False

        try:
            self.write(fh)
        finally:
            if close_fh:
                fh.close()

    @open_file('path', 'wb')
    def writer_kwarg(self, **kwargs):
        path = kwargs.get('path', None)
        if path is None:
            fh = tempfile.NamedTemporaryFile('wb+', delete=False)
            close_fh = True
        else:
            fh = path
            close_fh = False

        try:
            self.write(fh)
        finally:
            if close_fh:
                fh.close()

    def test_writer_arg0_str(self):
        self.writer_arg0(self.name)

    def test_writer_arg0_fobj(self):
        self.writer_arg0(self.fobj)

    def test_writer_arg1_str(self):
        self.writer_arg1(self.name)
        assert_equal( self.read(self.name), ''.join(self.text) )

    def test_writer_arg1_fobj(self):
        self.writer_arg1(self.fobj)
        assert_false(self.fobj.closed)
        self.fobj.close()
        assert_equal( self.read(self.name), ''.join(self.text) )

    def test_writer_arg2default_str(self):
        self.writer_arg2default(0, path=None)
        self.writer_arg2default(0, path=self.name)
        assert_equal( self.read(self.name), ''.join(self.text) )

    def test_writer_arg2default_fobj(self):
        self.writer_arg2default(0, path=self.fobj)
        assert_false(self.fobj.closed)
        self.fobj.close()
        assert_equal( self.read(self.name), ''.join(self.text) )

    def test_writer_arg2default_fobj(self):
        self.writer_arg2default(0, path=None)

    def test_writer_arg4default_fobj(self):
        self.writer_arg4default(0, 1, dog='dog', other='other2')
        self.writer_arg4default(0, 1, dog='dog', other='other2', path=self.name)
        assert_equal( self.read(self.name), ''.join(self.text) )

    def test_writer_kwarg_str(self):
        self.writer_kwarg(path=self.name)
        assert_equal( self.read(self.name), ''.join(self.text) )

    def test_writer_kwarg_fobj(self):
        self.writer_kwarg(path=self.fobj)
        self.fobj.close()
        assert_equal( self.read(self.name), ''.join(self.text) )

    def test_writer_kwarg_fobj(self):
        self.writer_kwarg(path=None)

    def tearDown(self):
        os.remove(self.name)

