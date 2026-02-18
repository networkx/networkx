"""
    Unit tests for rumor centrality.
"""
import math

import pytest

import networkx as nx


def test_rumor_centrality_1():
    K2 = nx.complete_graph(2)
    d = nx.rumor_centrality(K2)
    exact = dict(zip(range(2), [1] * 2))
    for n, rc in d.items():
        assert exact[n] == pytest.approx(rc, abs=1e-7)


def test_rumor_centrality_2():
    P3 = nx.path_graph(3)
    d = nx.rumor_centrality(P3)
    exact = {0: 1, 1: 2, 2: 1}
    for n, rc in d.items():
        assert exact[n] == pytest.approx(rc, abs=1e-7)


def test_rumor_centrality_3():
    P5 = nx.path_graph(5)
    d = nx.rumor_centrality(P5)
    exact = {0: 1, 1: 4, 2: 6, 3: 4, 4: 1}
    for n, rc in d.items():
        assert exact[n] == pytest.approx(rc, abs=1e-7)


def test_rumor_centrality_4():
    S4 = nx.star_graph(4)
    d = nx.rumor_centrality(S4)
    exact = {0: 24, 1: 6, 2: 6, 3: 6, 4: 6}
    for n, rc in d.items():
        assert exact[n] == pytest.approx(rc, abs=1e-7)


def test_rumor_centrality_5():
    S9 = nx.star_graph(9)
    d = nx.rumor_centrality(S9)
    exact = {
        0: math.factorial(9),
        1: math.factorial(8),
        2: math.factorial(8),
        3: math.factorial(8),
        4: math.factorial(8),
        5: math.factorial(8),
        6: math.factorial(8),
        7: math.factorial(8),
        8: math.factorial(8),
        9: math.factorial(8),
    }
    for n, rc in d.items():
        assert exact[n] == pytest.approx(rc, abs=1e-7)


def test_rumor_centrality_6():
    G = nx.Graph()
    G.add_nodes_from(range(5))
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(1, 4)
    # 0 -- 1 -- 2 -- 3
    #      |
    #      4

    d = nx.rumor_centrality(G)
    exact = {0: 3, 1: 12, 2: 8, 3: 2, 4: 3}
    for n, rc in d.items():
        assert exact[n] == pytest.approx(rc, abs=1e-7)


def test_rumor_centrality_7_weighted_graph():
    G = nx.Graph()
    G.add_nodes_from(range(5))
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(1, 4)
    # 0 -- 1 -- 2 -- 3
    #      |
    #      4

    d = nx.rumor_centrality(G)
    exact = {0: 3, 1: 12, 2: 8, 3: 2, 4: 3}
    for n, rc in d.items():
        assert exact[n] == pytest.approx(rc, abs=1e-7)


def test_rumor_centrality_8_multigraph():
    e = [(1, 2), (1, 2), (2, 3), (3, 4)]
    G = nx.MultiGraph(e)

    with pytest.raises(nx.NetworkXNotImplemented):
        nx.rumor_centrality(G)


def test_rumor_centrality_9_directed():
    e = [(1, 2), (2, 3), (3, 4)]
    G = nx.DiGraph(e)

    with pytest.raises(nx.NetworkXNotImplemented):
        nx.rumor_centrality(G)


def test_rumor_centrality_10_cycles():
    G = nx.cycle_graph(3)

    with pytest.raises(nx.NetworkXNotImplemented):
        nx.rumor_centrality(G)
