# test_quality.py - unit tests for the quality module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.community.quality`
module.

"""
from __future__ import division

from nose.tools import assert_almost_equal

import networkx as nx
from networkx import barbell_graph
from networkx import coverage
from networkx import performance


class TestPerformance(object):
    """Unit tests for the :func:`performance` function."""

    def test_bad_partition(self):
        """Tests that a poor partition has a low performance measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 4}, {2, 3, 5}]
        assert_almost_equal(8 / 15, performance(G, partition))

    def test_good_partition(self):
        """Tests that a good partition has a high performance measure.

        """
        G = barbell_graph(3, 0)
        partition = [{0, 1, 2}, {3, 4, 5}]
        assert_almost_equal(14 / 15, performance(G, partition))


class TestCoverage(object):
    """Unit tests for the :func:`coverage` function."""

    def test_bad_partition(self):
        """Tests that a poor partition has a low coverage measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 4}, {2, 3, 5}]
        assert_almost_equal(3 / 7, coverage(G, partition))

    def test_good_partition(self):
        """Tests that a good partition has a high coverage measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 2}, {3, 4, 5}]
        assert_almost_equal(6 / 7, coverage(G, partition))


def test_modularity():
    G = nx.barbell_graph(3, 0)
    C = [{0, 1, 4}, {2, 3, 5}]
    assert_almost_equal(-16 / (14 ** 2), nx.modularity(G, C))
    C = [{0, 1, 2}, {3, 4, 5}]
    assert_almost_equal((35 * 2) / (14 ** 2), nx.modularity(G, C))
