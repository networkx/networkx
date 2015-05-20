# test_structuralholes.py - unit tests for the structuralholes module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.structuralholes` module."""
from nose.tools import assert_almost_equal

import networkx as nx


class TestStructuralHoles(object):
    """Unit tests for computing measures of structural holes.

    The expected values for these functions were originally computed using the
    proprietary software `UCINET`_. These tests assume that that software is
    correct, but since it is non-free software, we cannot verify its
    correctness.

    .. _UCINET: https://sites.google.com/site/ucinetsoftware/home

    """

    def setup(self):
        self.G = nx.DiGraph()
        self.G.add_edges_from([(0, 1), (0, 2), (1, 0), (2, 1)])

    def test_constraint(self):
        assert_almost_equal(nx.constraint(self.G, 0), 1.003)
        assert_almost_equal(nx.constraint(self.G, 1), 1.003)
        assert_almost_equal(nx.constraint(self.G, 2), 1.389)

    def test_effective_size(self):
        assert_almost_equal(nx.effective_size(self.G, 0), 1.167)
        assert_almost_equal(nx.effective_size(self.G, 1), 1.167)
        assert_almost_equal(nx.effective_size(self.G, 2), 1)

    def test_hierarchy(self):
        assert_almost_equal(nx.hierarchy(self.G, 0), 0.11)
        assert_almost_equal(nx.hierarchy(self.G, 1), 0.11)
        assert_almost_equal(nx.hierarchy(self.G, 2), 0)

    # def test_ego_density(self):
    #     assert_almost_equal(nx.ego_density(self.G, 0), 0.5)
    #     assert_almost_equal(nx.ego_density(self.G, 1), 0.5)
    #     assert_almost_equal(nx.ego_density(self.G, 2), 1)
