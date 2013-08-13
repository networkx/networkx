from nose.tools import assert_equal, assert_true, assert_false, raises
import networkx as nx

def test_dominating_set():
    G = nx.gnp_random_graph(100,0.1)
    D = nx.dominating_set(G)
    assert_true(nx.is_dominating_set(G,D))
    D = nx.dominating_set(G, start_with=0)
    assert_true(nx.is_dominating_set(G,D))

@raises(nx.NetworkXError)
def test_dominating_set_error():
    G = nx.path_graph(4)
    D = nx.dominating_set(G, start_with=10)

def test_is_dominating_set():
    G = nx.path_graph(4)
    d = set([1,3])
    assert_true(nx.is_dominating_set(G,d))
    d = set([0,2])
    assert_true(nx.is_dominating_set(G,d))
    d = set([1])
    assert_false(nx.is_dominating_set(G,d))
