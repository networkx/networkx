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

    def test_complete_graph(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(2, 3)
        coloring = bipartite_edge_coloring(G, strategy="iterated-matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_cube_graph(self):
        # Create a cube graph
        edge_list = [
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 1),
            (6, 7),
            (7, 8),
            (8, 5),
            (5, 6),
            (1, 6),
            (2, 7),
            (3, 8),
            (4, 5),
        ]
        G = nx.Graph()
        G.add_edges_from(edge_list)
        coloring = bipartite_edge_coloring(G, strategy="iterated-matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_even_cycle(self):
        # Create a an even cycle graph
        edge_list = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)]
        G = nx.Graph()
        G.add_edges_from(edge_list)
        coloring = bipartite_edge_coloring(G, strategy="iterated-matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    # def test_odd_cycle(self):

    def test_disconnected_graph_iterated_matching(self):
        edges = [(1, 2), (2, 3), (3, 4), (4, 1)]
        G = nx.Graph()
        G.add_edges_from(edges)
        top_nodes = [1, 3]
        coloring = bipartite_edge_coloring(G, top_nodes, strategy="iterated-matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complete_graph(self):
        G = nx.complete_bipartite_graph(4, 6)
        coloring = bipartite_edge_coloring(G, strategy="iterated-matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complete_balanced_graph(self):
        G = nx.complete_bipartite_graph(5, 5)
        coloring = bipartite_edge_coloring(G, strategy="iterated-matching")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree


class TestEdgeColoring_KempeChain:
    """Tests for bipartite Kempe Chain edge coloring algorithm"""

    def test_complete_graph(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(2, 3)
        coloring = bipartite_edge_coloring(G, strategy="kempe-chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_cube_graph(self):
        # Create a cube graph
        edge_list = [
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 1),
            (6, 7),
            (7, 8),
            (8, 5),
            (5, 6),
            (1, 6),
            (2, 7),
            (3, 8),
            (4, 5),
        ]
        G = nx.Graph()
        G.add_edges_from(edge_list)
        coloring = bipartite_edge_coloring(G, strategy="kempe-chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_even_cycle(self):
        # Create a an even cycle graph
        edge_list = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)]
        G = nx.Graph()
        G.add_edges_from(edge_list)
        coloring = bipartite_edge_coloring(G, strategy="kempe-chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    # def test_odd_cycle(self):

    def test_disconnected_graph_iterated_matching(self):
        edges = [(1, 2), (2, 3), (3, 4), (4, 1)]
        G = nx.Graph()
        G.add_edges_from(edges)
        top_nodes = [1, 3]
        coloring = bipartite_edge_coloring(G, top_nodes, strategy="kempe-chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complete_graph(self):
        G = nx.complete_bipartite_graph(4, 6)
        coloring = bipartite_edge_coloring(G, strategy="kempe-chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complete_balanced_graph(self):
        G = nx.complete_bipartite_graph(5, 5)
        coloring = bipartite_edge_coloring(G, strategy="kempe-chain")

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree
