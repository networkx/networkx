import os
import pathlib
import random
import tempfile
from contextlib import nullcontext as does_not_raise

import pytest

import networkx as nx
from networkx.utils.decorators import (
    argmap,
    not_implemented_for,
    np_random_state,
    open_file,
    py_random_state,
)
from networkx.utils.misc import PythonRandomInterface, PythonRandomViaNumpyBits


@pytest.mark.parametrize(
    "G,types,expectation",
    [
        (nx.Graph(), ("directed",), does_not_raise()),
        (nx.Graph(), ("undirected",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.Graph(), ("graph",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.Graph(), ("multigraph",), does_not_raise()),
        (nx.Graph(), ("directed", "graph"), does_not_raise()),
        (nx.Graph(), ("directed", "multigraph"), does_not_raise()),
        (nx.Graph(), ("undirected", "graph"), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.Graph(), ("undirected", "multigraph"), does_not_raise()),
        (nx.DiGraph(), ("directed",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.DiGraph(), ("undirected",), does_not_raise()),
        (nx.DiGraph(), ("graph",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.DiGraph(), ("multigraph",), does_not_raise()),
        (nx.DiGraph(), ("directed", "graph"), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.DiGraph(), ("directed", "multigraph"), does_not_raise()),
        (nx.DiGraph(), ("undirected", "graph"), does_not_raise()),
        (nx.DiGraph(), ("undirected", "multigraph"), does_not_raise()),
        (nx.MultiGraph(), ("directed",), does_not_raise()),
        (nx.MultiGraph(), ("undirected",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.MultiGraph(), ("graph",), does_not_raise()),
        (nx.MultiGraph(), ("multigraph",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.MultiGraph(), ("directed", "graph"), does_not_raise()),
        (nx.MultiGraph(), ("directed", "multigraph"), does_not_raise()),
        (nx.MultiGraph(), ("undirected", "graph"), does_not_raise()),
        (
            nx.MultiGraph(),
            ("undirected", "multigraph"),
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (nx.MultiDiGraph(), ("directed",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.MultiDiGraph(), ("undirected",), does_not_raise()),
        (nx.MultiDiGraph(), ("graph",), does_not_raise()),
        (nx.MultiDiGraph(), ("multigraph",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.MultiDiGraph(), ("directed", "graph"), does_not_raise()),
        (
            nx.MultiDiGraph(),
            ("directed", "multigraph"),
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (nx.MultiDiGraph(), ("undirected", "graph"), does_not_raise()),
        (nx.MultiDiGraph(), ("undirected", "multigraph"), does_not_raise()),
    ],
)
def test_not_implemented_decorator_one_line(G, types, expectation):
    with expectation:

        @not_implemented_for(*types)
        def test(G):
            pass

        test(G)


@pytest.mark.parametrize(
    "G,type1,type2,expectation",
    [
        (nx.Graph(), "directed", "graph", pytest.raises(nx.NetworkXNotImplemented)),
        (nx.Graph(), "directed", "multigraph", does_not_raise()),
        (nx.Graph(), "undirected", "graph", pytest.raises(nx.NetworkXNotImplemented)),
        (
            nx.Graph(),
            "undirected",
            "multigraph",
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (nx.DiGraph(), "directed", "graph", pytest.raises(nx.NetworkXNotImplemented)),
        (
            nx.DiGraph(),
            "directed",
            "multigraph",
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (nx.DiGraph(), "undirected", "graph", pytest.raises(nx.NetworkXNotImplemented)),
        (nx.DiGraph(), "undirected", "multigraph", does_not_raise()),
        (nx.MultiGraph(), "directed", "graph", does_not_raise()),
        (
            nx.MultiGraph(),
            "directed",
            "multigraph",
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (
            nx.MultiGraph(),
            "undirected",
            "graph",
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (
            nx.MultiGraph(),
            "undirected",
            "multigraph",
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (
            nx.MultiDiGraph(),
            "directed",
            "graph",
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (
            nx.MultiDiGraph(),
            "directed",
            "multigraph",
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (nx.MultiDiGraph(), "undirected", "graph", does_not_raise()),
        (
            nx.MultiDiGraph(),
            "undirected",
            "multigraph",
            pytest.raises(nx.NetworkXNotImplemented),
        ),
    ],
)
def test_not_implemented_decorator_two_lines(G, type1, type2, expectation):
    with expectation:

        @not_implemented_for(type1)
        @not_implemented_for(type2)
        def test(G):
            pass

        test(G)


@pytest.mark.parametrize(
    "types",
    [
        ("directed", "undirected"),
        ("graph", "multigraph"),
        ("directed", "undirected", "graph"),
        ("directed", "undirected", "multigraph"),
        ("directed", "graph", "multigraph"),
        ("undirected", "graph", "multigraph"),
        ("directed", "undirected", "graph", "multigraph"),
    ],
)
def test_not_implemented_decorator_no_graph_left(types):
    with pytest.raises(ValueError):
        not_implemented_for(*types)


def test_not_implemented_decorator_key():
    with pytest.raises(KeyError):

        @not_implemented_for("foo")
        def test1(G):
            pass

        test1(nx.Graph())


@pytest.mark.parametrize(
    "G,types,args,expectation",
    [
        (nx.Graph(), ("directed",), ("G",), does_not_raise()),
        (nx.Graph(), ("undirected",), ("G",), pytest.raises(nx.NetworkXNotImplemented)),
        (nx.Graph(), ("directed",), ("H",), pytest.raises(nx.NetworkXError)),
        (nx.Graph(), ("undirected",), ("H",), pytest.raises(nx.NetworkXError)),
        (nx.Graph(), ("multigraph",), (0,), does_not_raise()),
        (nx.Graph(), ("multigraph",), (1,), pytest.raises(nx.NetworkXError)),
    ],
)
def test_not_implemented_decorator_one_arg(G, types, args, expectation):
    with expectation:

        @not_implemented_for(*types, args=args)
        def test(G):
            pass

        test(G)


@pytest.mark.parametrize(
    "G,H,types,args,expectation",
    [
        (nx.Graph(), nx.DiGraph(), ("directed",), ("G",), does_not_raise()),
        (
            nx.Graph(),
            nx.DiGraph(),
            ("directed",),
            ("H",),
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (nx.Graph(), nx.Graph(), ("directed",), ("G", "H"), does_not_raise()),
        (
            nx.Graph(),
            nx.DiGraph(),
            ("directed",),
            ("G", "H"),
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (
            nx.Graph(),
            nx.DiGraph(),
            ("directed",),
            (1,),
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (nx.Graph(), nx.Graph(), ("directed",), (0, 1), does_not_raise()),
        (
            nx.Graph(),
            nx.DiGraph(),
            ("directed",),
            (0, 1),
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (
            nx.DiGraph(),
            nx.DiGraph(),
            ("directed",),
            (0, 1),
            pytest.raises(nx.NetworkXNotImplemented),
        ),
        (
            nx.Graph(),
            nx.DiGraph(),
            ("directed",),
            (0, 1, 2),
            pytest.raises(nx.NetworkXError),
        ),
        (
            nx.Graph(),
            nx.DiGraph(),
            ("directed",),
            (0, "H"),
            pytest.raises(nx.NetworkXNotImplemented),
        ),
    ],
)
def test_not_implemented_decorator_two_args(G, H, types, args, expectation):
    with expectation:

        @not_implemented_for(*types, args=args)
        def test(G, H):
            pass

        test(G, H)


def test_not_implemented_decorator_args_two_lines():
    with does_not_raise():

        @not_implemented_for("directed", args=("G",))
        @not_implemented_for("multigraph", args=("G",))
        def test(G, H):
            pass

        test(nx.Graph(), nx.DiGraph())

    with pytest.raises(nx.NetworkXNotImplemented):

        @not_implemented_for("directed", args=("G"))
        @not_implemented_for("multigraph", args=("G", "H"))
        def test(G, H):
            pass

        test(nx.Graph(), nx.MultiGraph())

    with pytest.raises(nx.NetworkXNotImplemented):

        @not_implemented_for("directed", args=("G", "H"))
        @not_implemented_for("multigraph", args=("G"))
        def test(G, H):
            pass

        test(nx.Graph(), nx.DiGraph())


class TestOpenFileDecorator:
    def setup_method(self):
        self.text = ["Blah... ", "BLAH ", "BLAH!!!!"]
        self.fobj = tempfile.NamedTemporaryFile("wb+", delete=False)
        self.name = self.fobj.name

    def teardown_method(self):
        self.fobj.close()
        os.unlink(self.name)

    def write(self, path):
        for text in self.text:
            path.write(text.encode("ascii"))

    @open_file(1, "r")
    def read(self, path):
        return path.readlines()[0]

    @staticmethod
    @open_file(0, "wb")
    def writer_arg0(path):
        path.write(b"demo")

    @open_file(1, "wb+")
    def writer_arg1(self, path):
        self.write(path)

    @open_file(2, "wb")
    def writer_arg2default(self, x, path=None):
        if path is None:
            with tempfile.NamedTemporaryFile("wb+") as fh:
                self.write(fh)
        else:
            self.write(path)

    @open_file(4, "wb")
    def writer_arg4default(self, x, y, other="hello", path=None, **kwargs):
        if path is None:
            with tempfile.NamedTemporaryFile("wb+") as fh:
                self.write(fh)
        else:
            self.write(path)

    @open_file("path", "wb")
    def writer_kwarg(self, **kwargs):
        path = kwargs.get("path", None)
        if path is None:
            with tempfile.NamedTemporaryFile("wb+") as fh:
                self.write(fh)
        else:
            self.write(path)

    def test_writer_arg0_str(self):
        self.writer_arg0(self.name)

    def test_writer_arg0_fobj(self):
        self.writer_arg0(self.fobj)

    def test_writer_arg0_pathlib(self):
        self.writer_arg0(pathlib.Path(self.name))

    def test_writer_arg1_str(self):
        self.writer_arg1(self.name)
        assert self.read(self.name) == "".join(self.text)

    def test_writer_arg1_fobj(self):
        self.writer_arg1(self.fobj)
        assert not self.fobj.closed
        self.fobj.close()
        assert self.read(self.name) == "".join(self.text)

    def test_writer_arg2default_str(self):
        self.writer_arg2default(0, path=None)
        self.writer_arg2default(0, path=self.name)
        assert self.read(self.name) == "".join(self.text)

    def test_writer_arg2default_fobj(self):
        self.writer_arg2default(0, path=self.fobj)
        assert not self.fobj.closed
        self.fobj.close()
        assert self.read(self.name) == "".join(self.text)

    def test_writer_arg2default_fobj_path_none(self):
        self.writer_arg2default(0, path=None)

    def test_writer_arg4default_fobj(self):
        self.writer_arg4default(0, 1, dog="dog", other="other")
        self.writer_arg4default(0, 1, dog="dog", other="other", path=self.name)
        assert self.read(self.name) == "".join(self.text)

    def test_writer_kwarg_str(self):
        self.writer_kwarg(path=self.name)
        assert self.read(self.name) == "".join(self.text)

    def test_writer_kwarg_fobj(self):
        self.writer_kwarg(path=self.fobj)
        self.fobj.close()
        assert self.read(self.name) == "".join(self.text)

    def test_writer_kwarg_path_none(self):
        self.writer_kwarg(path=None)


class TestRandomState:
    @classmethod
    def setup_class(cls):
        global np
        np = pytest.importorskip("numpy")

    @np_random_state(1)
    def instantiate_np_random_state(self, random_state):
        allowed = (np.random.RandomState, np.random.Generator)
        assert isinstance(random_state, allowed)
        return random_state.random()

    @py_random_state(1)
    def instantiate_py_random_state(self, random_state):
        allowed = (random.Random, PythonRandomInterface, PythonRandomViaNumpyBits)
        assert isinstance(random_state, allowed)
        return random_state.random()

    def test_random_state_None(self):
        np.random.seed(42)
        rv = np.random.random()
        np.random.seed(42)
        assert rv == self.instantiate_np_random_state(None)

        random.seed(42)
        rv = random.random()
        random.seed(42)
        assert rv == self.instantiate_py_random_state(None)

    def test_random_state_np_random(self):
        np.random.seed(42)
        rv = np.random.random()
        np.random.seed(42)
        assert rv == self.instantiate_np_random_state(np.random)
        np.random.seed(42)
        assert rv == self.instantiate_py_random_state(np.random)

    def test_random_state_int(self):
        np.random.seed(42)
        np_rv = np.random.random()
        random.seed(42)
        py_rv = random.random()

        np.random.seed(42)
        seed = 1
        rval = self.instantiate_np_random_state(seed)
        rval_expected = np.random.RandomState(seed).rand()
        assert rval == rval_expected
        # test that global seed wasn't changed in function
        assert np_rv == np.random.random()

        random.seed(42)
        rval = self.instantiate_py_random_state(seed)
        rval_expected = random.Random(seed).random()
        assert rval == rval_expected
        # test that global seed wasn't changed in function
        assert py_rv == random.random()

    def test_random_state_np_random_Generator(self):
        np.random.seed(42)
        np_rv = np.random.random()
        np.random.seed(42)
        seed = 1

        rng = np.random.default_rng(seed)
        rval = self.instantiate_np_random_state(rng)
        rval_expected = np.random.default_rng(seed).random()
        assert rval == rval_expected

        rval = self.instantiate_py_random_state(rng)
        rval_expected = np.random.default_rng(seed).random(size=2)[1]
        assert rval == rval_expected
        # test that global seed wasn't changed in function
        assert np_rv == np.random.random()

    def test_random_state_np_random_RandomState(self):
        np.random.seed(42)
        np_rv = np.random.random()
        np.random.seed(42)
        seed = 1

        rng = np.random.RandomState(seed)
        rval = self.instantiate_np_random_state(rng)
        rval_expected = np.random.RandomState(seed).random()
        assert rval == rval_expected

        rval = self.instantiate_py_random_state(rng)
        rval_expected = np.random.RandomState(seed).random(size=2)[1]
        assert rval == rval_expected
        # test that global seed wasn't changed in function
        assert np_rv == np.random.random()

    def test_random_state_py_random(self):
        seed = 1
        rng = random.Random(seed)
        rv = self.instantiate_py_random_state(rng)
        assert rv == random.Random(seed).random()

        pytest.raises(ValueError, self.instantiate_np_random_state, rng)


def test_random_state_string_arg_index():
    with pytest.raises(nx.NetworkXError):

        @np_random_state("a")
        def make_random_state(rs):
            pass

        rstate = make_random_state(1)


def test_py_random_state_string_arg_index():
    with pytest.raises(nx.NetworkXError):

        @py_random_state("a")
        def make_random_state(rs):
            pass

        rstate = make_random_state(1)


def test_random_state_invalid_arg_index():
    with pytest.raises(nx.NetworkXError):

        @np_random_state(2)
        def make_random_state(rs):
            pass

        rstate = make_random_state(1)


def test_py_random_state_invalid_arg_index():
    with pytest.raises(nx.NetworkXError):

        @py_random_state(2)
        def make_random_state(rs):
            pass

        rstate = make_random_state(1)


class TestArgmap:
    class ArgmapError(RuntimeError):
        pass

    def test_trivial_function(self):
        def do_not_call(x):
            raise ArgmapError("do not call this function")

        @argmap(do_not_call)
        def trivial_argmap():
            return 1

        assert trivial_argmap() == 1

    def test_trivial_iterator(self):
        def do_not_call(x):
            raise ArgmapError("do not call this function")

        @argmap(do_not_call)
        def trivial_argmap():
            yield from (1, 2, 3)

        assert tuple(trivial_argmap()) == (1, 2, 3)

    def test_contextmanager(self):
        container = []

        def contextmanager(x):
            nonlocal container
            return x, lambda: container.append(x)

        @argmap(contextmanager, 0, 1, 2, try_finally=True)
        def foo(x, y, z):
            return x, y, z

        x, y, z = foo("a", "b", "c")

        # context exits are called in reverse
        assert container == ["c", "b", "a"]

    def test_tryfinally_generator(self):
        container = []

        def singleton(x):
            return (x,)

        with pytest.raises(nx.NetworkXError):

            @argmap(singleton, 0, 1, 2, try_finally=True)
            def foo(x, y, z):
                yield from (x, y, z)

        @argmap(singleton, 0, 1, 2)
        def foo(x, y, z):
            return x + y + z

        q = foo("a", "b", "c")

        assert q == ("a", "b", "c")

    def test_actual_vararg(self):
        @argmap(lambda x: -x, 4)
        def foo(x, y, *args):
            return (x, y) + tuple(args)

        assert foo(1, 2, 3, 4, 5, 6) == (1, 2, 3, 4, -5, 6)

    def test_signature_destroying_intermediate_decorator(self):
        def add_one_to_first_bad_decorator(f):
            """Bad because it doesn't wrap the f signature (clobbers it)"""

            def decorated(a, *args, **kwargs):
                return f(a + 1, *args, **kwargs)

            return decorated

        add_two_to_second = argmap(lambda b: b + 2, 1)

        @add_two_to_second
        @add_one_to_first_bad_decorator
        def add_one_and_two(a, b):
            return a, b

        assert add_one_and_two(5, 5) == (6, 7)

    def test_actual_kwarg(self):
        @argmap(lambda x: -x, "arg")
        def foo(*, arg):
            return arg

        assert foo(arg=3) == -3

    def test_nested_tuple(self):
        def xform(x, y):
            u, v = y
            return x + u + v, (x + u, x + v)

        # we're testing args and kwargs here, too
        @argmap(xform, (0, ("t", 2)))
        def foo(a, *args, **kwargs):
            return a, args, kwargs

        a, args, kwargs = foo(1, 2, 3, t=4)

        assert a == 1 + 4 + 3
        assert args == (2, 1 + 3)
        assert kwargs == {"t": 1 + 4}

    def test_flatten(self):
        assert tuple(argmap._flatten([[[[[], []], [], []], [], [], []]], set())) == ()

        rlist = ["a", ["b", "c"], [["d"], "e"], "f"]
        assert "".join(argmap._flatten(rlist, set())) == "abcdef"

    def test_indent(self):
        code = "\n".join(
            argmap._indent(
                *[
                    "try:",
                    "try:",
                    "pass#",
                    "finally:",
                    "pass#",
                    "#",
                    "finally:",
                    "pass#",
                ]
            )
        )
        assert (
            code
            == """try:
 try:
  pass#
 finally:
  pass#
 #
finally:
 pass#"""
        )

    def test_immediate_raise(self):
        @not_implemented_for("directed")
        def yield_nodes(G):
            yield from G

        G = nx.Graph([(1, 2)])
        D = nx.DiGraph()

        # test first call (argmap is compiled and executed)
        with pytest.raises(nx.NetworkXNotImplemented):
            node_iter = yield_nodes(D)

        # test second call (argmap is only executed)
        with pytest.raises(nx.NetworkXNotImplemented):
            node_iter = yield_nodes(D)

        # ensure that generators still make generators
        node_iter = yield_nodes(G)
        next(node_iter)
        next(node_iter)
        with pytest.raises(StopIteration):
            next(node_iter)
