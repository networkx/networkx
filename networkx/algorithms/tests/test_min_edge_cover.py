from nose.tools import assert_equal, assert_true
import networkx as nx


def test_empty_graph():
    G = nx.Graph()
    assert_equal(nx.min_edge_cover(G), set([]))


def test_graph_with_loop():
    G = nx.Graph()
    G.add_edge(0, 0)
    assert_equal(nx.min_edge_cover(G), set([(0, 0)]))


def test_graph_single_edge():
    G = nx.Graph()
    G.add_edge(0, 1)
    assert_equal(nx.min_edge_cover(G),
                 set([(0, 1), (1, 0)]))


def test_bipartite():
    G = nx.Graph()
    G.add_nodes_from([1,2,3,4], bipartite=0)
    G.add_nodes_from(['a','b','c'], bipartite=1)
    G.add_edges_from([(1,'a'), (1,'b'), (2,'b'), (2,'c'), (3,'c'), (4,'a')])
    min_cover = nx.min_edge_cover(G)
    assert_true(nx.is_edge_covering(G, min_cover))
    assert_equal(len(min_cover), 8)

def test_complete_graph():
    G = nx.complete_graph(10)
    min_cover = nx.min_edge_cover(G)
    assert_true(nx.is_edge_covering(G, min_cover))
    assert_equal(len(min_cover), 10)
