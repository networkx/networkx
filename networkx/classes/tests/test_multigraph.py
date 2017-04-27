#!/usr/bin/env python
from nose.tools import assert_equal
from nose.tools import assert_is
from nose.tools import assert_not_equal
from nose.tools import assert_raises

import networkx as nx
from networkx.testing.utils import *

from test_graph import BaseAttrGraphTester, TestGraph

class BaseMultiGraphTester(BaseAttrGraphTester):
    def test_has_edge(self):
        G=self.K3
        assert_equal(G.has_edge(0,1),True)
        assert_equal(G.has_edge(0,-1),False)
        assert_equal(G.has_edge(0,1,0),True)
        assert_equal(G.has_edge(0,1,1),False)

    def test_get_edge_data(self):
        G=self.K3
        assert_equal(G.get_edge_data(0,1),{0:{}})
        assert_equal(G[0][1],{0:{}})
        assert_equal(G[0][1][0],{})
        assert_equal(G.get_edge_data(10,20),None)
        assert_equal(G.get_edge_data(0,1,0),{})
        

    def test_adjacency(self):
        G=self.K3
        assert_equal(dict(G.adjacency()),
                          {0: {1: {0:{}}, 2: {0:{}}},
                           1: {0: {0:{}}, 2: {0:{}}},
                           2: {0: {0:{}}, 1: {0:{}}}})

    def deepcopy_edge_attr(self,H,G):
        assert_equal(G[1][2][0]['foo'],H[1][2][0]['foo'])
        G[1][2][0]['foo'].append(1)
        assert_not_equal(G[1][2][0]['foo'],H[1][2][0]['foo'])

    def shallow_copy_edge_attr(self,H,G):
        assert_equal(G[1][2][0]['foo'],H[1][2][0]['foo'])
        G[1][2][0]['foo'].append(1)
        assert_equal(G[1][2][0]['foo'],H[1][2][0]['foo'])

    def same_attrdict(self, H, G):
        # same attrdict in the edgedata
        old_foo=H[1][2][0]['foo']
        H.add_edge(1,2,0,foo='baz')
        assert_equal(G.edge,H.edge)
        H.add_edge(1,2,0,foo=old_foo)
        assert_equal(G.edge,H.edge)
        # but not same edgedata dict
        H.add_edge(1,2,foo='baz')
        assert_not_equal(G.edge,H.edge)

        old_foo=H.node[0]['foo']
        H.node[0]['foo']='baz'
        assert_equal(G.node,H.node)
        H.node[0]['foo']=old_foo
        assert_equal(G.node,H.node)

    def different_attrdict(self, H, G):
        # used by graph_equal_but_different
        old_foo=H[1][2][0]['foo']
        H.add_edge(1,2,0,foo='baz')
        assert_not_equal(G.edge,H.edge)
        H.add_edge(1,2,0,foo=old_foo)
        assert_equal(G.edge,H.edge)
        HH=H.copy()
        H.add_edge(1,2,foo='baz')
        assert_not_equal(G.edge,H.edge)
        H=HH
        old_foo=H.node[0]['foo']
        H.node[0]['foo']='baz'
        assert_not_equal(G.node,H.node)
        H.node[0]['foo']=old_foo
        assert_equal(G.node,H.node)

    def test_to_undirected(self):
        G=self.K3
        self.add_attributes(G)
        H=nx.MultiGraph(G)
        self.is_shallow_copy(H,G)
        H=G.to_undirected()
        self.is_deepcopy(H,G)

    def test_to_directed(self):
        G=self.K3
        self.add_attributes(G)
        H=nx.MultiDiGraph(G)
        self.is_shallow_copy(H,G)
        H=G.to_directed()
        self.is_deepcopy(H,G)

    def test_selfloops(self):
        G=self.K3
        G.add_edge(0,0)
        assert_nodes_equal(G.nodes_with_selfloops(), [0])
        assert_edges_equal(G.selfloop_edges(), [(0, 0)])
        assert_edges_equal(G.selfloop_edges(data=True), [(0, 0, {})])
        assert_equal(G.number_of_selfloops(),1)

    def test_selfloops2(self):
        G=self.K3
        G.add_edge(0,0)
        G.add_edge(0,0)
        G.add_edge(0,0,key='parallel edge')
        G.remove_edge(0,0,key='parallel edge')
        assert_equal(G.number_of_edges(0,0),2)
        G.remove_edge(0,0)
        assert_equal(G.number_of_edges(0,0),1)

    def test_edge_attr4(self):
        G=self.Graph()
        G.add_edge(1,2,key=0,data=7,spam='bar',bar='foo')
        assert_edges_equal(G.edges(data=True),
                      [(1,2,{'data':7,'spam':'bar','bar':'foo'})])
        G[1][2][0]['data']=10 # OK to set data like this
        assert_edges_equal(G.edges(data=True),
                     [(1,2,{'data':10,'spam':'bar','bar':'foo'})])

        G.edge[1][2][0]['data']=20 # another spelling, "edge"
        assert_edges_equal(G.edges(data=True),
                      [(1,2,{'data':20,'spam':'bar','bar':'foo'})])
        G.edge[1][2][0]['listdata']=[20,200]
        G.edge[1][2][0]['weight']=20
        assert_edges_equal(G.edges(data=True),
                     [(1,2,{'data':20,'spam':'bar',
                            'bar':'foo','listdata':[20,200],'weight':20})])


