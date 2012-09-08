import networkx as nx
from nose.tools import *

def assert_partition_equal(x,y):
    assert_equal(set(map(frozenset,x)),set(map(frozenset,y)))

def test_greedy_max_modularity_partition():
    G = nx.barbell_graph(3,0)

    C = nx.greedy_max_modularity_partition(G)

    if 0 in C[0]:
        assert_equal(C,[set([0,1,2]),set([3,4,5])])
    else:
        assert_equal(C,[set([3,4,5]),set([0,1,2])])

    assert_raises(nx.NetworkXError,
                  nx.greedy_max_modularity_partition,
                  G,
                  C_init=[set(range(3)),set(range(2,6))])
    assert_raises(nx.NetworkXError,
                  nx.greedy_max_modularity_partition,
                  G,
                  C_init=[set(range(2)),set(range(2,3)),set(range(3,6))])

    G = nx.MultiGraph()

    assert_raises(nx.NetworkXError,
                  nx.greedy_max_modularity_partition,
                  G)

def test_spectral_modularity_partition():
    G = nx.barbell_graph(3,0)
    C = nx.spectral_modularity_partition(G)
    assert_partition_equal(C,[[3,4,5],[0,1,2]])
    G = nx.karate_club_graph()
    C = nx.spectral_modularity_partition(G)
    assert_partition_equal(C,[[0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21],
                              [8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]])
