"""Unit tests for the broadcasting module."""
import math

import networkx as nx
import networkx.algorithms.approximation as nx_app


def test_example_tree_broadcast():
    """
    Test the BROADCAST algorithm on the example in the paper titled: "Information Dissemination in Trees"
    """
    edge_list = [
        (0, 1),
        (1, 2),
        (2, 7),
        (3, 4),
        (5, 4),
        (4, 7),
        (6, 7),
        (7, 9),
        (8, 9),
        (9, 13),
        (13, 14),
        (14, 15),
        (14, 16),
        (14, 17),
        (13, 11),
        (11, 10),
        (11, 12),
        (13, 18),
        (18, 19),
        (18, 20),
    ]
    G = nx.Graph(edge_list)
    assert nx_app.tree_broadcast_center(G) == 6


def test_path_broadcast():
    for i in range(2, 12):
        G = nx.path_graph(i)
        assert nx_app.tree_broadcast_center(G) == math.ceil(i / 2)

    # test base case when the graph has only one node
    H = nx.empty_graph(1)
    assert nx_app.tree_broadcast_center(H) == 0


def test_star_broadcast():
    for i in range(4, 12):
        G = nx.star_graph(i)
        assert nx_app.tree_broadcast_center(G) == i
