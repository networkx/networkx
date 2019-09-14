# test_karger.py - unit tests for the approximation.karger module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.approximation.karger`
module.

"""

from nose.tools import assert_equal
import networkx as nx
import random

class TestKarger(object):
    """Unit tests for the
    :func:`~networkx.algorithms.approximation.karger` function.

    """

    def test_karger(self):
        G = nx.fast_gnp_random_graph(20, 0.5, seed=42)
        score, _ = nx.stoer_wagner(G)
        kscore, _ = nx.parallel_karger(G)
        assert_equal(kscore, score)

    def test_weighted_karger(self):
        G = nx.fast_gnp_random_graph(20, 0.5, seed=42)
        for (u, v) in G.edges():
            G.edges[u,v]['weight'] = random.randint(0,100)
        score, _ = nx.stoer_wagner(G)
        kscore, _ = nx.parallel_karger(G)
        assert_equal(kscore, score)
