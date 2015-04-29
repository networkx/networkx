# test_minors.py - unit tests for the minors module
#
# Copyright 2015 Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.minors` module."""
from nose.tools import assert_equal
from nose.tools import assert_true
from nose.tools import raises

import networkx as nx


class TestQuotient(object):
    """Unit tests for computing quotient graphs."""

    def test_quotient_graph_complete_multipartite(self):
        """Tests that the quotient graph of the complete *n*-partite graph
        under the "same neighbors" node relation is the complete graph on *n*
        nodes.

        """
        G = nx.complete_multipartite_graph(2, 3, 4)
        # Two nodes are equivalent if they are not adjacent but have the same
        # neighbor set.
        same_neighbors = lambda u, v: (u not in G[v] and v not in G[u]
                                       and G[u] == G[v])
        expected = nx.complete_graph(3)
        actual = nx.quotient_graph(G, same_neighbors)
        # It won't take too long to run a graph isomorphism algorithm on such
        # small graphs.
        assert_true(nx.is_isomorphic(expected, actual))

    def test_quotient_graph_complete_bipartite(self):
        """Tests that the quotient graph of the complete bipartite graph under
        the "same neighbors" node relation is `K_2`.

        """
        G = nx.complete_bipartite_graph(2, 3)
        # Two nodes are equivalent if they are not adjacent but have the same
        # neighbor set.
        same_neighbors = lambda u, v: (u not in G[v] and v not in G[u]
                                       and G[u] == G[v])
        expected = nx.complete_graph(2)
        actual = nx.quotient_graph(G, same_neighbors)
        # It won't take too long to run a graph isomorphism algorithm on such
        # small graphs.
        assert_true(nx.is_isomorphic(expected, actual))

    def test_quotient_graph_edge_relation(self):
        """Tests for specifying an alternate edge relation for the quotient
        graph.

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

    def test_condensation_as_quotient(self):
        """This tests that the condensation of a graph can be viewed as the
        quotient graph under the "in the same connected component" equivalence
        relation.

        """
        # This example graph comes from the file `test_strongly_connected.py`.
        G = nx.DiGraph()
        G.add_edges_from([(1, 2), (2, 3), (2, 11), (2, 12), (3, 4), (4, 3),
                          (4, 5), (5, 6), (6, 5), (6, 7), (7, 8), (7, 9),
                          (7, 10), (8, 9), (9, 7), (10, 6), (11, 2), (11, 4),
                          (11, 6), (12, 6), (12, 11)])
        scc = list(nx.strongly_connected_components(G))
        C = nx.condensation(G, scc)
        component_of = C.graph['mapping']
        # Two nodes are equivalent if they are in the same connected component.
        same_component = lambda u, v: component_of[u] == component_of[v]
        Q = nx.quotient_graph(G, same_component)
        assert_true(nx.is_isomorphic(C, Q))


class TestContraction(object):
    """Unit tests for node and edge contraction functions."""

    def test_undirected_node_contraction(self):
        """Tests for node contraction in an undirected graph."""
        G = nx.cycle_graph(4)
        actual = nx.contracted_nodes(G, 0, 1)
        expected = nx.complete_graph(3)
        expected.add_edge(0, 0)
        assert_true(nx.is_isomorphic(actual, expected))

    def test_directed_node_contraction(self):
        """Tests for node contraction in a directed graph."""
        G = nx.DiGraph(nx.cycle_graph(4))
        actual = nx.contracted_nodes(G, 0, 1)
        expected = nx.DiGraph(nx.complete_graph(3))
        expected.add_edge(0, 0)
        expected.add_edge(0, 0)
        assert_true(nx.is_isomorphic(actual, expected))

    def test_node_attributes(self):
        """Tests that node contraction preserves node attributes."""
        G = nx.cycle_graph(4)
        # Add some data to the two nodes being contracted.
        G.node[0] = dict(foo='bar')
        G.node[1] = dict(baz='xyzzy')
        actual = nx.contracted_nodes(G, 0, 1)
        # We expect that contracting the nodes 0 and 1 in C_4 yields K_3, but
        # with nodes labeled 0, 2, and 3, and with a self-loop on 0.
        expected = nx.complete_graph(3)
        expected = nx.relabel_nodes(expected, {1: 2, 2: 3})
        expected.add_edge(0, 0)
        expected.node[0] = dict(foo='bar', contraction={1: dict(baz='xyzzy')})
        assert_true(nx.is_isomorphic(actual, expected))
        assert_equal(actual.node, expected.node)

    def test_without_self_loops(self):
        """Tests for node contraction without preserving self-loops."""
        G = nx.cycle_graph(4)
        actual = nx.contracted_nodes(G, 0, 1, self_loops=False)
        expected = nx.complete_graph(3)
        assert_true(nx.is_isomorphic(actual, expected))

    def test_undirected_edge_contraction(self):
        """Tests for edge contraction in an undirected graph."""
        G = nx.cycle_graph(4)
        actual = nx.contracted_edge(G, (0, 1))
        expected = nx.complete_graph(3)
        expected.add_edge(0, 0)
        assert_true(nx.is_isomorphic(actual, expected))

    @raises(ValueError)
    def test_nonexistent_edge(self):
        """Tests that attempting to contract a non-existent edge raises an
        exception.

        """
        G = nx.cycle_graph(4)
        nx.contracted_edge(G, (0, 2))
