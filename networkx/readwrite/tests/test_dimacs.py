"""
    Unit tests for edgelists.
"""
import io

import networkx as nx
from networkx.testing import assert_edges_equal


class TestDimacs:
    @classmethod
    def setup_class(cls):
        pass

    def test_read_dimacs_1(self):
        s = b"""\
c this is a test graph in DIMACS Format

c another comment

p edge 3 3

e 1 2



e 2 3

e 3 1
"""
        bytesIO = io.BytesIO(s)
        G = nx.read_dimacs(bytesIO)
        assert_edges_equal(G.edges(), [(1, 2), (2, 3), (3, 1)])
