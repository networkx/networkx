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
    
