#!/usr/bin/env python

from nose.tools import assert_equal
import networkx as nx
from networkx import demon

def test_simple_communities():
    
    test = nx.Graph()
    
    # community 1
    test.add_edge('a', 'b')
    test.add_edge('c', 'b')
    test.add_edge('a', 'c')
    test.add_edge('a', 'd')
    test.add_edge('b', 'd')
    test.add_edge('c', 'd')
    
    # community 2
    test.add_edge('e', 'f')
    test.add_edge('e', 'g')
    test.add_edge('e', 'h')
    test.add_edge('f', 'g')
    test.add_edge('f', 'h')
    test.add_edge('h', 'g')

    # connection from community 1 to community 2
    test.add_edge('a', 'middle')
    test.add_edge('e', 'middle')

    # The expected communities are:    
    ground_truth = set([frozenset(['a', 'b', 'c', 'd']), 
                        frozenset(['e', 'f', 'g', 'h'])])
    
    communities = demon.demon_communities(test, 0.25, 3, None)
    result = set()
    for c in communities:
        result.add(frozenset(c))  
    assert_equal(result, ground_truth)
    

def test_karate():
    test = nx.karate_club_graph()
    
    # The expected communities are:    
    ground_truth = set([frozenset([0, 16, 4, 5, 6, 10]), 
                        frozenset([0, 1, 2, 3, 7, 8, 12, 13, 14, 15, 17, 18, 
                                   19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 
                                   32, 33])])
    
    communities = demon.demon_communities(test, 0.25, 3, None)
    result = set()
    for c in communities:
        result.add(frozenset(c))  
    assert_equal(result, ground_truth)
    

def test_min_number_of_nodes():
    test = nx.Graph()
    
    # community 1
    test.add_edge('a', 'b')
    test.add_edge('c', 'b')
    test.add_edge('a', 'c')
    test.add_edge('a', 'd')
    test.add_edge('b', 'd')
    test.add_edge('c', 'd')
    
    # community 2
    test.add_edge('e', 'f')
    test.add_edge('e', 'h')
    test.add_edge('f', 'h')   

    #******************* min_community_size = 3 *******************

    communities1 = demon.demon_communities(test, 0.25, 3, None)   
    
    # The expected communities are:    
    ground_truth1 = set([frozenset(['a', 'c', 'b', 'd'])])   
     
    result1 = set()
    for c in communities1:
        result1.add(frozenset(c))  
        
    assert_equal(result1, ground_truth1)
      
    #******************* min_community_size = 2 *******************
    
    communities2 = demon.demon_communities(test, 0.25, 2, None)   
    
    # The expected communities are:    
    ground_truth2 = set([frozenset(['a', 'b', 'c', 'd']), 
                        frozenset(['h', 'e', 'f'])])  
      
    result2 = set()
    for c in communities2:
        result2.add(frozenset(c))  
        
    assert_equal(result2, ground_truth2)