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
    H = G.to_directed()
    partition = louvain_communities(G)
    partition2 = louvain_communities(H)

    assert is_partition(G, partition)
    assert is_partition(H, partition2)


def test_partition():
    G = nx.karate_club_graph()
    part = [
        {0, 1, 2, 3, 7, 9, 11, 12, 13, 17, 19, 21},
        {16, 4, 5, 6, 10},
        {23, 25, 27, 28, 24, 31},
        {32, 33, 8, 14, 15, 18, 20, 22, 26, 29, 30},
    ]
    partition = louvain_communities(G, seed=2, weight=None)

    assert part == partition


def test_none_weight_param():
    G = nx.karate_club_graph()
    nx.set_edge_attributes(
        G, {edge: i * i for i, edge in enumerate(G.edges)}, name="foo"
    )

    part = [
        {0, 1, 2, 3, 7, 9, 11, 12, 13, 17, 19, 21},
        {16, 4, 5, 6, 10},
        {23, 25, 27, 28, 24, 31},
        {32, 33, 8, 14, 15, 18, 20, 22, 26, 29, 30},
    ]
    partition1 = louvain_communities(G, weight=None, seed=2)
    partition2 = louvain_communities(G, weight="foo", seed=2)
    partition3 = louvain_communities(G, weight="weight", seed=2)

    assert part == partition1
    assert part != partition2
    assert part != partition3
    assert partition2 != partition3


def test_quality():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    H = nx.gn_graph(200, seed=1234)
    I = nx.MultiGraph(G)
    J = nx.MultiDiGraph(H)

    partition = louvain_communities(G)
    partition2 = louvain_communities(H)
    partition3 = louvain_communities(I)
    partition4 = louvain_communities(J)

    quality = partition_quality(G, partition)[0]
    quality2 = partition_quality(H, partition2)[0]
    quality3 = partition_quality(I, partition3)[0]
    quality4 = partition_quality(J, partition4)[0]

    assert quality >= 0.65
    assert quality2 >= 0.85
    assert quality3 >= 0.65
    assert quality4 >= 0.85


def test_multigraph():
    G = nx.karate_club_graph()
    H = nx.MultiGraph(G)
    G.add_edge(0, 1, weight=10)
    H.add_edge(0, 1, weight=9)
    G.add_edge(0, 9, foo=20)
    H.add_edge(0, 9, foo=20)

    partition1 = louvain_communities(G, seed=1234)
    partition2 = louvain_communities(H, seed=1234)
    partition3 = louvain_communities(H, weight="foo", seed=1234)

    assert partition1 == partition2 != partition3


def test_resolution():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )

    partition1 = louvain_communities(G, resolution=0.5, seed=12)
    partition2 = louvain_communities(G, seed=12)
    partition3 = louvain_communities(G, resolution=2, seed=12)

    assert len(partition1) <= len(partition2) <= len(partition3)


def test_threshold():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition1 = louvain_communities(G, threshold=0.2, seed=2)
    partition2 = louvain_communities(G, seed=2)
    mod1 = modularity(G, partition1)
    mod2 = modularity(G, partition2)

    assert mod1 < mod2
