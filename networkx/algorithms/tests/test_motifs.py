"""Tests for motif counting functions using the ESU algorithm."""

import pytest

import networkx as nx


class TestCountMotifs:
    """Tests for the count_motifs function."""

    def test_count_motifs_triangle(self):
        """A triangle should have exactly one 3-node motif (the triangle itself)."""
        G = nx.cycle_graph(3)
        motifs = nx.count_motifs(G, size=3)
        assert sum(motifs.values()) == 1

    def test_count_motifs_complete_graph_size_3(self):
        """K4 has C(4,3) = 4 triangles as 3-node motifs."""
        G = nx.complete_graph(4)
        motifs = nx.count_motifs(G, size=3)
        assert sum(motifs.values()) == 4

    def test_count_motifs_complete_graph_size_4(self):
        """K5 has C(5,4) = 5 complete 4-subgraphs as 4-node motifs."""
        G = nx.complete_graph(5)
        motifs = nx.count_motifs(G, size=4)
        assert sum(motifs.values()) == 5

    def test_count_motifs_path_graph(self):
        """A path graph P4 has exactly 2 connected 3-node subgraphs (two paths)."""
        G = nx.path_graph(4)
        motifs = nx.count_motifs(G, size=3)
        assert sum(motifs.values()) == 2

    def test_count_motifs_star_graph(self):
        """A star graph S4 (1 hub + 3 leaves) has C(3,2) = 3 connected 3-node subgraphs."""
        G = nx.star_graph(3)
        motifs = nx.count_motifs(G, size=3)
        assert sum(motifs.values()) == 3

    def test_count_motifs_directed(self):
        """Test motif counting on a directed graph."""
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0)])
        motifs = nx.count_motifs(G, size=3)
        assert sum(motifs.values()) == 1

    def test_count_motifs_invalid_size(self):
        """Motif size must be at least 2."""
        G = nx.path_graph(5)
        with pytest.raises(ValueError, match="at least 2"):
            nx.count_motifs(G, size=1)

    def test_count_motifs_size_exceeds_max(self):
        """Motif size should not exceed max allowed (4)."""
        G = nx.path_graph(10)
        with pytest.raises(ValueError, match="at most 4"):
            nx.count_motifs(G, size=5)

    def test_count_motifs_empty_graph(self):
        """Empty graph should return empty motif counts."""
        G = nx.Graph()
        motifs = nx.count_motifs(G, size=3)
        assert motifs == {}

    def test_count_motifs_small_graph(self):
        """Graph smaller than motif size should return empty counts."""
        G = nx.path_graph(2)
        motifs = nx.count_motifs(G, size=3)
        assert motifs == {}

    def test_count_motifs_disconnected(self):
        """Test motif counting on a disconnected graph."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0)])
        G.add_edges_from([(3, 4), (4, 5), (5, 3)])
        motifs = nx.count_motifs(G, size=3)
        assert sum(motifs.values()) == 2

    def test_count_motifs_canonical_labels_consistent(self):
        """Same motif structure should have same canonical label."""
        G = nx.complete_graph(4)
        motifs = nx.count_motifs(G, size=3)
        assert len(motifs) == 1

    def test_count_motifs_non_integer_nodes(self):
        """Test that graphs with non-integer nodes are handled correctly."""
        G = nx.Graph()
        G.add_edges_from([("a", "b"), ("b", "c"), ("c", "a")])
        motifs = nx.count_motifs(G, size=3)
        assert sum(motifs.values()) == 1
