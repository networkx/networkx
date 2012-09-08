# test_partition.py - unit tests for the community.partition module
#
# Copyright 2011 Ben Edwards <bedwards@cs.unm.edu>.
# Copyright 2011 Aric Hagberg <hagberg@lanl.gov>.
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.community.partition`
module.

"""
from nose import SkipTest
from nose.tools import assert_equal
from nose.tools import raises
try:
    import scipy
except ImportError:
    is_scipy_available = False
else:
    is_scipy_available = True

import networkx as nx


def assert_partition_equal(x, y):
    assert_equal(set(map(frozenset, x)), set(map(frozenset, y)))


class TestGreedyMaxModularityPartition(object):
    """Unit tests for the :func:`greedy_max_modularity_partition`
    function.

    """

    def test_partition(self):
        G = nx.barbell_graph(3, 0)
        C = nx.greedy_max_modularity_partition(G)
        assert_partition_equal(C, ({0, 1, 2}, {3, 4, 5}))

    @raises(nx.NetworkXError)
    def test_non_disjoint_partition(self):
        G = nx.barbell_graph(3, 0)
        C_init = ({0, 1, 2}, {2, 3, 4, 5})
        nx.greedy_max_modularity_partition(G, C_init)

    @raises(nx.NetworkXError)
    def test_too_many_blocks(self):
        G = nx.barbell_graph(3, 0)
        C_init = ({0, 1}, {2}, {3, 4, 5})
        nx.greedy_max_modularity_partition(G, C_init)

    @raises(nx.NetworkXNotImplemented)
    def test_multigraph_disallowed(self):
        nx.greedy_max_modularity_partition(nx.MultiGraph())


class TestSpectralModularityPartition(object):
    """Unit tests for the :func:`spectral_modularity_partition`
    function.

    """

    def test_partition(self):
        if not is_scipy_available:
            raise SkipTest('SciPy not available')
        G = nx.barbell_graph(3, 0)
        C = nx.spectral_modularity_partition(G)
        assert_partition_equal(C, ({3, 4, 5}, {0, 1, 2}))

    # # The algorithm does not correctly partition the karate club graph into
    # # the two clubs.
    # def test_karate_club(self):
    #     if not is_scipy_available:
    #         raise SkipTest('SciPy not available')
    #     G = nx.karate_club_graph()
    #     left = {v for v in G if G.node[v]['club'] == 'Mr. Hi'}
    #     right = {v for v in G if G.node[v]['club'] == 'Officer'}
    #     C = nx.spectral_modularity_partition(G)
    #     assert_partition_equal(C, (left, right))
