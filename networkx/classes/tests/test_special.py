#!/usr/bin/env python
from nose.tools import *
import networkx
from test_graph import TestGraph
from test_digraph import TestDiGraph
from collections import OrderedDict

class SpecialGraphTester(TestGraph):
    def setUp(self):
        TestGraph.setUp(self)
        self.Graph=networkx.SpecialGraph

class OrderedGraphTester(TestGraph):
    def setUp(self):
        TestGraph.setUp(self)
        def graph_factory(data,**attr):
            g=networkx.SpecialGraph(data,node_dict_factory=OrderedDict,
                    adjlist_dict_factory=OrderedDict,
                    edge_attr_dict_factory=OrderedDict,**attr)
            return g
        self.Graph=graph_factory

class ThinGraphTester(TestGraph):
    def setUp(self):
        def graph_factory(data,**attr):
            g=networkx.SpecialGraph(data,
                    edge_attr_dict_factory=lambda :None,**attr)
            return g
        self.Graph=graph_factory
        # build dict-of-dict-of-dict K3
        ed1,ed2,ed3 = (None,None,None)
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




class SpecialDiGraphTester(TestDiGraph):
    def setUp(self):
        TestDiGraph.setUp(self)
        self.Graph=networkx.SpecialDiGraph

class OrderedDiGraphTester(TestDiGraph):
    def setUp(self):
        TestGraph.setUp(self)
        def graph_factory(data,**attr):
            g=networkx.SpecialDiGraph(data,node_dict_factory=OrderedDict,
                    adjlist_dict_factory=OrderedDict,
                    edge_attr_dict_factory=OrderedDict,**attr)
            return g
        self.Graph=graph_factory

class ThinDiGraphTester(TestDiGraph):
    def setUp(self):
        def graph_factory(data,**attr):
            g=networkx.SpecialDiGraph(data,
                    edge_attr_dict_factory=lambda :None,**attr)
            return g
        self.Graph=graph_factory
        # build dict-of-dict-of-dict K3
        ed1,ed2,ed3 = (None,None,None)
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

