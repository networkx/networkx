# test_walks.py - unit tests for sampling.walks
#
# Copyright 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.sampling.walks` module.

"""
from nose.tools import assert_equal
from nose.tools import assert_true

import networkx as nx
from networkx import sampling
from networkx.utils import pairwise


class RandomWalkTestBase(object):

    def setup(self):
        self.G = nx.cycle_graph(5)

    def random_walk(self, *args, **kw):
        raise NotImplementedError

    def is_walk(self, G, nodes):
        return all(v in G[u] for u, v in pairwise(nodes))

    def test_length(self):
        walk = list(self.random_walk(self.G, length=10))
        assert_equal(11, len(walk))
        assert_true(self.is_walk(self.G, walk))

    def test_length_zero(self):
        walk = list(self.random_walk(self.G, length=0, start_node=0))
        assert_equal(1, len(walk))
        assert_true(self.is_walk(self.G, walk))
        assert_equal(0, walk[0])

    def test_start_node(self):
        walk = list(self.random_walk(self.G, length=10, start_node=0))
        assert_equal(11, len(walk))
        assert_true(self.is_walk(self.G, walk))
        assert_equal(0, walk[0])


class TestRandomWalk(RandomWalkTestBase):

    def random_walk(self, *args, **kw):
        return sampling.random_walk(*args, **kw)


class LazyRandomWalkTestBase(RandomWalkTestBase):

    def is_walk(self, G, nodes):
        return all(u == v or v in G[u] for u, v in pairwise(nodes))


class TestLazyRandomWalk(LazyRandomWalkTestBase):

    def random_walk(self, *args, **kw):
        return sampling.lazy_random_walk(*args, **kw)


class TestMetropolisHastingsRandomWalk(LazyRandomWalkTestBase):

    def random_walk(self, *args, **kw):
        return sampling.metropolis_hastings_random_walk(*args, **kw)
