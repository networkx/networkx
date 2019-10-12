"""
    Unit tests for yaml.
"""

import os
import tempfile
import pytest

import networkx as nx
from networkx.testing import assert_edges_equal, assert_nodes_equal


class TestYaml(object):
    @classmethod
    def setup_class(cls):
        cls.build_graphs()

    @classmethod
    def build_graphs(cls):
        cls.G = nx.Graph(name="test")
        e = [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('a', 'f')]
        cls.G.add_edges_from(e)
        cls.G.add_node('g')

        cls.DG = nx.DiGraph(cls.G)

        cls.MG = nx.MultiGraph()
        cls.MG.add_weighted_edges_from([(1, 2, 5), (1, 2, 5), (1, 2, 1), (3, 3, 42)])

    def assert_equal(self, G, data=False):
        (fd, fname) = tempfile.mkstemp()
        nx.write_yaml(G, fname)
        Gin = nx.read_yaml(fname)

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


# fixture for pytest tests
def setup_module(module):
    import pytest
    yaml = pytest.importorskip("yaml")
