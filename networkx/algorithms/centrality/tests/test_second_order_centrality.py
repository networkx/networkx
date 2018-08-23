"""
Tests for second order centrality.
"""

import networkx as nx
from nose import SkipTest
from nose.tools import raises, assert_almost_equal


class TestSecondOrderCentrality(object):

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

    def test_florentine_families_graph(self):
        """Second order centrality: Florentine families graph"""
        G = nx.florentine_families_graph()
        b_answer = {'Acciaiuoli':    39.49,
                    'Albizzi':       19.91,
                    'Barbadori':     22.17,
                    'Bischeri':      22.75,
                    'Castellani':    23.67,
                    'Ginori':        58.92,
                    'Guadagni':      17.44,
                    'Lamberteschi':  56.45,
                    'Medici':        0.00,
                    'Pazzi':         76.49,
                    'Peruzzi':       25.90,
                    'Ridolfi':       13.75,
                    'Salviati':      37.49,
                    'Strozzi':       18.85,
                    'Tornabuoni':    13.80}

        b = nx.second_order_centrality(G)

        for n in sorted(G):
            assert_almost_equal(b[n], b_answer[n], delta=0.01)
