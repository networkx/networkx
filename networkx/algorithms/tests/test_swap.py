#!/usr/bin/env python
from nose.tools import *
from networkx import *

def test_double_edge_swap():
    graph = barabasi_albert_graph(200,1)
    degreeStart = sorted(graph.degree().values())
    G = connected_double_edge_swap(graph, 40)
    assert_true(is_connected(graph))
    degseq = sorted(graph.degree().values())
    assert_true(degreeStart == degseq)
    G = double_edge_swap(graph, 40)
    degseq2 = sorted(graph.degree().values())
    assert_true(degreeStart == degseq2)

def test_degree_seq_c4():
    G = cycle_graph(4)
    degree_start = sorted(G.degree().values())
    G = double_edge_swap(G,1,100)
    degseq = sorted(G.degree().values())
    assert_true(degree_start == degseq)

