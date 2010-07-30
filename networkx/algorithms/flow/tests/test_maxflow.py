# -*- coding: utf-8 -*-
"""Max flow algorithm test suite.

Run with nose: nosetests -v test_max_flow.py
"""

__author__ = u"""Loïc Séguin-C. <loicseguin@gmail.com>"""
u"""Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
All rights reserved.
BSD license.
"""

import networkx as nx
from nose.tools import *

def compare_flows(G, s, t, H, solnValue):
    output = nx.ford_fulkerson(G, s, t)
    flows = [edge[2]['flow']
            for edge in output[1].edges(data = True)]
    solnFlows = [H[u][v]['flow'] for (u, v) in output[1].edges()]

    assert_equal((output[0], flows), (solnValue, solnFlows))


class TestMaxflow:
    def test_graph1(self):
        # Trivial undirected graph
        G = nx.Graph()
        G.add_edge(1,2, capacity = 1.0)

        H = nx.Graph(G)
        H[1][2]['flow'] = 1.0

        compare_flows(G, 1, 2, H, 1.0)

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

        H = nx.Graph(G)
        H['x']['a']['flow'] = 3
        H['x']['b']['flow'] = 1
        H['a']['c']['flow'] = 3
        H['b']['c']['flow'] = 1
        H['b']['d']['flow'] = 2
        H['c']['y']['flow'] = 2
        H['d']['e']['flow'] = 2
        H['e']['y']['flow'] = 2

        compare_flows(G, 'x', 'y', H, 4.0)

    def test_digraph1(self):
        # The classic directed graph example
        G = nx.DiGraph()
        G.add_edge('a','b', capacity = 1000.0)
        G.add_edge('a','c', capacity = 1000.0)
        G.add_edge('b','c', capacity = 1.0)
        G.add_edge('b','d', capacity = 1000.0)
        G.add_edge('c','d', capacity = 1000.0)

        H = nx.DiGraph(G)
        H['a']['b']['flow'] = 1000.0
        H['a']['c']['flow'] = 1000.0
        H['b']['c']['flow'] = 0
        H['b']['d']['flow'] = 1000.0
        H['c']['d']['flow'] = 1000.0

        compare_flows(G, 'a', 'd', H, 2000.0)

        # An example in which some edges end up with zero flow.
        G = nx.DiGraph()
        G.add_edge('s', 'b', capacity = 2)
        G.add_edge('s', 'c', capacity = 1)
        G.add_edge('c', 'd', capacity = 1)
        G.add_edge('d', 'a', capacity = 1)
        G.add_edge('b', 'a', capacity = 2)
        G.add_edge('a', 't', capacity = 2)

        H = nx.DiGraph(G)
        H['s']['b']['flow'] = 2
        H['s']['c']['flow'] = 0
        H['c']['d']['flow'] = 0
        H['d']['a']['flow'] = 0
        H['b']['a']['flow'] = 2
        H['a']['t']['flow'] = 2

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

        H = nx.DiGraph(G)
        H['s']['v1']['flow'] = 12.0
        H['s']['v2']['flow'] = 11.0
        H['v2']['v1']['flow'] = 0
        H['v1']['v2']['flow'] = 0
        H['v3']['v2']['flow'] = 0
        H['v2']['v4']['flow'] = 11.0
        H['v4']['v3']['flow'] = 7.0
        H['v1']['v3']['flow'] = 12.0
        H['v3']['t']['flow'] = 19.0
        H['v4']['t']['flow'] = 4.0

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

        H = nx.DiGraph(G)
        H['x']['a']['flow'] = 2.0
        H['a']['c']['flow'] = 2.0
        H['x']['b']['flow'] = 1.0
        H['b']['c']['flow'] = 0
        H['b']['d']['flow'] = 1.0
        H['c']['y']['flow'] = 2.0
        H['d']['e']['flow'] = 1.0
        H['e']['y']['flow'] = 1.0

        compare_flows(G, 'x', 'y', H, 3.0)

    def test_digraph_infcap_edges(self):
        # DiGraph with infinite capacity edges
        G = nx.DiGraph()
        G.add_edge('s', 'a')
        G.add_edge('s', 'b', capacity = 30)
        G.add_edge('a', 'c', capacity = 25)
        G.add_edge('b', 'c', capacity = 12)
        G.add_edge('a', 't', capacity = 60)
        G.add_edge('c', 't')

        H = nx.DiGraph(G)
        H['s']['a']['flow'] = 85
        H['s']['b']['flow'] = 12
        H['a']['c']['flow'] = 25
        H['a']['t']['flow'] = 60
        H['b']['c']['flow'] = 12
        H['c']['t']['flow'] = 37

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

        H = nx.DiGraph(G)
        H['s']['a']['flow'] = 85
        H['s']['b']['flow'] = 12
        H['a']['c']['flow'] = 25
        H['c']['a']['flow'] = 0
        H['a']['t']['flow'] = 60
        H['b']['c']['flow'] = 12
        H['c']['t']['flow'] = 37

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

        assert_raises(nx.NetworkXError,
                      nx.ford_fulkerson, G, 's', 't')

    def test_graph_infcap_edges(self):
        # Undirected graph with infinite capacity edges
        G = nx.Graph()
        G.add_edge('s', 'a')
        G.add_edge('s', 'b', capacity = 30)
        G.add_edge('a', 'c', capacity = 25)
        G.add_edge('b', 'c', capacity = 12)
        G.add_edge('a', 't', capacity = 60)
        G.add_edge('c', 't')

        H = nx.Graph(G)
        H['s']['a']['flow'] = 85
        H['s']['b']['flow'] = 12
        H['a']['c']['flow'] = 25
        H['a']['t']['flow'] = 60
        H['b']['c']['flow'] = 12
        H['c']['t']['flow'] = 37

        compare_flows(G, 's', 't', H, 97)

