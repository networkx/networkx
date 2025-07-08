import pytest

import networkx as nx
import networkx.algorithms.regular as reg
import networkx.generators as gen


class TestKFactor:
    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_k_factor_cycle(self, n):
        g = nx.cycle_graph(n)
        kf = nx.k_factor(g, 2)
        assert g.edges == kf.edges
        assert g.nodes == kf.nodes

    @pytest.mark.parametrize("graph", [nx.complete_graph(4), nx.grid_2d_graph(4, 4)])
    @pytest.mark.parametrize("k", [1, 2])
    def test_k_factor(self, graph, k):
        kf = nx.k_factor(graph, k)
        for u, v in kf.edges():
            assert graph.has_edge(u, v)
        assert nx.is_k_regular(kf, k)

    def test_k_factor_degree(self):
        g = nx.grid_2d_graph(4, 4)
        with pytest.raises(nx.NetworkXUnfeasible, match=r"degree less than"):
            nx.k_factor(g, 3)

    def test_k_factor_no_matching(self):
        g = nx.hexagonal_lattice_graph(4, 4)
        # Perfect matching doesn't exist for 4,4 hexagonal lattice graph
        with pytest.raises(nx.NetworkXUnfeasible, match=r"no perfect matching"):
            nx.k_factor(g, 2)

    @pytest.mark.parametrize("graph_type", [nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph])
    def test_k_factor_not_implemented(self, graph_type):
        with pytest.raises(nx.NetworkXNotImplemented, match=r"not implemented for"):
            nx.k_factor(graph_type(), 2)


class TestIsRegular:
    def test_is_regular1(self):
        g = gen.cycle_graph(4)
        assert reg.is_regular(g)

    def test_is_regular2(self):
        g = gen.complete_graph(5)
        assert reg.is_regular(g)

    def test_is_regular3(self):
        g = gen.lollipop_graph(5, 5)
        assert not reg.is_regular(g)

    def test_is_regular4(self):
        g = nx.DiGraph()
        g.add_edges_from([(0, 1), (1, 2), (2, 0)])
        assert reg.is_regular(g)


def test_is_regular_empty_graph_raises():
    G = nx.Graph()
    with pytest.raises(nx.NetworkXPointlessConcept, match="Graph has no nodes"):
        nx.is_regular(G)


class TestIsKRegular:
    def test_is_k_regular1(self):
        g = gen.cycle_graph(4)
        assert reg.is_k_regular(g, 2)
        assert not reg.is_k_regular(g, 3)

    def test_is_k_regular2(self):
        g = gen.complete_graph(5)
        assert reg.is_k_regular(g, 4)
        assert not reg.is_k_regular(g, 3)
        assert not reg.is_k_regular(g, 6)

    def test_is_k_regular3(self):
        g = gen.lollipop_graph(5, 5)
        assert not reg.is_k_regular(g, 5)
        assert not reg.is_k_regular(g, 6)
