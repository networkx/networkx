#!/usr/bin/env python
from nose.tools import *
import networkx as nx

# Functions to test flow_hierarchy measure

def test_flow_hierarchy_exception():
    G = nx.cycle_graph(5)
    assert_raises(nx.NetworkXError,nx.flow_hierarchy,G)

def test_flow_hierarchy_cycle():
    G = nx.cycle_graph(5,create_using=nx.DiGraph())
    assert_equal(nx.flow_hierarchy(G),0.0)

def test_flow_hierarchy_tree():
    G = nx.full_rary_tree(2,16,create_using=nx.DiGraph())
    assert_equal(nx.flow_hierarchy(G),1.0)

def test_flow_hierarchy_1():
    G = nx.DiGraph()
    G.add_edges_from([(0,1),(1,2),(2,3),(3,1),(3,4),(0,4)])
    assert_equal(nx.flow_hierarchy(G),0.5)

def test_flow_hierarchy_weight():
    G = nx.DiGraph()
    G.add_edges_from([(0,1,{'weight':.3}),
                      (1,2,{'weight':.1}),
                      (2,3,{'weight':.1}),
                      (3,1,{'weight':.1}),
                      (3,4,{'weight':.3}),
                      (0,4,{'weight':.3})])
    assert_equal(nx.flow_hierarchy(G,weight='weight'),.75)

# Functions to test global_reaching_centrality measure

def test_grc_exception1():
    G = nx.DiGraph()
    assert_raises(nx.NetworkXError, nx.global_reaching_centrality, G)

def test_grc_directed_star():
    G = nx.DiGraph()
    G.add_edge(1,2)
    G.add_edge(1,3)
    assert_equal(nx.global_reaching_centrality(G), 1.0)

def test_grc_undirected_unweighted_star():
    G = nx.star_graph(2)
    assert_equal(nx.global_reaching_centrality(G), 0.25)

def test_grc_undirected_weighted_star():
    G = nx.Graph()
    G.add_edge(1,2,{"weight":1})
    G.add_edge(1,3,{"weight":2})
    assert_equal(nx.global_reaching_centrality(G), 0.25)

def test_grc_cycle_directed_unweighted():
    G = nx.DiGraph()
    G.add_edge(1, 2)
    G.add_edge(2, 1)
    assert_equal(nx.global_reaching_centrality(G), 0.)

def test_grc_cycle_undirected_unweighted():
    G = nx.Graph()
    G.add_edge(1, 2)
    assert_equal(nx.global_reaching_centrality(G), 0.)

def test_grc_cycle_directed_weighted():
    G = nx.DiGraph()
    G.add_edge(1, 2, {"weight": 1})
    G.add_edge(2, 1, {"weight": 1})
    assert_equal(nx.global_reaching_centrality(G, weight="weight"), 0.)

def test_grc_cycle_undirected_weighted():
    G = nx.Graph()
    G.add_edge(1, 2, {"weight": 1})
    assert_equal(nx.global_reaching_centrality(G, weight="weight"), 0.)

def test_grc_directed_weighted():
    G = nx.DiGraph()
    G.add_edge("A","B", {"weight":5.0})
    G.add_edge("B","C", {"weight":1.0})
    G.add_edge("B","D", {"weight":0.25})
    G.add_edge("D","E", {"weight":1.0})
    
    denom = G.order() - 1
    A_local = sum([5, 3, 2.625, 2.0833333333333]) / denom
    B_local = sum([1, 0.25, 0.625]) / denom
    C_local = 0
    D_local = sum([1.,]) / denom
    E_local = 0

    local_reach_ctrs = [A_local, C_local, B_local, D_local, E_local]
    max_local = max(local_reach_ctrs)
    handcomputed_grc = sum([max_local - lrc for lrc in local_reach_ctrs]) / denom

    algcomputed_grc = nx.global_reaching_centrality(G, weight="weight")
    assert_almost_equal(handcomputed_grc, algcomputed_grc, places=7)
