"""
Tests for linear geometric centrality.
"""

import pytest

import networkx as nx
from networkx.algorithms.centrality import (
    closeness_centrality,
    harmonic_centrality,
    linear_geometric_centrality,
)


class TestLinearGeometricCentrality:
    @classmethod
    def setup_class(cls):
        cls.P3 = nx.path_graph(3)
        cls.P4 = nx.path_graph(4)
        cls.K5 = nx.complete_graph(5)

        cls.C4 = nx.cycle_graph(4)
        cls.C4_directed = nx.cycle_graph(4, create_using=nx.DiGraph)

        cls.C5 = nx.cycle_graph(5)

        cls.T = nx.balanced_tree(r=2, h=2)

        cls.Gb = nx.DiGraph()
        cls.Gb.add_edges_from([(0, 1), (0, 2), (0, 4), (2, 1), (2, 3), (4, 3)])
        cls.Gbd = {
            0: {},
            1: {1: 2},
            2: {1: 1},
            3: {1: 2, 2: 1},
            4: {1: 1},
        }  # Maps node x to a dictionary with keys distances and values meaning count of nodes at that distance

    def fharm(self, x):
        return 1.0 / x

    def findeg(self, x):
        return 1 if x == 1 else 0

    def f1(self, x):
        return {1: 5, 2: 7}[x]

    def fexp(self, x):
        return 0.3**x

    def fpowerlaw(self, x):
        return x ** (-4)

    def test_all_undir(self):
        for G in [self.P3, self.P4, self.K5, self.C4, self.C5, self.T]:
            ch = harmonic_centrality(G)
            cd = G.degree()
            cfharm = linear_geometric_centrality(G, self.fharm)
            cfindeg = linear_geometric_centrality(G, self.findeg)
            for n in sorted(G):
                assert cfharm[n] == pytest.approx(ch[n], abs=1e-3)
                assert cfindeg[n] == pytest.approx(cd[n], abs=1e-3)

    def test_all_undir_str(self):
        for G in [self.P3, self.P4, self.K5, self.C4, self.C5, self.T]:
            ch = harmonic_centrality(G)
            cd = G.degree()
            ccl = closeness_centrality(G, wf_improved=False)
            print(ccl)
            cfharm = linear_geometric_centrality(G, "harmonic")
            cfindeg = linear_geometric_centrality(G, "indegree")
            cfnecc = linear_geometric_centrality(G, "negecc")
            for n in sorted(G):
                assert cfharm[n] == pytest.approx(ch[n], abs=1e-3)
                assert cfindeg[n] == pytest.approx(cd[n], abs=1e-3)
                assert cfnecc[n] == pytest.approx(
                    -(G.number_of_nodes() - 1) / ccl[n], abs=1e-3
                )

    def test_exampleGraph(self):
        ch = harmonic_centrality(self.Gb)
        cfharm = linear_geometric_centrality(self.Gb, self.fharm)
        for n in sorted(self.Gb):
            assert cfharm[n] == pytest.approx(ch[n], abs=1e-3)
        dd = {}
        for n, d2c in self.Gbd.items():
            sum = 0
            for d, c in d2c.items():
                sum += c * (self.f1(d))
            dd[n] = sum
        ld = linear_geometric_centrality(self.Gb, self.f1)
        for n in sorted(self.Gb):
            assert ld[n] == pytest.approx(dd[n], abs=1e-3)

    def test_exampleGraphExponential(self):
        ch = harmonic_centrality(self.Gb)
        cfharm = linear_geometric_centrality(self.Gb, self.fharm)
        for n in sorted(self.Gb):
            assert cfharm[n] == pytest.approx(ch[n], abs=1e-3)
        dd = {}
        for n, d2c in self.Gbd.items():
            sum = 0
            for d, c in d2c.items():
                sum += c * 0.3**d
            dd[n] = sum
        ld = linear_geometric_centrality(self.Gb, self.fexp)
        for n in sorted(self.Gb):
            assert ld[n] == pytest.approx(dd[n], abs=1e-3)

    def test_exampleGraphPowerlaw(self):
        ch = harmonic_centrality(self.Gb)
        cfharm = linear_geometric_centrality(self.Gb, self.fharm)
        for n in sorted(self.Gb):
            assert cfharm[n] == pytest.approx(ch[n], abs=1e-3)
        dd = {}
        for n, d2c in self.Gbd.items():
            sum = 0
            for d, c in d2c.items():
                sum += c * d ** (-4)
            dd[n] = sum
        ld = linear_geometric_centrality(self.Gb, self.fpowerlaw)
        for n in sorted(self.Gb):
            assert ld[n] == pytest.approx(dd[n], abs=1e-3)

    def test_weighted_harmonic(self):
        XG = nx.DiGraph()
        XG.add_weighted_edges_from(
            [
                ("a", "b", 10),
                ("d", "c", 5),
                ("a", "c", 1),
                ("e", "f", 2),
                ("f", "c", 1),
                ("a", "f", 3),
            ]
        )
        ch = harmonic_centrality(XG, distance="weight")
        cfharm = linear_geometric_centrality(XG, self.fharm, weight="weight")
        for n in sorted(XG):
            assert cfharm[n] == pytest.approx(ch[n], abs=1e-3)

    def test_empty(self):
        G = nx.DiGraph()
        c = linear_geometric_centrality(G, self.fharm, weight="weight")
        d = {}
        assert c == d

    def test_singleton(self):
        G = nx.DiGraph()
        G.add_node(0)
        c = linear_geometric_centrality(G, self.fharm, weight="weight")
        d = {0: 0}
        assert c == d

    def test_cycle_c4_directed(self):
        ch = harmonic_centrality(self.C4_directed, nbunch=[0, 1], sources=[1, 2])
        cfharm = linear_geometric_centrality(
            self.C4_directed, self.fharm, nbunch=[0, 1], sources=[1, 2]
        )
        for n in [0, 1]:
            assert cfharm[n] == pytest.approx(ch[n], abs=1e-3)

    def test_cycle_c4_directed_subset(self):
        c = linear_geometric_centrality(self.C4_directed, self.fharm, nbunch=[0, 1])
        d = 1.833
        for n in [0, 1]:
            assert c[n] == pytest.approx(d, abs=1e-3)

    def test_p3_harmonic_subset(self):
        ch = harmonic_centrality(self.P3, sources=[0, 1])
        cfharm = linear_geometric_centrality(self.P3, self.fharm, sources=[0, 1])
        for n in self.P3:
            assert ch[n] == pytest.approx(cfharm[n], abs=1e-3)

    def test_p4_harmonic_subset(self):
        ch = harmonic_centrality(self.P4, nbunch=[2, 3], sources=[0, 1])
        cfharm = linear_geometric_centrality(self.P4, self.fharm, sources=[0, 1])
        for n in [2, 3]:
            assert ch[n] == pytest.approx(cfharm[n], abs=1e-3)
