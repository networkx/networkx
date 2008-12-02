#!/usr/bin/env python
import copy
import unittest
from nose.tools import *
import networkx

class TestGraph:

    def setUp(self):
        self.Graph=networkx.Graph
        # build K3
        self.k3adj={0: {1: 1, 2: 1}, 1: {0: 1, 2: 1}, 2: {0: 1, 1: 1}}
        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        self.K3=self.Graph()
        self.K3.adj=self.k3adj


    def test_name(self):
        G=self.Graph(name='')
        assert_equal(G.name,"")
        G=self.Graph(name='test')
        assert_equal(G.__str__(),"test")
        assert_equal(G.name,"test")

    def test_data_input(self):
        G=self.Graph(data={1:[2],2:[1]}, name="test")
        assert_equal(G.name,"test")
        assert_equal(sorted(G.adj.items()),[(1, {2: 1}), (2, {1: 1})])
        G=self.Graph({1:[2],2:[1]}, name="test")
        assert_equal(G.name,"test")
        assert_equal(sorted(G.adj.items()),[(1, {2: 1}), (2, {1: 1})])


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
        assert_equal(G[0],{1: 1, 2: 1})
        assert_raises(KeyError, G.__getitem__, 'j')
        assert_raises((TypeError,networkx.NetworkXError), G.__getitem__, ['A'])

    def test_add_node(self):
        G=self.Graph()
        G.add_node(0)
        assert_equal(G.adj,{0:{}})
    
    def test_add_nodes_from(self):
        G=self.Graph()
        G.add_nodes_from([0,1,2])
        assert_equal(G.adj,{0:{},1:{},2:{}})

    def test_remove_node(self):
        G=self.K3
        G.remove_node(0)
        assert_equal(G.adj,{1:{2:1},2:{1:1}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_node,-1)

        # generator here to implement list,set,string...
    def test_remove_nodes_from(self):
        G=self.K3
        G.remove_nodes_from([0,1])
        assert_equal(G.adj,{2:{}})
        G.remove_nodes_from([-1]) # silent fail


    def test_nodes_iter(self):
        G=self.K3
        assert_equal(sorted(G.nodes_iter()),self.k3nodes)

    def test_nodes(self):
        G=self.K3
        assert_equal(sorted(G.nodes()),self.k3nodes)

    def test_has_node(self):
        G=self.K3
        assert(G.has_node(1))
        assert(not G.has_node(4))
        assert(not G.has_node([]))   # no exception for nonhashable
        assert(not G.has_node({1:1})) # no exception for nonhashable


    def test_add_edge(self):
        G=self.Graph()
        G.add_edge(0,1)
        assert_equal(G.adj,{0: {1: 1}, 1: {0: 1}})
        G=self.Graph()
        G.add_edge(*(0,1))
        assert_equal(G.adj,{0: {1: 1}, 1: {0: 1}})
    
    def test_add_edges_from(self):
        G=self.Graph()
        G.add_edges_from([(0,1),(0,2,3)])
        assert_equal(G.adj,{0: {1:1, 2:3}, 1: {0:1}, 2:{0:3}})
        G.add_edges_from([(0,1),(0,2,3)],data=2)
        assert_equal(G.adj,{0: {1:2, 2:3}, 1: {0:2}, 2:{0:3}})

        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,)])  # too few in tuple
        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,1,2,3)])  # too many in tuple
        assert_raises(TypeError, G.add_edges_from,[0])  # not a tuple


    def test_remove_edge(self):
        G=self.K3
        G.remove_edge(0,1)
        assert_equal(G.adj,{0:{2:1},1:{2:1},2:{0:1,1:1}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)

    def test_remove_edges_from(self):
        G=self.K3
        G.remove_edges_from([(0,1)])
        assert_equal(G.adj,{0:{2:1},1:{2:1},2:{0:1,1:1}})
        G.remove_edges_from([(0,0)]) # silent fail

    def test_has_edge(self):
        G=self.K3
        assert_equal(G.has_edge(0,1),True)
        assert_equal(G.has_edge(0,-1),False)

    def test_has_neighbor(self):
        G=self.K3
        assert_equal(G.has_neighbor(0,1),True)
        assert_equal(G.has_neighbor(0,-1),False)

    def test_neighbors(self):
        G=self.K3
        assert_equal(sorted(G.neighbors(0)),[1,2])
        assert_raises((KeyError,networkx.NetworkXError), G.neighbors,-1)

    def test_neighbors_iter(self):
        G=self.K3
        assert_equal(sorted(G.neighbors_iter(0)),[1,2])
        assert_raises((KeyError,networkx.NetworkXError), G.neighbors_iter,-1)

    def test_edges(self):
        G=self.K3
        assert_equal(sorted(G.edges()),[(0,1),(0,2),(1,2)])
        assert_equal(sorted(G.edges(0)),[(0,1),(0,2)])
        assert_raises((KeyError,networkx.NetworkXError), G.neighbors,-1)

    def test_edges_iter(self):
        G=self.K3
        assert_equal(sorted(G.edges_iter()),[(0,1),(0,2),(1,2)])
        assert_equal(sorted(G.edges_iter(0)),[(0,1),(0,2)])
        assert_raises((KeyError,networkx.NetworkXError), G.neighbors_iter,-1)

    def test_get_edge(self):
        G=self.K3
        assert_equal(G.get_edge(0,1),1)
        assert_equal(G[0][1],1)
        assert_raises((KeyError,networkx.NetworkXError), G.get_edge,-1,0)

    def test_adjacency_list(self):
        G=self.K3
        assert_equal(G.adjacency_list(),[[1,2],[0,2],[0,1]])

    def test_adjacency_iter(self):
        G=self.K3
        assert_equal(dict(G.adjacency_iter()),
                          {0: {1: 1, 2: 1}, 1: {0: 1, 2: 1}, 2: {0: 1, 1: 1}})
                          
    def test_degree(self):
        G=self.K3
        assert_equal(G.degree(),[2,2,2])
        assert_equal(G.degree(with_labels=True),{0:2,1:2,2:2})
        assert_equal(G.degree(0),2)
        assert_equal(G.degree(0,with_labels=True),{0:2})
        assert_raises((KeyError,networkx.NetworkXError), G.degree,-1)

    def test_degree_iter(self):
        G=self.K3
        assert_equal(list(G.degree_iter()),[(0,2),(1,2),(2,2)])
        assert_equal(dict(G.degree_iter()),{0:2,1:2,2:2})
        assert_equal(list(G.degree_iter(0)),[(0,2)])

    def test_clear(self):
        G=self.K3
        G.clear()
        assert_equal(G.adj,{})

    def test_copy(self):
        G=self.K3
        H=G.copy()
        assert_equal(G.adj,H.adj)
        H=G.__class__(G) # just copy
        assert_equal(G.adj,H.adj)

    def test_to_undirected(self):
        G=self.K3
        H=G.to_undirected()
        assert_equal(G.adj,H.adj)

    def test_to_directed(self):
        G=self.K3
        H=networkx.DiGraph(G)
        assert_equal(G.adj,H.adj)
        assert_equal(G.adj,H.succ)
        assert_equal(G.adj,H.pred)
        H=G.to_directed()
        assert_equal(G.adj,H.adj)
        assert_equal(G.adj,H.succ)
        assert_equal(G.adj,H.pred)

    def test_subgraph(self):
        G=self.K3
        H=G.subgraph([0,1,2])
        assert_equal(H.adj,G.adj) 
        H=G.subgraph(0)
        assert_equal(H.adj,{0:{}})
        H=G.subgraph([])
        assert_equal(H.adj,{})
        H=G.subgraph([],copy=False)
        assert_equal(H.adj,{})
        assert_equal(G.adj,{})
        assert_equal(G.adj,H.adj)

    def test_selfloops(self):
        G=self.K3.copy()
        G.add_edge(0,0)
        assert_equal(G.nodes_with_selfloops(),[0])
        assert_equal(G.selfloop_edges(data=True),[(0,0,1)])
        assert_equal(G.number_of_selfloops(),1)
        G.remove_node(0)
        assert_equal(G.order(),2)
        G=self.K3
        G.add_edge(0,0)
        G.add_edge(1,1)
        G.remove_nodes_from([0,1])
        assert_equal(G.order(),1)

    def test_size(self):
        G=self.K3
        assert_equal(G.size(),3)
        assert_equal(G.number_of_edges(),3)

    def test_add_star(self):
        G=self.K3.copy()
        nlist=[12,13,14,15]
        G.add_star(nlist)
        assert_equal(sorted(G.edges(nlist)),[(12,13),(12,14),(12,15)])
        G=self.K3.copy()
        data=[2.,3.,4.]
        G.add_star(nlist,data)
        assert_equal(sorted(G.edges(nlist,data=True)),[(12,13,2.),(12,14,3.),(12,15,4.)])

    def test_add_path(self):
        G=self.K3.copy()
        nlist=[12,13,14,15]
        G.add_path(nlist)
        assert_equal(sorted(G.edges(nlist)),[(12,13),(13,14),(14,15)])
        G=self.K3.copy()
        data=[2.,3.,4.]
        G.add_path(nlist,data)
        assert_equal(sorted(G.edges(nlist,data=True)),[(12,13,2.),(13,14,3.),(14,15,4.)])

    def test_add_cycle(self):
        G=self.K3.copy()
        nlist=[12,13,14,15]
        oklists=[ [(12,13),(12,15),(13,14),(14,15)], [(12,13),(13,14),(14,15),(15,12)] ]
        G.add_cycle(nlist)
        assert_true(sorted(G.edges(nlist)) in oklists)
        G=self.K3.copy()
        data=[2.,3.,4.,5.]
        oklists=[ [(12,13,2.),(12,15,5.),(13,14,3.),(14,15,4.)], [(12,13,2.),(13,14,3.),(14,15,4.),(15,12,5.)] ]
        G.add_cycle(nlist,data)
        assert_true(sorted(G.edges(nlist,data=True)) in oklists)

    def test_nbunch_iter(self):
        G=self.K3
        assert_equal(list(G.nbunch_iter()),self.k3nodes) # all nodes
        assert_equal(list(G.nbunch_iter(0)),[0]) # single node
        assert_equal(list(G.nbunch_iter([0,1])),[0,1]) # sequence
        assert_equal(list(G.nbunch_iter([-1])),[]) # sequence with none in graph
        assert_equal(list(G.nbunch_iter("foo")),[]) # string sequence with none in graph
        bunch=G.nbunch_iter(-1)    # nonsequence not in graph doesn't get caught upon creation of iterator
        assert_raises(networkx.NetworkXError,bunch.next) # but gets caught when iterator used
        bunch=G.nbunch_iter([0,1,2,{}])    # unhashable doesn't get caught upon creation of iterator
        assert_raises(networkx.NetworkXError,list,bunch) # but gets caught when iterator hits the unhashable




