# test_isolate.py - unit tests for the isolate module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.isolates` module."""

import networkx as nx


def test_is_isolate():
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_node(2)
    assert not nx.is_isolate(G, 0)
    assert not nx.is_isolate(G, 1)
    assert nx.is_isolate(G, 2)


def test_isolates():
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_nodes_from([2, 3])
    assert sorted(nx.isolates(G)) == [2, 3]


def test_number_of_isolates():
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_nodes_from([2, 3])
    assert nx.number_of_isolates(G) == 2
