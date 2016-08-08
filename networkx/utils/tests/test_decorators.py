import tempfile
import os

from nose.tools import *

import networkx as nx
from networkx.utils.decorators import open_file,not_implemented_for

def test_not_implemented_decorator():
    @not_implemented_for('directed')
    def test1(G):
        pass
    test1(nx.Graph())

@raises(KeyError)
def test_not_implemented_decorator_key():
    @not_implemented_for('foo')
    def test1(G):
        pass
    test1(nx.Graph())

@raises(nx.NetworkXNotImplemented)
def test_not_implemented_decorator_raise():
    @not_implemented_for('graph')
    def test1(G):
        pass
    test1(nx.Graph())



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
            with tempfile.NamedTemporaryFile('wb+') as fh:
                self.write(fh)
        else:
            self.write(path)

    @open_file(4, 'wb')
    def writer_arg4default(self, x, y, other='hello', path=None, **kwargs):
        if path is None:
            with tempfile.NamedTemporaryFile('wb+') as fh:
                self.write(fh)
        else:
            self.write(path)

    @open_file('path', 'wb')
    def writer_kwarg(self, **kwargs):
        path = kwargs.get('path', None)
        if path is None:
            with tempfile.NamedTemporaryFile('wb+') as fh:
                self.write(fh)
        else:
            self.write(path)

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
        self.fobj.close()
        os.unlink(self.name)
