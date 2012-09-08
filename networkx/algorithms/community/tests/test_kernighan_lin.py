import networkx as nx
from nose.tools import *

def assert_partition_equal(x,y):
    assert_equal(set(map(frozenset,x)),set(map(frozenset,y)))

def test_kernighan_lin():
    G = nx.barbell_graph(3,0)
    C = nx.kernighan_lin_bisection(G)
    assert_partition_equal(C,[set([0,1,2]),set([3,4,5])])

    assert_raises(nx.NetworkXError, nx.kernighan_lin_bisection, G,
                  partition=[set(range(3)),set(range(2,6))])
    assert_raises(nx.NetworkXError, nx.kernighan_lin_bisection, G,
                  partition=[set(range(2)),set(range(2,3)),set(range(3,6))])


def test_kernighan_lin_multigraph():
    G = nx.cycle_graph(4)
    M = nx.MultiGraph(G.edges())
    M.add_edges_from(G.edges())
    M.remove_edge(1,2)
    A,B = nx.kernighan_lin_bisection(M)
    assert_partition_equal([A,B],[set([0,1]),set([2,3])])

