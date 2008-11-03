#!/usr/bin/env python
import copy
import unittest
from nose.tools import *
import networkx
from test_graph import TestGraph


class TestMultiGraph(TestGraph):
    def setUp(self):
        self.Graph=networkx.MultiGraph
        # build K3
        self.k3adj={0: {1: [1], 2: [1]}, 
                    1: {0: [1], 2: [1]}, 
                    2: {0: [1], 1: [1]}}
        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        self.K3=self.Graph()
        self.K3.adj=self.k3adj


    def test_data_input(self):
        pass
#        G=self.Graph(data={1:[2],2:[1]}, name="test")
#        assert_equal(G.name,"test")
#        assert_equal(sorted(G.adj.items()),[(1, {2: [1]}), (2, {1: [1]})])


    def test_contains(self):
        G=self.K3
        assert(1 in G )
        assert(4 not in G )
        assert('b' not in G )
        assert([] not in G )   # no exception for nonhashable
        assert({1:1} not in G) # no exception for nonhashable

    def test_order(self):
        G=self.K3
        assert_equal(len(G),3)
        assert_equal(G.order(),3)
        assert_equal(G.number_of_nodes(),3)

    def test_getitem(self):
        G=self.K3
        assert_equal(G[0],{1: [1], 2: [1]})
        assert_raises(KeyError, G.__getitem__, 'j')
        assert_raises((TypeError,networkx.NetworkXError), G.__getitem__, ['A'])

    def test_remove_node(self):
        G=self.K3
        G.remove_node(0)
        assert_equal(G.adj,{1:{2:[1]},2:{1:[1]}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_node,-1)


    def test_add_edge(self):
        G=self.Graph()
        G.add_edge(0,1)
        assert_equal(G.adj,{0: {1: [1]}, 1: {0: [1]}})
        G=self.Graph()
        G.add_edge(*(0,1))
        assert_equal(G.adj,{0: {1: [1]}, 1: {0: [1]}})
    
    def test_add_edges_from(self):
        G=self.Graph()
        G.add_edges_from([(0,1)])
        assert_equal(G.adj,{0: {1: [1]}, 1: {0: [1]}})


    def test_remove_edge(self):
        G=self.K3
        G.remove_edge(0,1)
        assert_equal(G.adj,{0:{2:[1]},1:{2:[1]},2:{0:[1],1:[1]}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)

    def test_remove_edges_from(self):
        G=self.K3
        G.remove_edges_from([(0,1)])
        assert_equal(G.adj,{0:{2:[1]},1:{2:[1]},2:{0:[1],1:[1]}})
        G.remove_edges_from([(0,0)]) # silent fail

    def test_get_edge(self):
        G=self.K3
        assert_equal(G.get_edge(0,1),[1])
        assert_equal(G[0][1],[1])
        assert_raises((KeyError,networkx.NetworkXError), G.get_edge,-1,0)

    def test_adjacency_iter(self):
        G=self.K3
        assert_equal(dict(G.adjacency_iter()),
                          {0: {1: [1], 2: [1]}, 
                           1: {0: [1], 2: [1]},
                           2: {0: [1], 1: [1]}})
                          
    def test_to_directed(self):
        G=self.K3
        H=networkx.MultiDiGraph(G)
        assert_equal(G.adj,H.adj)
        assert_equal(G.adj,H.succ)
        assert_equal(G.adj,H.pred)
        H=G.to_directed()
        assert_equal(G.adj,H.adj)
        assert_equal(G.adj,H.succ)
        assert_equal(G.adj,H.pred)

    def test_selfloops(self):
        G=self.K3
        G.add_edge(0,0)
        assert_equal(G.nodes_with_selfloops(),[0])
        assert_equal(G.selfloop_edges(),[(0,0,1)])
        assert_equal(G.number_of_selfloops(),1)
