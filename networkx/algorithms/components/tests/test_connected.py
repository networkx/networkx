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
