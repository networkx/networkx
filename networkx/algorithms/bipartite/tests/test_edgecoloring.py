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
            print(vertex_colors[u])
            print(vertex_colors[v])
            print(u, v, color)
            return False

        vertex_colors[u].add(color)

    return True


class TestEdgeColoring:
    """Tests for bipartite edge coloring algorithms"""

    def test_simple_edge_coloring(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(2, 3)
        coloring = bipartite_edge_coloring(G)

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complex_edge_coloring(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(10, 20)
        coloring = bipartite_edge_coloring(G)

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_another_edge_coloring(self):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(40, 200)
        coloring = bipartite_edge_coloring(G)

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(coloring)

        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    # need to write for disconnected case
