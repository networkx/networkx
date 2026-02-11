"""Shared graph-builder fixtures for backbone tests."""

import pytest
import networkx as nx


@pytest.fixture
def two_cluster_undirected():
    """Two 4-cliques joined by a single weak bridge.

    Cluster A (nodes 0-3): internal weights = 10
    Cluster B (nodes 4-7): internal weights = 100
    Bridge: (3, 4) weight = 1
    """
    G = nx.Graph()
    for i in range(4):
        for j in range(i + 1, 4):
            G.add_edge(i, j, weight=10)
    for i in range(4, 8):
        for j in range(i + 1, 8):
            G.add_edge(i, j, weight=100)
    G.add_edge(3, 4, weight=1)
    return G


@pytest.fixture
def two_cluster_directed():
    """Directed version of the two-cluster graph.

    Same structure but with directed edges (both directions for
    intra-cluster, single direction for bridge: 3 -> 4).
    """
    G = nx.DiGraph()
    for i in range(4):
        for j in range(4):
            if i != j:
                G.add_edge(i, j, weight=10)
    for i in range(4, 8):
        for j in range(4, 8):
            if i != j:
                G.add_edge(i, j, weight=100)
    G.add_edge(3, 4, weight=1)
    return G


@pytest.fixture
def star_undirected():
    """Star graph with node 0 as hub (6 nodes)."""
    n, hub_weight, spoke_weight = 6, 100, 5
    G = nx.Graph()
    for i in range(1, n):
        G.add_edge(0, i, weight=hub_weight)
    for i in range(1, n):
        j = (i % (n - 1)) + 1
        if i != j:
            G.add_edge(i, j, weight=spoke_weight)
    return G


@pytest.fixture
def star_directed():
    """Directed star: hub 0 -> spokes (6 nodes), plus directed rim."""
    n, hub_weight, spoke_weight = 6, 100, 5
    G = nx.DiGraph()
    for i in range(1, n):
        G.add_edge(0, i, weight=hub_weight)
    for i in range(1, n):
        j = (i % (n - 1)) + 1
        if i != j:
            G.add_edge(i, j, weight=spoke_weight)
    return G


@pytest.fixture
def path_weighted():
    """Weighted path graph: 0 --10-- 1 --20-- 2 --30-- 3 --40-- 4."""
    G = nx.Graph()
    for i in range(4):
        G.add_edge(i, i + 1, weight=(i + 1) * 10)
    return G


@pytest.fixture
def complete_uniform():
    """Complete undirected graph (K5) with uniform weight 10."""
    G = nx.complete_graph(5)
    for u, v in G.edges():
        G[u][v]["weight"] = 10
    return G


@pytest.fixture
def triangle_unequal():
    """Triangle: edges with weights 1, 2, 3."""
    G = nx.Graph()
    G.add_edge("A", "B", weight=1)
    G.add_edge("B", "C", weight=2)
    G.add_edge("A", "C", weight=3)
    return G


@pytest.fixture
def disconnected_graph():
    """Two disconnected components: (0-1, w=10) and (2-3, w=20)."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=10)
    G.add_edge(2, 3, weight=20)
    return G


@pytest.fixture
def single_edge_graph():
    """Graph with one edge."""
    G = nx.Graph()
    G.add_edge("x", "y", weight=42)
    return G


@pytest.fixture
def single_node_graph():
    """Graph with one node, no edges."""
    G = nx.Graph()
    G.add_node("alone")
    return G
