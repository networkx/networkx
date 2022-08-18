"""Unit tests for the :mod:`networkx.algorithms.walks` module."""

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


def test_neither_source_nor_target():
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
    num_walks = nx.number_of_walks(G, 3)
    expected = {0: {0: 1, 1: 0, 2: 0}, 1: {0: 0, 1: 1, 2: 0}, 2: {0: 0, 1: 0, 2: 1}}
    assert num_walks == expected


def test_no_target():
    G = nx.cycle_graph(4)
    source = 0
    k = 3
    num_walks = nx.number_of_walks(G, k)
    expected = {0: 0, 1: 4, 2: 0, 3: 4}
    assert num_walks[source] == expected


def test_source_and_target():
    G = nx.DiGraph([("A", "B"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")])
    source = "A"
    target = "D"
    k = 2
    num_walks = nx.number_of_walks(G, k)
    assert num_walks[source][target] == 2
