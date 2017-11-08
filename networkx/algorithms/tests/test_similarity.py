#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from networkx.algorithms.similarity import *
from networkx.generators.classic import *

class TestSimilarity:

    @classmethod
    def setupClass(cls):
        global numpy
        global scipy
        try:
            import numpy
        except ImportError:
            raise SkipTest('NumPy not available.')
        try:
            import scipy
        except ImportError:
            raise SkipTest('SciPy not available.')

    def test_graph_edit_distance(self):
        G1 = path_graph(6)
        G2 = cycle_graph(6)
        G3 = wheel_graph(7)

        assert_equal(graph_edit_distance(G1, G1), 0)
        assert_equal(graph_edit_distance(G2, G2), 0)
        assert_equal(graph_edit_distance(G3, G3), 0)
        assert_equal(graph_edit_distance(G1, G2), 1)
        assert_equal(graph_edit_distance(G2, G1), 1)
        assert_equal(graph_edit_distance(G2, G3), 7)
        assert_equal(graph_edit_distance(G3, G2), 7)
        assert_equal(graph_edit_distance(G1, G3), 8)
        assert_equal(graph_edit_distance(G3, G1), 8)

    def test_graph_edit_distance_node_match(self):
        G1 = cycle_graph(5)
        G2 = cycle_graph(5)
        for n, attr in G1.nodes.items():
            attr['color'] = 'red' if n % 2 == 0 else 'blue'
        for n, attr in G2.nodes.items():
            attr['color'] = 'red' if n % 2 == 1 else 'blue'
        assert_equal(graph_edit_distance(G2, G1), 0)
        assert_equal(graph_edit_distance(G1, G2, node_match = lambda n1, n2: n1['color'] == n2['color']), 1)

    def test_graph_edit_distance_edge_match(self):
        G1 = path_graph(6)
        G2 = path_graph(6)
        for e, attr in G1.edges.items():
            attr['color'] = 'red' if min(e) % 2 == 0 else 'blue'
        for e, attr in G2.edges.items():
            attr['color'] = 'red' if min(e) // 3 == 0 else 'blue'
        assert_equal(graph_edit_distance(G2, G1), 0)
        assert_equal(graph_edit_distance(G1, G2, edge_match = lambda e1, e2: e1['color'] == e2['color']), 2)

    def test_graph_edit_distance_bigger(self):
        G1 = circular_ladder_graph(2)
        G2 = circular_ladder_graph(6)
        #G1 = circular_ladder_graph(12)
        #G2 = circular_ladder_graph(16)
        assert_equal(graph_edit_distance(G1, G2), 22)
