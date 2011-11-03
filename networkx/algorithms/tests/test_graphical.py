#!/usr/bin/env python
from nose.tools import *
import networkx as nx

def test_valid_degree_sequence1():
    n = 100
    p = .3
    for i in range(10):
        G = nx.erdos_renyi_graph(n,p)
        deg = list(G.degree().values())
        assert_true( nx.is_valid_degree_sequence(deg, method='eg') )
        assert_true( nx.is_valid_degree_sequence(deg, method='hh') )        

def test_valid_degree_sequence2():
    n = 100
    for i in range(10):
        G = nx.barabasi_albert_graph(n,1)
        deg = list(G.degree().values())
        assert_true( nx.is_valid_degree_sequence(deg, method='eg') )
        assert_true( nx.is_valid_degree_sequence(deg, method='hh') )        

def test_atlas():
    for graph in nx.graph_atlas_g():
        deg = list(graph.degree().values())
        assert_true( nx.is_valid_degree_sequence(deg, method='eg') )
        assert_true( nx.is_valid_degree_sequence(deg, method='hh') )        
        
def test_small_graph_true():
        z=[5,3,3,3,3,2,2,2,1,1,1]
        assert_true(nx.is_valid_degree_sequence(z, method='hh'))
        assert_true(nx.is_valid_degree_sequence(z, method='eg'))       
        z=[10,3,3,3,3,2,2,2,2,2,2]
        assert_true(nx.is_valid_degree_sequence(z, method='hh'))
        assert_true(nx.is_valid_degree_sequence(z, method='eg'))        
        z=[1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
        assert_true(nx.is_valid_degree_sequence(z, method='hh'))
        assert_true(nx.is_valid_degree_sequence(z, method='eg'))        



def test_small_graph_false():
        z=[1000,3,3,3,3,2,2,2,1,1,1]
        assert_false(nx.is_valid_degree_sequence(z, method='hh'))
        assert_false(nx.is_valid_degree_sequence(z, method='eg'))
        z=[6,5,4,4,2,1,1,1]
        assert_false(nx.is_valid_degree_sequence(z, method='hh'))
        assert_false(nx.is_valid_degree_sequence(z, method='eg'))
        z=[1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
        assert_false(nx.is_valid_degree_sequence(z, method='hh'))
        assert_false(nx.is_valid_degree_sequence(z, method='eg'))        


