"""
    Unit tests for randic index.
"""

import networkx as nx
import unittest

from networkx.algorithms.connectivity.molecular_connectivity import randic_index


def exception_digraph():
    g = nx.DiGraph()
    return randic_index(g)


def exception_multigraph():
    g = nx.MultiGraph()
    return randic_index(g)


def exception_multiDigraph():
    g = nx.MultiDiGraph()
    return randic_index(g)


class TestDegreeCentrality(unittest.TestCase):
    def test_exception_digraph(self):
        self.assertRaises(nx.NetworkXNotImplemented, exception_digraph)

    def test_exception_multigraph(self):
        self.assertRaises(nx.NetworkXNotImplemented, exception_multigraph)

    def test_exception_multiDigraph(self):
        self.assertRaises(nx.NetworkXNotImplemented, exception_multiDigraph)

    def test_empty(self):
        g = nx.Graph()
        assert randic_index(g) == 0.0

    def test_sparse(self):
        g = nx.Graph()
        g.add_edge(1, 2)
        g.add_edge(3, 4)
        g.add_edge(5, 6)
        g.add_edge(7, 8)
        g.add_edge(9, 10)
        g.add_edge(11, 12)
        assert randic_index(g) == 6.0

    def test_dense(self):
        g = nx.random_regular_graph(4, 6)
        assert randic_index(g) == 3

    def test_k_5(self):
        g = nx.complete_graph(5)
        assert randic_index(g) == 2.5
