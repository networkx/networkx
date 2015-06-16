#!/usr/bin/env python
from nose.tools import *
import networkx
from test_multigraph import BaseMultiGraphTester, TestMultiGraph

class BaseMultiDiGraphTester(BaseMultiGraphTester):
    def test_edges(self):
        G=self.K3
        assert_equal(sorted(G.edges()),[(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.edges(0)),[(0,1),(0,2)])
        assert_raises((KeyError,networkx.NetworkXError), G.edges,-1)

    def test_edges_data(self):
        G=self.K3
        assert_equal(sorted(G.edges(data=True)),
                     [(0,1,{}),(0,2,{}),(1,0,{}),(1,2,{}),(2,0,{}),(2,1,{})])
        assert_equal(sorted(G.edges(0,data=True)),[(0,1,{}),(0,2,{})])
        assert_raises((KeyError,networkx.NetworkXError), G.neighbors,-1)


    def test_edges_iter(self):
        G=self.K3
        assert_equal(sorted(G.edges_iter()),
                     [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.edges_iter(0)),[(0,1),(0,2)])
        G.add_edge(0,1)
        assert_equal(sorted(G.edges_iter()),
                     [(0,1),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])

    def test_out_edges(self):
        G=self.K3
        assert_equal(sorted(G.out_edges()),
                     [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.out_edges(0)),[(0,1),(0,2)])
        assert_raises((KeyError,networkx.NetworkXError), G.out_edges,-1)
        assert_equal(sorted(G.out_edges(0,keys=True)),[(0,1,0),(0,2,0)])

    def test_out_edges_iter(self):
        G=self.K3
        assert_equal(sorted(G.out_edges_iter()),
                     [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.out_edges_iter(0)),[(0,1),(0,2)])
        G.add_edge(0,1,2)
        assert_equal(sorted(G.out_edges_iter()),
                     [(0,1),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])

    def test_in_edges(self):
        G=self.K3
        assert_equal(sorted(G.in_edges()),
                     [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.in_edges(0)),[(1,0),(2,0)])
        assert_raises((KeyError,networkx.NetworkXError), G.in_edges,-1)
        G.add_edge(0,1,2)
        assert_equal(sorted(G.in_edges()),
                     [(0,1),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.in_edges(0,keys=True)),[(1,0,0),(2,0,0)])

    def test_in_edges_iter(self):
        G=self.K3
        assert_equal(sorted(G.in_edges_iter()),
                     [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])
        assert_equal(sorted(G.in_edges_iter(0)),[(1,0),(2,0)])
        G.add_edge(0,1,2)
        assert_equal(sorted(G.in_edges_iter()),
                     [(0,1),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)])

        assert_equal(sorted(G.in_edges_iter(data=True,keys=False)),
                     [(0,1,{}),(0,1,{}),(0,2,{}),(1,0,{}),(1,2,{}),
                      (2,0,{}),(2,1,{})])


    def is_shallow(self,H,G):
        # graph
        assert_equal(G.graph['foo'],H.graph['foo'])
        G.graph['foo'].append(1)
        assert_equal(G.graph['foo'],H.graph['foo'])
        # node
        assert_equal(G.node[0]['foo'],H.node[0]['foo'])
        G.node[0]['foo'].append(1)
        assert_equal(G.node[0]['foo'],H.node[0]['foo'])
        # edge
        assert_equal(G[1][2][0]['foo'],H[1][2][0]['foo'])
        G[1][2][0]['foo'].append(1)
        assert_equal(G[1][2][0]['foo'],H[1][2][0]['foo'])

    def is_deep(self,H,G):
        # graph
        assert_equal(G.graph['foo'],H.graph['foo'])
        G.graph['foo'].append(1)
        assert_not_equal(G.graph['foo'],H.graph['foo'])
        # node
        assert_equal(G.node[0]['foo'],H.node[0]['foo'])
        G.node[0]['foo'].append(1)
        assert_not_equal(G.node[0]['foo'],H.node[0]['foo'])
        # edge
        assert_equal(G[1][2][0]['foo'],H[1][2][0]['foo'])
        G[1][2][0]['foo'].append(1)
        assert_not_equal(G[1][2][0]['foo'],H[1][2][0]['foo'])

    def test_to_undirected(self):
        # MultiDiGraph -> MultiGraph changes number of edges so it is
        # not a copy operation... use is_shallow, not is_shallow_copy
        G=self.K3
        self.add_attributes(G)
        H=networkx.MultiGraph(G)
        self.is_shallow(H,G)
        H=G.to_undirected()
        self.is_deep(H,G)

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
        assert_equal(list(G.degree().values()),[4,4,4])
        assert_equal(G.degree(),{0:4,1:4,2:4})
        assert_equal(G.degree(0),4)
        assert_equal(G.degree([0]),{0:4})
        assert_equal(G.degree(iter([0])),{0:4})
        assert_raises((KeyError,networkx.NetworkXError), G.degree,-1)

    def test_degree_iter(self):
        G=self.K3
        assert_equal(list(G.degree_iter()),[(0,4),(1,4),(2,4)])
        assert_equal(dict(G.degree_iter()),{0:4,1:4,2:4})
        assert_equal(list(G.degree_iter(0)),[(0,4)])
        assert_equal(list(G.degree_iter(iter([0]))),[(0,4)])
        G.add_edge(0,1,weight=0.3,other=1.2)
        assert_equal(list(G.degree_iter(weight='weight')),[(0,4.3),(1,4.3),(2,4)])
        assert_equal(list(G.degree_iter(weight='other')),[(0,5.2),(1,5.2),(2,4)])


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
        assert_equal(list(G.in_degree_iter(iter([0]))),[(0,2)])
        assert_equal(list(G.in_degree_iter(0,weight='weight')),[(0,2)])

    def test_out_degree(self):
        G=self.K3
        assert_equal(list(G.out_degree().values()),[2,2,2])
        assert_equal(G.out_degree(),{0:2,1:2,2:2})
        assert_equal(G.out_degree(0),2)
        assert_equal(G.out_degree([0]),{0:2})
        assert_equal(G.out_degree(iter([0])),{0:2})
        assert_raises((KeyError,networkx.NetworkXError), G.out_degree,-1)

    def test_out_degree_iter(self):
        G=self.K3
        assert_equal(list(G.out_degree_iter()),[(0,2),(1,2),(2,2)])
        assert_equal(dict(G.out_degree_iter()),{0:2,1:2,2:2})
        assert_equal(list(G.out_degree_iter(0)),[(0,2)])
        assert_equal(list(G.out_degree_iter(iter([0]))),[(0,2)])
        assert_equal(list(G.out_degree_iter(0,weight='weight')),[(0,2)])


    def test_size(self):
        G=self.K3
        assert_equal(G.size(),6)
        assert_equal(G.number_of_edges(),6)
        G.add_edge(0,1,weight=0.3,other=1.2)
        assert_equal(G.size(weight='weight'),6.3)
        assert_equal(G.size(weight='other'),7.2)

    def test_to_undirected_reciprocal(self):
        G=self.Graph()
        G.add_edge(1,2)
        assert_true(G.to_undirected().has_edge(1,2))
        assert_false(G.to_undirected(reciprocal=True).has_edge(1,2))
        G.add_edge(2,1)
        assert_true(G.to_undirected(reciprocal=True).has_edge(1,2))

    def test_reverse_copy(self):
        G=networkx.MultiDiGraph([(0,1),(0,1)])
        R=G.reverse()
        assert_equal(sorted(R.edges()),[(1,0),(1,0)])
        R.remove_edge(1,0)
        assert_equal(sorted(R.edges()),[(1,0)])
        assert_equal(sorted(G.edges()),[(0,1),(0,1)])

    def test_reverse_nocopy(self):
        G=networkx.MultiDiGraph([(0,1),(0,1)])
        R=G.reverse(copy=False)
        assert_equal(sorted(R.edges()),[(1,0),(1,0)])
        R.remove_edge(1,0)
        assert_equal(sorted(R.edges()),[(1,0)])
        assert_equal(sorted(G.edges()),[(1,0)])


