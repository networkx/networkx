
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
    result = {frozenset(c) for c in communities}
    assert_equal(result, ground_truth)


def test_unconnected_communities():
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
    result = {frozenset(c) for c in communities} 
    assert_equal(result, ground_truth)

    
def test_connected_communities():
    test = nx.Graph()
    # community 1
    test.add_edge('a', 'b')
    test.add_edge('c', 'a')
    test.add_edge('c', 'b')
    test.add_edge('d', 'a')
    test.add_edge('d', 'b')
    test.add_edge('d', 'c')
    test.add_edge('e', 'a')
    test.add_edge('e', 'b')
    test.add_edge('e', 'c')
    test.add_edge('e', 'd')
    # community 2
    test.add_edge('1', '2')
    test.add_edge('3', '1')
    test.add_edge('3', '2')
    test.add_edge('4', '1')
    test.add_edge('4', '2')
    test.add_edge('4', '3')
    test.add_edge('5', '1')
    test.add_edge('5', '2')
    test.add_edge('5', '3')
    test.add_edge('5', '4')
    #edge between community 1 and 2    
    test.add_edge('a', '1')
    # community 3
    test.add_edge('x', 'y')
    # community 4 with only a single node
    test.add_node('z')
    
    # The expected communities are:    
    ground_truth = set([frozenset(['a','b','c','d','e']), 
                        frozenset(['1','2','3','4','5']), 
                        frozenset(['x', 'y']), 
                        frozenset(['z'])])
                        
    communities = label_propagation.label_propagation_communities(test)
    result = {frozenset(c) for c in communities} 
    assert_equal(result, ground_truth)
