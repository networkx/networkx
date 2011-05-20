#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestGeneratorsGeometric():
    def test_random_geometric_graph(self):
        G=nx.random_geometric_graph(50,0.25)
        assert_equal(len(G),50)

    def test_geographical_threshold_graph(self):
        G=nx.geographical_threshold_graph(50,100)
        assert_equal(len(G),50)

    def test_waxman_graph(self):
        G=nx.waxman_graph(50,0.5,0.1)
        assert_equal(len(G),50)
        G=nx.waxman_graph(50,0.5,0.1,L=1)
        assert_equal(len(G),50)
        
    def test_naviable_small_world(self):
        G = nx.navigable_small_world_graph(5,p=1,q=0)
        gg = nx.grid_2d_graph(5,5).to_directed()
        assert_true(nx.is_isomorphic(G,gg))

        G = nx.navigable_small_world_graph(5,p=1,q=0,dim=3)
        gg = nx.grid_graph([5,5,5]).to_directed()
        assert_true(nx.is_isomorphic(G,gg))

        G = nx.navigable_small_world_graph(5,p=1,q=0,dim=1)
        gg = nx.grid_graph([5]).to_directed()
        assert_true(nx.is_isomorphic(G,gg))
