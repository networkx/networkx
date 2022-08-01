"""Unit tests for the :mod:`networkx.algorithms.walks` module."""

from functools import partial

from networkx import (
    DiGraph,
    all_pairs_number_of_walks,
    cycle_graph,
    empty_graph,
    number_of_walks,
    relabel_nodes,
    single_source_number_of_walks,
)
from networkx.utils import pairwise


class NumberOfWalks:
    """Unit tests for the
    :func:`networkx.algorithms.walks.number_of_walks` function.
    This is an abstract base class; concrete subclasses must set the
    :attr:`method` class attribute to be one of the possible values for
    the `method` keyword argument to the function under test.
    """

    @classmethod
    def setUp(self):
        self.G = DiGraph(pairwise(range(3), cyclic=True))
        self.number_of_walks = partial(number_of_walks)

    def test_neither_source_nor_target(self):
        num_walks = self.number_of_walks(self.G, 3)
        expected = {0: {0: 1, 1: 0, 2: 0}, 1: {0: 0, 1: 1, 2: 0}, 2: {0: 0, 1: 0, 2: 1}}
        assert num_walks == expected

    def test_source_only(self):
        num_walks = self.number_of_walks(self.G, 2, source=2)
        expected = {0: 0, 1: 1, 2: 0}
        assert num_walks == expected

    def test_target_only(self):
        num_walks = self.number_of_walks(self.G, 2, target=2)
        expected = {0: 1, 1: 0, 2: 0}
        assert num_walks == expected

    def test_source_and_target(self):
        num_walks = self.number_of_walks(self.G, 2, source=0, target=2)
        assert num_walks == 1


class SingleSourceNumberOfWalksTestBase:
    """Unit tests for the
    :func:`networkx.algorithms.walks.single_source_number_of_walks`
    function.
    This is an abstract base class; concrete subclasses must set the
    :attr:`method` class attribute to be one of the possible values for
    the `method` keyword argument to the function under test.
    """

    @classmethod
    def setUp(self):
        self.single_source_number_of_walks = partial(single_source_number_of_walks)

    def test_no_target(self):
        G = cycle_graph(4)
        source = 0
        k = 3
        num_walks = self.single_source_number_of_walks(G, k, source)
        expected = {0: 0, 1: 4, 2: 0, 3: 4}
        assert num_walks == expected

    def test_target(self):
        G = cycle_graph(4)
        source = 0
        target = 1
        k = 3
        num_walks = self.single_source_number_of_walks(G, k, source, target=target)
        assert num_walks == 4


class AllPairsNumberOfWalksTestBase:
    """Unit tests for the
    :func:`networkx.algorithms.walks.all_pairs_number_of_walks`
    function.
    This is an abstract base class; concrete subclasses must set the
    :attr:`method` class attribute to be one of the possible values for
    the `method` keyword argument to the function under test.
    """

    @classmethod
    def setUp(self):
        self.all_pairs_number_of_walks = partial(all_pairs_number_of_walks)

    def test_basic(self):
        G = cycle_graph(4)
        k = 3
        num_walks = self.all_pairs_number_of_walks(G, k)
        expected = {
            0: {0: 0, 1: 4, 2: 0, 3: 4},
            1: {0: 4, 1: 0, 2: 4, 3: 0},
            2: {0: 0, 1: 4, 2: 0, 3: 4},
            3: {0: 4, 1: 0, 2: 4, 3: 0},
        }
        assert num_walks == expected
