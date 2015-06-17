#!/usr/bin/env python
from nose.tools import *
import networkx
from test_graph import BaseGraphTester, BaseAttrGraphTester, TestGraph

class BaseDiGraphTester(BaseGraphTester):
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

    def test_edges(self):
        G=self.K3
        assert_equal(sorted(G.edges()),[(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.edges(0)),[(0,1),(0,2)])
        assert_raises((KeyError,networkx.NetworkXError), G.edges,-1)

    def test_edges_iter(self):
        G=self.K3
        assert_equal(sorted(G.edges_iter()),
                     [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.edges_iter(0)),[(0,1),(0,2)])

    def test_edges_data(self):
        G=self.K3
        assert_equal(sorted(G.edges(data=True)),
                     [(0,1,{}),(0,2,{}),(1,0,{}),(1,2,{}),(2,0,{}),(2,1,{})])
        assert_equal(sorted(G.edges(0,data=True)),[(0,1,{}),(0,2,{})])
        assert_raises((KeyError,networkx.NetworkXError), G.edges,-1)

    def test_out_edges(self):
        G=self.K3
        assert_equal(sorted(G.out_edges()),
                     [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.out_edges(0)),[(0,1),(0,2)])
        assert_raises((KeyError,networkx.NetworkXError), G.out_edges,-1)

    def test_out_edges_iter(self):
        G=self.K3
        assert_equal(sorted(G.out_edges_iter()),
                     [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.edges_iter(0)),[(0,1),(0,2)])

    def test_out_edges_dir(self):
        G=self.P3
        assert_equal(sorted(G.out_edges()),[(0, 1), (1, 2)])
        assert_equal(sorted(G.out_edges(0)),[(0, 1)])
        assert_equal(sorted(G.out_edges(2)),[])

    def test_out_edges_iter_dir(self):
        G=self.P3
        assert_equal(sorted(G.out_edges_iter()),[(0, 1), (1, 2)])
        assert_equal(sorted(G.out_edges_iter(0)),[(0, 1)])
        assert_equal(sorted(G.out_edges_iter(2)),[])

    def test_in_edges_dir(self):
        G=self.P3
        assert_equal(sorted(G.in_edges()),[(0, 1), (1, 2)])
        assert_equal(sorted(G.in_edges(0)),[])
        assert_equal(sorted(G.in_edges(2)),[(1,2)])

    def test_in_edges_iter_dir(self):
        G=self.P3
        assert_equal(sorted(G.in_edges_iter()),[(0, 1), (1, 2)])
        assert_equal(sorted(G.in_edges_iter(0)),[])
        assert_equal(sorted(G.in_edges_iter(2)),[(1,2)])

    def test_degree(self):
        G=self.K3
        assert_equal(list(G.degree().values()),[4,4,4])
        assert_equal(G.degree(),{0:4,1:4,2:4})
        assert_equal(G.degree(0),4)
        assert_equal(G.degree([0]),{0:4})
        assert_raises((KeyError,networkx.NetworkXError), G.degree,-1)

    def test_degree_iter(self):
        G=self.K3
        assert_equal(list(G.degree_iter()),[(0,4),(1,4),(2,4)])
        assert_equal(dict(G.degree_iter()),{0:4,1:4,2:4})
        assert_equal(list(G.degree_iter(0)),[(0,4)])
        assert_equal(list(G.degree_iter(iter([0]))),[(0,4)]) #run through iterator

    def test_in_degree(self):
        G=self.K3
        assert_equal(list(G.in_degree().values()),[2,2,2])
        assert_equal(G.in_degree(),{0:2,1:2,2:2})
        assert_equal(G.in_degree(0),2)
        assert_equal(G.in_degree([0]),{0:2})
        assert_equal(G.in_degree(iter([0])),{0:2})
        assert_raises((KeyError,networkx.NetworkXError), G.in_degree,-1)

    def test_in_degree_iter(self):
        G=self.K3
        assert_equal(list(G.in_degree_iter()),[(0,2),(1,2),(2,2)])
        assert_equal(dict(G.in_degree_iter()),{0:2,1:2,2:2})
        assert_equal(list(G.in_degree_iter(0)),[(0,2)])
        assert_equal(list(G.in_degree_iter(iter([0]))),[(0,2)]) #run through iterator

    def test_in_degree_iter_weighted(self):
        G=self.K3
        G.add_edge(0,1,weight=0.3,other=1.2)
        assert_equal(list(G.in_degree_iter(weight='weight')),[(0,2),(1,1.3),(2,2)])
        assert_equal(dict(G.in_degree_iter(weight='weight')),{0:2,1:1.3,2:2})
        assert_equal(list(G.in_degree_iter(1,weight='weight')),[(1,1.3)])
        assert_equal(list(G.in_degree_iter(weight='other')),[(0,2),(1,2.2),(2,2)])
        assert_equal(dict(G.in_degree_iter(weight='other')),{0:2,1:2.2,2:2})
        assert_equal(list(G.in_degree_iter(1,weight='other')),[(1,2.2)])
        assert_equal(list(G.in_degree_iter(iter([1]),weight='other')),[(1,2.2)])

    def test_out_degree(self):
        G=self.K3
        assert_equal(list(G.out_degree().values()),[2,2,2])
        assert_equal(G.out_degree(),{0:2,1:2,2:2})
        assert_equal(G.out_degree(0),2)
        assert_equal(G.out_degree([0]),{0:2})
        assert_equal(G.out_degree(iter([0])),{0:2})
        assert_raises((KeyError,networkx.NetworkXError), G.out_degree,-1)

    def test_out_degree_iter_weighted(self):
        G=self.K3
        G.add_edge(0,1,weight=0.3,other=1.2)
        assert_equal(list(G.out_degree_iter(weight='weight')),[(0,1.3),(1,2),(2,2)])
        assert_equal(dict(G.out_degree_iter(weight='weight')),{0:1.3,1:2,2:2})
        assert_equal(list(G.out_degree_iter(0,weight='weight')),[(0,1.3)])
        assert_equal(list(G.out_degree_iter(weight='other')),[(0,2.2),(1,2),(2,2)])
        assert_equal(dict(G.out_degree_iter(weight='other')),{0:2.2,1:2,2:2})
        assert_equal(list(G.out_degree_iter(0,weight='other')),[(0,2.2)])
        assert_equal(list(G.out_degree_iter(iter([0]),weight='other')),[(0,2.2)])

    def test_out_degree_iter(self):
        G=self.K3
        assert_equal(list(G.out_degree_iter()),[(0,2),(1,2),(2,2)])
        assert_equal(dict(G.out_degree_iter()),{0:2,1:2,2:2})
        assert_equal(list(G.out_degree_iter(0)),[(0,2)])
        assert_equal(list(G.out_degree_iter(iter([0]))),[(0,2)])

    def test_size(self):
        G=self.K3
        assert_equal(G.size(),6)
        assert_equal(G.number_of_edges(),6)

    def test_to_undirected_reciprocal(self):
        G=self.Graph()
        G.add_edge(1,2)
        assert_true(G.to_undirected().has_edge(1,2))
        assert_false(G.to_undirected(reciprocal=True).has_edge(1,2))
        G.add_edge(2,1)
        assert_true(G.to_undirected(reciprocal=True).has_edge(1,2))

    def test_reverse_copy(self):
        G=networkx.DiGraph([(0,1),(1,2)])
        R=G.reverse()
        assert_equal(sorted(R.edges()),[(1,0),(2,1)])
        R.remove_edge(1,0)
        assert_equal(sorted(R.edges()),[(2,1)])
        assert_equal(sorted(G.edges()),[(0,1),(1,2)])

    def test_reverse_nocopy(self):
        G=networkx.DiGraph([(0,1),(1,2)])
        R=G.reverse(copy=False)
        assert_equal(sorted(R.edges()),[(1,0),(2,1)])
        R.remove_edge(1,0)
        assert_equal(sorted(R.edges()),[(2,1)])
        assert_equal(sorted(G.edges()),[(2,1)])

class BaseAttrDiGraphTester(BaseDiGraphTester,BaseAttrGraphTester):
    pass


class TestDiGraph(BaseAttrDiGraphTester,TestGraph):
    """Tests specific to dict-of-dict-of-dict digraph data structure"""
    def setUp(self):
        self.Graph=networkx.DiGraph
        # build dict-of-dict-of-dict K3
        ed1,ed2,ed3,ed4,ed5,ed6 = ({},{},{},{},{},{})
        self.k3adj={0: {1: ed1, 2: ed2}, 1: {0: ed3, 2: ed4}, 2: {0: ed5, 1:ed6}}
        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        self.K3=self.Graph()
        self.K3.adj = self.K3.succ = self.K3.edge = self.k3adj
        self.K3.pred={0: {1: ed3, 2: ed5}, 1: {0: ed1, 2: ed6}, 2: {0: ed2, 1:ed4}}

        ed1,ed2 = ({},{})
        self.P3=self.Graph()
        self.P3.adj={0: {1: ed1}, 1: {2: ed2}, 2: {}}
        self.P3.succ=self.P3.adj
        self.P3.pred={0: {}, 1: {0: ed1}, 2: {1: ed2}}
        self.K3.node={}
        self.K3.node[0]={}
        self.K3.node[1]={}
        self.K3.node[2]={}
        self.P3.node={}
        self.P3.node[0]={}
        self.P3.node[1]={}
        self.P3.node[2]={}

    def test_data_input(self):
        G=self.Graph(data={1:[2],2:[1]}, name="test")
        assert_equal(G.name,"test")
        assert_equal(sorted(G.adj.items()),[(1, {2: {}}), (2, {1: {}})])
        assert_equal(sorted(G.succ.items()),[(1, {2: {}}), (2, {1: {}})])
        assert_equal(sorted(G.pred.items()),[(1, {2: {}}), (2, {1: {}})])

    def test_add_edge(self):
        G=self.Graph()
        G.add_edge(0,1)
        assert_equal(G.adj,{0: {1: {}}, 1: {}})
        assert_equal(G.succ,{0: {1: {}}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:{}}})
        G=self.Graph()
        G.add_edge(*(0,1))
        assert_equal(G.adj,{0: {1: {}}, 1: {}})
        assert_equal(G.succ,{0: {1: {}}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:{}}})

    def test_add_edges_from(self):
        G=self.Graph()
        G.add_edges_from([(0,1),(0,2,{'data':3})],data=2)
        assert_equal(G.adj,{0: {1: {'data':2}, 2: {'data':3}}, 1: {}, 2: {}})
        assert_equal(G.succ,{0: {1: {'data':2}, 2: {'data':3}}, 1: {}, 2: {}})
        assert_equal(G.pred,{0: {}, 1: {0: {'data':2}}, 2: {0: {'data':3}}})

        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,)])  # too few in tuple
        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,1,2,3)])  # too many in tuple
        assert_raises(TypeError, G.add_edges_from,[0])  # not a tuple

    def test_remove_edge(self):
        G=self.K3
        G.remove_edge(0,1)
        assert_equal(G.succ,{0:{2:{}},1:{0:{},2:{}},2:{0:{},1:{}}})
        assert_equal(G.pred,{0:{1:{}, 2:{}}, 1:{2:{}}, 2:{0:{},1:{}}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)

    def test_remove_edges_from(self):
        G=self.K3
        G.remove_edges_from([(0,1)])
        assert_equal(G.succ,{0:{2:{}},1:{0:{},2:{}},2:{0:{},1:{}}})
        assert_equal(G.pred,{0:{1:{}, 2:{}}, 1:{2:{}}, 2:{0:{},1: {}}})
        G.remove_edges_from([(0,0)]) # silent fail
