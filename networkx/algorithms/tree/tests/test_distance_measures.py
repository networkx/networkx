import math

import pytest

import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti


class TestDistance:
    def setup_method(self):
        self.G = cnlti(nx.grid_2d_graph(4, 4), first_label=1, ordering="sorted")

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
        G = nx.Graph()
        nx.add_star(G, [0, 1, 2, 3, 4, 5, 6])
        nx.add_path(G, [6, 7, 8, 9, 10])
        # nx.center(G) would be [7]
        assert nx.tree_centroid(G) == [0]

    def test_tree_centroid_not_a_tree(self):
        with pytest.raises(nx.NotATree):
            nx.tree_centroid(self.G)
