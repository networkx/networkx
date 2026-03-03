# TODO: delete this random import
import random

import pytest

import networkx as nx
from networkx.algorithms.community import voronoi_communities

# undirected weighted
# undirected unweighted
# directed weighted
# directed unweighted


def test_karate_club_partition():
    G = nx.karate_club_graph()
    part = [
        {0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21},
        {8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33},
    ]

    partition = nx.community.voronoi_communities(G)

    assert part == partition


def test_empty_graph():
    G = nx.Graph()
    partition = nx.community.voronoi_communities(G)

    assert partition == []


def test_one_node_graph():
    G = nx.Graph()
    G.add_node(0)

    partition = nx.community.voronoi_communities(G)
    expected = [{0}]

    assert partition == expected


def test_nodes_without_edges():
    G = nx.Graph()
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)

    partition = nx.community.voronoi_communities(G)
    expected = [{0}, {1}, {2}]

    assert partition == expected


def test_raises_multigraph():
    G = nx.MultiGraph()

    with pytest.raises(nx.NetworkXNotImplemented):
        nx.community.voronoi_communities(G)


# TODO: didnt test yet
def test_modes():
    G = nx.karate_club_graph()
    # Test "flow" mode logic
    p_flow = voronoi_communities(G, mode="flow")

    assert isinstance(p_flow, list)

    # Test invalid mode
    with pytest.raises(ValueError, match="Invalid mode"):
        voronoi_communities(G, mode="invalid_string")


def test_unweighted_graph():
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)])

    partition = voronoi_communities(G)

    assert isinstance(partition, list)
    assert len(partition) > 0

    assert set().union(*partition) == set(G.nodes())
    assert sum(len(community) for community in partition) == len(G.nodes())


def test_voronoi_weighted_graph():
    G = nx.Graph()
    edges_with_weights = [
        (0, 1, 1.5),
        (1, 2, 0.8),
        (2, 3, 2.1),
        (3, 4, 1.1),
        (4, 0, 0.5),
        (0, 2, 3.0),
    ]
    G.add_weighted_edges_from(edges_with_weights)

    partition = voronoi_communities(G)

    assert set().union(*partition) == set(G.nodes())
    assert sum(len(community) for community in partition) == len(G.nodes())


def test_voronoi_unweighted_digraph():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)])

    partition = voronoi_communities(G)

    assert set().union(*partition) == set(G.nodes())
    assert sum(len(community) for community in partition) == len(G.nodes())


def test_voronoi_weighted_digraph():
    G = nx.DiGraph()
    edges_with_weights = [
        (0, 1, 1.5),
        (1, 2, 0.8),
        (2, 3, 2.1),
        (3, 4, 1.1),
        (4, 0, 0.5),
        (0, 2, 3.0),
    ]
    G.add_weighted_edges_from(edges_with_weights)

    partition = voronoi_communities(G)

    assert set().union(*partition) == set(G.nodes())
    assert sum(len(community) for community in partition) == len(G.nodes())


def test_quality():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    H = nx.gn_graph(200, seed=1234)

    partition_G = nx.community.voronoi_communities(G)

    quality_G = nx.community.partition_quality(G, partition_G)[0]
    print(quality_G)

    modularity_G = nx.community.modularity(G, partition_G)
    print(modularity_G)

    assert quality_G >= 0.99

    assert modularity_G >= 0.45


def test_quality2():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    # H is no longer used for assertions, but leaving it here if you still want it generated
    H = nx.gn_graph(200, seed=1234)

    # --- SAVE LFR GRAPH FOR C CODE ---
    # Convert to directed
    D = G.to_directed()

    # Assign deterministic random weights
    random.seed(42)
    for u, v in D.edges():
        D[u][v]["weight"] = random.uniform(1.0, 100.0)

    # Normalize weights by the maximum weight
    max_weight = max(d["weight"] for u, v, d in D.edges(data=True))
    for u, v, d in D.edges(data=True):
        D[u][v]["weight"] /= max_weight

    # Save to file (nodes are +1 to make them 1-indexed for C)
    with open("lfr_directed_weighted_for_c.txt", "w") as f:
        for u, v, d in D.edges(data=True):
            f.write(f"{u + 1}\t{v + 1}\t{d['weight']:.8f}\n")
    # ---------------------------------

    # Run the Voronoi algorithm on the Python side
    partition_G = nx.community.voronoi_communities(G)

    # Measure and print quality metrics
    quality_G = nx.community.partition_quality(G, partition_G)[0]
    print(f"Coverage G: {quality_G}")

    modularity_G = nx.community.modularity(G, partition_G)
    print(f"Modularity G: {modularity_G}")

    # Assertions
    assert quality_G >= 0.99
    assert modularity_G >= 0.45
