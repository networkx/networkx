# -*- coding: utf-8 -*-
"""Maximum flow algorithms test suite on large graphs.
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.


import os
from functools import partial
from nose.tools import *

import networkx as nx
from networkx.algorithms.flow.utils import *
from networkx.algorithms.flow.edmonds_karp import *
from networkx.algorithms.flow.ford_fulkerson import *
from networkx.algorithms.flow.preflow_push import *
from networkx.algorithms.flow.shortest_augmenting_path import *

flow_funcs = [edmonds_karp, ford_fulkerson, preflow_push,
              shortest_augmenting_path]

ford_fulkerson = partial(ford_fulkerson, legacy=False)
ford_fulkerson.__name__ = 'ford_fulkerson'
preflow_push = partial(preflow_push, value_only=False)
preflow_push.__name__ = 'preflow_push'

flow_funcs = [edmonds_karp, ford_fulkerson, preflow_push,
                shortest_augmenting_path]

msg = "Assertion failed in function: {0}"

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


def validate_flows(G, s, t, solnValue, R, flow_func):
    legacy = R.graph.get('algorithm') == "ford_fulkerson_legacy"
    flowValue = R.graph['flow_value']
    if legacy:
        flowDict = R.graph['flow_dict']
    else:
        flowDict = build_flow_dict(G, R)
    assert_equal(solnValue, flowValue, msg=msg.format(flow_func.__name__))
    assert_equal(set(G), set(flowDict), msg=msg.format(flow_func.__name__))
    for u in G:
        assert_equal(set(G[u]), set(flowDict[u]),
                     msg=msg.format(flow_func.__name__))
    excess = dict((u, 0) for u in flowDict)
    for u in flowDict:
        for v, flow in flowDict[u].items():
            ok_(flow <= G[u][v].get('capacity', float('inf')),
                msg=msg.format(flow_func.__name__))
            ok_(flow >= 0, msg=msg.format(flow_func.__name__))
            excess[u] -= flow
            excess[v] += flow
    for u, exc in excess.items():
        if u == s:
            assert_equal(exc, -solnValue, msg=msg.format(flow_func.__name__))
        elif u == t:
            assert_equal(exc, solnValue, msg=msg.format(flow_func.__name__))
        else:
            assert_equal(exc, 0, msg=msg.format(flow_func.__name__))


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

        for flow_func in flow_funcs:
            R = flow_func(G, 1, 2)
            flow_value = R.graph['flow_value']
            assert_equal(flow_value, 5 * (N - 1),
                         msg=msg.format(flow_func.__name__))

    def test_pyramid(self):
        N = 10
#        N = 100 # this gives a graph with 5051 nodes
        G = gen_pyramid(N)
        for flow_func in flow_funcs:
            R = flow_func(G, (0, 0), 't')
            flow_value = R.graph['flow_value']
            assert_almost_equal(flow_value, 1.,
                                msg=msg.format(flow_func.__name__))

    def test_gl1(self):
        G = read_graph('gl1')
        s = 1
        t = len(G)
        for flow_func in flow_funcs:
            validate_flows(G, s, t, 156545, flow_func(G, s, t),
                           flow_func)

    def test_gw1(self):
        G = read_graph('gw1')
        s = 1
        t = len(G)
        for flow_func in flow_funcs:
            validate_flows(G, s, t, 1202018, flow_func(G, s, t),
                           flow_func)

    def test_wlm3(self):
        G = read_graph('wlm3')
        s = 1
        t = len(G)
        for flow_func in flow_funcs:
            validate_flows(G, s, t, 11875108, flow_func(G, s, t),
                           flow_func)

    def test_preflow_push_global_relabel(self):
        G = read_graph('gw1')
        R = nx.preflow_push(G, 1, len(G), global_relabel_freq=50)
        assert_equal(R.graph['flow_value'], 1202018)
