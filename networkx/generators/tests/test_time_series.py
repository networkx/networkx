"""Unit tests for the :mod:`networkx.generators.time_series` module."""
import itertools

import networkx as nx


def test_visibility_graph_static_series():
    # arrange
    series = range(10)
    expected_series_length = len(series)

    # act
    actual_graph = nx.visibility_graph(series)

    # assert
    assert actual_graph.number_of_nodes() == expected_series_length
    assert actual_graph.number_of_edges() == 9


def test_visibility_graph_cyclic_series():
    # arrange
    series = list(itertools.islice(itertools.cycle((2, 1, 3)), 12))
    expected_series_length = len(series)

    # act
    actual_graph = nx.visibility_graph(series)

    # assert
    assert actual_graph.number_of_nodes() == expected_series_length
    assert actual_graph.number_of_edges() == 18
