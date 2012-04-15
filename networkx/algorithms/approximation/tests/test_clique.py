from nose.tools import *
import networkx as nx
import networkx.algorithms.approximation as apxa

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
    assert_equal(len(apxa.max_clique(G)),0)

def test_max_clique():
    # create a complete graph
    graph = nx.complete_graph(30)
    # this should return the entire graph
    mc = apxa.max_clique(graph)
    assert_equals(30, len(mc))
