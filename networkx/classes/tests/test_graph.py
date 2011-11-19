#!/usr/bin/env python
from nose.tools import *
import networkx

class BaseGraphTester(object):
    """ Tests for data-structure independent graph class features."""
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

    def test_nodes_iter(self):
        G=self.K3
        assert_equal(sorted(G.nodes_iter()),self.k3nodes)
        assert_equal(sorted(G.nodes_iter(data=True)),[(0,{}),(1,{}),(2,{})])

    def test_nodes(self):
        G=self.K3
        assert_equal(sorted(G.nodes()),self.k3nodes)
        assert_equal(sorted(G.nodes(data=True)),[(0,{}),(1,{}),(2,{})])

    def test_has_node(self):
        G=self.K3
        assert(G.has_node(1))
        assert(not G.has_node(4))
        assert(not G.has_node([]))   # no exception for nonhashable
        assert(not G.has_node({1:1})) # no exception for nonhashable

    def test_has_edge(self):
        G=self.K3
        assert_equal(G.has_edge(0,1),True)
        assert_equal(G.has_edge(0,-1),False)

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
        assert_raises((KeyError,networkx.NetworkXError), G.edges,-1)

    def test_edges_iter(self):
        G=self.K3
        assert_equal(sorted(G.edges_iter()),[(0,1),(0,2),(1,2)])
        assert_equal(sorted(G.edges_iter(0)),[(0,1),(0,2)])
        f=lambda x:list(G.edges_iter(x))
        assert_raises((KeyError,networkx.NetworkXError), f, -1)

    def test_adjacency_list(self):
        G=self.K3
        assert_equal(G.adjacency_list(),[[1,2],[0,2],[0,1]])

    def test_degree(self):
        G=self.K3
        assert_equal(list(G.degree().values()),[2,2,2])
        assert_equal(G.degree(),{0:2,1:2,2:2})
        assert_equal(G.degree(0),2)
        assert_equal(G.degree([0]),{0:2})
        assert_raises((KeyError,networkx.NetworkXError), G.degree,-1)

    def test_weighted_degree(self):
        G=self.Graph()
        G.add_edge(1,2,weight=2)
        G.add_edge(2,3,weight=3)
        assert_equal(list(G.degree(weight='weight').values()),[2,5,3])
        assert_equal(G.degree(weight='weight'),{1:2,2:5,3:3})
        assert_equal(G.degree(1,weight='weight'),2)
        assert_equal(G.degree([1],weight='weight'),{1:2})

    def test_degree_iter(self):
        G=self.K3
        assert_equal(list(G.degree_iter()),[(0,2),(1,2),(2,2)])
        assert_equal(dict(G.degree_iter()),{0:2,1:2,2:2})
        assert_equal(list(G.degree_iter(0)),[(0,2)])

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
        G.add_star(nlist,weight=2.0)
        assert_equal(sorted(G.edges(nlist,data=True)),\
                     [(12,13,{'weight':2.}),
                      (12,14,{'weight':2.}),
                      (12,15,{'weight':2.})])

    def test_add_path(self):
        G=self.K3.copy()
        nlist=[12,13,14,15]
        G.add_path(nlist)
        assert_equal(sorted(G.edges(nlist)),[(12,13),(13,14),(14,15)])
        G=self.K3.copy()
        G.add_path(nlist,weight=2.0)
        assert_equal(sorted(G.edges(nlist,data=True)),\
                     [(12,13,{'weight':2.}),
                      (13,14,{'weight':2.}),
                      (14,15,{'weight':2.})])

    def test_add_cycle(self):
        G=self.K3.copy()
        nlist=[12,13,14,15]
        oklists=[ [(12,13),(12,15),(13,14),(14,15)], \
                      [(12,13),(13,14),(14,15),(15,12)] ]
        G.add_cycle(nlist)
        assert_true(sorted(G.edges(nlist)) in oklists)
        G=self.K3.copy()
        oklists=[ [(12,13,{'weight':1.}),\
                (12,15,{'weight':1.}),\
                (13,14,{'weight':1.}),\
                (14,15,{'weight':1.})], \
                \
                [(12,13,{'weight':1.}),\
                (13,14,{'weight':1.}),\
                (14,15,{'weight':1.}),\
                (15,12,{'weight':1.})] \
                ]

        G.add_cycle(nlist,weight=1.0)
        assert_true(sorted(G.edges(nlist,data=True)) in oklists)

    def test_nbunch_iter(self):
        G=self.K3
        assert_equal(list(G.nbunch_iter()),self.k3nodes) # all nodes
        assert_equal(list(G.nbunch_iter(0)),[0]) # single node
        assert_equal(list(G.nbunch_iter([0,1])),[0,1]) # sequence
        # sequence with none in graph
        assert_equal(list(G.nbunch_iter([-1])),[])
        # string sequence with none in graph
        assert_equal(list(G.nbunch_iter("foo")),[])
        # node not in graph doesn't get caught upon creation of iterator
        bunch=G.nbunch_iter(-1)
        # but gets caught when iterator used
        assert_raises(networkx.NetworkXError,list,bunch)
        # unhashable doesn't get caught upon creation of iterator
        bunch=G.nbunch_iter([0,1,2,{}])
        # but gets caught when iterator hits the unhashable
        assert_raises(networkx.NetworkXError,list,bunch)

    def test_selfloop_degree(self):
        G=self.Graph()
        G.add_edge(1,1)
        assert_equal(list(G.degree().values()),[2])
        assert_equal(G.degree(),{1:2})
        assert_equal(G.degree(1),2)
        assert_equal(G.degree([1]),{1:2})
        assert_equal(G.degree([1],weight='weight'),{1:2})

    def test_selfloops(self):
        G=self.K3.copy()
        G.add_edge(0,0)
        assert_equal(G.nodes_with_selfloops(),[0])
        assert_equal(G.selfloop_edges(),[(0,0)])
        assert_equal(G.number_of_selfloops(),1)
        G.remove_edge(0,0)
        G.add_edge(0,0)
        G.remove_edges_from([(0,0)])
        G.add_edge(1,1)
        G.remove_node(1)
        G.add_edge(0,0)
        G.add_edge(1,1)
        G.remove_nodes_from([0,1])


