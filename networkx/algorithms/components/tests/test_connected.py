#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti
from networkx import NetworkXError

class TestConnected:

    def setUp(self):
        G1=cnlti(nx.grid_2d_graph(2,2),first_label=0,ordering="sorted")
        G2=cnlti(nx.lollipop_graph(3,3),first_label=4,ordering="sorted")
        G3=cnlti(nx.house_graph(),first_label=10,ordering="sorted")
        self.G=nx.union(G1,G2)
        self.G=nx.union(self.G,G3)
        self.DG=nx.DiGraph([(1,2),(1,3),(2,3)])
        self.grid=cnlti(nx.grid_2d_graph(4,4),first_label=1)

    def test_connected_components(self):
        cc=nx.connected_components
        G=self.G
        C=[[0, 1, 2, 3], [4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14]]
        assert_equal(sorted([sorted(g) for g in cc(G)]),sorted(C))

    def test_number_connected_components(self):
        ncc=nx.number_connected_components
        assert_equal(ncc(self.G),3)

    def test_number_connected_components2(self):
        ncc=nx.number_connected_components
        assert_equal(ncc(self.grid),1)

    def test_connected_components2(self):
        cc=nx.connected_components
        G=self.grid
        C=[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]
        assert_equal(sorted([sorted(g) for g in cc(G)]),sorted(C))

    def test_node_connected_components(self):
        ncc=nx.node_connected_component
        G=self.grid
        C=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        assert_equal(sorted(ncc(G,1)),sorted(C))

    def test_connected_component_subgraphs(self):
        ncc=nx.connected_component_subgraphs
        G=self.grid
        C=[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]
        assert_equal(sorted([sorted(g.nodes()) for g in ncc(G)]),sorted(C))

    def test_is_connected(self):
        assert_true(nx.is_connected(self.grid))
        G=nx.Graph()
        G.add_nodes_from([1,2])
        assert_false(nx.is_connected(G))

    def test_connected_raise(self):
        assert_raises(NetworkXError,nx.connected_components,self.DG)
        assert_raises(NetworkXError,nx.number_connected_components,self.DG)
        assert_raises(NetworkXError,nx.connected_component_subgraphs,self.DG)
        assert_raises(NetworkXError,nx.node_connected_component,self.DG,1)
        assert_raises(NetworkXError,nx.is_connected,self.DG)

class TestIncrementalConnected(object):
    def setUp(self):
        self.G1 = nx.Graph()
        self.G2 = nx.MultiGraph()
        self.G3 = nx.DiGraph()
        self.graphs = [self.G1, self.G2]

        for G in self.graphs:
            G.add_edge(0,1)
            G.add_edge(2,3)
            G.add_edge(4,2)
        
        self.icc1 = nx.IncrementalConnectedComponents(self.G1)
        self.icc2 = nx.IncrementalConnectedComponents(self.G2)
        self.iccs = [self.icc1, self.icc2]
            
    def test_initdirected(self):
        assert_raises(NetworkXError, nx.IncrementalConnectedComponents, self.G3)

    def test_getitem(self):
        for icc in self.iccs:
            assert_equal(icc[0], set([0,1]))
            assert_equal(icc[2], set([2,3,4]))
            icc.add_edge(5,6)
            assert_equal(icc[5], set([5,6]))
            
    def test_len(self):
        for icc in self.iccs:
            assert_equal(len(icc), 2)
            icc.add_edge(5,6)
            assert_equal(len(icc), 3)
            
    def test_addedge1(self):
        # add two nodes in same group
        for icc in self.iccs:
            icc.add_edge(0,1)
            assert_equal(icc[0], set([0,1]))
            assert_equal(len(icc), 2)
    
    def test_addedge2(self):
        # add two nodes in different groups
        for icc in self.iccs:
            icc.add_edge(1,2)
            assert_equal(icc[0], set([0,1,2,3,4]))
            assert_equal(len(icc), 1)

    def test_addedge3(self):
        # add two nodes in different groups, different order
        for icc in self.iccs:
            icc.add_edge(2,1)
            assert_equal(icc[0], set([0,1,2,3,4]))
            assert_equal(len(icc), 1)

    def test_addedge4(self):
        # add two nodes in different groups, one of which is new
        for icc in self.iccs:
            icc.add_edge(1,5)
            assert_equal(icc[0], set([0,1,5]))
            assert_equal(len(icc), 2)
                    
    def test_addedge5(self):
        # add two nodes in different groups, both of which are new
        for icc in self.iccs:
            icc.add_edge(5,6)
            assert_equal(icc[5], set([5,6]))
            assert_equal(len(icc), 3)

    def test_cc(self):
        for icc in self.iccs:
            assert_equal(icc.connected_component(0), set([0,1]))
            assert_equal(icc.connected_component(2), set([2,3,4]))
            icc.add_edge(5,6)
            assert_equal(icc.connected_component(5), set([5,6]))
            
    def test_ccs(self):
        for icc in self.iccs:
            assert_equal(icc.connected_components(), [set([2,3,4]), set([0,1])])
            
    def test_index(self):
        for icc in self.iccs:
            assert_equal(icc.index(0), 1)
            assert_raises(NetworkXError, icc.index, 5)
            
    def test_isconnected(self):
        for icc in self.iccs:
            assert_false(icc.is_connected())
            icc.add_edge(1,2)
            assert_true(icc.is_connected())
            
    def test_samecomponent(self):
        for icc in self.iccs:
            assert_true(icc.same_component(0,1))
            assert_true(icc.same_component(1,0))
            assert_false(icc.same_component(1,2))
            assert_false(icc.same_component(2,1))
            assert_false(icc.same_component(5,2))
            assert_false(icc.same_component(5,6))
            assert_false(icc.same_component(6,6))
            assert_true(icc.same_component(1,1))            
        
