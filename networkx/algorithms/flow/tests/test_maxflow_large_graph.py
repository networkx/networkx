# -*- coding: utf-8 -*-
"""Max flow algorithm test suite on large graphs.

Run with nose: nosetests -v test_max_flow.py
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.


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


class TestMaxflowLargeGraph:
    def test_complete_graph(self):
        N = 50
        G = nx.complete_graph(N)
        for (u, v) in G.edges():
            G[u][v]['capacity'] = 5
        assert_equal(nx.ford_fulkerson(G, 1, 2)[0], 5 * (N - 1))

    def test_pyramid(self):
        N = 10 
#        N = 100 # this gives a graph with 5051 nodes
        G = gen_pyramid(N)
        assert_almost_equal(nx.ford_fulkerson(G, (0, 0), 't')[0], 1.)

