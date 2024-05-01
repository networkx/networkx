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

    if isinstance(G, nx.MultiGraph):
        edges = G.edges(keys=True)
    else:
        edges = G.edges()

    for edge in edges:
        if isinstance(G, nx.MultiGraph):
            u, v, key = edge
            e1 = (u, v, key)
            e2 = (v, u, key)
        else:
            u, v = edge
            e1 = (u, v)
            e2 = (v, u)

        if e1 not in coloring:
            return False
        if e2 not in coloring:
            return False
        if coloring[e1] != coloring[e2]:
            return False
        else:
            color = coloring[e1]

        print(color)
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
        coloring = edge_coloring(G, strategy=strategy)

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
        coloring = edge_coloring(G, strategy=strategy)

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
        coloring = edge_coloring(G, strategy=strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_disconnected_graph(self, strategy):
        edges = [(1, 2), (1, 3), (3, 4), (3, 5), (5, 6), (7, 9), (8, 9)]
        G = nx.Graph()
        G.add_edges_from(edges)
        top_nodes = {1, 4, 5, 9}
        coloring = edge_coloring(G, top_nodes, strategy=strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complete_graph_1(self, strategy):
        G = nx.complete_bipartite_graph(4, 6)
        coloring = edge_coloring(G, strategy=strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_complete_balanced_graph(self, strategy):
        G = nx.complete_bipartite_graph(5, 5)
        coloring = edge_coloring(G, strategy=strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_disconnected_exception(self, strategy):
        edges = [(1, 2), (1, 3), (3, 4), (3, 5), (5, 6), (7, 9), (8, 9)]
        G = nx.Graph()
        G.add_edges_from(edges)

        # asserts that when edge_coloring() is called without top_nodes an error is raised
        if strategy == "iterated-matching":
            with pytest.raises(nx.AmbiguousSolution):
                coloring = edge_coloring(G, top_nodes=None, strategy=strategy)
        else:
            coloring = edge_coloring(G, strategy=strategy)
            # Check that no node has two edges with the same color
            assert _is_proper_edge_coloring(G, coloring)

            # Checking if the coloring is minimal
            # Check that the number of colors used is equal to the maximum degree
            max_degree = max(G.degree(), key=lambda x: x[1])[1]
            used_colors = set(coloring.values())
            assert len(used_colors) == max_degree

    def test_digraphs(self, strategy):
        edges = [(1, 2), (3, 4), (5, 6)]
        G = nx.DiGraph()
        G.add_edges_from(edges)

        # asserts `not_implemeted` error
        with pytest.raises(nx.exception.NetworkXNotImplemented):
            coloring = edge_coloring(G, strategy=strategy)


@pytest.mark.parametrize("strategy", ["iterated-matching", "kempe_chain"])
class TestEdgeColoringMultiGraphs:
    """Tests for bipartite edge coloring algorithms"""

    def test_complete_graph(self, strategy):
        # Create a simple bipartite graph
        G = nx.MultiGraph()
        G.add_edges_from(
            [(1, 4), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5), (3, 5)]
        )
        coloring = edge_coloring(G, strategy=strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_cube_graph(self, strategy):
        # Create a simple bipartite graph
        G = nx.MultiGraph()
        G.add_edges_from(
            [
                (1, 2),
                (1, 2),
                (1, 2),
                (1, 4),
                (1, 4),
                (1, 4),
                (1, 5),
                (1, 5),
                (1, 5),
                (2, 3),
                (2, 3),
                (2, 3),
                (2, 6),
                (2, 6),
                (2, 6),
                (3, 4),
                (3, 4),
                (3, 4),
                (3, 7),
                (3, 7),
                (3, 7),
                (4, 8),
                (4, 8),
                (4, 8),
                (5, 6),
                (5, 6),
                (5, 6),
                (5, 8),
                (5, 8),
                (5, 8),
                (6, 7),
                (6, 7),
                (6, 7),
                (7, 8),
                (7, 8),
                (7, 8),
            ]
        )
        coloring = edge_coloring(G, strategy=strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_disconnected(self, strategy):
        # Create a simple bipartite multigraph
        G = nx.MultiGraph()
        G.add_edges_from(
            [
                (1, 4),
                (1, 4),
                (1, 5),
                (2, 3),
                (2, 3),
                (2, 3),
                (6, 7),
                (6, 7),
            ]
        )

        top_nodes = [1, 2, 6]
        coloring = edge_coloring(G, top_nodes, strategy=strategy)

        # Check that no node has two edges with the same color
        assert _is_proper_edge_coloring(G, coloring)

        # Checking if the coloring is minimal
        # Check that the number of colors used is equal to the maximum degree
        max_degree = max(G.degree(), key=lambda x: x[1])[1]
        used_colors = set(coloring.values())
        assert len(used_colors) == max_degree

    def test_disconnected_error(self, strategy):
        # Create a simple bipartite disconnected multigraph
        G = nx.MultiGraph()
        G.add_edges_from([(1, 2), (1, 2), (1, 2), (3, 1), (1, 3), (4, 5), (4, 5)])

        # asserts that when edge_coloring() is called without top_nodes an error is raised
        if strategy == "iterated-matching":
            with pytest.raises(nx.AmbiguousSolution):
                coloring = edge_coloring(G, strategy=strategy)
        else:
            coloring = edge_coloring(G, strategy=strategy)
            # Check that no node has two edges with the same color
            assert _is_proper_edge_coloring(G, coloring)
