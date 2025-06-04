import math

import pytest

import networkx as nx


class TestDistance:
    @pytest.mark.parametrize("n", [1, 2, 99, 100])
    def test_tree_centroid_path_graphs(self, n):
        G = nx.path_graph(n)
        expected = {(n - 1) // 2, math.ceil((n - 1) / 2)}
        assert set(nx.tree_centroid(G)) == expected

    @pytest.mark.parametrize("r", range(2, 5))
    @pytest.mark.parametrize("h", range(1, 5))
    def test_tree_centroid_balanced_tree(self, r, h):
        G = nx.balanced_tree(r, h)
        assert nx.tree_centroid(G) == [0]

    def test_tree_centroid_multiple_centroids(self):
        G = nx.full_rary_tree(2, 8)
        assert nx.tree_centroid(G) == [0, 1]

    def test_tree_centroid_different_from_graph_center(self):
        G = nx.star_graph(6)
        nx.add_path(G, [6, 7, 8, 9, 10])
        # nx.center(G) would be [7]
        assert nx.tree_centroid(G) == [0]

    def test_tree_centroid_not_a_tree(self):
        G = nx.cycle_graph(3)
        with pytest.raises(nx.NotATree, match=r"not a tree"):
            nx.tree_centroid(G)

    def test_tree_centroid_empty(self):
        G = nx.Graph()
        with pytest.raises(nx.NetworkXPointlessConcept, match=r"has no nodes"):
            nx.tree_centroid(G)
