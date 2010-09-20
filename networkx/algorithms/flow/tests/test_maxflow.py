# -*- coding: utf-8 -*-
"""Max flow algorithm test suite.

Run with nose: nosetests -v test_max_flow.py
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.


import networkx as nx
from nose.tools import *

def compare_flows(G, s, t, solnFlows, solnValue):
    flowValue, flowDict = nx.ford_fulkerson(G, s, t)
    assert_equal(flowValue, solnValue)
    assert_equal(flowDict, solnFlows)
    assert_equal(nx.min_cut(G, s, t), solnValue)
    assert_equal(nx.max_flow(G, s, t), solnValue)
    assert_equal(nx.ford_fulkerson_flow(G, s, t), solnFlows)


class TestMaxflow:
    def test_graph1(self):
        # Trivial undirected graph
        G = nx.Graph()
        G.add_edge(1,2, capacity = 1.0)

        solnFlows = {1: {2: 1.0},
                     2: {1: 1.0}}

        compare_flows(G, 1, 2, solnFlows, 1.0)

    def test_graph2(self):
        # A more complex undirected graph
        # adapted from www.topcoder.com/tc?module=Statc&d1=tutorials&d2=maxFlow
        G = nx.Graph()
        G.add_edge('x','a', capacity = 3.0)
        G.add_edge('x','b', capacity = 1.0)
        G.add_edge('a','c', capacity = 3.0)
        G.add_edge('b','c', capacity = 5.0)
        G.add_edge('b','d', capacity = 4.0)
        G.add_edge('d','e', capacity = 2.0)
        G.add_edge('c','y', capacity = 2.0)
        G.add_edge('e','y', capacity = 3.0)

        H = {'x': {'a': 3, 'b': 1},
             'a': {'c': 3, 'x': 3},
             'b': {'c': 1, 'd': 2, 'x': 1},
             'c': {'a': 3, 'b': 1, 'y': 2},
             'd': {'b': 2, 'e': 2},
             'e': {'d': 2, 'y': 2},
             'y': {'c': 2, 'e': 2}}

        compare_flows(G, 'x', 'y', H, 4.0)

    def test_digraph1(self):
        # The classic directed graph example
        G = nx.DiGraph()
        G.add_edge('a','b', capacity = 1000.0)
        G.add_edge('a','c', capacity = 1000.0)
        G.add_edge('b','c', capacity = 1.0)
        G.add_edge('b','d', capacity = 1000.0)
        G.add_edge('c','d', capacity = 1000.0)

        H = {'a': {'b': 1000.0, 'c': 1000.0},
             'b': {'c': 0, 'd': 1000.0},
             'c': {'d': 1000.0},
             'd': {}}

        compare_flows(G, 'a', 'd', H, 2000.0)

        # An example in which some edges end up with zero flow.
        G = nx.DiGraph()
        G.add_edge('s', 'b', capacity = 2)
        G.add_edge('s', 'c', capacity = 1)
        G.add_edge('c', 'd', capacity = 1)
        G.add_edge('d', 'a', capacity = 1)
        G.add_edge('b', 'a', capacity = 2)
        G.add_edge('a', 't', capacity = 2)

        H = {'s': {'b': 2, 'c': 0},
             'c': {'d': 0},
             'd': {'a': 0},
             'b': {'a': 2},
             'a': {'t': 2},
             't': {}}

        compare_flows(G, 's', 't', H, 2)

    def test_digraph2(self):
        # A directed graph example from Cormen et al.
        G = nx.DiGraph()
        G.add_edge('s','v1', capacity = 16.0)
        G.add_edge('s','v2', capacity = 13.0)
        G.add_edge('v1','v2', capacity = 10.0)
        G.add_edge('v2','v1', capacity = 4.0)
        G.add_edge('v1','v3', capacity = 12.0)
        G.add_edge('v3','v2', capacity = 9.0)
        G.add_edge('v2','v4', capacity = 14.0)
        G.add_edge('v4','v3', capacity = 7.0)
        G.add_edge('v3','t', capacity = 20.0)
        G.add_edge('v4','t', capacity = 4.0)

        H = {'s': {'v1': 12.0, 'v2': 11.0},
             'v2': {'v1': 0, 'v4': 11.0},
             'v1': {'v2': 0, 'v3': 12.0},
             'v3': {'v2': 0, 't': 19.0},
             'v4': {'v3': 7.0, 't': 4.0},
             't': {}}

        compare_flows(G, 's', 't', H, 23.0)

    def test_digraph3(self):
        # A more complex directed graph
        # from www.topcoder.com/tc?module=Statc&d1=tutorials&d2=maxFlow
        G = nx.DiGraph()
        G.add_edge('x','a', capacity = 3.0)
        G.add_edge('x','b', capacity = 1.0)
        G.add_edge('a','c', capacity = 3.0)
        G.add_edge('b','c', capacity = 5.0)
        G.add_edge('b','d', capacity = 4.0)
        G.add_edge('d','e', capacity = 2.0)
        G.add_edge('c','y', capacity = 2.0)
        G.add_edge('e','y', capacity = 3.0)

        H = {'x': {'a': 2.0, 'b': 1.0},
             'a': {'c': 2.0},
             'b': {'c': 0, 'd': 1.0},
             'c': {'y': 2.0},
             'd': {'e': 1.0},
             'e': {'y': 1.0},
             'y': {}}

        compare_flows(G, 'x', 'y', H, 3.0)

    def test_optional_capacity(self):
        # Test optional capacity parameter.
        G = nx.DiGraph()
        G.add_edge('x','a', spam = 3.0)
        G.add_edge('x','b', spam = 1.0)
        G.add_edge('a','c', spam = 3.0)
        G.add_edge('b','c', spam = 5.0)
        G.add_edge('b','d', spam = 4.0)
        G.add_edge('d','e', spam = 2.0)
        G.add_edge('c','y', spam = 2.0)
        G.add_edge('e','y', spam = 3.0)

        solnFlows = {'x': {'a': 2.0, 'b': 1.0},
                     'a': {'c': 2.0},
                     'b': {'c': 0, 'd': 1.0},
                     'c': {'y': 2.0},
                     'd': {'e': 1.0},
                     'e': {'y': 1.0},
                     'y': {}}
        solnValue = 3.0
        s = 'x'
        t = 'y'
        
        flowValue, flowDict = nx.ford_fulkerson(G, s, t, capacity = 'spam')
        assert_equal(flowValue, solnValue)
        assert_equal(flowDict, solnFlows)
        assert_equal(nx.min_cut(G, s, t, capacity = 'spam'), solnValue)
        assert_equal(nx.max_flow(G, s, t, capacity = 'spam'), solnValue)
        assert_equal(nx.ford_fulkerson_flow(G, s, t, capacity = 'spam'),
                     solnFlows)

    def test_digraph_infcap_edges(self):
        # DiGraph with infinite capacity edges
        G = nx.DiGraph()
        G.add_edge('s', 'a')
        G.add_edge('s', 'b', capacity = 30)
        G.add_edge('a', 'c', capacity = 25)
        G.add_edge('b', 'c', capacity = 12)
        G.add_edge('a', 't', capacity = 60)
        G.add_edge('c', 't')

        H = {'s': {'a': 85, 'b': 12},
             'a': {'c': 25, 't': 60},
             'b': {'c': 12},
             'c': {'t': 37},
             't': {}}

        compare_flows(G, 's', 't', H, 97)

        # DiGraph with infinite capacity digon
        G = nx.DiGraph()
        G.add_edge('s', 'a', capacity = 85)
        G.add_edge('s', 'b', capacity = 30)
        G.add_edge('a', 'c')
        G.add_edge('c', 'a')
        G.add_edge('b', 'c', capacity = 12)
        G.add_edge('a', 't', capacity = 60)
        G.add_edge('c', 't', capacity = 37)

        H = {'s': {'a': 85, 'b': 12},
             'a': {'c': 25, 't': 60},
             'c': {'a': 0, 't': 37},
             'b': {'c': 12},
             't': {}}

        compare_flows(G, 's', 't', H, 97)
        

    def test_digraph_infcap_path(self):
        # Graph with infinite capacity (s, t)-path
        G = nx.DiGraph()
        G.add_edge('s', 'a')
        G.add_edge('s', 'b', capacity = 30)
        G.add_edge('a', 'c')
        G.add_edge('b', 'c', capacity = 12)
        G.add_edge('a', 't', capacity = 60)
        G.add_edge('c', 't')

        assert_raises(nx.NetworkXUnbounded,
                      nx.ford_fulkerson, G, 's', 't')
        assert_raises(nx.NetworkXUnbounded,
                      nx.max_flow, G, 's', 't')
        assert_raises(nx.NetworkXUnbounded,
                      nx.ford_fulkerson_flow, G, 's', 't')
        assert_raises(nx.NetworkXUnbounded,
                      nx.min_cut, G, 's', 't')

    def test_graph_infcap_edges(self):
        # Undirected graph with infinite capacity edges
        G = nx.Graph()
        G.add_edge('s', 'a')
        G.add_edge('s', 'b', capacity = 30)
        G.add_edge('a', 'c', capacity = 25)
        G.add_edge('b', 'c', capacity = 12)
        G.add_edge('a', 't', capacity = 60)
        G.add_edge('c', 't')

        H = {'s': {'a': 85, 'b': 12},
             'a': {'c': 25, 's': 85, 't': 60},
             'b': {'c': 12, 's': 12},
             'c': {'a': 25, 'b': 12, 't': 37},
             't': {'a': 60, 'c': 37}}

        compare_flows(G, 's', 't', H, 97)

    def test_digraph4(self):
        # From ticket #429 by mfrasca.
        G = nx.DiGraph()
        G.add_edge('s', 'a', capacity = 2)
        G.add_edge('s', 'b', capacity = 2)
        G.add_edge('a', 'b', capacity = 5)
        G.add_edge('a', 't', capacity = 1)
        G.add_edge('b', 'a', capacity = 1)
        G.add_edge('b', 't', capacity = 3)
        flowSoln = {'a': {'b': 1, 't': 1},
                    'b': {'a': 0, 't': 3},
                    's': {'a': 2, 'b': 2},
                    't': {}}
        compare_flows(G, 's', 't', flowSoln, 4)