class TestMultiDiGraph(BaseMultiDiGraphTester,TestMultiGraph):
    def setUp(self):
        self.Graph=networkx.MultiDiGraph
        # build K3
        self.k3edges=[(0, 1), (0, 2), (1, 2)]
        self.k3nodes=[0, 1, 2]
        self.K3=self.Graph()
        self.K3.adj={0:{},1:{},2:{}}
        self.K3.succ=self.K3.adj
        self.K3.pred={0:{},1:{},2:{}}
        for u in self.k3nodes:
            for v in self.k3nodes:
                if u==v: continue
                d={0:{}}
                self.K3.succ[u][v]=d
                self.K3.pred[v][u]=d
        self.K3.adj=self.K3.succ
        self.K3.edge=self.K3.adj
        self.K3.node={}
        self.K3.node[0]={}
        self.K3.node[1]={}
        self.K3.node[2]={}


    def test_add_edge(self):
        G=self.Graph()
        G.add_edge(0,1)
        assert_equal(G.adj,{0: {1: {0:{}}}, 1: {}})
        assert_equal(G.succ,{0: {1: {0:{}}}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:{0:{}}}})
        G=self.Graph()
        G.add_edge(*(0,1))
        assert_equal(G.adj,{0: {1: {0:{}}}, 1: {}})
        assert_equal(G.succ,{0: {1: {0:{}}}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:{0:{}}}})

    def test_add_edges_from(self):
        G=self.Graph()
        G.add_edges_from([(0,1),(0,1,{'weight':3})])
        assert_equal(G.adj,{0: {1: {0:{},1:{'weight':3}}}, 1: {}})
        assert_equal(G.succ,{0: {1: {0:{},1:{'weight':3}}}, 1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:{0:{},1:{'weight':3}}}})

        G.add_edges_from([(0,1),(0,1,{'weight':3})],weight=2)
        assert_equal(G.succ,{0: {1: {0:{},
                                     1:{'weight':3},
                                     2:{'weight':2},
                                     3:{'weight':3}}},
                             1: {}})
        assert_equal(G.pred,{0: {}, 1: {0:{0:{},1:{'weight':3},
                                           2:{'weight':2},
                                           3:{'weight':3}}}})

        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,)])  # too few in tuple
        assert_raises(networkx.NetworkXError, G.add_edges_from,[(0,1,2,3,4)])  # too many in tuple
        assert_raises(TypeError, G.add_edges_from,[0])  # not a tuple

    def test_remove_edge(self):
        G=self.K3
        G.remove_edge(0,1)
        assert_equal(G.succ,{0:{2:{0:{}}},
                             1:{0:{0:{}},2:{0:{}}},
                             2:{0:{0:{}},1:{0:{}}}})
        assert_equal(G.pred,{0:{1:{0:{}}, 2:{0:{}}},
                             1:{2:{0:{}}},
                             2:{0:{0:{}},1:{0:{}}}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,0,2,
                      key=1)


    def test_remove_multiedge(self):
        G=self.K3
        G.add_edge(0,1,key='parallel edge')
        G.remove_edge(0,1,key='parallel edge')
        assert_equal(G.adj,{0: {1: {0:{}}, 2: {0:{}}},
                           1: {0: {0:{}}, 2: {0:{}}},
                           2: {0: {0:{}}, 1: {0:{}}}})

        assert_equal(G.succ,{0: {1: {0:{}}, 2: {0:{}}},
                           1: {0: {0:{}}, 2: {0:{}}},
                           2: {0: {0:{}}, 1: {0:{}}}})

        assert_equal(G.pred,{0:{1: {0:{}},2:{0:{}}},
                             1:{0:{0:{}},2:{0:{}}},
                             2:{0:{0:{}},1:{0:{}}}})
        G.remove_edge(0,1)
        assert_equal(G.succ,{0:{2:{0:{}}},
                             1:{0:{0:{}},2:{0:{}}},
                             2:{0:{0:{}},1:{0:{}}}})
        assert_equal(G.pred,{0:{1:{0:{}}, 2:{0:{}}},
                             1:{2:{0:{}}},
                             2:{0:{0:{}},1:{0:{}}}})
        assert_raises((KeyError,networkx.NetworkXError), G.remove_edge,-1,0)

    def test_remove_edges_from(self):
        G=self.K3
        G.remove_edges_from([(0,1)])
        assert_equal(G.succ,{0:{2:{0:{}}},
                             1:{0:{0:{}},2:{0:{}}},
                             2:{0:{0:{}},1:{0:{}}}})
        assert_equal(G.pred,{0:{1:{0:{}}, 2:{0:{}}},
                             1:{2:{0:{}}},
                             2:{0:{0:{}},1:{0:{}}}})
        G.remove_edges_from([(0,0)]) # silent fail
