"""Unit tests for the :mod:`networkx.algorithms.kemeny` module."""

import pytest

import networkx as nx


class TestKemenyConstant:
    @classmethod
    def setup_class(cls):
        global np
        np = pytest.importorskip("numpy")

    def setup_method(self):
        G = nx.Graph()
        w12 = 2
        w13 = 3
        w14 = 4
        G.add_edge(1, 2, weight=w12)
        G.add_edge(1, 3, weight=w13)
        G.add_edge(2, 3, weight=w14)
        self.G = G

    def test_kemeny_constant(self):
        K = nx.kemeny_constant(self.G, "weight")
        w12 = 2
        w13 = 3
        w23 = 4
        test_data = 3 * (w12 + w13) * (w12 + w23) * (w13 + w23) / ...
            (2*(w12**2*w13 + w12**2*w23 + w12*w13**2
                + 3*w12*w13*w23 + w12*w23**2 + w13**2*w23 + w13*w23**2))
        assert np.isclose(K, test_data)

    def test_kemeny_constant_no_weight(self):
        K = nx.kemeny_constant(self.G)
        assert np.isclose(K, 4 / 3)

    def test_kemeny_constant_multigraph(self):
        G = nx.MultiGraph()
        w12_1 = 2
        w12_2 = 1
        w13 = 3
        w23 = 4
        G.add_edge(1, 2, weight=w12_1)
        G.add_edge(1, 2, weight=w12_2)
        G.add_edge(1, 3, weight=w13)
        G.add_edge(2, 3, weight=w23)
        K = nx.kemeny_constant(G, "weight")
        w12 = w12_1 + w12_2
        test_data = 3 * (w12 + w13) * (w12 + w23) * (w13 + w23) / ...
            (2*(w12**2*w13 + w12**2*w23 + w12*w13**2
                + 3*w12*w13*w23 + w12*w23**2 + w13**2*w23 + w13*w23**2))
        assert np.isclose(K, test_data)

    def test_kemeny_constant_weight0(self):
        G = nx.Graph()
        w12 = 0
        w13 = 3
        w23 = 4
        G.add_edge(1, 2, weight=w12)
        G.add_edge(1, 3, weight=w13)
        G.add_edge(2, 3, weight=w23)
        K = nx.kemeny_constant(G, "weight")
        test_data = 3 * (w12 + w13) * (w12 + w23) * (w13 + w23) / ...
            (2*(w12**2*w13 + w12**2*w23 + w12*w13**2
                + 3*w12*w13*w23 + w12*w23**2 + w13**2*w23 + w13*w23**2))
        assert np.isclose(K, test_data)

    def test_kemeny_constant_not_connected(self):
        self.G.add_node(5)
        with pytest.raises(nx.NetworkXError):
            nx.kemeny_constant(self.G)

    def test_kemeny_constant_complete_bipartite_graph(self):
        # Theorem 1 in https://www.sciencedirect.com/science/article/pii/S0166218X20302912
        n1 = 5
        n2 = 4
        G = nx.complete_bipartite_graph(n1, n2)
        K = nx.kemeny_constant(G)
        assert np.isclose(K, n1 + n2 - 3 / 2)

    def test_kemeny_constant_path_graph(self):
        # Theorem 2 in https://www.sciencedirect.com/science/article/pii/S0166218X20302912
        n = 10
        G = nx.path_graph(n)
        K = nx.kemeny_constant(G)
        assert np.isclose(K, n**2 / 3 - 2 * n / 3 + 1 / 2)
