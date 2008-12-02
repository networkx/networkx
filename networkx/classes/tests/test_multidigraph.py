#!/usr/bin/env python
import copy
import unittest
from nose.tools import *
import networkx
from test_multigraph import TestMultiGraph


class TestMultiDiGraph(TestMultiGraph):
    def setUp(self):
        self.Graph=networkx.MultiDiGraph
        # build K3
        self.k3adj={0: {1: [1], 2: [1]}, 
                    1: {0: [1], 2: [1]}, 
                    2: {0: [1], 1: [1]}}
        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        self.K3=self.Graph()
        self.K3.adj=self.k3adj
        self.K3.pred=copy.deepcopy(self.k3adj)
        self.K3.succ=self.k3adj


    def test_data_input(self):
        G=self.Graph(data={1:[2],2:[1]}, name="test")
        assert_equal(G.name,"test")
        assert_equal(sorted(G.adj.items()),[(1, {2: [1]}), (2, {1: [1]})])
        assert_equal(sorted(G.succ.items()),[(1, {2: [1]}), (2, {1: [1]})])
        assert_equal(sorted(G.pred.items()),[(1, {2: [1]}), (2, {1: [1]})])


    def test_add_edge(self):
        G=self.Graph()
        G.add_edge(0,1)
        assert_equal(G.adj,{0: {1: [1]}, 1: {}})
        assert_equal(G.succ,{0: {1: [1]}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:[1]}})
        G=self.Graph()
        G.add_edge(*(0,1))
        assert_equal(G.adj,{0: {1: [1]}, 1: {}})
        assert_equal(G.succ,{0: {1: [1]}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:[1]}})


    
    def test_add_edges_from(self):
        G=self.Graph()
        G.add_edges_from([(0,1),(0,1,3)])
        assert_equal(G.adj,{0: {1: [1,3]}, 1: {}})
        assert_equal(G.succ,{0: {1: [1,3]}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:[1,3]}})
        G.add_edges_from([(0,1),(0,1,3)],data=2)
        assert_equal(G.succ,{0: {1: [1,3,2,3]}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:[1,3,2,3]}})

        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,)])  # too few in tuple
        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,1,2,3)])  # too many in tuple
        assert_raises(TypeError, G.add_edges_from,[0])  # not a tuple


    def test_remove_edge(self):
        G=self.K3
        G.remove_edge(0,1)
        assert_equal(G.succ,{0:{2:[1]},1:{0:[1],2:[1]},2:{0:[1],1:[1]}})        
        assert_equal(G.pred,{0:{1:[1], 2:[1]}, 1:{2:[1]}, 2:{0:[1],1:[1]}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)


    def test_remove_edges_from(self):
        G=self.K3
        G.remove_edges_from([(0,1)])
        assert_equal(G.succ,{0:{2:[1]},1:{0:[1],2:[1]},2:{0:[1],1:[1]}})        
        assert_equal(G.pred,{0:{1:[1], 2:[1]}, 1:{2:[1]}, 2:{0:[1],1:[1]}})
        G.remove_edges_from([(0,0)]) # silent fail


    def test_edges(self):
        G=self.K3
        assert_equal(sorted(G.edges()),[(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.edges(0)),[(0,1),(0,2)])
        assert_raises((KeyError,networkx.NetworkXError), G.neighbors,-1)


    def test_edges_iter(self):
        G=self.K3
        assert_equal(sorted(G.edges()),[(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.edges_iter(0)),[(0,1),(0,2)])
        assert_raises((KeyError,networkx.NetworkXError), G.neighbors_iter,-1)
        G.add_edge(0,1,2)
        assert_equal(sorted(G.edges(data=True)),[(0,1,1),(0,1,2),(0,2,1),(1,0,1),(1,2,1),(2,0,1),(2,1,1)])


    def test_copy(self):
        G=self.K3
        H=G.copy()
        assert_equal(G.succ,H.succ)
        assert_equal(G.pred,H.pred)

    def test_to_directed(self):
        G=self.K3
        H=networkx.MultiDiGraph(G)
        assert_equal(G.pred,H.pred)
        assert_equal(G.succ,H.succ)
        H=G.to_directed()
        assert_equal(G.pred,H.pred)
        assert_equal(G.succ,H.succ)

    def test_to_undirected(self):
        G=self.K3
        H=networkx.MultiGraph(G)
        assert_equal(G.adj,H.adj)

    def test_has_successor(self):
        G=self.K3
        assert_equal(G.has_successor(0,1),True)
        assert_equal(G.has_successor(0,-1),False)

    def test_successors(self):
        G=self.K3
        assert_equal(sorted(G.successors(0)),[1,2])
        assert_raises((KeyError,networkx.NetworkXError), G.successors,-1)

    def test_successors_iter(self):
        G=self.K3
        assert_equal(sorted(G.successors_iter(0)),[1,2])
        assert_raises((KeyError,networkx.NetworkXError), G.successors_iter,-1)

    def test_has_predecessor(self):
        G=self.K3
        assert_equal(G.has_predecessor(0,1),True)
        assert_equal(G.has_predecessor(0,-1),False)

    def test_predecessors(self):
        G=self.K3
        assert_equal(sorted(G.predecessors(0)),[1,2])
        assert_raises((KeyError,networkx.NetworkXError), G.predecessors,-1)

    def test_predecessors_iter(self):
        G=self.K3
        assert_equal(sorted(G.predecessors_iter(0)),[1,2])
        assert_raises((KeyError,networkx.NetworkXError), G.predecessors_iter,-1)


    def test_degree(self):
        G=self.K3
        assert_equal(G.degree(),[4,4,4])
        assert_equal(G.degree(with_labels=True),{0:4,1:4,2:4})
        assert_equal(G.degree(0),4)
        assert_equal(G.degree(0,with_labels=True),{0:4})
        assert_raises((KeyError,networkx.NetworkXError), G.degree,-1)

    def test_degree_iter(self):
        G=self.K3
        assert_equal(list(G.degree_iter()),[(0,4),(1,4),(2,4)])
        assert_equal(dict(G.degree_iter()),{0:4,1:4,2:4})
        assert_equal(list(G.degree_iter(0)),[(0,4)])


    def test_in_degree(self):
        G=self.K3
        assert_equal(G.in_degree(),[2,2,2])
        assert_equal(G.in_degree(with_labels=True),{0:2,1:2,2:2})
        assert_equal(G.in_degree(0),2)
        assert_equal(G.in_degree(0,with_labels=True),{0:2})
        assert_raises((KeyError,networkx.NetworkXError), G.in_degree,-1)

    def test_in_degree_iter(self):
        G=self.K3
        assert_equal(list(G.in_degree_iter()),[(0,2),(1,2),(2,2)])
        assert_equal(dict(G.in_degree_iter()),{0:2,1:2,2:2})
        assert_equal(list(G.in_degree_iter(0)),[(0,2)])

    def test_out_degree(self):
        G=self.K3
        assert_equal(G.out_degree(),[2,2,2])
        assert_equal(G.out_degree(with_labels=True),{0:2,1:2,2:2})
        assert_equal(G.out_degree(0),2)
        assert_equal(G.out_degree(0,with_labels=True),{0:2})
        assert_raises((KeyError,networkx.NetworkXError), G.out_degree,-1)

    def test_out_degree_iter(self):
        G=self.K3
        assert_equal(list(G.out_degree_iter()),[(0,2),(1,2),(2,2)])
        assert_equal(dict(G.out_degree_iter()),{0:2,1:2,2:2})
        assert_equal(list(G.out_degree_iter(0)),[(0,2)])


    def test_size(self):
        G=self.K3
        assert_equal(G.size(),6)
        assert_equal(G.number_of_edges(),6)

