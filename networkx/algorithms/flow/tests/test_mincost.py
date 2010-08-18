# -*- coding: utf-8 -*-

import networkx as nx
from nose.tools import assert_equal, assert_raises

class TestNetworkSimplex:
    def test_simple_digraph(self):
        G = nx.DiGraph()
        G.add_node('a', demand = -5)
        G.add_node('d', demand = 5)
        G.add_edge('a', 'b', weight = 3, capacity = 4)
        G.add_edge('a', 'c', weight = 6, capacity = 10)
        G.add_edge('b', 'd', weight = 1, capacity = 9)
        G.add_edge('c', 'd', weight = 2, capacity = 5)
        flowCost, H = nx.network_simplex(G)
        soln = {'a': {'b': 4, 'c': 1},
                'b': {'d': 4},
                'c': {'d': 1},
                'd': {}}
        assert_equal(flowCost, 24)
        assert_equal(nx.min_cost_flow_cost(G), 24)
        assert_equal(H, soln)
        assert_equal(nx.min_cost_flow(G), soln)
        assert_equal(nx.cost_of_flow(G, H), 24)

    def test_negcycle_infcap(self):
        G = nx.DiGraph()
        G.add_node('s', demand = -5)
        G.add_node('t', demand = 5)
        G.add_edge('s', 'a', weight = 1, capacity = 3)
        G.add_edge('a', 'b', weight = 3)
        G.add_edge('c', 'a', weight = -6)
        G.add_edge('b', 'd', weight = 1)
        G.add_edge('d', 'c', weight = -2)
        G.add_edge('d', 't', weight = 1, capacity = 3)
        assert_raises(nx.NetworkXUnbounded, nx.network_simplex, G)

    def test_sum_demands_not_zero(self):
        G = nx.DiGraph()
        G.add_node('s', demand = -5)
        G.add_node('t', demand = 4)
        G.add_edge('s', 'a', weight = 1, capacity = 3)
        G.add_edge('a', 'b', weight = 3)
        G.add_edge('a', 'c', weight = -6)
        G.add_edge('b', 'd', weight = 1)
        G.add_edge('c', 'd', weight = -2)
        G.add_edge('d', 't', weight = 1, capacity = 3)
        assert_raises(nx.NetworkXUnfeasible, nx.network_simplex, G)

    def test_no_flow_satisfying_demands(self):
        G = nx.DiGraph()
        G.add_node('s', demand = -5)
        G.add_node('t', demand = 5)
        G.add_edge('s', 'a', weight = 1, capacity = 3)
        G.add_edge('a', 'b', weight = 3)
        G.add_edge('a', 'c', weight = -6)
        G.add_edge('b', 'd', weight = 1)
        G.add_edge('c', 'd', weight = -2)
        G.add_edge('d', 't', weight = 1, capacity = 3)
        assert_raises(nx.NetworkXUnfeasible, nx.network_simplex, G)

    def test_transshipment(self):
        G = nx.DiGraph()
        G.add_node('a', demand = 1)
        G.add_node('b', demand = -2)
        G.add_node('c', demand = -2)
        G.add_node('d', demand = 3)
        G.add_node('e', demand = -4)
        G.add_node('f', demand = -4)
        G.add_node('g', demand = 3)
        G.add_node('h', demand = 2)
        G.add_node('r', demand = 3)
        G.add_edge('a', 'c', weight = 3)
        G.add_edge('r', 'a', weight = 2)
        G.add_edge('b', 'a', weight = 9)
        G.add_edge('r', 'c', weight = 0)
        G.add_edge('b', 'r', weight = -6)
        G.add_edge('c', 'd', weight = 5)
        G.add_edge('e', 'r', weight = 4)
        G.add_edge('e', 'f', weight = 3)
        G.add_edge('h', 'b', weight = 4)
        G.add_edge('f', 'd', weight = 7)
        G.add_edge('f', 'h', weight = 12)
        G.add_edge('g', 'd', weight = 12)
        G.add_edge('f', 'g', weight = -1)
        G.add_edge('h', 'g', weight = -10)
        flowCost, H = nx.network_simplex(G)
        soln = {'a': {'c': 0},
                'b': {'a': 0, 'r': 2},
                'c': {'d': 3},
                'd': {},
                'e': {'r': 3, 'f': 1},
                'f': {'d': 0, 'g': 3, 'h': 2},
                'g': {'d': 0},
                'h': {'b': 0, 'g': 0},
                'r': {'a': 1, 'c': 1}}
        assert_equal(flowCost, 41)
        assert_equal(nx.min_cost_flow_cost(G), 41)
        assert_equal(H, soln)
        assert_equal(nx.min_cost_flow(G), soln)
        assert_equal(nx.cost_of_flow(G, H), 41)

    def test_max_flow_min_cost(self):
        G = nx.DiGraph()
        G.add_edge('s', 'a', bandwidth = 6)
        G.add_edge('s', 'c', bandwidth = 10, cost = 10)
        G.add_edge('a', 'b', cost = 6)
        G.add_edge('b', 'd', bandwidth = 8, cost = 7)
        G.add_edge('c', 'd', cost = 10)
        G.add_edge('d', 't', bandwidth = 5, cost = 5)
        soln = {'s': {'a': 5, 'c': 0},
                'a': {'b': 5},
                'b': {'d': 5},
                'c': {'d': 0},
                'd': {'t': 5},
                't': {}}
        flow = nx.max_flow_min_cost(G, 's', 't', capacity = 'bandwidth',
                                    weight = 'cost')
        assert_equal(flow, soln)
        assert_equal(nx.cost_of_flow(G, flow, weight = 'cost'), 90)

    def test_digraph1(self):
        # From Bradley, S. P., Hax, A. C. and Magnanti, T. L. Applied
        # Mathematical Programming. Addison-Wesley, 1977.
        G = nx.DiGraph()
        G.add_node(1, demand = -20)
        G.add_node(4, demand = 5)
        G.add_node(5, demand = 15)
        G.add_edges_from([(1, 2, {'capacity': 15, 'weight': 4}),
                          (1, 3, {'capacity': 8, 'weight': 4}),
                          (2, 3, {'weight': 2}),
                          (2, 4, {'capacity': 4, 'weight': 2}),
                          (2, 5, {'capacity': 10, 'weight': 6}),
                          (3, 4, {'capacity': 15, 'weight': 1}),
                          (3, 5, {'capacity': 5, 'weight': 3}),
                          (4, 5, {'weight': 2}),
                          (5, 3, {'capacity': 4, 'weight': 1})])
        flowCost, H = nx.network_simplex(G)
        soln = {1: {2: 12, 3: 8},
                2: {3: 8, 4: 4, 5: 0},
                3: {4: 11, 5: 5},
                4: {5: 10},
                5: {3: 0}}
        assert_equal(flowCost, 150)
        assert_equal(nx.min_cost_flow_cost(G), 150)
        assert_equal(H, soln)
        assert_equal(nx.min_cost_flow(G), soln)
        assert_equal(nx.cost_of_flow(G, H), 150)

