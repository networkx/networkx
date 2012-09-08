import networkx as nx
from nose.tools import *

def test_affiliation():
    C = [set(range(5)),set(range(5,10))]
    for i in range(5):
        assert_equal([0],nx.affiliation(i,C))
    for i in range(5,10):
        assert_equal([1],nx.affiliation(i,C))

    C = [set(range(5)),set(range(2,7))]
    assert_equal([0,1],nx.affiliation(2,C))
    

def test_is_partition():
    C =[set(range(5)),set(range(5,10))]
    assert_true(nx.is_partition(range(10),C))
    C = [set(range(5)),set(range(4,10))]
    assert_false(nx.is_partition(range(10),C))

    
    
