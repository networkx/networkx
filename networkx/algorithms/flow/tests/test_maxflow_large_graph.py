# -*- coding: utf-8 -*-
"""Max flow algorithm test suite on large graphs.

Run with nose: nosetests -v test_max_flow.py
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.


import os

import networkx as nx
from nose.tools import *

def gen_pyramid(N):
        # This graph admits a flow of value 1 for which every arc is at
        # capacity (except the arcs incident to the sink which have
        # infinite capacity).
        G = nx.DiGraph()

        for i in range(N - 1):
            cap = 1. / (i + 2)
            for j in range(i + 1):
                G.add_edge((i, j), (i + 1, j),
                           capacity = cap)
                cap = 1. / (i + 1) - cap
                G.add_edge((i, j), (i + 1, j + 1),
                        capacity = cap)
                cap = 1. / (i + 2) - cap

        for j in range(N):
            G.add_edge((N - 1, j), 't')

        return G


def read_graph(name):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, name + '.gpickle.bz2')
    return nx.read_gpickle(path)


def validate_flows(G, s, t, solnValue, flowValue, flowDict):
    assert_equal(solnValue, flowValue)
    assert_equal(set(G), set(flowDict))
    for u in G:
        assert_equal(set(G[u]), set(flowDict[u]))
    excess = {}
    for u in flowDict:
        excess[u] = 0
    for u in flowDict:
        for v, flow in flowDict[u].items():
            ok_(flow <= G[u][v]['capacity'])
            ok_(flow >= 0)
            excess[u] -= flow
            excess[v] += flow
    for u, exc in excess.items():
        if u == s:
            assert_equal(exc, -solnValue)
        elif u == t:
            assert_equal(exc, solnValue)
        else:
            assert_equal(exc, 0)


class TestMaxflowLargeGraph:
    def test_complete_graph(self):
        N = 50
        G = nx.complete_graph(N)
        for (u, v) in G.edges():
            G[u][v]['capacity'] = 5
        assert_equal(nx.ford_fulkerson(G, 1, 2)[0], 5 * (N - 1))
        assert_equal(nx.preflow_push(G, 1, 2)[0], 5 * (N - 1))

    def test_pyramid(self):
        N = 10 
#        N = 100 # this gives a graph with 5051 nodes
        G = gen_pyramid(N)
        assert_almost_equal(nx.ford_fulkerson(G, (0, 0), 't')[0], 1.)
        assert_almost_equal(nx.preflow_push(G, (0, 0), 't')[0], 1.)

    def test_gl1(self):
        G = read_graph('gl1')
        s = 1
        t = len(G)
        validate_flows(G, s, t, 156545, *nx.ford_fulkerson(G, s, t))
        validate_flows(G, s, t, 156545, nx.preflow_push_value(G, s, t),
                       nx.preflow_push_flow(G, s, t))

    def test_gw1(self):
        G = read_graph('gw1')
        s = 1
        t = len(G)
        validate_flows(G, s, t, 1202018, *nx.ford_fulkerson(G, s, t))
        validate_flows(G, s, t, 1202018, nx.preflow_push_value(G, s, t),
                       nx.preflow_push_flow(G, s, t))

    def test_wlm3(self):
        G = read_graph('wlm3')
        s = 1
        t = len(G)
        validate_flows(G, s, t, 11875108, *nx.ford_fulkerson(G, s, t))
        validate_flows(G, s, t, 11875108, nx.preflow_push_value(G, s, t),
                       nx.preflow_push_flow(G, s, t))

    def test_preflow_push_global_relabel(self):
        G = read_graph('gw1')
        assert_equal(nx.preflow_push(G, 1, len(G), global_relabel_freq=50)[0],
                     1202018)
