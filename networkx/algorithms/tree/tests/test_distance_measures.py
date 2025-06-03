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


class TestDistance:
    def setup_method(self):
        self.G = nx.convert_node_labels_to_integers(
            nx.grid_2d_graph(4, 4), first_label=1, ordering="sorted"
        )

    @pytest.mark.parametrize("n", [1, 2, 99, 100])
    def test_tree_centroid_path_graphs(self, n):
        G = nx.path_graph(n)
        expected = {(n - 1) // 2, math.ceil((n - 1) / 2)}
        assert set(nx.tree.centroid(G)) == expected

    @pytest.mark.parametrize("r", range(2, 5))
    @pytest.mark.parametrize("h", range(1, 5))
    def test_tree_centroid_balanced_tree(self, r, h):
        G = nx.balanced_tree(r, h)
        assert nx.tree.centroid(G) == [0]

    def test_tree_centroid_multiple_centroids(self):
        G = nx.full_rary_tree(2, 8)
        assert nx.tree.centroid(G) == [0, 1]

    def test_tree_centroid_not_a_tree(self):
        with pytest.raises(nx.NotATree):
            nx.tree.centroid(self.G)