class BaseAttrGraphTester(BaseGraphTester):
    """ Tests of graph class attribute features."""
    def test_weighted_degree(self):
        G=self.Graph()
        G.add_edge(1,2,weight=2,other=3)
        G.add_edge(2,3,weight=3,other=4)
        assert_equal(list(G.degree(weight='weight').values()),[2,5,3])
        assert_equal(G.degree(weight='weight'),{1:2,2:5,3:3})
        assert_equal(G.degree(1,weight='weight'),2)
        assert_equal(G.degree([1],weight='weight'),{1:2})

        assert_equal(list(G.degree(weight='other').values()),[3,7,4])
        assert_equal(G.degree(weight='other'),{1:3,2:7,3:4})
        assert_equal(G.degree(1,weight='other'),3)
        assert_equal(G.degree([1],weight='other'),{1:3})

    def add_attributes(self,G):
        G.graph['foo']=[]
        G.node[0]['foo']=[]
        G.remove_edge(1,2)
        ll=[]
        G.add_edge(1,2,foo=ll)
        G.add_edge(2,1,foo=ll)
        # attr_dict must be dict
        assert_raises(networkx.NetworkXError,G.add_edge,0,1,attr_dict=[])

    def test_name(self):
        G=self.Graph(name='')
        assert_equal(G.name,"")
        G=self.Graph(name='test')
        assert_equal(G.__str__(),"test")
        assert_equal(G.name,"test")

    def test_copy(self):
        G=self.K3
        self.add_attributes(G)
        H=G.copy()
        self.is_deepcopy(H,G)
        H=G.__class__(G)
        self.is_shallow_copy(H,G)

    def test_copy_attr(self):
        G=self.Graph(foo=[])
        G.add_node(0,foo=[])
        G.add_edge(1,2,foo=[])
        H=G.copy()
        self.is_deepcopy(H,G)
        H=G.__class__(G) # just copy
        self.is_shallow_copy(H,G)

    def is_deepcopy(self,H,G):
        self.graphs_equal(H,G)
        self.different_attrdict(H,G)
        self.deep_copy_attrdict(H,G)

    def deep_copy_attrdict(self,H,G):
        self.deepcopy_graph_attr(H,G)
        self.deepcopy_node_attr(H,G)
        self.deepcopy_edge_attr(H,G)

    def deepcopy_graph_attr(self,H,G):
        assert_equal(G.graph['foo'],H.graph['foo'])
        G.graph['foo'].append(1)
        assert_not_equal(G.graph['foo'],H.graph['foo'])

    def deepcopy_node_attr(self,H,G):
        assert_equal(G.node[0]['foo'],H.node[0]['foo'])
        G.node[0]['foo'].append(1)
        assert_not_equal(G.node[0]['foo'],H.node[0]['foo'])

    def deepcopy_edge_attr(self,H,G):
        assert_equal(G[1][2]['foo'],H[1][2]['foo'])
        G[1][2]['foo'].append(1)
        assert_not_equal(G[1][2]['foo'],H[1][2]['foo'])

    def is_shallow_copy(self,H,G):
        self.graphs_equal(H,G)
        self.different_attrdict(H,G)
        self.shallow_copy_attrdict(H,G)

    def shallow_copy_attrdict(self,H,G):
        self.shallow_copy_graph_attr(H,G)
        self.shallow_copy_node_attr(H,G)
        self.shallow_copy_edge_attr(H,G)

    def shallow_copy_graph_attr(self,H,G):
        assert_equal(G.graph['foo'],H.graph['foo'])
        G.graph['foo'].append(1)
        assert_equal(G.graph['foo'],H.graph['foo'])

    def shallow_copy_node_attr(self,H,G):
        assert_equal(G.node[0]['foo'],H.node[0]['foo'])
        G.node[0]['foo'].append(1)
        assert_equal(G.node[0]['foo'],H.node[0]['foo'])

    def shallow_copy_edge_attr(self,H,G):
        assert_equal(G[1][2]['foo'],H[1][2]['foo'])
        G[1][2]['foo'].append(1)
        assert_equal(G[1][2]['foo'],H[1][2]['foo'])

    def same_attrdict(self, H, G):
        old_foo=H[1][2]['foo']
        H.add_edge(1,2,foo='baz')
        assert_equal(G.edge,H.edge)
        H.add_edge(1,2,foo=old_foo)
        assert_equal(G.edge,H.edge)
        old_foo=H.node[0]['foo']
        H.node[0]['foo']='baz'
        assert_equal(G.node,H.node)
        H.node[0]['foo']=old_foo
        assert_equal(G.node,H.node)

    def different_attrdict(self, H, G):
        old_foo=H[1][2]['foo']
        H.add_edge(1,2,foo='baz')
        assert_not_equal(G.edge,H.edge)
        H.add_edge(1,2,foo=old_foo)
        assert_equal(G.edge,H.edge)
        old_foo=H.node[0]['foo']
        H.node[0]['foo']='baz'
        assert_not_equal(G.node,H.node)
        H.node[0]['foo']=old_foo
        assert_equal(G.node,H.node)

    def graphs_equal(self,H,G):
        assert_equal(G.adj,H.adj)
        assert_equal(G.edge,H.edge)
        assert_equal(G.node,H.node)
        assert_equal(G.graph,H.graph)
        assert_equal(G.name,H.name)
        if not G.is_directed() and not H.is_directed():
                assert_true(H.adj[1][2] is H.adj[2][1])
                assert_true(G.adj[1][2] is G.adj[2][1])
        else: # at least one is directed
            if not G.is_directed():
                G.pred=G.adj
                G.succ=G.adj
            if not H.is_directed():
                H.pred=H.adj
                H.succ=H.adj
            assert_equal(G.pred,H.pred)
            assert_equal(G.succ,H.succ)
            assert_true(H.succ[1][2] is H.pred[2][1])
            assert_true(G.succ[1][2] is G.pred[2][1])

    def test_graph_attr(self):
        G=self.K3
        G.graph['foo']='bar'
        assert_equal(G.graph['foo'], 'bar')
        del G.graph['foo']
        assert_equal(G.graph, {})
        H=self.Graph(foo='bar')
        assert_equal(H.graph['foo'], 'bar')

    def test_node_attr(self):
        G=self.K3
        G.add_node(1,foo='bar')
        assert_equal(G.nodes(), [0,1,2])
        assert_equal(G.nodes(data=True), [(0,{}),(1,{'foo':'bar'}),(2,{})])
        G.node[1]['foo']='baz'
        assert_equal(G.nodes(data=True), [(0,{}),(1,{'foo':'baz'}),(2,{})])

    def test_node_attr2(self):
        G=self.K3
        a={'foo':'bar'}
        G.add_node(3,attr_dict=a)
        assert_equal(G.nodes(), [0,1,2,3])
        assert_equal(G.nodes(data=True),
                     [(0,{}),(1,{}),(2,{}),(3,{'foo':'bar'})])

    def test_edge_attr(self):
        G=self.Graph()
        G.add_edge(1,2,foo='bar')
        assert_equal(G.edges(data=True), [(1,2,{'foo':'bar'})])

    def test_edge_attr2(self):
        G=self.Graph()
        G.add_edges_from([(1,2),(3,4)],foo='foo')
        assert_equal(sorted(G.edges(data=True)),
                     [(1,2,{'foo':'foo'}),(3,4,{'foo':'foo'})])

    def test_edge_attr3(self):
        G=self.Graph()
        G.add_edges_from([(1,2,{'weight':32}),(3,4,{'weight':64})],foo='foo')
        assert_equal(G.edges(data=True),
                     [(1,2,{'foo':'foo','weight':32}),\
                      (3,4,{'foo':'foo','weight':64})])

        G.remove_edges_from([(1,2),(3,4)])
        G.add_edge(1,2,data=7,spam='bar',bar='foo')
        assert_equal(G.edges(data=True),
                      [(1,2,{'data':7,'spam':'bar','bar':'foo'})])

    def test_edge_attr4(self):
        G=self.Graph()
        G.add_edge(1,2,data=7,spam='bar',bar='foo')
        assert_equal(G.edges(data=True),
                      [(1,2,{'data':7,'spam':'bar','bar':'foo'})])
        G[1][2]['data']=10 # OK to set data like this
        assert_equal(G.edges(data=True),
                     [(1,2,{'data':10,'spam':'bar','bar':'foo'})])

        G.edge[1][2]['data']=20 # another spelling, "edge"
        assert_equal(G.edges(data=True),
                      [(1,2,{'data':20,'spam':'bar','bar':'foo'})])
        G.edge[1][2]['listdata']=[20,200]
        G.edge[1][2]['weight']=20
        assert_equal(G.edges(data=True),
                     [(1,2,{'data':20,'spam':'bar',
                            'bar':'foo','listdata':[20,200],'weight':20})])

    def test_attr_dict_not_dict(self):
        # attr_dict must be dict
        G=self.Graph()
        edges=[(1,2)]
        assert_raises(networkx.NetworkXError,G.add_edges_from,edges,
                      attr_dict=[])

    def test_to_undirected(self):
        G=self.K3
        self.add_attributes(G)
        H=networkx.Graph(G)
        self.is_shallow_copy(H,G)
        H=G.to_undirected()
        self.is_deepcopy(H,G)

    def test_to_directed(self):
        G=self.K3
        self.add_attributes(G)
        H=networkx.DiGraph(G)
        self.is_shallow_copy(H,G)
        H=G.to_directed()
        self.is_deepcopy(H,G)

    def test_subgraph(self):
        G=self.K3
        self.add_attributes(G)
        H=G.subgraph([0,1,2,5])
