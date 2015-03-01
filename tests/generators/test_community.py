import networkx as nx
from nose.tools import *

def test_random_partition_graph():
    G = nx.random_partition_graph([3,3,3],1,0)
    C = G.graph['partition'] 
    assert_equal(C,[set([0,1,2]), set([3,4,5]), set([6,7,8])])
    assert_equal(len(G),9)
    assert_equal(len(G.edges()),9)

    G = nx.random_partition_graph([3,3,3],0,1)
    C = G.graph['partition'] 
    assert_equal(C,[set([0,1,2]), set([3,4,5]), set([6,7,8])])
    assert_equal(len(G),9)
    assert_equal(len(G.edges()),27)

    G = nx.random_partition_graph([3,3,3],1,0,directed=True)
    C = G.graph['partition'] 
    assert_equal(C,[set([0,1,2]), set([3,4,5]), set([6,7,8])])
    assert_equal(len(G),9)
    assert_equal(len(G.edges()),18)

    G = nx.random_partition_graph([3,3,3],0,1,directed=True)
    C = G.graph['partition'] 
    assert_equal(C,[set([0,1,2]), set([3,4,5]), set([6,7,8])])
    assert_equal(len(G),9)
    assert_equal(len(G.edges()),54)

    G = nx.random_partition_graph([1,2,3,4,5], 0.5, 0.1)
    C = G.graph['partition'] 
    assert_equal(C,[set([0]), set([1,2]), set([3,4,5]),
                    set([6,7,8,9]), set([10,11,12,13,14])])
    assert_equal(len(G),15)

    assert_raises(nx.NetworkXError, nx.random_partition_graph,[1,2,3],1.1,0.1)
    assert_raises(nx.NetworkXError, nx.random_partition_graph,[1,2,3],-0.1,0.1)
    assert_raises(nx.NetworkXError, nx.random_partition_graph,[1,2,3],0.1,1.1)
    assert_raises(nx.NetworkXError, nx.random_partition_graph,[1,2,3],0.1,-0.1)

def test_planted_partition_graph():
    G = nx.planted_partition_graph(4,3,1,0)
    C = G.graph['partition'] 
    assert_equal(len(C),4)
    assert_equal(len(G),12)
    assert_equal(len(G.edges()),12)

    G = nx.planted_partition_graph(4,3,0,1)
    C = G.graph['partition'] 
    assert_equal(len(C),4)
    assert_equal(len(G),12)
    assert_equal(len(G.edges()),54)

    G = nx.planted_partition_graph(10,4,.5,.1,seed=42)
    C = G.graph['partition']
    assert_equal(len(C),10)
    assert_equal(len(G),40)
    assert_equal(len(G.edges()),108)

    G = nx.planted_partition_graph(4,3,1,0,directed=True)
    C = G.graph['partition'] 
    assert_equal(len(C),4)
    assert_equal(len(G),12)
    assert_equal(len(G.edges()),24)

    G = nx.planted_partition_graph(4,3,0,1,directed=True)
    C = G.graph['partition'] 
    assert_equal(len(C),4)
    assert_equal(len(G),12)
    assert_equal(len(G.edges()),108)

    G = nx.planted_partition_graph(10,4,.5,.1,seed=42,directed=True)
    C = G.graph['partition'] 
    assert_equal(len(C),10)
    assert_equal(len(G),40)
    assert_equal(len(G.edges()),218)

    assert_raises(nx.NetworkXError, nx.planted_partition_graph, 3, 3, 1.1, 0.1)
    assert_raises(nx.NetworkXError, nx.planted_partition_graph, 3, 3,-0.1, 0.1)
    assert_raises(nx.NetworkXError, nx.planted_partition_graph, 3, 3, 0.1, 1.1)
    assert_raises(nx.NetworkXError, nx.planted_partition_graph, 3, 3, 0.1,-0.1)
    
def test_relaxed_caveman_graph():
    G = nx.relaxed_caveman_graph(4,3,0)
    assert_equal(len(G),12)
    assert_equal(len(G.nodes()),12)
    
    G = nx.relaxed_caveman_graph(4,3,1)
    assert_equal(len(G),12)
    assert_equal(len(G.nodes()),12)

    G = nx.relaxed_caveman_graph(4,3,0.5)
    assert_equal(len(G),12)
    assert_equal(len(G.edges()),12)

def test_connected_caveman_graph():
    G = nx.connected_caveman_graph(4,3)
    assert_equal(len(G),12)
    assert_equal(len(G.nodes()),12)
    
    G = nx.connected_caveman_graph(1,5)
    K5 = nx.complete_graph(5)
    K5.remove_edge(3,4)
    assert_true(nx.is_isomorphic(G,K5))

def test_caveman_graph():
    G = nx.caveman_graph(4,3)
    assert_equal(len(G),12)
    assert_equal(len(G.nodes()),12)
    
    G = nx.caveman_graph(1,5)
    K5 = nx.complete_graph(5)
    assert_true(nx.is_isomorphic(G,K5))

def test_gaussian_random_partition_graph():
    G = nx.gaussian_random_partition_graph(100, 10, 10, 0.3, 0.01)
    assert_equal(len(G),100)
    assert_raises(nx.NetworkXError,
                  nx.gaussian_random_partition_graph, 100, 101, 10, 1, 0)

