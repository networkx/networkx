# test_nodes.py - unit tests for sampling.nodes
#
# Copyright 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.sampling.nodes` module.

"""
from nose.tools import assert_equal
from nose.tools import assert_true
from nose.tools import raises

import networkx as nx
from networkx import sampling


class NodeSampleTestBase(object):
    """Abstract base class for unit tests for functions that sample
    nodes.

    Subclasses must override and implement the :func:`sample` method,
    which should execute the sampling function under test.

    """

    def setup(self):
        self.G = nx.cycle_graph(5)

    def sample(self, *args, **kw):
        raise NotImplementedError

    def test_sample(self):
        nodes = list(self.sample(self.G, 3))
        assert_equal(3, len(nodes))
        assert_true(all(v in self.G for v in nodes))


class TestUniformIndependentNodeSample(NodeSampleTestBase):
    """Unit tests for the :func:`~networkx.uniform_independent_node_sample`
    function.

    """

    def sample(self, *args, **kw):
        return sampling.uniform_independent_node_sample(*args, **kw)

    @raises(ValueError)
    def test_oversample_without_replacement(self):
        self.sample(self.G, 10, with_replacement=False)

    def test_oversample_with_replacement(self):
        nodes = list(self.sample(self.G, 10, with_replacement=True))
        assert_equal(10, len(nodes))
        assert_true(all(v in self.G for v in nodes))


class TestDegreeWeightedIndependentSample(NodeSampleTestBase):
    """Unit tests for the
    :func:`~networkx.degree_weighted_independent_node_sample` function.

    """

    def sample(self, *args, **kw):
        return sampling.degree_weighted_independent_node_sample(*args, **kw)

    def test_oversample(self):
        nodes = list(self.sample(self.G, 10))
        assert_equal(10, len(nodes))
        assert_true(all(v in self.G for v in nodes))
