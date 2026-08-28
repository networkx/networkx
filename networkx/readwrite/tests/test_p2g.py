import io
import sys
import warnings

import pytest

import networkx as nx
from networkx.utils import edges_equal


def _clear_modules():
    # Clear python modules cache
    sys.modules.pop("networkx.readwrite.p2g")
    # Clear dispatching registration manifest
    to_del = [k for k in nx.utils.backends._registered_algorithms if "p2g" in k]
    for fn in to_del:
        nx.utils.backends._registered_algorithms.pop(fn)


@pytest.fixture(autouse=True)
def import_cache_clearer():
    ### Initialize - clear import cache if the module exists already (e.g.
    #   from doctests
    if "networkx.readwrite.p2g" in sys.modules:
        _clear_modules()
    yield "Resetting imports"
    ### Cleanup
    _clear_modules()


def test_fn_import_from_module_deprecation():
    with pytest.deprecated_call():
        from networkx.readwrite.p2g import read_p2g


def test_import_deprecation():
    with pytest.deprecated_call():
        import networkx.readwrite.p2g


class TestP2G:
    @classmethod
    def setup_class(cls):
        cls.G = nx.Graph(name="test")
        e = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f"), ("a", "f")]
        cls.G.add_edges_from(e)
        cls.G.add_node("g")
        cls.DG = nx.DiGraph(cls.G)

    def test_read_p2g(self):
        from networkx.readwrite.p2g import read_p2g

        s = b"""\
name
3 4
a
1 2
b

c
0 2
"""
        bytesIO = io.BytesIO(s)
        DG = read_p2g(bytesIO)
        assert DG.name == "name"
        assert sorted(DG) == ["a", "b", "c"]
        assert edges_equal(
            DG.edges(), [("a", "c"), ("a", "b"), ("c", "a"), ("c", "c")], directed=True
        )

    def test_write_p2g(self):
        from networkx.readwrite.p2g import write_p2g

        s = b"""foo
3 2
1
1 
2
2 
3

"""
        fh = io.BytesIO()
        G = nx.DiGraph()
        G.name = "foo"
        G.add_edges_from([(1, 2), (2, 3)])
        write_p2g(G, fh)
        fh.seek(0)
        r = fh.read()
        assert r == s

    def test_write_read_p2g(self):
        from networkx.readwrite.p2g import read_p2g, write_p2g

        fh = io.BytesIO()
        G = nx.DiGraph()
        G.name = "foo"
        G.add_edges_from([("a", "b"), ("b", "c")])
        write_p2g(G, fh)
        fh.seek(0)
        H = read_p2g(fh)
        assert edges_equal(G.edges(), H.edges(), directed=True)
