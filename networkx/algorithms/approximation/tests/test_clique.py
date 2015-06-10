# test_clique.py - unit tests for the approximation.clique module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.approximation.clique`
module.

"""
from nose.tools import eq_
from nose.tools import assert_greater
import networkx as nx
import networkx.algorithms.approximation as apxa
from networkx.algorithms.approximation import max_clique


def test_clique_removal():
    graph = nx.complete_graph(10)
    i, cs = apxa.clique_removal(graph)
    idens = nx.density(graph.subgraph(i))
    eq_(idens, 0.0, "i-set not found by clique_removal!")
    for clique in cs:
        cdens = nx.density(graph.subgraph(clique))
        eq_(cdens, 1.0, "clique not found by clique_removal!")

    graph = nx.trivial_graph(nx.Graph())
    i, cs = apxa.clique_removal(graph)
    idens = nx.density(graph.subgraph(i))
    eq_(idens, 0.0, "i-set not found by ramsey!")
    # we should only have 1-cliques. Just singleton nodes.
    for clique in cs:
        cdens = nx.density(graph.subgraph(clique))
        eq_(cdens, 0.0, "clique not found by clique_removal!")

    graph = nx.barbell_graph(10, 5, nx.Graph())
    i, cs = apxa.clique_removal(graph)
    idens = nx.density(graph.subgraph(i))
    eq_(idens, 0.0, "i-set not found by ramsey!")
    for clique in cs:
        cdens = nx.density(graph.subgraph(clique))
        eq_(cdens, 1.0, "clique not found by clique_removal!")


def test_max_clique_smoke():
    # smoke test
    G = nx.Graph()
    eq_(len(apxa.max_clique(G)),0)


def test_max_clique():
    # create a complete graph
    graph = nx.complete_graph(30)
    # this should return the entire graph
    mc = apxa.max_clique(graph)
    eq_(30, len(mc))


def test_max_clique_by_cardinality():
    """Tests that the maximum clique is computed according to maximum
    cardinality of the sets.

    For more information, see pull request #1531.

    """
    G = nx.complete_graph(5)
    G.add_edge(4, 5)
    clique = max_clique(G)
    assert_greater(len(clique), 1)

    G = nx.lollipop_graph(30, 2)
    clique = max_clique(G)
    assert_greater(len(clique), 2)
