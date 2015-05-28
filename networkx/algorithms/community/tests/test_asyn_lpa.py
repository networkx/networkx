#!/usr/bin/env python
from nose.tools import assert_equal
from networkx import asyn_lpa, Graph

def test_simple_communities():
    test = Graph()
    
    # c1
    test.add_edge('a', 'b')
    test.add_edge('a', 'c')
    test.add_edge('b', 'c')
    
    # c2
    test.add_edge('d', 'e')
    test.add_edge('d', 'f')
    test.add_edge('f', 'e')
    
    # ground truth
    ground_truth = set([frozenset(['a', 'c', 'b']), 
                        frozenset(['e', 'd', 'f'])])
                        
    communities = asyn_lpa.asyn_lpa_communities(test)
    result = set()
    for c in communities:
        result.add(frozenset(c))  
    assert_equal(result, ground_truth)
    
def test_single_node():
    test = Graph()
    
    test.add_node('a')
    
    # ground truth
    ground_truth = set([frozenset(['a'])])
                        
    communities = asyn_lpa.asyn_lpa_communities(test)
    result = set()
    for c in communities:
        result.add(frozenset(c))  
    assert_equal(result, ground_truth)