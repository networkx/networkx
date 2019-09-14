"""
Tests for parallel harmonic centrality.
"""
from nose.tools import assert_almost_equal, assert_equal
import networkx as nx
from networkx.algorithms.centrality import harmonic_centrality, parallel_harmonic_centrality


class TestParallelHarmonicCentrality:
    def setUp(self):
        self.P3 = nx.path_graph(3)
        self.P4 = nx.path_graph(4)
        self.K5 = nx.complete_graph(5)

        self.C4 = nx.cycle_graph(4)
        self.C5 = nx.cycle_graph(5)

        self.T = nx.balanced_tree(r=2, h=2)

        self.Gb = nx.DiGraph()
        self.Gb.add_edges_from([(0, 1), (0, 2), (0, 4), (2, 1),
                                (2, 3), (4, 3)])

    def test_p3_harmonic(self):
        c = harmonic_centrality(self.P3)
        d = parallel_harmonic_centrality(self.P3)

        for n in sorted(self.P3):
            assert_almost_equal(c[n], d[n], places=3)

    def test_p4_harmonic(self):
        c = harmonic_centrality(self.P4)
        d = parallel_harmonic_centrality(self.P4)
        for n in sorted(self.P4):
            assert_almost_equal(c[n], d[n], places=3)

    def test_clique_complete(self):
        c = harmonic_centrality(self.K5)
        d = parallel_harmonic_centrality(self.K5)
        for n in sorted(self.K5):
            assert_almost_equal(c[n], d[n], places=3)

    def test_cycle_C4(self):
        c = harmonic_centrality(self.C4)
        d = parallel_harmonic_centrality(self.C4)
        for n in sorted(self.C4):
            assert_almost_equal(c[n], d[n], places=3)

    def test_cycle_C5(self):
        c = harmonic_centrality(self.C5)
        d = parallel_harmonic_centrality(self.C5)
        for n in sorted(self.C5):
            assert_almost_equal(c[n], d[n], places=3)

    def test_bal_tree(self):
        c = harmonic_centrality(self.T)
        d = parallel_harmonic_centrality(self.T)
        for n in sorted(self.T):
            assert_almost_equal(c[n], d[n], places=3)

    def test_exampleGraph(self):
        c = harmonic_centrality(self.Gb)
        d = parallel_harmonic_centrality(self.Gb)
        for n in sorted(self.Gb):
            assert_almost_equal(c[n], d[n], places=3)

    def test_weighted_harmonic(self):
        XG = nx.DiGraph()
        XG.add_weighted_edges_from([('a', 'b', 10), ('d', 'c', 5), ('a', 'c', 1),
                                    ('e', 'f', 2), ('f', 'c', 1), ('a', 'f', 3),
                                    ])
        c = harmonic_centrality(XG, distance='weight')
        d = parallel_harmonic_centrality(XG, distance='weight')
        for n in sorted(XG):
            assert_almost_equal(c[n], d[n], places=3)

    def test_empty(self):
        G = nx.DiGraph()
        c = harmonic_centrality(G, distance='weight')
        d = parallel_harmonic_centrality(G, distance='weight')
        assert_equal(c, d)

    def test_singleton(self):
        G = nx.DiGraph()
        G.add_node(0)
        c = harmonic_centrality(G, distance='weight')
        d = parallel_harmonic_centrality(G, distance='weight')
        assert_equal(c, d)
