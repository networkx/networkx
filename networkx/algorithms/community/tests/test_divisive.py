import networkx as nx
from nose.tools import *

def test_edge_betweenness_partition():
    G = nx.barbell_graph(3,0)
    C = nx.edge_betweenness_partition(G,2)
    assert_equal([set([0,1,2]),set([3,4,5])],C)

    G = nx.barbell_graph(3,1)
    C = nx.edge_betweenness_partition(G,3)
    assert_equal(C,[set([0,1,2]),set([4,5,6]),set([3])])

    C = nx.edge_betweenness_partition(G,7)
    assert_equal(map(set,[[n] for n in G]),C)

    C = nx.edge_betweenness_partition(G,1)
    assert_equal([set(G)],C)

    assert_raises(nx.NetworkXError,
                  nx.edge_betweenness_partition,
                  G,
                  0)

    assert_raises(nx.NetworkXError,
                  nx.edge_betweenness_partition,
                  G,
                  -1)
    assert_raises(nx.NetworkXError,
                  nx.edge_betweenness_partition,
                  G,
                  10)

def test_edge_current_flow_betweenness_partition():
    G = nx.barbell_graph(3,0)
    C = nx.edge_current_flow_betweenness_partition(G,2)
    assert_equal([set([0,1,2]),set([3,4,5])],C)

    G = nx.barbell_graph(3,1)
    C = nx.edge_current_flow_betweenness_partition(G,7)
    assert_equal(map(set,[[n] for n in G]),C)

    C = nx.edge_current_flow_betweenness_partition(G,1)
    assert_equal([set(G)],C)

    assert_raises(nx.NetworkXError,
                  nx.edge_current_flow_betweenness_partition,
                  G,
                  0)

    assert_raises(nx.NetworkXError,
                  nx.edge_current_flow_betweenness_partition,
                  G,
                  -1)
    assert_raises(nx.NetworkXError,
                  nx.edge_current_flow_betweenness_partition,
                  G,
                  10)
