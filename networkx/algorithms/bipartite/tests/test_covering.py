import networkx as nx
from networkx.algorithms import bipartite


class TestMinEdgeCover:
    """Tests for :func:`networkx.algorithms.bipartite.min_edge_cover`"""

    def test_empty_graph(self):
        G = nx.Graph()
        assert bipartite.min_edge_cover(G) == set()

    def test_graph_single_edge(self):
        G = nx.Graph()
        G.add_edge(0, 1)
        # Should return one tuple per edge, not both directions
        result = bipartite.min_edge_cover(G)
        assert result == {(0, 1)} or result == {(1, 0)}
        assert len(result) == 1

    def test_bipartite_default(self):
        G = nx.Graph()
        G.add_nodes_from([1, 2, 3, 4], bipartite=0)
        G.add_nodes_from(["a", "b", "c"], bipartite=1)
        G.add_edges_from([(1, "a"), (1, "b"), (2, "b"), (2, "c"), (3, "c"), (4, "a")])
        min_cover = bipartite.min_edge_cover(G)
        assert nx.is_edge_cover(G, min_cover)
        # Fixed: Should be 4 edges, not 8 (was counting both directions)
        assert len(min_cover) == 4

    def test_bipartite_explicit(self):
        G = nx.Graph()
        G.add_nodes_from([1, 2, 3, 4], bipartite=0)
        G.add_nodes_from(["a", "b", "c"], bipartite=1)
        G.add_edges_from([(1, "a"), (1, "b"), (2, "b"), (2, "c"), (3, "c"), (4, "a")])
        min_cover = bipartite.min_edge_cover(G, bipartite.eppstein_matching)
        assert nx.is_edge_cover(G, min_cover)
        # Fixed: Should be 4 edges, not 8 (was counting both directions)
        assert len(min_cover) == 4
