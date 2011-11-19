from nose.tools import assert_true, assert_equal,assert_raises
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


def test_stochastic_error():
    G=nx.Graph()
    assert_raises(Exception,nx.stochastic_graph,G)
    G=nx.MultiGraph()
    assert_raises(Exception,nx.stochastic_graph,G)
