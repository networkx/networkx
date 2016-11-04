import networkx as nx
from nose.tools import *

import networkx.generators.line as line
from networkx.testing.utils import *

def test_node_func():
    # graph
    G = nx.Graph()
    G.add_edge(1,2)
    nf = line._node_func(G)
    assert_equal(nf(1,2), (1,2))
    assert_equal(nf(2,1), (1,2))

    # multigraph
    G = nx.MultiGraph()
    G.add_edge(1,2)
    G.add_edge(1,2)
    nf = line._node_func(G)
    assert_equal(nf(1,2,0), (1,2,0))
    assert_equal(nf(2,1,0), (1,2,0))

def test_edge_func():
    # graph
    G = nx.Graph()
    G.add_edge(1,2)
    G.add_edge(2,3)
    ef = line._edge_func(G)
    expected = [(1,2),(2,3)]
    assert_edges_equal(ef(), expected)

    # digraph
    G = nx.MultiDiGraph()
    G.add_edge(1,2)
    G.add_edge(2,3)
    G.add_edge(2,3)
    ef = line._edge_func(G)
    expected = [(1,2,0),(2,3,0),(2,3,1)]
    result = sorted(ef())
    assert_equal(expected, result)

def test_sorted_edge():
    assert_equal( (1,2), line._sorted_edge(1,2) )
    assert_equal( (1,2), line._sorted_edge(2,1) )

class TestGeneratorLine():
    def test_star(self):
        G = nx.star_graph(5)
        L = nx.line_graph(G)
        assert_true(nx.is_isomorphic(L, nx.complete_graph(5)))

    def test_path(self):
        G = nx.path_graph(5)
        L = nx.line_graph(G)
        assert_true(nx.is_isomorphic(L, nx.path_graph(4)))

    def test_cycle(self):
        G = nx.cycle_graph(5)
        L = nx.line_graph(G)
        assert_true(nx.is_isomorphic(L, G))

    def test_digraph1(self):
        G = nx.DiGraph()
        G.add_edges_from([(0,1),(0,2),(0,3)])
        L = nx.line_graph(G)
        # no edge graph, but with nodes
        assert_equal(L.adj, {(0,1):{}, (0,2):{}, (0,3):{}})

    def test_digraph2(self):
        G = nx.DiGraph()
        G.add_edges_from([(0,1),(1,2),(2,3)])
        L = nx.line_graph(G)
        assert_edges_equal(L.edges(), [((0, 1), (1, 2)), ((1, 2), (2, 3))])

    def test_create1(self):
        G = nx.DiGraph()
        G.add_edges_from([(0,1),(1,2),(2,3)])
        L = nx.line_graph(G, create_using=nx.Graph())
        assert_edges_equal(L.edges(), [((0, 1), (1, 2)), ((1, 2), (2, 3))])

    def test_create2(self):
        G = nx.Graph()
        G.add_edges_from([(0,1),(1,2),(2,3)])
        L = nx.line_graph(G, create_using=nx.DiGraph())
        assert_edges_equal(L.edges(), [((0, 1), (1, 2)), ((1, 2), (2, 3))])
