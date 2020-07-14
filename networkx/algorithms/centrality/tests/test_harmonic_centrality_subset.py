"""
Tests for harmonic centrality applied only to a subset of nodes in a graph.
"""

import networkx as nx
from networkx.algorithms.centrality.harmonic_subset import harmonic_centrality_subset
from networkx.testing import almost_equal


class TestHarmonicCentralitySubset:
    
    @classmethod
    def setup_class(cls):
        cls.P3 = nx.path_graph(3)
        cls.P4 = nx.path_graph(4)
        cls.K5 = nx.complete_graph(5)

        cls.C4 = nx.cycle_graph(4, create_using=nx.DiGraph)
        cls.C5 = nx.cycle_graph(5)

        cls.T = nx.balanced_tree(r=2, h=2, create_using=nx.DiGraph)

        cls.Gb = nx.DiGraph()
        cls.Gb.add_edges_from([(0, 1), (0, 2), (0, 4), (2, 1),
                               (2, 3), (4, 3)])

    def test_p3_harmonic_subset(self):
        c = harmonic_centrality_subset(self.P3, nbunch_v=[0, 1])
        d = {0: 1,
             1: 1,
             2: 1.5}
        for n in sorted(self.P3):
            assert almost_equal(c[n], d[n], places=3)

    def test_p4_harmonic_subset(self):
        c = harmonic_centrality_subset(self.P4, nbunch_u=[2, 3], nbunch_v=[0, 1])
        d = {2: 1.5,
             3: 0.8333333}
        for n in [2, 3]:
            assert almost_equal(c[n], d[n], places=3)

    def test_clique_complete(self):
        c = harmonic_centrality_subset(self.K5)
        d = {0: 4,
             1: 4,
             2: 4,
             3: 4,
             4: 4}
        for n in sorted(self.P3):
            assert almost_equal(c[n], d[n], places=3)

    def test_cycle_C4(self):
        c = harmonic_centrality_subset(self.C4, nbunch_u=[0, 1], nbunch_v=[1, 2])
        d = {0: 0.833,
             1: 0.333}
        for n in sorted([0, 1]):
            assert almost_equal(c[n], d[n], places=3)

    def test_bal_tree(self):
        c = harmonic_centrality_subset(self.T, [0, 6], 2)
        d = {0: 0.0,
             6: 1.0}
        for n in sorted([0, 6]):
            assert almost_equal(c[n], d[n], places=3)

    def test_exampleGraph(self):
        c = harmonic_centrality_subset(self.Gb)
        d = {0: 0,
             1: 2,
             2: 1,
             3: 2.5,
             4: 1}
        for n in sorted(self.Gb):
            assert almost_equal(c[n], d[n], places=3)

    def test_weighted_harmonic(self):
        XG = nx.DiGraph()
        XG.add_weighted_edges_from([('a', 'b', 10), ('d', 'c', 5), ('a', 'c', 1),
                                    ('e', 'f', 2), ('f', 'c', 1), ('a', 'f', 3),
                                    ])
        c = harmonic_centrality_subset(XG, distance='weight')
        d = {'a': 0,
             'b': 0.1,
             'c': 2.533,
             'd': 0,
             'e': 0,
             'f': 0.83333}
        for n in sorted(XG):
            assert almost_equal(c[n], d[n], places=3)

    def test_empty(self):
        G = nx.DiGraph()
        c = harmonic_centrality_subset(G, distance='weight')
        d = {}
        assert c == d

    def test_singleton(self):
        G = nx.DiGraph()
        G.add_node(0)
        c = harmonic_centrality_subset(G, distance='weight')
        d = {0: 0}
        assert c == d

