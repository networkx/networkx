"""Unit tests for the :mod:`networkx.algorithms.bipartite.edge_coloring` module."""
import pytest

import networkx as nx
from networkx.algorithms.bipartite.edge_coloring import bipartite_edge_coloring


def _is_proper_edge_coloring(coloring):
    """
    Checks through each vertex and saves the colors at each vertex to find out
    if there is any conflict
    """
    vertex_colors = {}  # Dictionary to track colors of incident edges for each vertex

    for edge, color in coloring.items():
        u, v = edge  # Assuming the edges are represented as pairs (u, v)

        if u not in vertex_colors:
            vertex_colors[u] = set()

        if color in vertex_colors[u]:
            return False

        vertex_colors[u].add(color)

    return True


class TestEdgeColoring_IteratedMatching:
    """Tests for bipartite iterated matching edge coloring algorithm"""

    def test_1_iterated_matching(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(2, 3)
        coloring = bipartite_edge_coloring(G, strategy="iterated_matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_2_iterated_matching(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(10, 20)
        coloring = bipartite_edge_coloring(G, strategy="iterated_matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_3_iterated_matching(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(40, 200)
        coloring = bipartite_edge_coloring(G, strategy="iterated_matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_disconnected_graph_iterated_matching(self):
        edges = [(1, 2), (2, 3), (3, 4), (4, 1)]
        G = nx.Graph()
        G.add_edges_from(edges)
        top_nodes = [1, 3]
        coloring = bipartite_edge_coloring(G, top_nodes, strategy="iterated_matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree


class TestEdgeColoring_KempeChain:
    def test_1_kempe_chain(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(2, 3)
        coloring = bipartite_edge_coloring(G, strategy="kempe_chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_2_kempe_chain(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(2, 3)
        coloring = bipartite_edge_coloring(G, strategy="kempe_chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_3_kempe_chain(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(2, 3)
        coloring = bipartite_edge_coloring(G, strategy="kempe_chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_disconnected_graph_kempe_chain(self):
        edges = [(1, 2), (2, 3), (3, 4), (4, 1)]
        G = nx.Graph()
        G.add_edges_from(edges)
        top_nodes = [1, 3]
        coloring = bipartite_edge_coloring(G, top_nodes, strategy="iterated_matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree
