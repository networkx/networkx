"""
Tests for second order centrality centrality.
"""

import networkx as nx
from nose import SkipTest
from nose.tools import raises


class TestSecondOrderCentrality(object):

    def setup_module(module):
        try:
            import numpy
        except:
            raise SkipTest("NumPy not available")

    @raises(nx.NetworkXException)
    def test_empty(self):
        G = nx.empty_graph()
        nx.second_order_centrality(G)

    @raises(nx.NetworkXException)
    def test_nonconnected(self):
        G = nx.Graph()
        G.add_node(0)
        G.add_node(1)
        nx.second_order_centrality(G)
