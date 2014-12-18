# test_walks.py - unit tests for the walks module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.walks` module."""
from nose.tools import assert_equal
from nose.tools import raises

from networkx import all_pairs_number_of_walks
from networkx import cycle_graph
from networkx import DiGraph
from networkx import empty_graph
from networkx import number_of_walks
from networkx import single_source_number_of_walks


class TestNumberOfWalks(object):
    """Unit tests for the
    :func:`networkx.algorithms.walks.number_of_walks` function.

    """

    def setup(self):
        self.G = DiGraph(['ab', 'bc', 'ca'])

    def test_neither_source_nor_target(self):
        num_walks = number_of_walks(self.G, 3)
        expected = {'a': {'a': 1, 'b': 0, 'c': 0},
                    'b': {'a': 0, 'b': 1, 'c': 0},
                    'c': {'a': 0, 'b': 0, 'c': 1}}
        assert_equal(num_walks, expected)

    def test_source_only(self):
        num_walks = number_of_walks(self.G, 2, source='c')
        expected = {'a': 0, 'b': 1, 'c': 0}
        assert_equal(num_walks, expected)

    def test_target_only(self):
        num_walks = number_of_walks(self.G, 2, target='c')
        expected = {'a': 1, 'b': 0, 'c': 0}
        assert_equal(num_walks, expected)

    def test_source_and_target(self):
        num_walks = number_of_walks(self.G, 2, source='a', target='c')
        assert_equal(num_walks, 1)


class TestSingleSourceNumberOfWalks(object):
    """Unit tests for the
    :func:`networkx.algorithms.walks.single_source_number_of_walks`
    function.

    """

    def test_no_target(self):
        G = cycle_graph(4)
        source = 0
        k = 3
        num_walks = single_source_number_of_walks(G, k, source)
        expected = {0: 0, 1: 4, 2: 0, 3: 4}
        assert_equal(num_walks, expected)

    def test_target(self):
        G = cycle_graph(4)
        source = 0
        target = 1
        k = 3
        num_walks = single_source_number_of_walks(G, k, source, target=target)
        assert_equal(num_walks, 4)

    @raises(ValueError)
    def test_single_source_negative_length(self):
        single_source_number_of_walks(empty_graph(1), -1, 0)


class TestAllPairsNumberOfWalks(object):
    """Unit tests for the
    :func:`networkx.algorithms.walks.all_pairs_number_of_walks`
    function.

    """

    def test_basic(self):
        G = cycle_graph(4)
        k = 3
        num_walks = all_pairs_number_of_walks(G, k)
        expected = {0: {0: 0, 1: 4, 2: 0, 3: 4},
                    1: {0: 4, 1: 0, 2: 4, 3: 0},
                    2: {0: 0, 1: 4, 2: 0, 3: 4},
                    3: {0: 4, 1: 0, 2: 4, 3: 0}}
        assert_equal(num_walks, expected)
