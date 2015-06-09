# test_dominating_set.py - unit tests for the dominating_set module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.approximation.dominating_set`
module.

"""
from nose.tools import ok_
from nose.tools import eq_

import networkx as nx
from networkx.algorithms.approximation import min_weighted_dominating_set
from networkx.algorithms.approximation import min_edge_dominating_set


class TestMinWeightDominatingSet:

    def test_min_weighted_dominating_set(self):
        graph = nx.Graph()
        graph.add_edge(1, 2)
        graph.add_edge(1, 5)
        graph.add_edge(2, 3)
        graph.add_edge(2, 5)
        graph.add_edge(3, 4)
        graph.add_edge(3, 6)
        graph.add_edge(5, 6)

        vertices = set([1, 2, 3, 4, 5, 6])
        # due to ties, this might be hard to test tight bounds
        dom_set = min_weighted_dominating_set(graph)
        for vertex in vertices - dom_set:
            neighbors = set(graph.neighbors(vertex))
            ok_(len(neighbors & dom_set) > 0, "Non dominating set found!")

    def test_postprocessing(self):
        """Tests for the additional postprocessing heuristic.

        For more information, see issue #1572.

        """
        # The graph looks like this:
        #
        #       *   *
        #      / \  |
        #     0-*-2-3
        #      \ /  |
        #       *   *
        #
        G = nx.path_graph(4)
        G.add_edges_from([(0, 4), (0, 5), (2, 4), (2, 5), (3, 6), (3, 7)])
        eq_(min_weighted_dominating_set(G, _postprocessing=True), {0, 3})
        eq_(min_weighted_dominating_set(G, _postprocessing=False), {0, 2, 3})
        # The graph now looks like this:
        #
        #     *   * *
        #    / \ /|/
        # *-1-*-3-4-*
        #  / \ / \|\
        # *   *   * *
        #
        G = nx.path_graph(6)
        G.add_edges_from([(0, 3), (1, 6), (1, 8), (1, 11), (3, 6), (3, 7),
                          (3, 10), (4, 7), (4, 9), (4, 10), (4, 12)])
        eq_(min_weighted_dominating_set(G, _postprocessing=True), {1, 4})
        eq_(min_weighted_dominating_set(G, _postprocessing=False), {1, 3, 4})

    def test_star_graph(self):
        """Tests that an approximate dominating set for the star graph,
        even when the center node does not have the smallest integer
        label, gives just the center node.

        For more information, see #1527.

        """
        # Create a star graph in which the center node has the highest
        # label instead of the lowest.
        G = nx.star_graph(10)
        G = nx.relabel_nodes(G, {0: 9, 9: 0})
        eq_(min_weighted_dominating_set(G), {9})

    def test_min_edge_dominating_set(self):
        graph = nx.path_graph(5)
        dom_set = min_edge_dominating_set(graph)

        # this is a crappy way to test, but good enough for now.
        for edge in graph.edges():
            if edge in dom_set:
                continue
            else:
                u, v = edge
                found = False
                for dom_edge in dom_set:
                    found |= u == dom_edge[0] or u == dom_edge[1]
                ok_(found, "Non adjacent edge found!")

        graph = nx.complete_graph(10)
        dom_set = min_edge_dominating_set(graph)

        # this is a crappy way to test, but good enough for now.
        for edge in graph.edges():
            if edge in dom_set:
                continue
            else:
                u, v = edge
                found = False
                for dom_edge in dom_set:
                    found |= u == dom_edge[0] or u == dom_edge[1]
                ok_(found, "Non adjacent edge found!")
