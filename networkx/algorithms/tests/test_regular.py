import pytest

import networkx as nx
import networkx.algorithms.regular as reg
import networkx.generators as gen


class TestKFactor:
    def test_k_factor_trivial(self):
        g = gen.cycle_graph(4)
        f = reg.k_factor(g, 2)
        assert g.edges == f.edges

    def test_k_factor1(self):
        g = gen.grid_2d_graph(4, 4)
        g_kf = reg.k_factor(g, 2)
        for edge in g_kf.edges():
            assert g.has_edge(edge[0], edge[1])
        for _, degree in g_kf.degree():
            assert degree == 2

    def test_k_factor2(self):
        g = gen.complete_graph(6)
        g_kf = reg.k_factor(g, 3)
        for edge in g_kf.edges():
            assert g.has_edge(edge[0], edge[1])
        for _, degree in g_kf.degree():
            assert degree == 3

    def test_k_factor3(self):
        g = gen.grid_2d_graph(4, 4)
        with pytest.raises(nx.NetworkXUnfeasible):
            reg.k_factor(g, 3)

    def test_k_factor4(self):
        g = gen.lattice.hexagonal_lattice_graph(4, 4)
        # Perfect matching doesn't exist for 4,4 hexagonal lattice graph
        with pytest.raises(nx.NetworkXUnfeasible):
            reg.k_factor(g, 2)

    def test_k_factor5(self):
        g = gen.complete_graph(6)
        # small k to exercise SmallKGadget
        g_kf = reg.k_factor(g, 2)
        for edge in g_kf.edges():
            assert g.has_edge(edge[0], edge[1])
        for _, degree in g_kf.degree():
            assert degree == 2


class TestIsRegular:
    @pytest.mark.parametrize(
        "graph,expected",
        [
            (nx.cycle_graph(5), True),
            (nx.complete_graph(5), True),
            (nx.path_graph(5), False),
            (nx.lollipop_graph(5, 5), False),
            (nx.cycle_graph(5, create_using=nx.DiGraph), True),
            (nx.Graph([(0, 1)]), True),
            (nx.DiGraph([(0, 1)]), False),
            (nx.MultiGraph([(0, 1), (0, 1)]), True),
            (nx.MultiDiGraph([(0, 1), (0, 1)]), False),
        ],
    )
    def test_is_regular(self, graph, expected):
        assert reg.is_regular(graph) == expected

    def test_is_regular_empty_graph_raises(self):
        graph = nx.Graph()
        with pytest.raises(nx.NetworkXPointlessConcept, match="Graph has no nodes"):
            nx.is_regular(graph)


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
