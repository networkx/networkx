"""
Unit tests for decay centrality

"""

import pytest

import networkx as nx


def test_decay_centrality_krackhardt_kite_graph():
    """
    Test the decay centrality of the krackhardt kite graph.

    """

    K = nx.krackhardt_kite_graph()
    c = nx.decay_centrality(K)

    d = {
        0: 2.9375,
        1: 2.9375,
        2: 2.6875,
        3: 3.4375,
        4: 2.6875,
        5: 3.375,
        6: 3.375,
        7: 3.0,
        8: 2.125,
        9: 1.3125,
    }

    for n in sorted(K):
        assert c[n] == pytest.approx(d[n], abs=1e-3)


def test_decay_centrality_balanced_tree():
    T = nx.balanced_tree(r=2, h=2)
    T.add_edge(5, 6)
    T.add_edge(3, 4)

    c = nx.decay_centrality(T)
    d = {0: 2.0, 1: 2.0, 2: 2.0, 3: 1.5, 4: 1.5, 5: 1.5, 6: 1.5}

    for n in sorted(T):
        assert c[n] == pytest.approx(d[n], abs=1e-3)


def test_decay_centrality_digraph():
    D = nx.DiGraph()
    D.add_edges_from(
        [
            (1, 3),
            (1, 5),
            (1, 2),
            (1, 6),
            (1, 9),
            (2, 4),
            (2, 7),
            (3, 5),
            (3, 6),
            (4, 8),
            (4, 7),
            (5, 6),
            (5, 9),
            (7, 8),
        ]
    )

    c = nx.decay_centrality(D, mode="in")
    d = {
        1: 0,
        3: 0.5,
        5: 1.0,
        2: 0.5,
        6: 1.5,
        9: 1.25,
        4: 0.75,
        7: 1.25,
        8: 1.375,
    }

    for n in sorted(D):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(D, mode="out")
    d = {
        1: 3.125,
        3: 1.25,
        5: 1.0,
        2: 1.25,
        6: 0,
        9: 0,
        4: 1.0,
        7: 0.5,
        8: 0,
    }

    for n in sorted(D):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(D, mode="all")
    d = {
        1: 3.125,
        3: 2.3125,
        5: 2.5625,
        2: 2.75,
        6: 2.3125,
        9: 2.0625,
        4: 2.25,
        7: 2.25,
        8: 1.625,
    }

    for n in sorted(D):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    assert D.is_directed()


def test_decay_centrality_Gb():
    Gb = nx.Graph()

    Gb.add_edges_from(
        [
            (1, 3),
            (1, 5),
            (1, 2),
            (1, 6),
            (1, 9),
            (2, 4),
            (2, 7),
            (3, 5),
            (3, 6),
            (4, 8),
            (4, 7),
            (5, 6),
            (5, 9),
            (7, 8),
        ]
    )

    c = nx.decay_centrality(Gb, delta=0.05)
    d = {
        1: 0.255125,
        3: 0.15525625,
        5: 0.20275625,
        2: 0.16250000000000003,
        6: 0.15525625,
        9: 0.10775625000000001,
        4: 0.15299999999999997,
        7: 0.15299999999999997,
        8: 0.10265,
    }

    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.15)
    d = {
        1: 0.798375,
        3: 0.5022562500000001,
        5: 0.62975625,
        2: 0.5624999999999999,
        6: 0.5022562500000001,
        9: 0.37475625000000007,
        4: 0.48600000000000004,
        7: 0.48600000000000004,
        8: 0.32789999999999997,
    }

    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.25)
    d = {
        1: 1.390625,
        3: 0.91015625,
        5: 1.09765625,
        2: 1.0625,
        6: 0.91015625,
        9: 0.72265625,
        4: 0.875,
        7: 0.875,
        8: 0.59375,
    }

    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.35)
    d = {
        1: 2.037875,
        3: 1.3957562499999998,
        5: 1.6232562499999998,
        2: 1.6625,
        6: 1.3957562499999998,
        9: 1.1682562499999998,
        4: 1.3439999999999999,
        7: 1.3439999999999999,
        8: 0.9253999999999999,
    }
    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.45)
    d = {
        1: 2.746125,
        3: 1.97825625,
        5: 2.22575625,
        2: 2.3625000000000007,
        6: 1.97825625,
        9: 1.73075625,
        4: 1.9169999999999998,
        7: 1.9169999999999998,
        8: 1.3576499999999996,
    }
    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.55)
    d = {
        1: 3.5213750000000004,
        3: 2.6792562500000003,
        5: 2.9267562500000004,
        2: 3.162500000000001,
        6: 2.6792562500000003,
        9: 2.4317562500000003,
        4: 2.618,
        7: 2.618,
        8: 1.9349000000000007,
    }
    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.65)
    d = {
        1: 4.369625,
        3: 3.5227562499999996,
        5: 3.7502562499999996,
        2: 4.0625,
        6: 3.5227562499999996,
        9: 3.2952562499999996,
        4: 3.4709999999999996,
        7: 3.4709999999999996,
        8: 2.7111499999999995,
    }
    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.75)
    d = {
        1: 5.296875,
        3: 4.53515625,
        5: 4.72265625,
        2: 5.0625,
        6: 4.53515625,
        9: 4.34765625,
        4: 4.5,
        7: 4.5,
        8: 3.75,
    }
    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.85)
    d = {
        1: 6.309125,
        3: 5.745256249999999,
        5: 5.872756249999998,
        2: 6.1625000000000005,
        6: 5.745256249999999,
        9: 5.6177562499999985,
        4: 5.728999999999999,
        7: 5.728999999999999,
        8: 5.124649999999999,
    }
    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)

    c = nx.decay_centrality(Gb, delta=0.95)
    d = {
        1: 7.412375,
        3: 7.18425625,
        5: 7.23175625,
        2: 7.362499999999999,
        6: 7.18425625,
        9: 7.13675625,
        4: 7.182,
        7: 7.182,
        8: 6.9178999999999995,
    }
    for n in sorted(Gb):
        assert c[n] == pytest.approx(d[n], abs=1e-3)


def test_decay_centrality_empty():
    G = nx.Graph()
    c = nx.decay_centrality(G)
    assert c == {}

    c = nx.decay_centrality(G, delta=0.1)
    assert c == {}


def test_decay_centrality_single_node():
    G = nx.Graph()
    G.add_node(1)
    c = nx.decay_centrality(G)
    d = {1: 0}

    for n in sorted(G):
        assert c[n] == pytest.approx(d[n], abs=1e-3)


def test_decay_centrality_subset_nodes():
    G = nx.Graph()
    G.add_nodes_from([1, 2, 3])
    G.add_edges_from([(1, 2), (1, 3), [1, 4]])
    c = nx.decay_centrality(G, u=[1, 3])
    d = {1: 1.5, 3: 1.0}
    assert sorted(c.keys()) == sorted(d.keys())
    for n in sorted(d):
        assert c[n] == pytest.approx(d[n], abs=1e-3)
