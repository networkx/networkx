from nose.tools import assert_true, assert_equal, raises
import networkx as nx

def test_stochastic():
    G=nx.DiGraph()
    G.add_edge(0,1)
    G.add_edge(0,2)
    S=nx.stochastic_graph(G)
    assert_true(nx.is_isomorphic(G,S))
    assert_equal(sorted(S.edges(data=True)),
                 [(0, 1, {'weight': 0.5}), 
                  (0, 2, {'weight': 0.5})])
    S=nx.stochastic_graph(G,copy=True)
    assert_equal(sorted(S.edges(data=True)),
                 [(0, 1, {'weight': 0.5}), 
                  (0, 2, {'weight': 0.5})])

def test_stochastic_ints():
    G=nx.DiGraph()
    G.add_edge(0,1,weight=1)
    G.add_edge(0,2,weight=1)
    S=nx.stochastic_graph(G)
    assert_equal(sorted(S.edges(data=True)),
                 [(0, 1, {'weight': 0.5}), 
                  (0, 2, {'weight': 0.5})])

@raises(nx.NetworkXNotImplemented)
def test_stochastic_graph_input():
    S = nx.stochastic_graph(nx.Graph())

@raises(nx.NetworkXNotImplemented)
def test_stochastic_multigraph_input():
    S = nx.stochastic_graph(nx.MultiGraph())
