import networkx as nx
from nose.tools import *

def assert_partition_equal(x,y):
    assert_equal(set(map(frozenset,x)),set(map(frozenset,y)))

def test_spectral_partition():
    G = nx.barbell_graph(3,0)
    C = nx.spectral_bisection(G)
    assert_partition_equal(C,[[0,1,2],[3,4,5]])
    mapping=dict(enumerate('badfec'))

    G = nx.relabel_nodes(G,mapping)
    C = nx.spectral_bisection(G)
    assert_partition_equal(C,[[mapping[0],mapping[1],mapping[2]],
                              [mapping[3],mapping[4],mapping[5]]])
#    assert_raises(nx.NetworkXError,
#                  nx.spectral_partition, G, size=0)
#    assert_raises(nx.NetworkXError,
#                  nx.spectral_partition ,G, size=6)
