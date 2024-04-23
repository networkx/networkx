"""Unit tests for the :mod:`networkx.algorithms.bipartite.edge_coloring` module."""
from collections import defaultdict

import pytest

import networkx as nx
from networkx.algorithms.bipartite.edge_colorings import edge_coloring


def _is_proper_edge_coloring(G, coloring):
    """Checks through each node and saves the colors at each node to find out
    if there is any conflict
    """
    node_colors = defaultdict(set)

    # iterate through each edge in the graph
    for u, v in G.edges():
        if (u, v) not in coloring:
            return False
        if (v, u) not in coloring:
            return False
        if coloring[(u, v)] != coloring[(v, u)]:
            return False
        else:
            color = coloring[(u, v)]

        if color in node_colors[u] or color in node_colors[v]:
            return False

        # add the edge color to the dictionary at each node
        node_colors[u].add(color)
        node_colors[v].add(color)

    return True


@pytest.mark.parametrize("strategy", ["iterated-matching", "kempe_chain"])
class TestEdgeColoring:
    """Tests for bipartite edge coloring algorithms"""

    def test_complete_graph(self, strategy):
        # Create a simple bipartite graph
        G = nx.complete_bipartite_graph(2, 3)
        coloring = edge_coloring(G, strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_cube_graph(self, strategy):
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
        coloring = edge_coloring(G, strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_even_cycle(self, strategy):
        # Create a an even cycle graph
        edge_list = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)]
        G = nx.Graph()
        G.add_edges_from(edge_list)
        coloring = edge_coloring(G, strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    # def test_odd_cycle(self, strategy):

    def test_disconnected_graph(self, strategy):
        edges = [(1, 2), (1, 3), (3, 4), (3, 5), (5, 6), (7, 9), (8, 9)]
        G = nx.Graph()
        G.add_edges_from(edges)
        top_nodes = {1, 4, 5, 9}
        coloring = edge_coloring(G, top_nodes, strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complete_graph_1(self, strategy):
        G = nx.complete_bipartite_graph(4, 6)
        coloring = edge_coloring(G, strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complete_balanced_graph(self, strategy):
        G = nx.complete_bipartite_graph(5, 5)
        coloring = edge_coloring(G, strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree
