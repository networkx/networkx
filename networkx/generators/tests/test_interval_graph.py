# -*- encoding: utf-8 -*-
# test_interval_graph.py - unit tests for interval_graph generators
#
# Copyright 2010-2019 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.generators.interval_graph` module.

"""

import networkx as nx
import networkx.generators.interval_graph as interval

from networkx.testing import assert_edges_equal

import math


class TestIntervalGraph:
    """Unit tests for :func:`networkx.generators.interval_graph.interval_graph`"""

    def test_none(self):
        """ Tests for trival case that a parameter is None or empty"""
        intervals = None
        assert interval.interval_graph(intervals) is None
        intervals = []
        assert interval.interval_graph(intervals) is None

    def test_interval_graph_check_invalid(self):
        """ Tests for conditions that invalidate an interval """
        invalids = [1, (1, 3, 2), {1, 2}, [1, 2], None]

        graph_with_no_vertices = interval.interval_graph(invalids)

        assert len(graph_with_no_vertices.nodes) == 0 and \
            len(graph_with_no_vertices.edges) == 0

    def test_interval_graph_0(self):
        intervals = [(1, 2), (1, 3)]

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from(intervals)
        e = ((1, 2), (1, 3))
        expected_graph.add_edge(*e)
        actual_g = interval.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)

    def test_interval_graph_1(self):
        intervals = [(1, 2), (2, 3), (3, 0)]
        # last one is valid but it is actually empty interval.
        # Hence its degree must be zero.

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from(intervals)
        e = ((1, 2), (2, 3))

        expected_graph.add_edge(*e)
        actual_g = interval.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)

    def test_interval_graph_2(self):
        intervals = [(1, 2), (2, 3), (3, 4), (1, 4)]

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from(intervals)
        e1 = ((1, 4), (1, 2))
        e2 = ((1, 4), (2, 3))
        e3 = ((1, 4), (3, 4))
        e4 = ((3, 4), (2, 3))
        e5 = ((1, 2), (2, 3))

        expected_graph.add_edge(*e1)
        expected_graph.add_edge(*e2)
        expected_graph.add_edge(*e3)
        expected_graph.add_edge(*e4)
        expected_graph.add_edge(*e5)

        actual_g = interval.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)

    def test_interval_graph_3(self):
        intervals = [(1, 2), (3, 5), (5.5, 7)]

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from(intervals)

        actual_g = interval.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)

    def test_interval_graph_4(self):
        """ this test is to see that an interval supports infinite number"""
        intervals = {(-math.inf, 0), (-1,-1), (1,1), (1, math.inf)}

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from(intervals)
        e1 = ((-math.inf, 0), (-1, -1))
        e2 = ((1, 1), (1, math.inf))

        expected_graph.add_edge(*e1)
        expected_graph.add_edge(*e2)
        actual_g = interval.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)
