"""Unit tests for the :mod:`networkx.algorithms.sink` module."""

import networkx as nx
from networkx.algorithms.sink import is_sink, sinks, number_of_sinks


def test_is_sink():
    G = nx.DiGraph()
    G.add_edge(0, 1)
    G.add_node(2)
    assert not is_sink(G, 0)
    assert is_sink(G, 1)
    assert is_sink(G, 2)


def test_sinks():
    G = nx.DiGraph()
    G.add_edge(0, 1)
    G.add_nodes_from([2, 3])
    assert sorted(sinks(G)) == [1, 2, 3]


def test_number_of_sinks():
    G = nx.DiGraph()
    G.add_edge(0, 1)
    G.add_nodes_from([2, 3])
    assert number_of_sinks(G) == 3
