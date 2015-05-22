#!/usr/bin/env python

from nose.tools import *
import networkx as nx
from networkx import label_propagation

@raises(nx.NetworkXNotImplemented)
def test_directed_not_supported():
    # not supported for directed graphs
    test = nx.DiGraph()
    test.add_edge('a','b')
    test.add_edge('a','c')
    test.add_edge('b','d')    
    result = label_propagation.label_propagation_communities(test)
    
def test_one_node():
    test = nx.Graph()
    test.add_node('a')
    
    # The expected communities are:    
    ground_truth = set([frozenset(['a'])])
    
    communities = label_propagation.label_propagation_communities(test)
    result = set()
    for c in communities:
        result.add(frozenset(c))  
    assert_equal(result, ground_truth)

def test_simple_communities():
    test = nx.Graph()
    # community 1
    test.add_edge('a', 'c')
    test.add_edge('a', 'd')
    test.add_edge('d', 'c')
    # community 2
    test.add_edge('b', 'e')
    test.add_edge('e', 'f')
    test.add_edge('f', 'b')
    
    # The expected communities are:    
    ground_truth = set([frozenset(['a', 'c', 'd']), 
                        frozenset(['b', 'e', 'f'])])
    
    communities = label_propagation.label_propagation_communities(test)
    result = set()
    for c in communities:
        result.add(frozenset(c))  
    assert_equal(result, ground_truth)
    
def test_unconnected_communities():
    test = nx.Graph()
    # community 1
    test.add_edge('a', 'b')
    test.add_edge('c', 'b')
    test.add_edge('a', 'c')
    # community 2
    test.add_edge('d', 'e')
    test.add_edge('e', 'f')
    test.add_edge('f', 'd')
    # connection from community 1 to community 2
    test.add_edge('a', 'd')
    # community 3
    test.add_edge('w', 'y')
    # community 4 with only a single node
    test.add_node('z')
    
    # The expected communities are:    
    ground_truth = set([frozenset(['z']), 
                        frozenset(['a', 'c', 'b']), 
                        frozenset(['e', 'd', 'f']), 
                        frozenset(['y', 'w'])])
                        
    communities = label_propagation.label_propagation_communities(test)
    result = set()
    for c in communities:
        result.add(frozenset(c))  
    assert_equal(result, ground_truth)
    
      
