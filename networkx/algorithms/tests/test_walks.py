"""Unit tests for the :mod:`networkx.algorithms.walks` module."""

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


class TestNumberOfWalks:
    @classmethod
    def setup_class(cls):
        cls.G = nx.DiGraph(nx.utils.pairwise(range(3), cyclic=True))

    def test_neither_source_nor_target(self):
        num_walks = nx.number_of_walks(self.G, 3)
        expected = {0: {0: 1, 1: 0, 2: 0}, 1: {0: 0, 1: 1, 2: 0}, 2: {0: 0, 1: 0, 2: 1}}
        assert num_walks == expected

    def test_source_only(self):
        num_walks = nx.number_of_walks(self.G, 2, source=2)
        expected = {0: 0, 1: 1, 2: 0}
        assert num_walks == expected

    def test_target_only(self):
        num_walks = nx.number_of_walks(self.G, 2, target=2)
        expected = {0: 1, 1: 0, 2: 0}
        assert num_walks == expected

    def test_source_and_target(self):
        num_walks = nx.number_of_walks(self.G, 2, source=0, target=2)
        assert num_walks == 1


class TestSingleSourceNumberOfWalksTestBase:
    """Unit tests for the
    :func:`networkx.algorithms.walks.single_source_number_of_walks`
    function.
    This is an abstract base class; concrete subclasses must set the
    :attr:`method` class attribute to be one of the possible values for
    the `method` keyword argument to the function under test.
    """

    def test_no_target(self):
        G = nx.cycle_graph(4)
        source = 0
        k = 3
        num_walks = nx.single_source_number_of_walks(G, k, source)
        expected = {0: 0, 1: 4, 2: 0, 3: 4}
        assert num_walks == expected

    def test_target(self):
        G = nx.cycle_graph(4)
        source = 0
        target = 1
        k = 3
        num_walks = nx.single_source_number_of_walks(G, k, source=source, target=target)
        assert num_walks == 4

    def test_source_and_target2(self):
        G = nx.DiGraph([("A", "B"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")])
        source = "A"
        target = "D"
        k = 2
        num_walks = nx.single_source_number_of_walks(G, k, source=source, target=target)
        assert num_walks == 2


class TestAllPairsNumberOfWalksTestBase:
    """Unit tests for the
    :func:`networkx.algorithms.walks.all_pairs_number_of_walks`
    function.
    This is an abstract base class; concrete subclasses must set the
    :attr:`method` class attribute to be one of the possible values for
    the `method` keyword argument to the function under test.
    """

    def test_basic(self):
        G = nx.cycle_graph(4)
        k = 3
        num_walks = nx.all_pairs_number_of_walks(G, k)
        expected = {
            0: {0: 0, 1: 4, 2: 0, 3: 4},
            1: {0: 4, 1: 0, 2: 4, 3: 0},
            2: {0: 0, 1: 4, 2: 0, 3: 4},
            3: {0: 4, 1: 0, 2: 4, 3: 0},
        }
        assert num_walks == expected
