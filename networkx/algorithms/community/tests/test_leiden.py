import pytest

import networkx as nx
from networkx.algorithms.community import leiden_communities, leiden_partitions
from networkx.algorithms.community.quality import modularity, constant_potts_model
# Leiden is not yet implemented by networkx, so only run tests in this file for
# backends that implement Leiden.
# no_backends_for_leiden_communities = (
#     "not set(nx.config.backend_priority.algos) & leiden_communities.backends"
# )

# no_backends_for_leiden_partitions = (
#     "not set(nx.config.backend_priority.algos) & leiden_partitions.backends"
# )

# def test_leiden_with_nx_backend():
#     G = nx.karate_club_graph()
#     with pytest.raises(NotImplementedError):
#         nx.community.leiden_partitions(G, backend="networkx")
#     with pytest.raises(NotImplementedError):
#         nx.community.leiden_communities(G, backend="networkx")








def check_connected_community(G, community):
    C = G.subgraph(community).copy()
    return nx.is_connected(C)



def test_connected_communities_LFR():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    
    partition = nx.community.leiden.leiden_communities(
        G,
        weight=None,
        resolution=0.3,
        theta=0.1,
        seed=10
    )

    for C in partition:
        assert check_connected_community(G, C)


def test_connected_communities():

    for i in range(10):
        G = nx.karate_club_graph()
        n = i*4 + 59
        r = 0.5 - 0.005*i
        part = leiden_communities(G, resolution=r, seed=n)
        for C in part:
            assert check_connected_community(G, C)

def test_connected_communities():

    for i in range(10):
        G = nx.karate_club_graph()
        n = i*4 + 59
        r = 0.5 - 0.005*i
        part = leiden_communities(G,weight=None,quality_function=modularity, resolution=r, seed=n)
        for C in part:
            assert check_connected_community(G, C)






def test_connected_communities():

    for i in range(10):
        G = nx.karate_club_graph()
        n = i*4 + 59
        r = 0.5 - 0.005*i
        part = leiden_communities(G,weight=None, resolution=r, seed=n)
        for C in part:
            assert check_connected_community(G, C)


def test_modularity_increase():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = [{u} for u in G.nodes()]
    mod = nx.community.modularity(G, partition)
    partition = nx.community.leiden_communities(G, resolution=0.1, quality_function=modularity, seed=10)

    assert nx.community.modularity(G, partition) > mod

def test_cpm_increase():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = [{u} for u in G.nodes()]
    r = 0.3
    mod = constant_potts_model(G, partition, resolution=r)
    partition = nx.community.leiden_communities(G, quality_function=constant_potts_model, resolution=r, seed=10)

    assert constant_potts_model(G, partition, resolution=r) > mod


def test_valid_partition():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    partition = nx.community.leiden_communities(G)

    assert nx.community.is_partition(G, partition)



#def test_partition_iterator():
#    G = nx.karate_club_graph()
#    parts_iter = nx.community.leiden_partitions(G, seed=42, resolution=0.5)
#    first_part = next(parts_iter)
#    first_copy = [s.copy() for s in first_part]
#
#    # check 1st part stays fixed even after 2nd iteration (like gh-5901 in louvain)
#    assert first_copy[0] == first_part[0]
#    second_part = next(parts_iter)
#    assert first_copy[0] == first_part[0]


def test_none_weight_param():
    G = nx.karate_club_graph()
    nx.set_edge_attributes(
        G, {edge: i*i for i, edge in enumerate(G.edges)}, name="foo"
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
    singleton_partition = [{u} for u in G.nodes()]

    r = 0.7
    partition = nx.community.leiden_communities(G, resolution=r, seed=10)
    partition2 = nx.community.leiden_communities(H, resolution=r, seed=10)

    quality = nx.community.partition_quality(G, partition)[0]
    quality2 = nx.community.partition_quality(H, partition2)[0]

    assert quality >= nx.community.partition_quality(G, singleton_partition)[0]
    assert quality2 >= nx.community.partition_quality(H, singleton_partition)[0]


def test_resolution_cpm():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )

    partition1 = nx.community.leiden_communities(G, resolution=0.5, seed=12)
    partition2 = nx.community.leiden_communities(G, seed=12)
    partition3 = nx.community.leiden_communities(G, resolution=2, seed=12)

    assert len(partition1) <= len(partition2)
    assert len(partition2) <= len(partition3)


def test_resolution_modularity():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )


    partition1 = nx.community.leiden_communities(G, quality_function=modularity, resolution=0.5, seed=12)
    partition2 = nx.community.leiden_communities(G, quality_function=modularity, seed=12)
    partition3 = nx.community.leiden_communities(G, quality_function=modularity, resolution=2, seed=12)

    assert len(partition1) <= len(partition2)
    assert len(partition2) <= len(partition3)

def test_empty_graph():
    G = nx.Graph()
    G.add_nodes_from(range(5))
    expected = [{0}, {1}, {2}, {3}, {4}]
    assert nx.community.leiden_communities(G) == expected


# def test_directed_not_implemented():
#     G = nx.cycle_graph(4, create_using=nx.DiGraph)
#     with pytest.raises(nx.NetworkXNotImplemented):
#         nx.community.leiden_communities(G)



def test_max_level():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    r = 1
    parts_iter = nx.community.leiden_partitions(G, resolution=r, seed=42)
    for max_level, expected in enumerate(parts_iter, 1):
        partition = nx.community.leiden_communities(G, resolution=r, max_level=max_level, seed=42)
        assert partition == expected
    assert max_level > 1  # Ensure we are actually testing max_level
    # max_level is an upper limit; it's okay if we stop before it's hit.
    partition = nx.community.leiden_communities(G, resolution=r, max_level=max_level + 1, seed=42)
    assert partition == expected
    with pytest.raises(
        ValueError, match="max_level argument must be a positive integer"
    ):
        nx.community.leiden_communities(G, resolution=r, max_level=0)
