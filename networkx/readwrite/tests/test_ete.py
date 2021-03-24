"""
    Unit tests for ete.
"""

import os
import tempfile
import pytest

nx_ete = pytest.importorskip("nx_ete")

import networkx as nx
from networkx.testing import assert_edges_equal, assert_nodes_equal


class TestETE:
    @classmethod
    def setup_class(cls):
        cls.build_graphs()

    @classmethod
    def build_graphs(cls):
        cls.G = nx.Graph(name="test")
        e = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f"), ("a", "f")]
        cls.G.add_edges_from(e)
        cls.DG = nx.DiGraph(cls.G)
        cls.MG = nx.MultiGraph(cls.G)

    def assert_equal(self, G, data=False):
        (fd, fname) = tempfile.mkstemp()
        nx_ete.write_ete(G, fname)
        Gin = nx_ete.read_ete(fname)

        assert_nodes_equal(list(G), list(Gin))
        assert_edges_equal(G.edges(data=data), Gin.edges(data=data))

        os.close(fd)
        os.unlink(fname)

    def testUndirected(self):
        self.assert_equal(self.G, data=False)

    def testDirected(self):
        self.assert_equal(self.DG, data=False)

    def testMultiGraph(self):
        self.assert_equal(self.MG, data=True)
