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
    test.add_edge('a', 'c')
    test.add_edge('a', 'd')
    test.add_edge('d', 'c')
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
    
      
