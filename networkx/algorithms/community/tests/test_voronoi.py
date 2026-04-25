import pytest

import networkx as nx


def test_communities_no_nodes():
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


@pytest.mark.parametrize("invalid_weight", [0.0, -2.5])
def test_communities_raises_invalid_weight(invalid_weight):
    G = nx.Graph()
    G.add_edge(0, 1, weight=invalid_weight)
    with pytest.raises(nx.NetworkXError, match="All edge weights must be positive"):
        nx.community.voronoi_communities(G)


@pytest.mark.parametrize("invalid_n_steps", [0, -1])
def test_communities_raises_invalid_n_steps(invalid_n_steps):
    G = nx.Graph()
    G.add_edge(0, 1)
    with pytest.raises(ValueError, match="n_steps must be a positive integer"):
        nx.community.voronoi_communities(G, n_steps=invalid_n_steps)


def test_communities_weight_transform():
    G = nx.karate_club_graph()

    p_flow = nx.community.voronoi_communities(G, weight_transform="flow")
    assert isinstance(p_flow, list)
    assert nx.community.is_partition(G, p_flow)

    p_strength = nx.community.voronoi_communities(G, weight_transform="strength")
    assert isinstance(p_strength, list)
    assert nx.community.is_partition(G, p_strength)

    def my_custom_transform(G, node, strengths, densities, eps):
        # A simple custom logic: just double the density
        return float(densities[node]) * 2.0

    p_custom = nx.community.voronoi_communities(G, weight_transform=my_custom_transform)
    assert isinstance(p_custom, list)
    assert nx.community.is_partition(G, p_custom)

    with pytest.raises(ValueError, match="Expected 'strength', 'flow', or a callable"):
        nx.community.voronoi_communities(G, weight_transform="invalid_string")

    with pytest.raises(
        TypeError, match="weight_transform must be a string or a callable"
    ):
        nx.community.voronoi_communities(G, weight_transform=12345)


def test_communities_karate_club():
    G = nx.karate_club_graph()
    part = [
        {0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21},
        {8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33},
    ]

    partition = nx.community.voronoi_communities(G)

    expected = {frozenset(c) for c in part}
    result = {frozenset(c) for c in partition}

    assert result == expected


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

    modularity_G = nx.community.modularity(G, partition_G)

    assert quality_G >= 0.99

    assert modularity_G >= 0.45


@pytest.mark.parametrize(
    "edges, expected_min_len",
    [
        # Single edge. Forces max_r <= min_r
        ([(0, 1, {"weight": 1.0})], 1),
        # Only self-loops. Forces min_r == float("inf")
        ([(0, 0, {"weight": 1.0}), (1, 1, {"weight": 1.0})], 1),
    ],
)
def test_communities_radius_edge_cases(edges, expected_min_len):
    G = nx.Graph()
    G.add_edges_from(edges)

    partition = nx.community.voronoi_communities(G)

    assert isinstance(partition, list)
    assert len(partition) >= expected_min_len


def test_partitions_raises_invalid_direction():
    G = nx.Graph([(0, 1)])

    with pytest.raises(ValueError, match="direction must be 'in' or 'out'"):
        nx.community.voronoi_partitions(G, generator_points=[0], direction="invalid")


def test_partitions_raises_invalid_generators():
    G = nx.Graph([(0, 1), (1, 2)])

    # Node 3 is not in the graph
    with pytest.raises(
        nx.NodeNotFound, match="Invalid node ID given as Voronoi generator"
    ):
        nx.community.voronoi_partitions(G, generator_points=[0, 3])


def test_partitions_undirected_fallback():
    # Exercises the fallback to nx.voronoi_cells when all_pairs_distances is None.
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3)])

    partition = nx.community.voronoi_partitions(G, generator_points=[0, 3])

    sorted_partition = sorted([sorted(p) for p in partition])
    assert sorted_partition == [[0, 1], [2, 3]]


def test_partitions_directed_in():
    G = nx.DiGraph()
    # 0 -> 1 -> 2
    G.add_edges_from([(0, 1), (1, 2)])

    partition = nx.community.voronoi_partitions(
        G, generator_points=[0, 2], direction="in"
    )

    sorted_partition = sorted([sorted(p) for p in partition])
    assert sorted_partition == [[0], [1, 2]]


def test_partitions_precomputed_distances():
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3])

    all_pairs_distances = {
        0: {0: 0.0, 1: 1.0, 2: 5.0, 3: 10.0},
        3: {0: 10.0, 1: 5.0, 2: 1.0, 3: 0.0},
    }

    partition = nx.community.voronoi_partitions(
        G,
        generator_points=[0, 3],
        all_pairs_distances=all_pairs_distances,
        direction="out",
    )

    sorted_partition = sorted([sorted(p) for p in partition])
    assert sorted_partition == [[0, 1], [2, 3]]


def test_partitions_unreachable_nodes():
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2])

    # Node 2 is disconnected/unreachable
    all_pairs_distances = {0: {0: 0.0, 1: 1.0}}

    partition = nx.community.voronoi_partitions(
        G,
        generator_points=[0],
        all_pairs_distances=all_pairs_distances,
        direction="out",
    )

    # The unreachable logic should group node 2 into its own set
    sorted_partition = sorted([sorted(p) for p in partition])
    assert sorted_partition == [[0, 1], [2]]


def test_partitions_directed_in_precomputed():
    # Covers direction="in" branch of _voronoi_cells_from_distances,
    # including a node that cannot reach any generator (unreachable).
    G = nx.DiGraph()
    G.add_nodes_from([0, 1, 2, 3])
    all_pairs_distances = {
        0: {0: 0.0},
        1: {0: 1.0},
        2: {0: 5.0},
        # node 3 absent - unreachable
    }
    partition = nx.community.voronoi_partitions(
        G, generator_points=[0], all_pairs_distances=all_pairs_distances, direction="in"
    )
    assert {0, 1, 2} in partition
    assert {3} in partition
