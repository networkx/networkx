"""Unit tests for the :mod:`networkx.algorithms.coloring.edge_coloring` module."""

from collections import defaultdict

import pytest

import networkx as nx
from networkx.algorithms.coloring.edge_colorings import edge_coloring


def _is_proper_edge_coloring(G, coloring):
    """Checks through each node and saves the colors at each node to find out
    if there is any conflict
    """
    try:
        node_colors = defaultdict(set)

        # iterate through each edge in the graph
        for u, v in G.edges():
            assert (u, v) in coloring, f"Edge {(u, v)} not in coloring."
            assert (v, u) in coloring, f"Edge {(v, u)} not in coloring."
            assert (
                coloring[(u, v)] == coloring[(v, u)]
            ), f"Colors of {(u, v)} and {(v, u)} do not match."

            color = coloring[(u, v)]

            assert (
                color not in node_colors[u]
            ), f"Color {color} already used at node {u}."
            assert (
                color not in node_colors[v]
            ), f"Color {color} already used at node {v}."

            # add the edge color to the dictionary at each node
            node_colors[u].add(color)
            node_colors[v].add(color)

        # Calculate the maximum degree of the graph
        max_degree = max(G.degree(), key=lambda x: x[1])[1]

        # Calculate the number of used colors
        used_colors = set(coloring.values())

        # Verify that the number of used colors is at most (maximum degree + 1)
        assert (
            len(used_colors) <= (max_degree + 1)
        ), f"Number of used colors ({len(used_colors)}) exceeds (maximum degree + 1) ({max_degree + 1})."

        return True
    except AssertionError as e:
        print(e)
        return False


class TestEdgeColoring:
    """Tests for edge coloring algorithm"""

    def test_complete_graph(self):
        G = nx.complete_graph(13)
        coloring = edge_coloring(G)

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

    def test_odd_graph(self):
        n = 3
        G = nx.kneser_graph(2 * n - 1, n - 1)
        coloring = edge_coloring(G)

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

    def test_13(self):
        # Create a graph
        G = nx.Graph()

        edge_list = [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 12),
            (1, 2),
            (1, 3),
            (1, 11),
            (1, 5),
            (2, 3),
            (2, 4),
            (2, 5),
            (3, 4),
            (3, 5),
            (4, 5),
            (6, 7),
            (3, 8),
            (6, 9),
            (6, 10),
            (6, 11),
            (6, 12),
            (7, 8),
            (7, 9),
            (7, 10),
            (7, 11),
            (7, 12),
            (8, 9),
            (8, 10),
            (5, 11),
            (8, 12),
            (2, 10),
            (9, 11),
            (9, 12),
            (10, 11),
            (10, 12),
            (11, 12),
        ]

        G.add_edges_from(edge_list)

        coloring = edge_coloring(G)

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

    def test_disconnected_graph(self):
        # Create a graph
        G = nx.Graph()

        edge_list = [(0, 1), (0, 2), (0, 3), (1, 2), (4, 5), (4, 6), (6, 7)]

        G.add_edges_from(edge_list)

        coloring = edge_coloring(G)

        # Check that no vertex has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)
