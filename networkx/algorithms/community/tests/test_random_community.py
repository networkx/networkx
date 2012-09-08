import networkx as nx
from nose.tools import *

def test_random_partition():
    assert_raises(nx.NetworkXError,
                  nx.random_partition,
                  range(10),
                  number_of_partitions=None,
                  partition_sizes=None)
    assert_raises(nx.NetworkXError,
                  nx.random_partition,
                  range(10),
                  number_of_partitions=None,
                  partition_sizes=[1,12])
    C = nx.random_partition(range(10),number_of_partitions=3)
    assert_true(nx.is_partition(range(10),C))

    for i in range(10):
        assert_equal(1,len(nx.affiliation(i,C)))

    C = [set(range(5)),set(range(2,6))]
    assert_false(nx.is_partition(range(6),C))

    C = nx.random_partition(range(10),partition_sizes=[3,7])
    assert_equal(len(C[0]),3)
    assert_equal(len(C[1]),7)
    
def test_random_p_community():
    assert_raises(nx.NetworkXError,
                  nx.random_p_community,
                  range(10),
                  .1,
                  number_of_communities=None)
    
    C = nx.random_p_community(range(10),1.0,5)

    assert_equal(5,len(C))

    for c in C:
        assert_equal(c,set(range(10)))

    C = nx.random_p_community(range(10),0.0,5)

    assert_equal(5,len(C))

    for c in C:
        assert_equal(c,set())

    C = nx.random_p_community(range(10),[0.0,1.0,0.0])

    assert_equal(len(C),3)
    assert_equal(C[0],set())
    assert_equal(C[1],set(range(10)))
    assert_equal(C[2],set())

def test_random_m_community():

    assert_raises(nx.NetworkXError,
                  nx.random_m_community,
                  range(10),
                  3,
                  number_of_communities=None)

    assert_raises(nx.NetworkXError,
                  nx.random_m_community,
                  range(10),
                  [1,12],
                  number_of_communities=None)
    
    C = nx.random_m_community(range(10),10,5)
    assert_equal(5,len(C))
    for c in C:
        assert_equal(c,set(range(10)))


    C = nx.random_m_community(range(10),0,5)
    assert_equal(5,len(C))
    for c in C:
        assert_equal(c,set())

    C = nx.random_m_community(range(10),[0,1,3,5,10])
    assert_equal(len(C),5)
    assert_equal(C[0],set())
    assert_equal(len(C[1]),1)
    assert_equal(len(C[2]),3)
    assert_equal(len(C[3]),5)
    assert_equal(C[4],set(range(10)))
