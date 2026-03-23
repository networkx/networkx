import pytest

import networkx as nx

# TODO: look at comments, no redundancy


def test_communities_empty():
    G = nx.Graph()
    partition = nx.community.voronoi_communities(G)

    assert partition == []


def test_communities_single_node():
    G = nx.Graph()
    G.add_node(0)

    partition = nx.community.voronoi_communities(G)
    expected = [{0}]

    assert partition == expected


def test_communities_no_edges():
    G = nx.Graph()
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)

    partition = nx.community.voronoi_communities(G)
    expected = [{0}, {1}, {2}]

    assert partition == expected


def test_communities_raises_multigraph():
    G = nx.MultiGraph()

    with pytest.raises(nx.NetworkXNotImplemented):
        nx.community.voronoi_communities(G)


def test_communities_raises_negative_or_zero_weight():
    G = nx.Graph()
    G.add_edge(0, 1, weight=0.0)

    with pytest.raises(ValueError, match="All edge weights must be positive"):
        nx.community.voronoi_communities(G)

    G.add_edge(0, 1, weight=-2.5)

    with pytest.raises(ValueError, match="All edge weights must be positive"):
        nx.community.voronoi_communities(G)


def test_communities_modes():
    G = nx.karate_club_graph()

    p_flow = nx.community.voronoi_communities(G, mode="flow")
    assert isinstance(p_flow, list)
    assert nx.community.is_partition(G, p_flow)

    p_strength = nx.community.voronoi_communities(G, mode="strength")
    assert isinstance(p_strength, list)
    assert nx.community.is_partition(G, p_strength)

    with pytest.raises(ValueError, match="Invalid mode"):
        nx.community.voronoi_communities(G, mode="invalid_string")


def test_communities_karate_club():
    G = nx.karate_club_graph()
    part = [
        {0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21},
        {8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33},
    ]

    partition = nx.community.voronoi_communities(G)

    assert part == partition


@pytest.mark.parametrize(
    "G",
    [
        # Undirected LFR benchmark
        nx.LFR_benchmark_graph(
            250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
        ),
        # Directed growing network
        nx.gn_graph(200, seed=42),
        # Directed Erdos-Renyi graph
        nx.erdos_renyi_graph(100, 0.05, seed=42, directed=True),
    ],
)
def test_communities_generated_graphs(G):
    partition = nx.community.voronoi_communities(G)
    assert nx.community.is_partition(G, partition)


@pytest.mark.parametrize(
    "graph_class, is_weighted",
    [
        (nx.Graph, False),
        (nx.Graph, True),
        (nx.DiGraph, False),
        (nx.DiGraph, True),
    ],
)
def test_communities_graph_types(graph_class, is_weighted):
    G = graph_class()
    if is_weighted:
        G.add_weighted_edges_from(
            [
                (0, 1, 1.5),
                (1, 2, 0.8),
                (2, 3, 2.1),
                (3, 4, 1.1),
                (4, 0, 0.5),
                (0, 2, 3.0),
            ]
        )
    else:
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)])

    partition = nx.community.voronoi_communities(G)

    assert isinstance(partition, list)
    assert len(partition) > 0
    assert set().union(*partition) == set(G.nodes())
    assert sum(len(community) for community in partition) == len(G.nodes())


def test_communities_tie_breaking():
    G = nx.Graph()
    # A simple symmetric diamond with a cross-edge
    G.add_edges_from([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("A", "C")])

    partition = nx.community.voronoi_communities(G)

    assert nx.community.is_partition(G, partition)
    assert partition == [{"A", "B", "C", "D"}]


def test_communities_quality():
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )

    partition_G = nx.community.voronoi_communities(G)

    quality_G = nx.community.partition_quality(G, partition_G)[0]

    # TODO: mutual information test here

    modularity_G = nx.community.modularity(G, partition_G)

    assert quality_G >= 0.99

    assert modularity_G >= 0.45


# TODO: another test_quality lfr and i give out the weights,
# merge generateWeightedNetworks and assert mutual information, quality, modularity
# TODO: predefined number of communities test
# TODO: voronoi_partitions tests
def test_partitions_raises_invalid_direction():
    G = nx.Graph([(0, 1)])

    with pytest.raises(
        ValueError, match="direction must be 'in', 'out', or 'undirected'"
    ):
        nx.community.voronoi_partitions(G, generator_points=[0], direction="invalid")


def test_partitions_raises_invalid_generators():
    G = nx.Graph([(0, 1), (1, 2)])

    # Node 3 is not in the graph
    with pytest.raises(
        ValueError, match="Invalid vertex ID given as Voronoi generator."
    ):
        nx.community.voronoi_partitions(G, generator_points=[0, 3])
