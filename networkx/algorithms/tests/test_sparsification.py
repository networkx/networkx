from nose.tools import *
import networkx as nx
import random


def _test_spanner(G, spanner, stretch, weight=None):
    original_length = dict(nx.shortest_path_length(G, weight=weight))
    spanner_length = dict(nx.shortest_path_length(spanner, weight=weight))
    for u in G.nodes():
        for v in G.nodes():
            if u in original_length and v in original_length[u]:
                assert spanner_length[u][v] <= stretch * original_length[u][v]


def test_spanner_node_set():
    G = nx.complete_graph(100)
    spanner = nx.spanner(G, 4)
    assert set(G.nodes()) == set(spanner.nodes())


def test_spanner_unweighted_complete_graph():
    G = nx.complete_graph(100)

    spanner = nx.spanner(G, 1)
    _test_spanner(G, spanner, 1)

    spanner = nx.spanner(G, 4)
    _test_spanner(G, spanner, 4)

    spanner = nx.spanner(G, 10)
    _test_spanner(G, spanner, 10)


def test_spanner_weighted_complete_graph():
    G = nx.complete_graph(100)
    for u, v in G.edges():
        G[u][v]['weight'] = random.random()

    spanner = nx.spanner(G, 1, weight='weight')
    _test_spanner(G, spanner, 1, weight='weight')

    spanner = nx.spanner(G, 4, weight='weight')
    _test_spanner(G, spanner, 4, weight='weight')

    spanner = nx.spanner(G, 10, weight='weight')
    _test_spanner(G, spanner, 10, weight='weight')


def test_spanner_unweighted_gnp_graph():
    G = nx.gnp_random_graph(100, 0.2)

    spanner = nx.spanner(G, 1)
    _test_spanner(G, spanner, 1)

    spanner = nx.spanner(G, 4)
    _test_spanner(G, spanner, 4)

    spanner = nx.spanner(G, 10)
    _test_spanner(G, spanner, 10)


def test_spanner_weighted_gnp_graph():
    G = nx.gnp_random_graph(100, 0.2)
    for u, v in G.edges():
        G[u][v]['weight'] = random.random()

    spanner = nx.spanner(G, 1)
    _test_spanner(G, spanner, 1)

    spanner = nx.spanner(G, 4)
    _test_spanner(G, spanner, 4)

    spanner = nx.spanner(G, 10)
    _test_spanner(G, spanner, 10)


def test_spanner_unweighted_disconnected_graph():
    G = nx.disjoint_union(nx.complete_graph(50), nx.complete_graph(50))

    spanner = nx.spanner(G, 1)
    _test_spanner(G, spanner, 1)

    spanner = nx.spanner(G, 4)
    _test_spanner(G, spanner, 4)

    spanner = nx.spanner(G, 10)
    _test_spanner(G, spanner, 10)


@raises(ValueError)
def test_spanner_invalid_stretch():
    G = nx.empty_graph()
    nx.spanner(G, 0)