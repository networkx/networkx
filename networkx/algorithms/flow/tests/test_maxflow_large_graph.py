# -*- coding: utf-8 -*-
"""Max flow algorithm test suite on large graphs.

Run with nose: nosetests -v test_max_flow.py
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.


import os
from functools import partial
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


def validate_flows(G, s, t, solnValue, flowValue, flowDict, pred=assert_equal):
    pred(solnValue, flowValue)
    assert_equal(set(G), set(flowDict))
    for u in G:
        assert_equal(set(G[u]), set(flowDict[u]))
    excess = dict((u, 0) for u in flowDict)
    for u in flowDict:
        for v, flow in flowDict[u].items():
            ok_(flow <= G[u][v].get('capacity', float('inf')))
            ok_(flow >= 0)
            excess[u] -= flow
            excess[v] += flow
    for u, exc in excess.items():
        if u == s:
            pred(exc, -solnValue)
        elif u == t:
            pred(exc, solnValue)
        else:
            pred(exc, 0)


class TestMaxflowLargeGraph:
    def _test_graph(self, G, s, t, soln, pred=assert_equal):
        validate = partial(validate_flows, G, s, t, soln, pred=pred)
        #validate(*nx.ford_fulkerson(G, s, t))
        validate(*nx.edmonds_karp(G, s, t))
        validate(*nx.preflow_push(G, s, t))
        validate(*nx.shortest_augmenting_path(G, s, t, two_phase=False))
        validate(*nx.shortest_augmenting_path(G, s, t, two_phase=True))

    def test_complete_graph(self):
        N = 50
        G = nx.complete_graph(N)
        for (u, v) in G.edges():
            G[u][v]['capacity'] = 5
        self._test_graph(G, 1, 2, 5 * (N - 1))

    def test_pyramid(self):
        N = 10
#        N = 100 # this gives a graph with 5051 nodes
        G = gen_pyramid(N)
        self._test_graph(G, (0, 0), 't', 1., assert_almost_equal)

    def test_gl1(self):
        G = read_graph('gl1')
        self._test_graph(G, 1, len(G), 156545)

    def test_gw1(self):
        G = read_graph('gw1')
        self._test_graph(G, 1, len(G), 1202018)

    def test_wlm3(self):
        G = read_graph('wlm3')
        self._test_graph(G, 1, len(G), 11875108)

    def test_preflow_push_global_relabel(self):
        G = read_graph('gw1')
        assert_equal(nx.preflow_push(G, 1, len(G), global_relabel_freq=50)[0],
                     1202018)
