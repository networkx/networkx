#!/usr/bin/env python
from nose.tools import *
import networkx
from test_graph import BaseGraphTester

class BasePlanarGraphTester(BaseGraphTester):
    def test_adjacency_list(self):
        G=self.K3
        assert_equal(G.adjacency_list(),[[1,2],[2,0],[0,1]])

class TestPlanarGraph(BasePlanarGraphTester):
    """Tests specific to dict-of-dict-of-dict graph data structure"""
    def setUp(self):
        self.Graph=networkx.PlanarGraph
        # build dict-of-dict-of-dict K3

        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        self.K3=self.Graph()
        self.K3.add_node(0)
        self.K3.add_node(1)
        self.K3.add_node(2)

        self.K3.add_edges_from(self.k3edges)
        self.K3.provide_planarity_data(0, [1,2])
        self.K3.provide_planarity_data(1, [2,0])
        self.K3.provide_planarity_data(2, [0,1])

        self.K3.node[0]={}
        self.K3.node[1]={}
        self.K3.node[2]={}

    def test_adjacency_iter(self):
        G=self.K3
        assert_equal(dict(G.adjacency_iter()),
                {0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}})

    def test_getitem(self):
        G=self.K3
        assert_equal(G[0],{1: {}, 2: {}})
        assert_raises(KeyError, G.__getitem__, 'j')
        assert_raises((TypeError,networkx.NetworkXError), G.__getitem__, ['A'])

    def test_add_node(self):
        G=self.Graph()
        G.add_node(0)
        assert_equal(G.adj,{0:{}})
        # test add attributes
        G.add_node(1,c='red')
        G.add_node(2,{'c':'blue'})
        G.add_node(3,{'c':'blue'},c='red')
        assert_raises(networkx.NetworkXError, G.add_node, 4, [])
        assert_raises(networkx.NetworkXError, G.add_node, 4, 4)
        assert_equal(G.node[1]['c'],'red')
        assert_equal(G.node[2]['c'],'blue')
        assert_equal(G.node[3]['c'],'red')
        # test updating attributes
        G.add_node(1,c='blue')
        G.add_node(2,{'c':'red'})
        G.add_node(3,{'c':'red'},c='blue')
        assert_equal(G.node[1]['c'],'blue')
        assert_equal(G.node[2]['c'],'red')
        assert_equal(G.node[3]['c'],'blue')

    def test_add_nodes_from(self):
        G=self.Graph()
        G.add_nodes_from([0,1,2])
        assert_equal(G.adj,{0:{},1:{},2:{}})
        # test add attributes
        G.add_nodes_from([0,1,2],c='red')
        assert_equal(G.node[0]['c'],'red')
        assert_equal(G.node[2]['c'],'red')
        # test that attribute dicts are not the same
        assert(G.node[0] is not G.node[1])
        # test updating attributes
        G.add_nodes_from([0,1,2],c='blue')
        assert_equal(G.node[0]['c'],'blue')
        assert_equal(G.node[2]['c'],'blue')
        assert(G.node[0] is not G.node[1])
        # test tuple input
        H=self.Graph()
        H.add_nodes_from(G.nodes(data=True))
        assert_equal(H.node[0]['c'],'blue')
        assert_equal(H.node[2]['c'],'blue')
        assert(H.node[0] is not H.node[1])
        # specific overrides general
        H.add_nodes_from([0,(1,{'c':'green'}),(3,{'c':'cyan'})],c='red')
        assert_equal(H.node[0]['c'],'red')
        assert_equal(H.node[1]['c'],'green')
        assert_equal(H.node[2]['c'],'blue')
        assert_equal(H.node[3]['c'],'cyan')

    def test_remove_node(self):
        G=self.K3
        G.remove_node(0)
        assert_equal(G.adj,{1:{2:{}},2:{1:{}}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_node,-1)

        # generator here to implement list,set,string...
    def test_remove_nodes_from(self):
        G=self.K3
        G.remove_nodes_from([0,1])
        assert_equal(G.adj,{2:{}})
        G.remove_nodes_from([-1]) # silent fail

    def test_add_edge(self):
        G=self.Graph()
        G.add_edge(0,1)
        assert_equal(G.adj,{0: {1: {}}, 1: {0: {}}})
        G=self.Graph()
        G.add_edge(*(0,1))
        assert_equal(G.adj,{0: {1: {}}, 1: {0: {}}})

    def test_add_edges_from(self):
        G=self.Graph()
        G.add_edges_from([(0,1),(0,2,{'weight':3})])
        assert_equal(G.adj,{0: {1:{}, 2:{'weight':3}}, 1: {0:{}}, \
                2:{0:{'weight':3}}})
        G=self.Graph()
        G.add_edges_from([(0,1),(0,2,{'weight':3}),(1,2,{'data':4})],data=2)
        assert_equal(G.adj,{\
                0: {1:{'data':2}, 2:{'weight':3,'data':2}}, \
                1: {0:{'data':2}, 2:{'data':4}}, \
                2: {0:{'weight':3,'data':2}, 1:{'data':4}} \
                })

        assert_raises(networkx.NetworkXError,
                      G.add_edges_from,[(0,)])  # too few in tuple
        assert_raises(networkx.NetworkXError,
                      G.add_edges_from,[(0,1,2,3)])  # too many in tuple
        assert_raises(TypeError, G.add_edges_from,[0])  # not a tuple


    def test_remove_edge(self):
        G=self.K3
        G.remove_edge(0,1)
        assert_equal(G.adj,{0:{2:{}},1:{2:{}},2:{0:{},1:{}}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)

    def test_remove_edges_from(self):
        G=self.K3
        G.remove_edges_from([(0,1)])
        assert_equal(G.adj,{0:{2:{}},1:{2:{}},2:{0:{},1:{}}})
        G.remove_edges_from([(0,0)]) # silent fail

    def test_clear(self):
        G=self.K3
        G.clear()
        assert_equal(G.adj,{})

    def test_edges_data(self):
        G=self.K3
        assert_equal(sorted(G.edges(data=True)),[(0,1,{}),(0,2,{}),(1,2,{})])
        assert_equal(sorted(G.edges(0,data=True)),[(0,1,{}),(0,2,{})])
        assert_raises((KeyError,networkx.NetworkXError), G.edges,-1)

    def test_get_edge_data(self):
        G=self.K3
        assert_equal(G.get_edge_data(0,1),{})
        assert_equal(G[0][1],{})
        assert_equal(G.get_edge_data(10,20),None)
        assert_equal(G.get_edge_data(-1,0),None)
        assert_equal(G.get_edge_data(-1,0,default=1),1)
