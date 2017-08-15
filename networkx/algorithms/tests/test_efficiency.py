# test_efficiency.py - unit tests for the efficiency module
#
# Copyright 2017 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
# Unit tests for the :mod:`networkx.algorithms.efficiency` module.

from __future__ import division
from unittest import TestCase
from nose.tools import assert_equal
import networkx as nx


class TestEfficiency:

    def __init__(self):
        # G1 is a toy graph
        self.G1 = nx.barbell_graph(10, 3)
        # G2 is a disconnected graph
        self.G2 = nx.Graph()
        self.G2.add_nodes_from([1, 2, 3])
        # G3 is a cycle graph
        self.G3 = nx.cycle_graph(4)
        # G4 is a complete graph
        self.G4 = nx.complete_graph(5)
        # G5 is the triangle graph with one additional edge
        self.G4 = nx.lollipop_graph(3, 1)

    def test_efficiency(self):
        """
        Returns efficiency of two nodes
        """
        return nx.efficiency(self.G1, 1, 10)

    def test_efficiency_disconnected_nodes(self):
        """
        Returns 0 when nodes are disconnected
        """
        return nx.efficiency(self.G2, 1, 2)

    def test_local_efficiency(self):
        """
        Test local efficiency
        """
        return nx.local_efficiency(self.G1)

    def test_local_efficiency_disconnected_graph(self):
        """
        In a disconnected graph the efficiency is 0
        """
        return nx.local_efficiency(self.G2)

    def test_global_efficiency(self):
        """
        Test global efficiency
        """
        return nx.global_efficiency(self.G1)

    def test_efficiency_cycle_graph(self):
        assert_equal(nx.efficiency(self.G3, 0, 1), 1)
        assert_equal(nx.efficiency(self.G3, 0, 2), 1 / 2)

    def test_global_efficiency_cycle_graph(self):
        assert_equal(nx.global_efficiency(self.G3), 5 / 6)

    def test_global_efficiency_complete_graph(self):
        """
        Tests that the average global efficiency of the complete graph is one.
        """
        assert_equal(nx.global_efficiency(self.G4), 1)

    def test_using_ego_graph(self):
        """
        Test that the ego graph is used when computing local efficiency.
        For more information, see GitHub issue #2233.
        """
        assert_equal(nx.local_efficiency(self.G5), 23 / 24)
