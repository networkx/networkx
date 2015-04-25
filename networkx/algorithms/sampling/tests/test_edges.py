# test_edges.py - unit tests for sampling.edges
#
# Copyright 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.sampling.edges` module.

"""
from nose.tools import assert_equal
from nose.tools import assert_true
from nose.tools import raises

import networkx as nx
from networkx import sampling


class TestUniformIndependentEdgeSample(object):
    """Unit tests for the :func:`networkx.uniform_independent_edge_sample`
    function.

    """

    def setup(self):
        self.G = nx.cycle_graph(5)

    def sample(self, *args, **kw):
        return sampling.uniform_independent_edge_sample(*args, **kw)

    def test_size(self):
        edges = self.sample(self.G, 3)
        assert_equal(3, len(edges))

    def test_edges_in_graph(self):
        edges = self.sample(self.G, 3)
        assert_true(all(v in self.G[u] for u, v in edges))

    @raises(ValueError)
    def test_oversample_without_replacement(self):
        self.sample(self.G, 10, with_replacement=False)

    def test_oversample_with_replacement(self):
        edges = list(self.sample(self.G, 10, with_replacement=True))
        assert_equal(10, len(edges))
        assert_true(all(v in self.G[u] for u, v in edges))

    def test_keys(self):
        G = nx.MultiGraph(2 * list(self.G.edges()))
        edges = self.sample(G, 3, keys=True)
        assert_equal(3, len(edges))
        assert_true(all(len(edge) == 3 for edge in edges))
        assert_true(all(v in G[u] for u, v, k in edges))

    def test_data(self):
        edges = self.sample(self.G, 3, data=True)
        assert_equal(3, len(edges))
        assert_true(all(len(edge) == 3 for edge in edges))
        assert_true(all(v in self.G[u] for u, v, d in edges))
