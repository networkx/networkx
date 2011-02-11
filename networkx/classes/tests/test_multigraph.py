#!/usr/bin/env python
from nose.tools import *
import networkx
from test_graph import TestGraph


class TestMultiGraph(TestGraph):
    def setUp(self):
        self.Graph=networkx.MultiGraph
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
        assert_equal(G[0],{1: {0:{}}, 2: {0:{}}})
        assert_raises(KeyError, G.__getitem__, 'j')
        assert_raises((TypeError,networkx.NetworkXError), G.__getitem__, ['A'])

    def test_remove_node(self):
        G=self.K3
        G.remove_node(0)
        assert_equal(G.adj,{1:{2:{0:{}}},2:{1:{0:{}}}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_node,-1)


    def test_add_edge(self):
        G=self.Graph()
        G.add_edge(0,1)
        assert_equal(G.adj,{0: {1: {0:{}}}, 1: {0: {0:{}}}})
        G=self.Graph()
        G.add_edge(*(0,1))
        assert_equal(G.adj,{0: {1: {0:{}}}, 1: {0: {0:{}}}})
  
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
        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,)]) 
        # too many in tuple
        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,1,2,3,4)]) 
        assert_raises(TypeError, G.add_edges_from,[0])  # not a tuple


    def test_remove_edge(self):
        G=self.K3
        G.remove_edge(0,1)
        assert_equal(G.adj,{0: {2: {0: {}}}, 
                            1: {2: {0: {}}}, 
                            2: {0: {0: {}}, 
                                1: {0: {}}}})

        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)

    def test_remove_edges_from(self):
        G=self.K3
        G.remove_edges_from([(0,1)])
        assert_equal(G.adj,{0:{2:{0:{}}},1:{2:{0:{}}},2:{0:{0:{}},1:{0:{}}}})
        G.remove_edges_from([(0,0)]) # silent fail

    def test_remove_multiedge(self):
        G=self.K3
        G.add_edge(0,1,key='parallel edge')
        G.remove_edge(0,1,key='parallel edge')
        assert_equal(G.adj,{0: {1: {0:{}}, 2: {0:{}}}, 
                           1: {0: {0:{}}, 2: {0:{}}},
                           2: {0: {0:{}}, 1: {0:{}}}})
        G.remove_edge(0,1)
        assert_equal(G.adj,{0:{2:{0:{}}},1:{2:{0:{}}},2:{0:{0:{}},1:{0:{}}}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)


    def test_get_edge_data(self):
        G=self.K3
        assert_equal(G.get_edge_data(0,1),{0:{}})
        assert_equal(G[0][1],{0:{}})
        assert_equal(G[0][1][0],{})
        assert_equal(G.get_edge_data(10,20),None)
#        assert_raises((KeyError,networkx.NetworkXError), G.get_edge,-1,0)

    def test_adjacency_iter(self):
        G=self.K3
        assert_equal(dict(G.adjacency_iter()),
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
        H=networkx.MultiGraph(G)
        self.is_shallow_copy(H,G)
        H=G.to_undirected()
        self.is_deepcopy(H,G)

    def test_to_directed(self):
        G=self.K3
        self.add_attributes(G)
        H=networkx.MultiDiGraph(G)
        self.is_shallow_copy(H,G)
        H=G.to_directed()
        self.is_deepcopy(H,G)

    def test_selfloops(self):
        G=self.K3
        G.add_edge(0,0)
        assert_equal(G.nodes_with_selfloops(),[0])
        assert_equal(G.selfloop_edges(),[(0,0)])
        assert_equal(G.selfloop_edges(data=True),[(0,0,{})])
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
#         G.add_edge(1,1)
#         G.remove_node(1)
#         G.add_edge(0,0)
#         G.add_edge(1,1)
#         G.remove_nodes_from([0,1])

    def test_edge_attr4(self):
        G=self.Graph()
        G.add_edge(1,2,key=0,data=7,spam='bar',bar='foo')
        assert_equal(G.edges(data=True), 
                      [(1,2,{'data':7,'spam':'bar','bar':'foo'})])
        G[1][2][0]['data']=10 # OK to set data like this
        assert_equal(G.edges(data=True), 
                     [(1,2,{'data':10,'spam':'bar','bar':'foo'})])

        G.edge[1][2][0]['data']=20 # another spelling, "edge"
        assert_equal(G.edges(data=True), 
                      [(1,2,{'data':20,'spam':'bar','bar':'foo'})])
        G.edge[1][2][0]['listdata']=[20,200] 
        G.edge[1][2][0]['weight']=20 
        assert_equal(G.edges(data=True), 
                     [(1,2,{'data':20,'spam':'bar',
                            'bar':'foo','listdata':[20,200],'weight':20})])

