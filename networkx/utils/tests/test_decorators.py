import tempfile
import os
import random

from nose.tools import *
from nose import SkipTest

import networkx as nx
from networkx.utils.decorators import open_file, not_implemented_for
from networkx.utils.decorators import nodes_or_number, preserve_random_state, \
    py_random_state, np_random_state, random_state
from networkx.utils.misc import PythonRandomInterface

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

    def test_writer_arg0_pathlib(self):
        try:
            import pathlib
            self.writer_arg0(pathlib.Path(self.name))
        except ImportError:
            return

    def test_writer_arg1_str(self):
        self.writer_arg1(self.name)
        assert_equal(self.read(self.name), ''.join(self.text))

    def test_writer_arg1_fobj(self):
        self.writer_arg1(self.fobj)
        assert_false(self.fobj.closed)
        self.fobj.close()
        assert_equal(self.read(self.name), ''.join(self.text))

    def test_writer_arg2default_str(self):
        self.writer_arg2default(0, path=None)
        self.writer_arg2default(0, path=self.name)
        assert_equal(self.read(self.name), ''.join(self.text))

    def test_writer_arg2default_fobj(self):
        self.writer_arg2default(0, path=self.fobj)
        assert_false(self.fobj.closed)
        self.fobj.close()
        assert_equal(self.read(self.name), ''.join(self.text))

    def test_writer_arg2default_fobj_path_none(self):
        self.writer_arg2default(0, path=None)

    def test_writer_arg4default_fobj(self):
        self.writer_arg4default(0, 1, dog='dog', other='other')
        self.writer_arg4default(0, 1, dog='dog', other='other', path=self.name)
        assert_equal(self.read(self.name), ''.join(self.text))

    def test_writer_kwarg_str(self):
        self.writer_kwarg(path=self.name)
        assert_equal(self.read(self.name), ''.join(self.text))

    def test_writer_kwarg_fobj(self):
        self.writer_kwarg(path=self.fobj)
        self.fobj.close()
        assert_equal(self.read(self.name), ''.join(self.text))

    def test_writer_kwarg_path_none(self):
        self.writer_kwarg(path=None)

    def tearDown(self):
        self.fobj.close()
        os.unlink(self.name)


@preserve_random_state
def test_preserve_random_state():
    try:
        import numpy.random
        r = numpy.random.random()
    except ImportError:
        return
    assert(abs(r - 0.61879477158568) < 1e-16)


class TestRandomState(object):
    @classmethod
    def setUp(cls):
        global np
        try:
            import numpy as np
        except ImportError:
            raise SkipTest('NumPy not available.')

    @random_state(1)
    def instantiate_random_state(self, random_state):
        assert_true(isinstance(random_state, np.random.RandomState))
        return random_state.random_sample()

    @np_random_state(1)
    def instantiate_np_random_state(self, random_state):
        assert_true(isinstance(random_state, np.random.RandomState))
        return random_state.random_sample()

    @py_random_state(1)
    def instantiate_py_random_state(self, random_state):
        assert_true(isinstance(random_state, random.Random) or
                    isinstance(random_state, PythonRandomInterface))
        return random_state.random()

    def test_random_state_None(self):
        np.random.seed(42)
        rv = np.random.random_sample()
        np.random.seed(42)
        assert_equal(rv, self.instantiate_random_state(None))
        np.random.seed(42)
        assert_equal(rv, self.instantiate_np_random_state(None))

        random.seed(42)
        rv = random.random()
        random.seed(42)
        assert_equal(rv, self.instantiate_py_random_state(None))

    def test_random_state_np_random(self):
        np.random.seed(42)
        rv = np.random.random_sample()
        np.random.seed(42)
        assert_equal(rv, self.instantiate_random_state(np.random))
        np.random.seed(42)
        assert_equal(rv, self.instantiate_np_random_state(np.random))
        np.random.seed(42)
        assert_equal(rv, self.instantiate_py_random_state(np.random))

    def test_random_state_int(self):
        np.random.seed(42)
        np_rv = np.random.random_sample()
        random.seed(42)
        py_rv = random.random()

        np.random.seed(42)
        seed = 1
        rval = self.instantiate_random_state(seed)
        rval_expected = np.random.RandomState(seed).rand()
        assert_true(rval, rval_expected)

        rval = self.instantiate_np_random_state(seed)
        rval_expected = np.random.RandomState(seed).rand()
        assert_true(rval, rval_expected)
        # test that global seed wasn't changed in function
        assert_equal(np_rv, np.random.random_sample())

        random.seed(42)
        rval = self.instantiate_py_random_state(seed)
        rval_expected = random.Random(seed).random()
        assert_true(rval, rval_expected)
        # test that global seed wasn't changed in function
        assert_equal(py_rv, random.random())

    def test_random_state_np_random_RandomState(self):
        np.random.seed(42)
        np_rv = np.random.random_sample()

        np.random.seed(42)
        seed = 1
        rng = np.random.RandomState(seed)
        rval = self.instantiate_random_state(rng)
        rval_expected = np.random.RandomState(seed).rand()
        assert_true(rval, rval_expected)

        rval = self.instantiate_np_random_state(seed)
        rval_expected = np.random.RandomState(seed).rand()
        assert_true(rval, rval_expected)

        rval = self.instantiate_py_random_state(seed)
        rval_expected = np.random.RandomState(seed).rand()
        assert_true(rval, rval_expected)
        # test that global seed wasn't changed in function
        assert_equal(np_rv, np.random.random_sample())

    def test_random_state_py_random(self):
        seed = 1
        rng = random.Random(seed)
        rv = self.instantiate_py_random_state(rng)
        assert_true(rv, random.Random(seed).random())

        assert_raises(ValueError, self.instantiate_random_state, rng)
        assert_raises(ValueError, self.instantiate_np_random_state, rng)


@raises(nx.NetworkXError)
def test_random_state_string_arg_index():
    @random_state('a')
    def make_random_state(rs):
        pass
    rstate = make_random_state(1)


@raises(nx.NetworkXError)
def test_py_random_state_string_arg_index():
    @py_random_state('a')
    def make_random_state(rs):
        pass
    rstate = make_random_state(1)


@raises(nx.NetworkXError)
def test_random_state_invalid_arg_index():
    @random_state(2)
    def make_random_state(rs):
        pass
    rstate = make_random_state(1)


@raises(nx.NetworkXError)
def test_py_random_state_invalid_arg_index():
    @py_random_state(2)
    def make_random_state(rs):
        pass
    rstate = make_random_state(1)
