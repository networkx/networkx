import pytest

import networkx as nx
from networkx.algorithms.community import leiden_communities, leiden_partitions
from networkx.algorithms.community.quality import constant_potts_model, modularity


def test_modularity_increase():

    # by default leiden_communities uses constant_potts_model as the quality
    # function being optimised, not modularity.

    # The equivalent test test_cpm_increase is implemented below using constant_potts_model
    # and another test using modularity as the explicit quality function
    # test_modularity_increase_qf_parameter is also implemented below

    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = [{u} for u in G.nodes()]
    q_mod = nx.community.modularity(G, partition)
    partition = nx.community.leiden_communities(
        G, quality_function="modularity", resolution=0.2
    )

    assert nx.community.modularity(G, partition) > q_mod


def test_valid_partition():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = nx.community.leiden_communities(G, resolution=0.1, seed=10)

    assert nx.community.is_partition(G, partition)


def test_partition_iterator():
    G = nx.path_graph(15)
    parts_iter = nx.community.leiden_partitions(G, resolution=0.2, seed=42)
    first_part = next(parts_iter)
    first_copy = [s.copy() for s in first_part]

    # check 1st part stays fixed even after 2nd iteration (like gh-5901 in louvain)
    assert first_copy[0] == first_part[0]
    second_part = next(parts_iter)
    assert first_copy[0] == first_part[0]


def test_none_weight_param():
    G = nx.karate_club_graph()
    nx.set_edge_attributes(
        G, {edge: i * i for i, edge in enumerate(G.edges)}, name="foo"
    )

    partition1 = nx.community.leiden_communities(G, weight=None, seed=2)
    partition2 = nx.community.leiden_communities(G, weight="foo", seed=2)
    partition3 = nx.community.leiden_communities(G, weight="weight", seed=2)

    assert partition1 != partition2
    assert partition2 != partition3


def test_quality():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    H = nx.MultiGraph(G)

    partition = nx.community.leiden_communities(
        G, quality_function="modularity", resolution=0.05, seed=10
    )
    partition2 = nx.community.leiden_communities(
        H, quality_function="modularity", resolution=0.05, seed=10
    )

    quality = nx.community.partition_quality(G, partition)[0]
    quality2 = nx.community.partition_quality(H, partition2)[0]

    assert quality >= 0.45
    assert quality2 >= 0.45


def test_quality_cpm():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    H = nx.MultiGraph(G)
    singleton_partition = [{u} for u in G]

    r = 0.05
    partition = nx.community.leiden_communities(G, resolution=r, seed=10)
    partition2 = nx.community.leiden_communities(H, resolution=r, seed=10)

    quality = nx.community.partition_quality(G, partition)[0]
    quality2 = nx.community.partition_quality(H, partition2)[0]

    assert quality > 0.45
    assert quality2 > 0.45
    assert quality > nx.community.partition_quality(G, singleton_partition)[0]
    assert quality2 > nx.community.partition_quality(H, singleton_partition)[0]


def test_resolution():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )

    partition1 = nx.community.leiden_communities(G, resolution=0.05, seed=12)
    partition2 = nx.community.leiden_communities(G, resolution=0.10, seed=12)
    partition3 = nx.community.leiden_communities(G, resolution=0.5, seed=12)

    assert len(partition1) < len(partition2)
    assert len(partition2) < len(partition3)


def test_empty_graph():
    G = nx.Graph()
    G.add_nodes_from(range(5))
    expected = [{0}, {1}, {2}, {3}, {4}]
    assert nx.community.leiden_communities(G) == expected


def test_max_level():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    parts_iter = nx.community.leiden_partitions(G, resolution=0.1, seed=42)
    for max_level, expected in enumerate(parts_iter, 1):
        partition = nx.community.leiden_communities(
            G, max_level=max_level, resolution=0.1, seed=42
        )
        assert partition == expected

    assert max_level > 1  # Ensure we are actually testing max_level
    # max_level is an upper limit; it's okay if we stop before it's hit.
    partition = nx.community.leiden_communities(
        G, max_level=max_level + 1, resolution=0.1, seed=42
    )
    assert partition == expected
    with pytest.raises(
        ValueError, match="max_level argument must be a positive integer"
    ):
        nx.community.leiden_communities(G, max_level=0)


def test_connected_communities_LFR():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )

    partition = nx.community.leiden.leiden_communities(
        G, weight=None, resolution=0.3, theta=0.1, seed=10
    )

    for C in partition:
        assert _check_connected_community(G, C)


