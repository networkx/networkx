# test_walks.py - unit tests for the walks module
#
# Copyright 2015, 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.walks` module."""
from functools import partial
from unittest import TestCase
from unittest import skipUnless

# Import scipy just to see whether it is unavailable, so that we can
# skip tests that require it.
try:
    import scipy
except ImportError:
    is_scipy_available = False
else:
    is_scipy_available = True

from nose.tools import assert_equal
from nose.tools import raises

from networkx import all_pairs_number_of_walks
from networkx import cycle_graph
from networkx import DiGraph
from networkx import empty_graph
from networkx import number_of_walks
from networkx import relabel_nodes
from networkx import single_source_number_of_walks
from networkx.utils import pairwise


class NumberOfWalksTestBase(object):
    """Unit tests for the
    :func:`networkx.algorithms.walks.number_of_walks` function.

    This is an abstract base class; concrete subclasses must set the
    :attr:`method` class attribute to be one of the possible values for
    the `method` keyword argument to the function under test.

    """

    #: String indicating the implementation to use when testing the
    #: `number_of_walks` function.
    method = None

    def setUp(self):
        self.G = DiGraph(pairwise(range(3), cyclic=True))
        self.number_of_walks = partial(number_of_walks, method=self.method)

    def test_neither_source_nor_target(self):
        num_walks = self.number_of_walks(self.G, 3)
        expected = {0: {0: 1, 1: 0, 2: 0},
                    1: {0: 0, 1: 1, 2: 0},
                    2: {0: 0, 1: 0, 2: 1}}
        assert_equal(num_walks, expected)

    def test_source_only(self):
        num_walks = self.number_of_walks(self.G, 2, source=2)
        expected = {0: 0, 1: 1, 2: 0}
        assert_equal(num_walks, expected)

    def test_target_only(self):
        num_walks = self.number_of_walks(self.G, 2, target=2)
        expected = {0: 1, 1: 0, 2: 0}
        assert_equal(num_walks, expected)

    def test_source_and_target(self):
        num_walks = self.number_of_walks(self.G, 2, source=0, target=2)
        assert_equal(num_walks, 1)


@skipUnless(is_scipy_available, 'scipy is not available')
class TestNumberOfWalksSciPy(NumberOfWalksTestBase, TestCase):
    """Unit tests for the `number_of_walks` function using the SciPy
    implementation.

    These tests will be skipped if SciPy is not available at the time
    this module is loaded.

    """

    method = 'scipy'

    @raises(TypeError)
    def test_wrong_type(self):
        """Tests that an exception is raised if the node labels are not
        all integers.

        """
        mapping = dict(zip(self.G, 'abc'))
        relabel_nodes(self.G, mapping=mapping, copy=False)
        self.number_of_walks(self.G, 1)

    @raises(ValueError)
    def test_wrong_integers(self):
        """Tests that an exception is raised if the node labels are not
        the first *n* integers.

        """
        mapping = {v: v + 1 for v in self.G}
        relabel_nodes(self.G, mapping=mapping, copy=False)
        self.number_of_walks(self.G, 1)


class TestNumberOfWalksNetworkX(NumberOfWalksTestBase, TestCase):
    """Unit tests for the `number_of_walks` function using the pure
    NetworkX implementation.

    """

    method = 'networkx'

    def test_non_integer_nodes(self):
        """Tests that the function works when the nodes are not
        necessarily the first *n* integers.

        """
        G = DiGraph(pairwise('abc', cyclic=True))
        num_walks = self.number_of_walks(G, 3)
        expected = {'a': {'a': 1, 'b': 0, 'c': 0},
                    'b': {'a': 0, 'b': 1, 'c': 0},
                    'c': {'a': 0, 'b': 0, 'c': 1}}
        assert_equal(num_walks, expected)


class SingleSourceNumberOfWalksTestBase(object):
    """Unit tests for the
    :func:`networkx.algorithms.walks.single_source_number_of_walks`
    function.

    This is an abstract base class; concrete subclasses must set the
    :attr:`method` class attribute to be one of the possible values for
    the `method` keyword argument to the function under test.

    """

    #: String indicating the implementation to use when testing the
    #: `single_source_number_of_walks` function.
    method = None

    def setUp(self):
        self.single_source_number_of_walks = \
            partial(single_source_number_of_walks, method=self.method)

    def test_no_target(self):
        G = cycle_graph(4)
        source = 0
        k = 3
        num_walks = self.single_source_number_of_walks(G, k, source)
        expected = {0: 0, 1: 4, 2: 0, 3: 4}
        assert_equal(num_walks, expected)

    def test_target(self):
        G = cycle_graph(4)
        source = 0
        target = 1
        k = 3
        num_walks = self.single_source_number_of_walks(G, k, source,
                                                       target=target)
        assert_equal(num_walks, 4)

    @raises(ValueError)
    def test_single_source_negative_length(self):
        self.single_source_number_of_walks(empty_graph(1), -1, 0)


@skipUnless(is_scipy_available, 'scipy is not available')
class TestSingleSourceNumberOfWalksSciPy(SingleSourceNumberOfWalksTestBase,
                                         TestCase):
    """Unit tests for the `single_source_number_of_walks` function using
    the SciPy implementation.

    These tests will be skipped if SciPy is not available at the time
    this module is loaded.

    """

    method = 'scipy'


class TestSingleSourceNumberOfWalksNetworkX(SingleSourceNumberOfWalksTestBase,
                                            TestCase):
    """Unit tests for the `single_source_number_of_walks` function using
    the pure NetworkX implementation.

    """

    method = 'networkx'


class AllPairsNumberOfWalksTestBase(object):
    """Unit tests for the
    :func:`networkx.algorithms.walks.all_pairs_number_of_walks`
    function.

    This is an abstract base class; concrete subclasses must set the
    :attr:`method` class attribute to be one of the possible values for
    the `method` keyword argument to the function under test.

    """

    #: String indicating the implementation to use when testing the
    #: `all_pairs_number_of_walks` function.
    method = None

    def setUp(self):
        self.all_pairs_number_of_walks = \
            partial(all_pairs_number_of_walks, method=self.method)

    def test_basic(self):
        G = cycle_graph(4)
        k = 3
        num_walks = self.all_pairs_number_of_walks(G, k)
        expected = {0: {0: 0, 1: 4, 2: 0, 3: 4},
                    1: {0: 4, 1: 0, 2: 4, 3: 0},
                    2: {0: 0, 1: 4, 2: 0, 3: 4},
                    3: {0: 4, 1: 0, 2: 4, 3: 0}}
        assert_equal(num_walks, expected)


@skipUnless(is_scipy_available, 'scipy is not available')
class TestAllPairsNumberOfWalksSciPy(AllPairsNumberOfWalksTestBase, TestCase):
    """Unit tests for the `all_pairs_number_of_walks` function using
    the SciPy implementation.

    These tests will be skipped if SciPy is not available at the time
    this module is loaded.

    """

    method = 'scipy'


class TestAllPairsNumberOfWalksNetworkX(SingleSourceNumberOfWalksTestBase,
                                        TestCase):
    """Unit tests for the `all_pairs_number_of_walks` function using
    the pure NetworkX implementation.

    """

    method = 'networkx'
