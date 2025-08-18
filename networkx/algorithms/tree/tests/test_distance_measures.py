import math

import pytest

import networkx as nx


class TestCenter:
    @pytest.mark.parametrize("graph_type", (nx.Graph, nx.MultiGraph))
    def test_center_simple_tree(self, graph_type):
        G = nx.Graph([(1, 2), (1, 3), (2, 4), (2, 5)], create_using=graph_type)
        assert set(nx.tree.center(G)) == {1, 2}

    @pytest.mark.parametrize("r", range(2, 5))
    @pytest.mark.parametrize("h", range(1, 5))
    def test_center_balanced_tree(self, r, h):
        G = nx.balanced_tree(r, h)
        assert nx.tree.center(G) == [0]

    @pytest.mark.parametrize("n", [1, 2, 99, 100])
    def test_center_path_graph(self, n):
        G = nx.path_graph(n)
        expected = {(n - 1) // 2, math.ceil((n - 1) / 2)}
        assert set(nx.tree.center(G)) == expected

    @pytest.mark.parametrize("n", [0, 2, 3, 5, 99, 100])
    def test_center_star_graph(self, n):
        G = nx.star_graph(n)
        assert nx.tree.center(G) == [0]

    @pytest.mark.parametrize(
        "G",
        (
            nx.cycle_graph(5),
            nx.complete_graph(5),
            nx.Graph([(0, 1), (2, 3)]),
            nx.empty_graph(2),
            nx.Graph(),
            nx.MultiGraph([(0, 1), (0, 1)]),
            nx.Graph([(0, 1), (1, 2), (3, 4)]),
            nx.Graph([(0, 1), (1, 2), (3, 4), (4, 5)]),
            pytest.param(
                nx.Graph([(0, 0)]),
                marks=pytest.mark.xfail(reason="no check for self-loops"),
            ),
        ),
    )
    def test_center_non_tree(self, G):
        with pytest.raises(nx.NotATree, match=r"not a tree"):
            nx.tree.center(G)

    @pytest.mark.parametrize("graph_type", (nx.DiGraph, nx.MultiDiGraph))
    def test_center_directed(self, graph_type):
        G = nx.path_graph(4, create_using=graph_type)
        with pytest.raises(
            nx.NetworkXNotImplemented, match=r"not implemented for directed"
        ):
            nx.tree.center(G)
