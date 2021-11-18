"""Unit tests for the :mod:`networkx.algorithms.source` module."""

import networkx as nx
from networkx.algorithms.source import is_source, sources, number_of_sources

def test_is_source():
    G = nx.DiGraph()
    G.add_edge(0, 1)
    G.add_node(2)
    assert is_source(G, 0)
    assert not is_source(G, 1)
    assert is_source(G, 2)


def test_sources():
    G = nx.DiGraph()
    G.add_edge(0, 1)
    G.add_nodes_from([2, 3])
    assert sorted(sources(G)) == [0, 2, 3]


def test_number_of_sources():
    G = nx.DiGraph()
    G.add_edge(0, 1)
    G.add_nodes_from([2, 3])
    assert number_of_sources(G) == 3
