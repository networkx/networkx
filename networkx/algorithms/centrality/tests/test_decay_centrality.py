"""
Unit tests for decay centrality
"""

import pytest
import networkx as nx


class TestDecayCentrality:
    @classmethod
    def setup_class(cls):
        cls.K = nx.krackhardt_kite_graph()
        cls.P3 = nx.path_graph(3)
        cls.P4 = nx.path_graph(4)
        cls.K5 = nx.complete_graph(5)

        cls.C4 = nx.cycle_graph(4)
        cls.T = nx.balanced_tree(r=2, h=2)
        cls.T.add_edge(5, 6)
        cls.T.add_edge(3, 4)
        cls.Gb = nx.Graph()
        cls.Gb.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (4, 5), (3, 5)])

        F = nx.florentine_families_graph()
        cls.F = F

        cls.LM = nx.les_miserables_graph()

    def test_decay_centrality_K(self):
        d = nx.decay_centrality(self.K)
        assert d == {
            0: 2.9375,
            1: 2.9375,
            2: 2.6875,
            3: 3.4375,
            4: 2.6875,
            5: 3.375,
            6: 3.375,
            7: 3.0,
            8: 2.125,
            9: 1.3125,
        }

    def test_decay_centrality_T(self):
        d = nx.decay_centrality(self.T)
        assert d == {0: 2.0, 1: 2.0, 2: 2.0, 3: 1.5, 4: 1.5, 5: 1.5, 6: 1.5}
