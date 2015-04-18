from nose.tools import *
import networkx as nx
import sys
sys.path.append('..')
from exact_maximum_clique import *

def test_exception():
    graph = nx.complete_graph(10)
    G=graph.copy()
    cs    = maxclique_set(graph)
    cdens = nx.density(G.subgraph(cs))
    
    eq_(cdens, 1.0, "clique not found by maxclique_set!")

    graph = nx.trivial_graph(nx.Graph())
    G=graph.copy()
    cs    = maxclique_set(graph)
    cdens = nx.density(G.subgraph(cs))
    eq_(cdens, 0.0, "clique not found by maxclique_set!")

    graph = nx.barbell_graph(10, 5, nx.Graph())
    G=graph.copy()
    cs    = maxclique_set(graph)
    cdens = nx.density(G.subgraph(cs))
    eq_(cdens, 1.0, "clique not found by maxclique_set!")

def test_maxclique_set_smoke():
    # smoke test
    G = nx.Graph()
    assert_equal(len(maxclique_set(G)),0)

def test_maxclique_set():
    # create a complete graph
    graph = nx.complete_graph(30)
    # this should return the entire graph
    mc = maxclique_set(graph)
    assert_equals(30, len(mc))
