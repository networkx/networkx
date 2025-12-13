"""Unit tests for the :mod:`networkx.algorithms.walks` module."""

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


def test_directed():
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
    num_walks = nx.number_of_walks(G, 3)
    expected = {0: {0: 1, 1: 0, 2: 0}, 1: {0: 0, 1: 1, 2: 0}, 2: {0: 0, 1: 0, 2: 1}}
    assert num_walks == expected


def test_undirected():
    G = nx.cycle_graph(3)
    num_walks = nx.number_of_walks(G, 3)
    expected = {0: {0: 2, 1: 3, 2: 3}, 1: {0: 3, 1: 2, 2: 3}, 2: {0: 3, 1: 3, 2: 2}}
    assert num_walks == expected


def test_non_integer_nodes():
    G = nx.DiGraph([("A", "B"), ("B", "C"), ("C", "A")])
    num_walks = nx.number_of_walks(G, 2)
    expected = {
        "A": {"A": 0, "B": 0, "C": 1},
        "B": {"A": 1, "B": 0, "C": 0},
        "C": {"A": 0, "B": 1, "C": 0},
    }
    assert num_walks == expected


def test_zero_length():
    G = nx.cycle_graph(3)
    num_walks = nx.number_of_walks(G, 0)
    expected = {0: {0: 1, 1: 0, 2: 0}, 1: {0: 0, 1: 1, 2: 0}, 2: {0: 0, 1: 0, 2: 1}}
    assert num_walks == expected


def test_negative_length_exception():
    G = nx.cycle_graph(3)
    with pytest.raises(ValueError):
        nx.number_of_walks(G, -1)


def test_hidden_weight_attr():
    G = nx.cycle_graph(3)
    G.add_edge(1, 2, weight=5)
    num_walks = nx.number_of_walks(G, 3)
    expected = {0: {0: 2, 1: 3, 2: 3}, 1: {0: 3, 1: 2, 2: 3}, 2: {0: 3, 1: 3, 2: 2}}
    assert num_walks == expected


def test_unweighted_random_walk_reproducible():
    G = nx.cycle_graph(5)
    walk_a = nx.unweighted_random_walk(G, start=0, walk_length=6, seed=5)
    walk_b = nx.unweighted_random_walk(G, start=0, walk_length=6, seed=5)
    assert walk_a == walk_b


def test_unweighted_random_walk_dead_end():
    G = nx.DiGraph([(0, 1), (1, 2), (2, 3)])
    walk = nx.unweighted_random_walk(G, start=3, walk_length=3, seed=0)
    assert walk == [3]


def test_unweighted_random_walk_directed():
    G = nx.DiGraph([(0, 1), (1, 2), (2, 2)])
    walk = nx.unweighted_random_walk(G, start=0, walk_length=3, seed=0)
    assert walk == [0, 1, 2, 2]


def test_unweighted_random_walk_negative_length():
    G = nx.path_graph(2)
    with pytest.raises(ValueError):
        nx.unweighted_random_walk(G, start=0, walk_length=-1)


def test_unweighted_random_walk_missing_start():
    G = nx.path_graph(2)
    with pytest.raises(nx.NodeNotFound):
        nx.unweighted_random_walk(G, start=3, walk_length=2)


def test_weighted_random_walk_reproducible():
    G = nx.Graph()
    G.add_edge(0, 1, weight=2)
    G.add_edge(1, 2, weight=1)
    walk_a = nx.weighted_random_walk(G, start=0, walk_length=4, seed=0)
    walk_b = nx.weighted_random_walk(G, start=0, walk_length=4, seed=0)
    assert walk_a == walk_b


def test_weighted_random_walk_default_weight():
    G = nx.path_graph(3)
    H = nx.Graph()
    H.add_edge(0, 1, weight=1)
    H.add_edge(1, 2, weight=1)
    walk = nx.weighted_random_walk(G, start=0, walk_length=3, seed=1)
    walk_with_attrs = nx.weighted_random_walk(H, start=0, walk_length=3, seed=1)
    assert walk == walk_with_attrs


def test_weighted_random_walk_zero_weight_stops():
    G = nx.DiGraph()
    G.add_edge(0, 1, weight=0)
    walk = nx.weighted_random_walk(G, start=0, walk_length=3, seed=0)
    assert walk == [0]


def test_weighted_random_walk_negative_weight_raises():
    G = nx.Graph()
    G.add_edge(0, 1, weight=-2)
    with pytest.raises(ValueError):
        nx.weighted_random_walk(G, start=0, walk_length=1, seed=0)
