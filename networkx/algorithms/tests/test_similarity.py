#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from networkx.algorithms.similarity import *
from networkx.generators.classic import *

class TestSimilarity:

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
        G1 = path_graph(5)
        G2 = path_graph(5)
        for n in G1.nodes():
            G1.nodes[n]['color'] = 'red' if n % 2 == 0 else 'blue'
        for n in G2.nodes():
            G2.nodes[n]['color'] = 'red' if n % 2 == 1 else 'blue'
        assert_equal(graph_edit_distance(G2, G1), 0)
        assert_equal(graph_edit_distance(G1, G2, lambda n1, n2: n1['color'] == n2['color']), 2)
