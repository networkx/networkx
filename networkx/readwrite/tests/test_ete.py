"""
    Unit tests for ete.
"""

import os
import tempfile
import pytest

import networkx as nx
from networkx.testing import assert_edges_equal, assert_nodes_equal


class TestETE:
    @classmethod
    def setup_class(cls):
        cls.build_graphs()

    @classmethod
    def build_graphs(cls):
        e = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f")]
        cls.G = nx.Graph(name="test_undirected_graph")
        cls.DG = nx.DiGraph(name="test_directed_graph")
        cls.MG = nx.MultiGraph(name="test_multi_graph")

        cls.G.add_edges_from(e)
        cls.DG.add_edges_from(e)
        cls.MG.add_edges_from(e)

    def assert_equal(self, G, data=False):
        (fd, fname) = tempfile.mkstemp()
        nx.write_ete(G, fname)
        Gin = nx.read_ete(fname)

        assert_nodes_equal(list(G), list(Gin))
        assert_edges_equal(G.edges(data=data), Gin.edges(data=data))

        os.close(fd)
        os.unlink(fname)

    def test_undirected(self):
        self.assert_equal(self.G, data=False)

    def test_directed(self):
        self.assert_equal(self.DG, data=False)

    def test_multigraph(self):
        self.assert_equal(self.MG, data=True)
