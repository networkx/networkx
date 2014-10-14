#!/usr/bin/env python

from nose.tools import *
import networkx as nx
from networkx import girvan_newman

@raises(nx.NetworkXError)
def test_directed_not_supported():
    # not supported for directed graphs
    test = nx.DiGraph()
    test.add_edge('a','b')
    test.add_edge('a','c')
    test.add_edge('b','d')    
    result = girvan_newman.girvan_newman_communities(test)
    
@raises(nx.NetworkXError)
def test_no_communities_0():
    # more than one needed to detect communities
    test = nx.Graph()
    result = girvan_newman.girvan_newman_communities(test)
    
@raises(nx.NetworkXError)
def test_no_communities_1():
    # more than one needed to detect communities
    test = nx.Graph()
    test.add_node('a')
    result = girvan_newman.girvan_newman_communities(test)

def test_simple_communities():
    # When two edges have the same betweenness the one to be deleted is choosen
    # randomly, thats why the test graph must be very simple.
    test = nx.Graph()
    test.add_edge('a','b')
    test.add_edge('a','c')
    test.add_edge('b','d')    
    ground_truth = set([frozenset(['a', 'c']), 
                        frozenset(['a']), 
                        frozenset(['c']), 
                        frozenset(['b', 'd']), 
                        frozenset(['b']),
                        frozenset(['d'])])
    
    
    communities = girvan_newman.girvan_newman_communities(test)
    result = set()
    for c in communities:
        result.add(frozenset(c))
        
    assert_equal(result, ground_truth)
    
      
