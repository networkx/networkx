# -*- encoding: utf-8 -*-
# test_wheel_graph.py - unit tests for wheel_graph generators
#
# Copyright 2010-2019 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.generators.wheel_graph` module.
"""
import networkx as nx
import networkx.generators.wheel_graph as wheel_graph

import pytest


class TestWheelGraph:
    """Unit tests for :func:`networkx.generators.wheel_graph.wheel_graph`"""

    def test_wheel_graph_invalid(self):
        """ Tests for conditions that raise Exceptions """

        with pytest.raises(ValueError):
            wheel_graph(0)

        with pytest.raises(ValueError):
            wheel_graph(-2)

        with pytest.raises(ValueError):
            wheel_graph(1.5)

    def test_wheel_graph_0(self):
        n = 4

        expected_graph = nx.Graph()
        expected_graph.add_nodes_from([1, 2, 3, 4])
        expected_graph.add_edges_from([(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (2, 4)])
        w_graph = wheel_graph(n)

        assert set(w_graph.nodes) == set(expected_graph.nodes)
        assert set(w_graph.edges) == set(expected_graph.edges)

    def test_wheel_graph_1(self):
        n = 10

        w_graph = wheel_graph(n)

        assert len(w_graph.nodes) == 10
        assert len(w_graph.edges) == 18

        assert w_graph.degree[1] == 9
        for i in range(2, n + 1):
            assert w_graph.degree[i] == 3
