"""
Tests for second order centrality.
"""

import networkx as nx
from nose import SkipTest
from nose.tools import raises, assert_almost_equal


class TestSecondOrderCentrality(object):
    numpy = 1  # nosetests attribute, use nosetests -a 'not numpy' to skip test

    @classmethod
    def setupClass(cls):
        global np
        try:
            import numpy as np
            import scipy
        except ImportError:
            raise SkipTest('NumPy not available.')

    @raises(nx.NetworkXException)
    def test_empty(self):
        G = nx.empty_graph()
        nx.second_order_centrality(G)

    @raises(nx.NetworkXException)
    def test_non_connected(self):
        G = nx.Graph()
        G.add_node(0)
        G.add_node(1)
        nx.second_order_centrality(G)

    @raises(nx.NetworkXException)
    def test_non_negative_edge_weights(self):
        G = nx.path_graph(2)
        G.add_edge(0, 1, weight=-1)
        nx.second_order_centrality(G)

    def test_one_node_graph(self):
        """Second order centrality: single node"""
        G = nx.Graph()
        G.add_node(0)
        G.add_edge(0, 0)
        assert nx.second_order_centrality(G)[0] == 0

    def test_P3(self):
        """Second order centrality: line graph, as defined in paper"""
        G = nx.path_graph(3)
        b_answer = {0: 3.741, 1: 1.414, 2: 3.741}

        b = nx.second_order_centrality(G)

        for n in sorted(G):
            assert_almost_equal(b[n], b_answer[n], places=2)

    def test_K3(self):
        """Second order centrality: complete graph, as defined in paper"""
        G = nx.complete_graph(3)
        b_answer = {0: 1.414, 1: 1.414, 2: 1.414}

        b = nx.second_order_centrality(G)

        for n in sorted(G):
            assert_almost_equal(b[n], b_answer[n], places=2)

    def test_ring_graph(self):
        """Second order centrality: ring graph, as defined in paper"""
        G = nx.cycle_graph(5)
        b_answer = {0: 4.472, 1: 4.472, 2: 4.472,
                    3: 4.472, 4: 4.472}

        b = nx.second_order_centrality(G)

        for n in sorted(G):
            assert_almost_equal(b[n], b_answer[n], places=2)
