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
from networkx.testing import assert_edges_equal
import math
import pytest


class TestIntervalGraph:
    """Unit tests for :func:`networkx.generators.interval_graph.interval_graph`"""

    def test_none(self):
        """ Tests for trivial case that a parameter is None or empty"""
        intervals = None
        assert nx.interval_graph(intervals) is None
        intervals = []
        assert nx.interval_graph(intervals) is None

    def test_interval_graph_check_invalid(self):
        """ Tests for conditions that raise Exceptions """

        invalids_having_none = [None, (1, 2)]
        with pytest.raises(TypeError):
            nx.interval_graph(invalids_having_none)

        invalids_having_set = [{1, 2}]
        with pytest.raises(TypeError):
            nx.interval_graph(invalids_having_set)

        invalids_having_seq_but_not_length2 = [(1, 2, 3)]
        with pytest.raises(TypeError):
            nx.interval_graph(invalids_having_seq_but_not_length2)

        invalids_interval = [[3, 2]]
        with pytest.raises(ValueError):
            nx.interval_graph(invalids_interval)

    def test_interval_graph_0(self):
        intervals = [(1, 2), (1, 3)]

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from(intervals)
        e = ((1, 2), (1, 3))
        expected_graph.add_edge(*e)
        actual_g = nx.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)

    def test_interval_graph_1(self):
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

        actual_g = nx.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)

    def test_interval_graph_2(self):
        intervals = [(1, 2), [3, 5], [6, 8], (9, 10)]

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from([(1, 2), (3, 5), (6, 8), (9, 10)])

        actual_g = nx.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)

    def test_interval_graph_3(self):
        intervals = [(1, 4), [3, 5], [2.5, 4]]

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from([(1, 4), (3, 5), (2.5, 4)])
        e1 = ((1, 4), (3, 5))
        e2 = ((1, 4), (2.5, 4))
        e3 = ((3, 5), (2.5, 4))

        expected_graph.add_edge(*e1)
        expected_graph.add_edge(*e2)
        expected_graph.add_edge(*e3)

        actual_g = nx.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)

    def test_interval_graph_4(self):
        """ this test is to see that an interval supports infinite number"""
        intervals = {(-math.inf, 0), (-1, -1), (1, 1), (1, math.inf)}

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from(intervals)
        e1 = ((-math.inf, 0), (-1, -1))
        e2 = ((1, 1), (1, math.inf))

        expected_graph.add_edge(*e1)
        expected_graph.add_edge(*e2)
        actual_g = nx.interval_graph(intervals)

        assert set(actual_g.nodes) == set(expected_graph.nodes)
        assert_edges_equal(expected_graph, actual_g)
