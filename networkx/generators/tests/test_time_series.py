"""Unit tests for the :mod:`networkx.generators.time_series` module."""
import itertools

import networkx as nx


def test_visibility_graph_static_series():
    # arrange
    series = [i ** 2 for i in range(10)]  # no obstructions
    expected_series_length = len(series)

    # act
    actual_graph = nx.visibility_graph(series)

    # assert
    assert actual_graph.number_of_nodes() == expected_series_length
    assert actual_graph.number_of_edges() == 45


def test_visibility_graph_corner_cases():
    edge_graph = nx.visibility_graph([10, 20])
    assert list(edge_graph.edges) == [(0, 1)]

    node_graph = nx.visibility_graph([10])
    assert node_graph.number_of_nodes() == 1
    assert node_graph.number_of_edges() == 0

    null_graph = nx.visibility_graph([])
    assert node_graph.number_of_nodes() == 0


def test_visibility_graph_cyclic_series():
    # arrange
    series = list(itertools.islice(itertools.cycle((2, 1, 3)), 15))
    expected_series_length = len(series)

    # act
    actual_graph = nx.visibility_graph(series)

    # assert
    assert actual_graph.number_of_nodes() == expected_series_length
    assert actual_graph.number_of_edges() == 23
