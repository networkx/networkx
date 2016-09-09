# test_efficiency.py - unit tests for the efficiency module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.efficiency` module."""
from __future__ import division
from unittest import TestCase

from nose.tools import assert_equal

import networkx as nx


def test_efficiency():
    G = nx.cycle_graph(4)
    assert_equal(nx.efficiency(G, 0, 1), 1)
    assert_equal(nx.efficiency(G, 0, 2), 1 / 2)


def test_global_efficiency():
    G = nx.cycle_graph(4)
    assert_equal(nx.global_efficiency(G), 5 / 6)


def test_complete_graph_global_efficiency():
    """Tests that the average global efficiency of the complete graph is
    one.

    """
    for n in range(10):
        G = nx.complete_graph(5)
        assert_equal(nx.global_efficiency(G), 1)


class TestLocalEfficiency(TestCase):
    """Unit tests for the local efficiency function."""

    def test_complete_graph(self):
        G = nx.complete_graph(4)
        assert_equal(nx.local_efficiency(G), 1)

    def test_using_ego_graph(self):
        """Test that the ego graph is used when computing local efficiency.

        For more information, see GitHub issue #2233.

        """
        # This is the triangle graph with one additional edge.
        G = nx.lollipop_graph(3, 1)
        assert_equal(nx.local_efficiency(G), 23 / 24)