def test_quality_function_not_implemented():
    G = nx.karate_club_graph()

    with pytest.raises(nx.NetworkXError):
        leiden_communities(
            G, quality_function="bad_quality_function", resolution=0.2, seed=1
        )


def test_expected():
    G = nx.karate_club_graph()

    part = leiden_communities(G, resolution=0.2, seed=1)

    part_expected = [
        {0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21},
        {16, 4, 5, 6, 10},
        {9},
        {8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33},
    ]

    assert _equivalent_partitions(part, part_expected)

    G = nx.karate_club_graph()

    part = leiden_communities(G, weight=None, resolution=0.2, seed=1)

    part_expected = [
        {11},
        {12},
        {0, 1, 2, 3, 7, 8, 13},
        {17},
        {19},
        {30},
        {9},
        {16, 4, 5, 6, 10},
        {21},
        {24, 25, 28, 31},
        {26},
        {32, 33, 14, 15, 18, 20, 22, 23, 27, 29},
    ]

    assert _equivalent_partitions(part, part_expected)


def test_connected_communities():
    G = nx.karate_club_graph()
    n = 42
    r = 0.2
    part = leiden_communities(G, resolution=r, seed=n)
    for C in part:
        assert _check_connected_community(G, C)


def test_connected_communities_modularity():
    G = nx.karate_club_graph()
    n = 42
    r = 0.3
    part = leiden_communities(
        G, weight=None, quality_function="modularity", resolution=r, seed=n
    )
    for C in part:
        assert _check_connected_community(G, C)


def test_connected_communities_no_weights():
    G = nx.karate_club_graph()
    r = 0.3
    part = leiden_communities(G, weight=None, resolution=r, seed=111)
    for C in part:
        assert _check_connected_community(G, C)


def test_directed_graphs_modularity():
    G = nx.gn_graph(n=100, seed=11)
    assert nx.is_directed(G)
    comms = leiden_communities(
        G, quality_function="modularity", weight=None, resolution=0.2, seed=11
    )


def test_directed_graphs_cpm():
    G = nx.gn_graph(n=100, seed=11)
    assert nx.is_directed(G)
    comms = leiden_communities(G, weight=None, resolution=0.2, seed=11)


def test_bipartite_graphs_modularity():
    G = nx.bipartite.random_graph(10, 20, 0.2, seed=11)
    with pytest.raises(nx.NetworkXError):
        leiden_communities(
            G, quality_function="barber_modularity", resolution=0.2, seed=1
        )


def test_bipartite_graphs_modularity_directed():
    G = nx.bipartite.random_graph(10, 20, 0.2, directed=True, seed=11)
    with pytest.raises(nx.NetworkXError):
        leiden_communities(
            G, quality_function="barber_modularity", resolution=0.2, seed=1
        )


def test_modularity_increase_qf_parameter():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = [{u} for u in G.nodes()]
    q_mod = nx.community.modularity(G, partition)
    partition = leiden_communities(
        G, resolution=0.1, quality_function="modularity", seed=10
    )

    assert nx.community.modularity(G, partition) > q_mod


def test_cpm_increase():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = [{u} for u in G.nodes()]
    r = 0.3
    cpm = constant_potts_model(
        G, partition, weight=None, node_weight=None, resolution=r
    )
    partition = leiden_communities(G, resolution=r, seed=10)

    assert constant_potts_model(G, partition, weight=None, resolution=r) > cpm


def test_resolution_cpm():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )

    partition1 = leiden_communities(G, resolution=0.05, seed=12)
    partition2 = leiden_communities(G, resolution=0.2, seed=12)
    partition3 = leiden_communities(G, resolution=0.7, seed=12)

    assert len(partition1) < len(partition2)
    assert len(partition2) < len(partition3)


def test_resolution_modularity():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )

    partition1 = leiden_communities(
        G, quality_function="modularity", resolution=0.01, seed=10
    )
    partition2 = leiden_communities(
        G, quality_function="modularity", resolution=2.0, seed=10
    )
    partition3 = leiden_communities(
        G, quality_function="modularity", resolution=10.0, seed=10
    )

    assert len(partition1) < len(partition2)
    assert len(partition2) < len(partition3)


def _equivalent_partitions(P1, P2):
    P1 = {frozenset(C) for C in P1}
    P2 = {frozenset(C) for C in P2}
    return P1 == P2


def _check_connected_community(G, community):
    C = G.subgraph(community).copy()
    return nx.is_connected(C)
