#!/usr/bin/env python
from nose.tools import *
from networkx import *

import random
random.seed(0)

def test_double_edge_swap():
    graph = barabasi_albert_graph(200,1)
    degrees = sorted(graph.degree().values())
    G = double_edge_swap(graph, 40)
    assert_equal(degrees, sorted(graph.degree().values()))

def test_connected_double_edge_swap():
    graph = barabasi_albert_graph(200,1)
    degrees = sorted(graph.degree().values())
    G = connected_double_edge_swap(graph, 40)
    assert_true(is_connected(graph))
    assert_equal(degrees, sorted(graph.degree().values()))

@raises(NetworkXError)
def test_double_edge_swap_small():
    G = nx.double_edge_swap(nx.path_graph(3))

@raises(NetworkXError)
def test_double_edge_swap_tries():
    G = nx.double_edge_swap(nx.path_graph(10),nswap=1,max_tries=0)

@raises(NetworkXError)
def test_connected_double_edge_swap_small():
    G = nx.connected_double_edge_swap(nx.path_graph(3))

@raises(NetworkXError)
def test_connected_double_edge_swap_not_connected():
    G = nx.path_graph(3)
    G.add_path([10,11,12])
    G = nx.connected_double_edge_swap(G)

def test_degree_seq_c4():
    G = cycle_graph(4)
    degrees = sorted(G.degree().values())
    G = double_edge_swap(G,1,100)
    assert_equal(degrees, sorted(G.degree().values()))

