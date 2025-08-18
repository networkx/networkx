"""Unit tests for low conductance cut"""

import math
import random

import pytest

import networkx as nx
from networkx.algorithms.spectral.expander_decomposition import expander_decomposition


def connected_cliques(n, k, r):
    """Returns k cliques of size n, with r edges placed at random between the
    different cliques.
    """
    G = nx.Graph()
    for i in range(k):
        G.add_edges_from(nx.complete_graph(range(i * n, (i + 1) * n)).edges)

    for _ in range(r):
        clique_1, clique_2 = random.sample(range(k), 2)
        u = random.choice(range(clique_1 * n, (clique_1 + 1) * n))
        v = random.choice(range(clique_2 * n, (clique_2 + 1) * n))
        G.add_edge(u, v)

    return G


def intercluster_edges(G, clusters):
    total_edges = 0
    for i in range(len(clusters)):
        for j in range(i, len(clusters)):
            total_edges += nx.cut_size(G, clusters[i], clusters[j])
    return total_edges


def test_expander_decomposition_cliques_1():
    G = connected_cliques(10, 10, 20)
    m = len(G.edges())
    clusters = expander_decomposition(G, 0.1, "_s", "_t")

    assert len(clusters) == 10
    assert intercluster_edges(G, clusters) < 0.1 * m * math.log(m) ** 3


def test_expander_decomposition_cliques_2():
    G = connected_cliques(15, 20, 40)
    m = len(G.edges())
    clusters = expander_decomposition(G, 0.1, "_s", "_t", fast_randomization=True)

    assert len(clusters) == 20
    assert intercluster_edges(G, clusters) < 0.1 * m * math.log(m) ** 3


def test_expander_decomposition_random():
    G = nx.gnp_random_graph(400, 0.1)
    clusters = expander_decomposition(G, 0.01, "_s", "_t")

    assert len(clusters) == 1
