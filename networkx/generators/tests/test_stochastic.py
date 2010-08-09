from nose.tools import assert_true, assert_equal
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

