import networkx as nx

from networkx.algorithms.moral.moralize import get_moral_graph

from nose.tools import assert_equal, assert_true, assert_raises


def test_get_moral_graph():
    graph = nx.DiGraph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    graph.add_edges_from([(1, 2), (3, 2), (4, 1), (4, 5), (6, 5), (7, 5)])
    moral_graph = get_moral_graph(graph)
    assert_true(not moral_graph.is_directed())
    assert_true(moral_graph.has_edge(1, 3))
    assert_true(moral_graph.has_edge(4, 6))
    assert_true(moral_graph.has_edge(6, 7))
    assert_true(moral_graph.has_edge(4, 7))
    assert_true(not moral_graph.has_edge(1, 5))
