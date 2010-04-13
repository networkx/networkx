#!/usr/bin/env python
import copy
import unittest
from nose.tools import *
import networkx
from test_graph import TestGraph

class TestGraphView(TestGraph):

    def setUp(self):
        def newgraphview(data=None,*args,**kwds):
            if data is None:
                data={0:{}, 1:{}, 2:{}}
            G=networkx.Graph(data,*args,**kwds)
            return networkx.GraphView(G,[1,2])
        self.Graph=newgraphview
        # build K3
        ed1,ed2,ed3 = ({},{},{})
        self.k3adj={0: {1: ed1, 2: ed2}, 
                    1: {0: ed1, 2: ed3}, 
                    2: {0: ed2, 1: ed3}}
        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        K3=self.Graph()
        K3.adj=K3.edge=self.k3adj
        K3.node={}
        K3.node[0]={}
        K3.node[1]={}
        K3.node[2]={}
        self.K3=K3.subgraphview([0,1,2])

    def add_attributes(self,G):
        G.graph['foo']=[]
        G.node[0]['foo']=[]
        ll=[]
        G.adj[1][2]['foo']=ll
        G.adj[2][1]['foo']=ll

    def test_copy_attr(self):
        G=self.K3
        G.graph['foo']=[]
        G.node[0]['foo']=[]
        G.adj[1][2]['foo']=[]

    def test_add_node(self):
        assert_raises(networkx.NetworkXError, self.K3.add_node, 0)
    def test_add_nodes_from(self):
        assert_raises(networkx.NetworkXError, self.K3.add_nodes_from, [0])
    def test_remove_node(self):
        assert_raises(networkx.NetworkXError, self.K3.remove_node, 0)
    def test_remove_nodes_from(self):
        assert_raises(networkx.NetworkXError, self.K3.remove_nodes_from, [0])
    def test_add_edge(self):
        assert_raises(networkx.NetworkXError, self.K3.add_edge, 0, 1)
    def test_add_edges_from(self):
        assert_raises(networkx.NetworkXError, self.K3.add_edges_from, [(0,1)])
    def test_remove_edge(self):
        assert_raises(networkx.NetworkXError, self.K3.remove_edge, 0, 1)
    def test_remove_edges_from(self):
        assert_raises(networkx.NetworkXError, self.K3.remove_edges_from, [(0,1)])
    def test_clear(self):
        assert_raises(networkx.NetworkXError, self.K3.clear)
    def test_copy(self):
        assert_raises(networkx.NetworkXError, self.K3.copy)
    def test_to_undirected(self):
        assert_raises(networkx.NetworkXError, self.K3.to_undirected)
    def test_to_directed(self):
        assert_raises(networkx.NetworkXError, self.K3.to_directed)
    def test_subgraph(self):
        assert_raises(networkx.NetworkXError, self.K3.subgraph, 0)
    def test_add_star(self):
        assert_raises(networkx.NetworkXError, self.K3.add_star, 0)
    def test_add_path(self):
        assert_raises(networkx.NetworkXError, self.K3.add_path, 0)
    def test_add_cycle(self):
        assert_raises(networkx.NetworkXError, self.K3.add_cycle, 0)
    def test_selfloops(self):
        pass
    def test_selfloop_degree(self):
        pass
    def test_weighted_degree(self):
        pass

    def test_node_attr(self):
        G=self.K3
        G.node[1]['foo']='baz'
        assert_equal(G.nodes(data=True), [(0,{}),(1,{'foo':'baz'}),(2,{})])

    def test_node_attr2(self):
        pass
    def test_edge_attr(self):
        pass
    def test_edge_attr2(self):
        pass
    def test_edge_attr3(self):
        pass
    def test_edge_attr4(self):
        G=self.K3
        G[1][2]['data']=10 # OK to set data like this
        assert_equal(G.edges(data=True), 
                     [(0,1,{}),(0,2,{}),(1,2,{'data':10})])
        G.edge[1][2]['data']=20 # another spelling, "edge"
        assert_equal(G.edges(data=True), 
                      [(0,1,{}),(0,2,{}),(1,2,{'data':20})])
        G.edge[1][2]['listdata']=[20,200] 
        G.edge[1][2]['weight']=20 
        assert_equal(G.edges(data=True), 
                     [(0,1,{}),(0,2,{}),(1,2,{'data':20,'listdata':[20,200],'weight':20})])