class TestMultiGraph(BaseMultiGraphTester,TestGraph):
    def setUp(self):
        self.Graph=nx.MultiGraph
        # build K3
        ed1,ed2,ed3 = ({0:{}},{0:{}},{0:{}})
        self.k3adj={0: {1: ed1, 2: ed2},
                    1: {0: ed1, 2: ed3},
                    2: {0: ed2, 1: ed3}}
        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        self.K3=self.Graph()
        self.K3.adj = self.K3.edge = self.k3adj
        self.K3.node={}
        self.K3.node[0]={}
        self.K3.node[1]={}
        self.K3.node[2]={}

    def test_data_input(self):
        G=self.Graph(data={1:[2],2:[1]}, name="test")
        assert_equal(G.name,"test")
        assert_equal(sorted(G.adj.items()),[(1, {2: {0:{}}}), (2, {1: {0:{}}})])

    def test_getitem(self):
        G=self.K3
        assert_equal(G[0],{1: {0:{}}, 2: {0:{}}})
        assert_raises(KeyError, G.__getitem__, 'j')
        assert_raises((TypeError,nx.NetworkXError), G.__getitem__, ['A'])

    def test_remove_node(self):
        G=self.K3
        G.remove_node(0)
        assert_equal(G.adj,{1:{2:{0:{}}},2:{1:{0:{}}}})
        assert_raises((KeyError,nx.NetworkXError), G.remove_node,-1)

    def test_add_edge(self):
        G=self.Graph()
        G.add_edge(0,1)
        assert_equal(G.adj,{0: {1: {0:{}}}, 1: {0: {0:{}}}})
        G=self.Graph()
        G.add_edge(*(0,1))
        assert_equal(G.adj,{0: {1: {0:{}}}, 1: {0: {0:{}}}})
        
    def test_add_edge_conflicting_key(self):
        G=self.Graph()
        G.add_edge(0,1,key=1)
        G.add_edge(0,1)
        assert_equal(G.number_of_edges(),2)
        G=self.Graph()
        G.add_edges_from([(0,1,1,{})])
        G.add_edges_from([(0,1)])
        assert_equal(G.number_of_edges(),2)

    def test_add_edges_from(self):
        G=self.Graph()
        G.add_edges_from([(0,1),(0,1,{'weight':3})])
        assert_equal(G.adj,{0: {1: {0:{},1:{'weight':3}}},
                            1: {0: {0:{},1:{'weight':3}}}})
        G.add_edges_from([(0,1),(0,1,{'weight':3})],weight=2)
        assert_equal(G.adj,{0: {1: {0:{},1:{'weight':3},
                                    2:{'weight':2},3:{'weight':3}}},
                            1: {0: {0:{},1:{'weight':3},
                                    2:{'weight':2},3:{'weight':3}}}})

        # too few in tuple
        assert_raises(nx.NetworkXError, G.add_edges_from,[(0,)])
        # too many in tuple
        assert_raises(nx.NetworkXError, G.add_edges_from,[(0,1,2,3,4)])
        assert_raises(TypeError, G.add_edges_from,[0])  # not a tuple

    def test_remove_edge(self):
        G=self.K3
        G.remove_edge(0,1)
        assert_equal(G.adj,{0: {2: {0: {}}},
                            1: {2: {0: {}}},
                            2: {0: {0: {}},
                                1: {0: {}}}})

        assert_raises((KeyError,nx.NetworkXError), G.remove_edge,-1,0)
        assert_raises((KeyError,nx.NetworkXError), G.remove_edge,0,2,
                      key=1)
        
    def test_remove_edges_from(self):
        G=self.K3.copy()
        G.remove_edges_from([(0,1)])
        assert_equal(G.adj,{0:{2:{0:{}}},1:{2:{0:{}}},2:{0:{0:{}},1:{0:{}}}})
        G.remove_edges_from([(0,0)]) # silent fail
        self.K3.add_edge(0,1)
        G=self.K3.copy()
        G.remove_edges_from(list(G.edges(data=True,keys=True)))
        assert_equal(G.adj,{0:{},1:{},2:{}})
        G=self.K3.copy()
        G.remove_edges_from(list(G.edges(data=False,keys=True)))
        assert_equal(G.adj,{0:{},1:{},2:{}})
        G=self.K3.copy()
        G.remove_edges_from(list(G.edges(data=False,keys=False)))
        assert_equal(G.adj,{0:{},1:{},2:{}})
        G=self.K3.copy()
        G.remove_edges_from([(0,1,0),(0,2,0,{}),(1,2)])
        assert_equal(G.adj,{0:{1:{1:{}}},1:{0:{1:{}}},2:{}})

    def test_remove_multiedge(self):
        G=self.K3
        G.add_edge(0,1,key='parallel edge')
        G.remove_edge(0,1,key='parallel edge')
        assert_equal(G.adj,{0: {1: {0:{}}, 2: {0:{}}},
                           1: {0: {0:{}}, 2: {0:{}}},
                           2: {0: {0:{}}, 1: {0:{}}}})
        G.remove_edge(0,1)
        assert_equal(G.adj,{0:{2:{0:{}}},1:{2:{0:{}}},2:{0:{0:{}},1:{0:{}}}})
        assert_raises((KeyError,nx.NetworkXError), G.remove_edge,-1,0)


