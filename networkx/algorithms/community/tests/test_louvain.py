import pytest

import networkx as nx
from networkx.algorithms.community import louvain_communities, modularity


def test_modularity_increase():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = [{u} for u in G.nodes()]
    mod = modularity(G, partition)
    partitions = louvain_communities(G)

    assert modularity(G, partitions[-1]) > mod
