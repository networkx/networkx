# test_minors.py - unit tests for the minors module
#
# Copyright 2015 Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.minors` module."""
from nose.tools import assert_true

import networkx as nx


# # This test requires merging pull request #1425.
# def test_quotient_graph_complete_multipartite():
#     """Tests that the quotient graph of the complete *n*-partite graph under
#     the "same neighbors" node relation is the complete graph on *n* nodes.

#     """
#     G = nx.complete_multipartite_graph(2, 3, 4)
#     # Two nodes are equivalent if they are not adjacent but have the same
#     # neighbor set.
#     same_neighbors = lambda u, v: (u not in G[v] and v not in G[u]
#                                    and G[u] == G[v])
#     expected = nx.complete_graph(3)
#     actual = nx.quotient_graph(G, same_neighbors)
#     # It won't take too long to run a graph isomorphism algorithm on such small
#     # graphs.
#     assert_true(nx.is_isomorphic(expected, actual))


def test_quotient_graph_complete_bipartite():
    """Tests that the quotient graph of the complete bipartite graph under the
    "same neighbors" node relation is `K_2`.

    """
    G = nx.complete_bipartite_graph(2, 3)
    # Two nodes are equivalent if they are not adjacent but have the same
    # neighbor set.
    same_neighbors = lambda u, v: (u not in G[v] and v not in G[u]
                                   and G[u] == G[v])
    expected = nx.complete_graph(2)
    actual = nx.quotient_graph(G, same_neighbors)
    # It won't take too long to run a graph isomorphism algorithm on such small
    # graphs.
    assert_true(nx.is_isomorphic(expected, actual))


def test_quotient_graph_edge_relation():
    """Tests for specifying an alternate edge relation for the quotient graph.

    """
    G = nx.path_graph(5)
    identity = lambda u, v: u == v
    peek = lambda x: next(iter(x))
    same_parity = lambda b, c: peek(b) % 2 == peek(c) % 2
    actual = nx.quotient_graph(G, identity, same_parity)
    expected = nx.Graph()
    expected.add_edges_from([(0, 2), (0, 4), (2, 4)])
    expected.add_edge(1, 3)
    assert_true(nx.is_isomorphic(actual, expected))


def test_condensation_as_quotient():
    """This tests that the condensation of a graph can be viewed as the
    quotient graph under the "in the same connected component" equivalence
    relation.

    """
    # This example graph comes from the file `test_strongly_connected.py`.
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (2, 3), (2, 11), (2, 12), (3, 4), (4, 3), (4, 5),
                      (5, 6), (6, 5), (6, 7), (7, 8), (7, 9), (7, 10), (8, 9),
                      (9, 7), (10, 6), (11, 2), (11, 4), (11, 6), (12, 6),
                      (12, 11)])
    scc = list(nx.strongly_connected_components(G))
    C = nx.condensation(G, scc)
    component_of = C.graph['mapping']
    # Two vertices are equivalent if they are in the same connected component.
    same_component = lambda u, v: component_of[u] == component_of[v]
    Q = nx.quotient_graph(G, same_component)
    assert_true(nx.is_isomorphic(C, Q))
