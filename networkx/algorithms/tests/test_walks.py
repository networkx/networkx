"""Unit tests for the :mod:`networkx.algorithms.walks` module."""

from itertools import islice

import pytest

import networkx as nx


class TestNumberOfWalks:
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")

    def test_directed(self):
        G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
        num_walks = nx.number_of_walks(G, 3)
        expected = {0: {0: 1, 1: 0, 2: 0}, 1: {0: 0, 1: 1, 2: 0}, 2: {0: 0, 1: 0, 2: 1}}
        assert num_walks == expected

    def test_undirected(self):
        G = nx.cycle_graph(3)
        num_walks = nx.number_of_walks(G, 3)
        expected = {0: {0: 2, 1: 3, 2: 3}, 1: {0: 3, 1: 2, 2: 3}, 2: {0: 3, 1: 3, 2: 2}}
        assert num_walks == expected

    def test_non_integer_nodes(self):
        G = nx.DiGraph([("A", "B"), ("B", "C"), ("C", "A")])
        num_walks = nx.number_of_walks(G, 2)
        expected = {
            "A": {"A": 0, "B": 0, "C": 1},
            "B": {"A": 1, "B": 0, "C": 0},
            "C": {"A": 0, "B": 1, "C": 0},
        }
        assert num_walks == expected

    def test_zero_length(self):
        G = nx.cycle_graph(3)
        num_walks = nx.number_of_walks(G, 0)
        expected = {0: {0: 1, 1: 0, 2: 0}, 1: {0: 0, 1: 1, 2: 0}, 2: {0: 0, 1: 0, 2: 1}}
        assert num_walks == expected

    def test_negative_length_exception(self):
        G = nx.cycle_graph(3)
        with pytest.raises(ValueError):
            nx.number_of_walks(G, -1)

    def test_hidden_weight_attr(self):
        G = nx.cycle_graph(3)
        G.add_edge(1, 2, weight=5)
        num_walks = nx.number_of_walks(G, 3)
        expected = {0: {0: 2, 1: 3, 2: 3}, 1: {0: 3, 1: 2, 2: 3}, 2: {0: 3, 1: 3, 2: 2}}
        assert num_walks == expected


def test_random_walk_unweighted_reproducible():
    """Two runs with the same seed should produce identical unweighted walks."""
    G = nx.cycle_graph(5)
    walk_a = islice(nx.random_walk(G, start=0, seed=5), 6)
    walk_b = islice(nx.random_walk(G, start=0, seed=5), 6)
    assert list(walk_a) == list(walk_b)


def test_random_walk_unweighted_dead_end():
    """Unweighted walk should yield start and stop at a dead end."""
    G = nx.DiGraph([(0, 1), (1, 2), (2, 3)])
    walk = nx.random_walk(G, start=3, seed=0)
    assert list(walk) == [3]


def test_random_walk_unweighted_directed():
    """Unweighted walk on a DiGraph should follow edge direction."""
    G = nx.DiGraph([(0, 1), (1, 2), (2, 2)])
    walk = islice(nx.random_walk(G, start=0, seed=0), 4)
    assert list(walk) == [0, 1, 2, 2]


def test_random_walk_omitted_start_raises_typeerror():
    """Omitting start should raise TypeError."""
    G = nx.cycle_graph(5)
    with pytest.raises(TypeError):
        nx.random_walk(G)


def test_random_walk_start_must_be_keyword():
    G = nx.path_graph(2)
    with pytest.raises(TypeError):
        nx.random_walk(G, 0)


def test_random_walk_missing_start_node_raises_nodenotfound():
    """Starting from a node not in the graph should raise NodeNotFound."""
    G = nx.path_graph(2)
    with pytest.raises(nx.NodeNotFound):
        list(nx.random_walk(G, start=3))


def test_random_walk_unexpected_walk_length_argument():
    """walk_length is not accepted in the generator API."""
    G = nx.path_graph(3)
    with pytest.raises(TypeError):
        nx.random_walk(G, start=0, walk_length=2)


def test_random_walk_multigraph_not_implemented():
    G = nx.MultiGraph([(0, 1), (0, 1)])
    with pytest.raises(nx.NetworkXNotImplemented):
        nx.random_walk(G, start=0, seed=0)


def test_random_walk_weighted_reproducible():
    """Using the same integer seed should reproduce the same weighted walk."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=2)
    G.add_edge(1, 2, weight=1)
    walk_a = islice(nx.random_walk(G, start=0, weight="weight", seed=0), 4)
    walk_b = islice(nx.random_walk(G, start=0, weight="weight", seed=0), 4)
    assert list(walk_a) == list(walk_b)


def test_random_walk_weighted_with_generator_seed():
    """Using the same NumPy Generator seed should reproduce the same weighted walk."""
    np = pytest.importorskip("numpy")

    G = nx.Graph()
    G.add_edge(0, 1, weight=2)
    G.add_edge(0, 2, weight=1)
    seed = 7
    walk_a = islice(
        nx.random_walk(G, start=0, weight="weight", seed=np.random.default_rng(seed)),
        4,
    )
    walk_b = islice(
        nx.random_walk(G, start=0, weight="weight", seed=np.random.default_rng(seed)),
        4,
    )
    assert list(walk_a) == list(walk_b)


def test_random_walk_weighted_default_weight():
    """Missing weight attributes should default to weight 1."""
    G = nx.path_graph(3)
    H = nx.Graph()
    H.add_edge(0, 1, weight=1)
    H.add_edge(1, 2, weight=1)
    walk = islice(nx.random_walk(G, start=0, weight="weight", seed=1), 3)
    walk_with_attrs = islice(nx.random_walk(H, start=0, weight="weight", seed=1), 3)
    assert list(walk) == list(walk_with_attrs)


def test_random_walk_weighted_zero_weight_stops():
    """Zero-weight edges should halt the walk after yielding the start node."""
    G = nx.DiGraph()
    G.add_edge(0, 1, weight=0)
    walk = nx.random_walk(G, start=0, weight="weight", seed=0)
    assert list(walk) == [0]


def test_random_walk_weighted_negative_weight_raises():
    """Negative weights should raise ValueError."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=-2)
    with pytest.raises(ValueError):
        list(islice(nx.random_walk(G, start=0, weight="weight", seed=0), 2))


def test_random_walk_unweighted_with_negative_weight_attr():
    """Negative weight attributes are ignored when no weight parameter is given."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=-5)
    # Should behave as unweighted and not raise
    walk = islice(nx.random_walk(G, start=0, seed=0), 2)
    assert list(walk) == [0, 1]
