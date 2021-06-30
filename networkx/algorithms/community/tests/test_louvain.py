import pytest

import networkx as nx
from networkx.algorithms.community import (
    louvain_communities,
    modularity,
    is_partition,
    partition_quality,
)


def test_modularity_increase():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = [{u} for u in G.nodes()]
    mod = modularity(G, partition)
    partition = louvain_communities(G)

    assert modularity(G, partition) > mod


def test_valid_partition():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = louvain_communities(G)

    assert is_partition(G, partition)


def test_partition():
    G = nx.karate_club_graph()
    part = [
        {0, 1, 2, 3, 7, 9, 11, 12, 13, 17, 19, 21},
        {16, 4, 5, 6, 10},
        {23, 25, 27, 28, 24, 31},
        {32, 33, 8, 14, 15, 18, 20, 22, 26, 29, 30},
    ]
    partition = louvain_communities(G, seed=2)

    assert part == partition


def test_quality():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = louvain_communities(G)

    quality = partition_quality(G, partition)[0]

    assert quality >= 0.7
