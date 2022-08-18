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
        num_walks = nx.number_of_walks(self.G, 2)
        expected = {0: 0, 1: 1, 2: 0}
        assert num_walks[2] == expected

    def test_source_and_target(self):
        num_walks = nx.number_of_walks(self.G, 2)
        assert num_walks[0][2] == 1

    def test_no_target(self):
        G = nx.cycle_graph(4)
        source = 0
        k = 3
        num_walks = nx.number_of_walks(G, k)
        expected = {0: 0, 1: 4, 2: 0, 3: 4}
        assert num_walks[source] == expected

    def test_target(self):
        G = nx.cycle_graph(4)
        source = 0
        target = 1
        k = 3
        num_walks = nx.number_of_walks(G, k)
        assert num_walks[source][target] == 4

    def test_source_and_target2(self):
        G = nx.DiGraph([("A", "B"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")])
        source = "A"
        target = "D"
        k = 2
        num_walks = nx.number_of_walks(G, k)
        assert num_walks[source][target] == 2

    def test_basic(self):
        G = nx.cycle_graph(4)
        k = 3
        num_walks = nx.number_of_walks(G, k)
        expected = {
            0: {0: 0, 1: 4, 2: 0, 3: 4},
            1: {0: 4, 1: 0, 2: 4, 3: 0},
            2: {0: 0, 1: 4, 2: 0, 3: 4},
            3: {0: 4, 1: 0, 2: 4, 3: 0},
        }
        assert num_walks == expected
