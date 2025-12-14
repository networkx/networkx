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


def test_random_walk_unweighted_reproducible():
    """Two runs with the same seed should produce identical unweighted walks."""
    G = nx.cycle_graph(5)
    walk_a = nx.random_walk(G, start=0, walk_length=6, seed=5)
    walk_b = nx.random_walk(G, start=0, walk_length=6, seed=5)
    assert walk_a == walk_b


def test_random_walk_unweighted_dead_end():
    """Unweighted walk should stop immediately when the start node has no neighbors."""
    G = nx.DiGraph([(0, 1), (1, 2), (2, 3)])
    walk = nx.random_walk(G, start=3, walk_length=3, seed=0)
    assert walk == [3]


def test_random_walk_unweighted_directed():
    """Unweighted walk on a DiGraph should follow edge direction."""
    G = nx.DiGraph([(0, 1), (1, 2), (2, 2)])
    walk = nx.random_walk(G, start=0, walk_length=3, seed=0)
    assert walk == [0, 1, 2, 2]


def test_random_walk_unweighted_negative_length():
    """Negative walk_length should raise ValueError."""
    G = nx.path_graph(2)
    with pytest.raises(ValueError):
        nx.random_walk(G, start=0, walk_length=-1)


def test_random_walk_unweighted_missing_start():
    """Starting from a node not in the graph should raise NodeNotFound."""
    G = nx.path_graph(2)
    with pytest.raises(nx.NodeNotFound):
        nx.random_walk(G, start=3, walk_length=2)


def test_random_walk_weighted_reproducible():
    """Weighted walks should be deterministic when seed is fixed."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=2)
    G.add_edge(1, 2, weight=1)
    walk_a = nx.random_walk(G, start=0, walk_length=4, weight="weight", seed=0)
    walk_b = nx.random_walk(G, start=0, walk_length=4, weight="weight", seed=0)
    assert walk_a == walk_b


def test_random_walk_weighted_default_weight():
    """Missing weight attributes should default to weight 1."""
    G = nx.path_graph(3)
    H = nx.Graph()
    H.add_edge(0, 1, weight=1)
    H.add_edge(1, 2, weight=1)
    walk = nx.random_walk(G, start=0, walk_length=3, weight="weight", seed=1)
    walk_with_attrs = nx.random_walk(H, start=0, walk_length=3, weight="weight", seed=1)
    assert walk == walk_with_attrs


def test_random_walk_weighted_zero_weight_stops():
    """Zero-weight edges should halt the walk when no positive weight neighbors remain."""
    G = nx.DiGraph()
    G.add_edge(0, 1, weight=0)
    walk = nx.random_walk(G, start=0, walk_length=3, weight="weight", seed=0)
    assert walk == [0]


def test_random_walk_weighted_negative_weight_raises():
    """Negative weights should raise ValueError."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=-2)
    with pytest.raises(ValueError):
        nx.random_walk(G, start=0, walk_length=1, weight="weight", seed=0)


def test_random_walk_unweighted_with_negative_weight_attr():
    """Negative weight attributes are ignored when no weight parameter is given."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=-5)
    # Should behave as unweighted and not raise
    walk = nx.random_walk(G, start=0, walk_length=1, seed=0)
    assert walk == [0, 1]