#        assert_equal(H.name, 'Subgraph of ('+G.name+')')
        H.name=G.name
        self.graphs_equal(H,G)
        self.same_attrdict(H,G)
        self.shallow_copy_attrdict(H,G)

        H=G.subgraph(0)
        assert_equal(H.adj,{0:{}})
        H=G.subgraph([])
        assert_equal(H.adj,{})
        assert_not_equal(G.adj,{})

    def test_selfloops_attr(self):
        G=self.K3.copy()
        G.add_edge(0,0)
        G.add_edge(1,1,weight=2)
        assert_equal(G.selfloop_edges(data=True),
                [(0,0,{}),(1,1,{'weight':2})])


class TestGraph(BaseAttrGraphTester):
    """Tests specific to dict-of-dict-of-dict graph data structure"""
    def setUp(self):
        self.Graph=networkx.Graph
        # build dict-of-dict-of-dict K3
        ed1,ed2,ed3 = ({},{},{})
        self.k3adj={0: {1: ed1, 2: ed2},
                    1: {0: ed1, 2: ed3},
                    2: {0: ed2, 1: ed3}}
        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        self.K3=self.Graph()
        self.K3.adj=self.K3.edge=self.k3adj
        self.K3.node={}
        self.K3.node[0]={}
        self.K3.node[1]={}
        self.K3.node[2]={}

    def test_data_input(self):
        G=self.Graph(data={1:[2],2:[1]}, name="test")
        assert_equal(G.name,"test")
        assert_equal(sorted(G.adj.items()),[(1, {2: {}}), (2, {1: {}})])
        G=self.Graph({1:[2],2:[1]}, name="test")
        assert_equal(G.name,"test")
        assert_equal(sorted(G.adj.items()),[(1, {2: {}}), (2, {1: {}})])

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
