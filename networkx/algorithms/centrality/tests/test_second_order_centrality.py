"""
Tests for second order centrality.
"""

import networkx as nx
from nose import SkipTest
from nose.tools import raises


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
    def test_nonconnected(self):
        G = nx.Graph()
        G.add_node(0)
        G.add_node(1)
        nx.second_order_centrality(G)