class TestEdgeSubgraph(object):
    """Unit tests for the :meth:`MultiGraph.edge_subgraph` method."""

    def setup(self):
        # Create a doubly-linked path graph on five nodes.
        G = nx.MultiGraph()
        nx.add_path(G, range(5))
        nx.add_path(G, range(5))
        # Add some node, edge, and graph attributes.
        for i in range(5):
            G.node[i]['name'] = 'node{}'.format(i)
        G.edge[0][1][0]['name'] = 'edge010'
        G.edge[0][1][1]['name'] = 'edge011'
        G.edge[3][4][0]['name'] = 'edge340'
        G.edge[3][4][1]['name'] = 'edge341'
        G.graph['name'] = 'graph'
        # Get the subgraph induced by one of the first edges and one of
        # the last edges.
        self.G = G
        self.H = G.edge_subgraph([(0, 1, 0), (3, 4, 1)])

    def test_correct_nodes(self):
        """Tests that the subgraph has the correct nodes."""
        assert_equal([0, 1, 3, 4], sorted(self.H.nodes()))

    def test_correct_edges(self):
        """Tests that the subgraph has the correct edges."""
        assert_equal([(0, 1, 0, 'edge010'), (3, 4, 1, 'edge341')],
                     sorted(self.H.edges(keys=True, data='name')))

    def test_add_node(self):
        """Tests that adding a node to the original graph does not
        affect the nodes of the subgraph.

        """
        self.G.add_node(5)
        assert_equal([0, 1, 3, 4], sorted(self.H.nodes()))

    def test_remove_node(self):
        """Tests that removing a node in the original graph does not
        affect the nodes of the subgraph.

        """
        self.G.remove_node(0)
        assert_equal([0, 1, 3, 4], sorted(self.H.nodes()))

    def test_node_attr_dict(self):
        """Tests that the node attribute dictionary of the two graphs is
        the same object.

        """
        for v in self.H:
            assert_equal(self.G.node[v], self.H.node[v])
        # Making a change to G should make a change in H and vice versa.
        self.G.node[0]['name'] = 'foo'
        assert_equal(self.G.node[0], self.H.node[0])
        self.H.node[1]['name'] = 'bar'
        assert_equal(self.G.node[1], self.H.node[1])

    def test_edge_attr_dict(self):
        """Tests that the edge attribute dictionary of the two graphs is
        the same object.

        """
        for u, v, k in self.H.edges(keys=True):
            assert_equal(self.G.edge[u][v][k], self.H.edge[u][v][k])
        # Making a change to G should make a change in H and vice versa.
        self.G.edge[0][1][0]['name'] = 'foo'
        assert_equal(self.G.edge[0][1][0]['name'],
                     self.H.edge[0][1][0]['name'])
        self.H.edge[3][4][1]['name'] = 'bar'
        assert_equal(self.G.edge[3][4][1]['name'],
                     self.H.edge[3][4][1]['name'])

    def test_graph_attr_dict(self):
        """Tests that the graph attribute dictionary of the two graphs
        is the same object.

        """
        assert_is(self.G.graph, self.H.graph)
