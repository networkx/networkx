import pytest

import networkx as nx


def test_dominating_set():
    G = nx.gnp_random_graph(100, 0.1)
    D = nx.dominating_set(G)
    assert nx.is_dominating_set(G, D)
    D = nx.dominating_set(G, start_with=0)
    assert nx.is_dominating_set(G, D)


def test_complete():
    """In complete graphs each node is a dominating set.
    Thus the dominating set has to be of cardinality 1.
    """
    K4 = nx.complete_graph(4)
    assert len(nx.dominating_set(K4)) == 1
    K5 = nx.complete_graph(5)
    assert len(nx.dominating_set(K5)) == 1


def test_raise_dominating_set():
    with pytest.raises(nx.NetworkXError):
        G = nx.path_graph(4)
        D = nx.dominating_set(G, start_with=10)


def test_is_dominating_set():
    G = nx.path_graph(4)
    d = {1, 3}
    assert nx.is_dominating_set(G, d)
    d = {0, 2}
    assert nx.is_dominating_set(G, d)
    d = {1}
    assert not nx.is_dominating_set(G, d)


def test_wikipedia_is_dominating_set():
    """Example from https://en.wikipedia.org/wiki/Dominating_set"""
    G = nx.cycle_graph(4)
    G.add_edges_from([(0, 4), (1, 4), (2, 5)])
    assert nx.is_dominating_set(G, {4, 3, 5})
    assert nx.is_dominating_set(G, {0, 2})
    assert nx.is_dominating_set(G, {1, 2})


def test_is_connected_dominating_set():
    G = nx.path_graph(4)
    D = {1, 2}
    assert nx.is_connected_dominating_set(G, D)
    D = {1, 3}
    assert not nx.is_connected_dominating_set(G, D)


def test_null_graph_connected_dominating_set():
    G = nx.Graph()
    assert 0 == len(nx.connected_dominating_set(G))


def test_single_node_graph_connected_dominating_set():
    G = nx.Graph()
    G.add_node(1)
    CD = nx.connected_dominating_set(G)
    assert nx.is_connected_dominating_set(G, CD)


def test_disconnected_graph_connected_dominating_set():
    G = nx.Graph()
    G.add_node(1)
    G.add_node(2)
    assert 0 == len(nx.connected_dominating_set(G))


def test_complete_graph_connected_dominating_set():
    K5 = nx.complete_graph(5)
    assert 1 == len(nx.connected_dominating_set(K5))
    K7 = nx.complete_graph(7)
    assert 1 == len(nx.connected_dominating_set(K7))


def test_small_connected_watts_strogatz_graph_connected_dominating_set():
    G = nx.connected_watts_strogatz_graph(10, 3, 0.5)
    D = nx.connected_dominating_set(G)
    assert nx.is_connected_dominating_set(G, D)


def test_medium_connected_watts_strogatz_graph_connected_dominating_set():
    G = nx.connected_watts_strogatz_graph(100, 10, 0.5)
    D = nx.connected_dominating_set(G)
    assert nx.is_connected_dominating_set(G, D)


def test_large_connected_watts_strogatz_graph_connected_dominating_set():
    G = nx.connected_watts_strogatz_graph(1000, 20, 0.5)
    D = nx.connected_dominating_set(G)
    assert nx.is_connected_dominating_set(G, D)


def test_empty_interval_graph_min_connected_dominating_set():
    G = nx.interval_graph([])
    D = nx.interval_graph_min_connected_dominating_set(G)
    assert 0 == len(D)


def test_disconnected_interval_graph_min_connected_dominating_set():
    G = nx.interval_graph([(1, 2), (3, 4)])
    D = nx.interval_graph_min_connected_dominating_set(G)
    assert 0 == len(D)


def test_interval_graph_min_connected_dominating_set():
    intervals = [
        (30, 37),
        (52, 53),
        (24, 26),
        (64, 66),
        (7, 31),
        (38, 40),
        (9, 18),
        (37, 64),
        (15, 21),
    ]
    G = nx.interval_graph(intervals)
    min_dom_set = {(7, 31), (30, 37), (37, 64)}
    D = nx.interval_graph_min_connected_dominating_set(G)
    assert min_dom_set == D


def test_raise_interval_graph_min_connected_dominating_set():
    with pytest.raises(TypeError):
        G = nx.Graph
        G.add_node(1)
        nx.interval_graph_min_connected_dominating_set(G)
