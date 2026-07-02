import pytest

import networkx as nx

comm = nx.community


@pytest.fixture(params=[nx.Graph, nx.MultiGraph])
def G(request):
    LFR_graph = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    G = request.param(LFR_graph)
    # duplicate edges if multigraph
    G.add_edges_from(e for i, e in enumerate(LFR_graph.edges()) if i < 50)
    return G


@pytest.fixture(params=[nx.Graph, nx.MultiGraph])
def small_G(request):
    LFR_graph = nx.LFR_benchmark_graph(
        50, 3, 1.5, 0.1, min_community=5, average_degree=2, seed=10
    )
    G = request.param(LFR_graph)
    # duplicate edges if multigraph
    G.add_edges_from(e for i, e in enumerate(LFR_graph.edges()) if i < 50)
    return G


@pytest.fixture
def singletons(G):
    return [{node} for node in G]


def _metrics():
    yield from ["cpm", "modularity"]


def _quality():
    def cpm(G, P):
        return comm.constant_potts_model(G, P, resolution=0.2)

    def qmod(G, P):
        return comm.modularity(G, P, resolution=0.2)

    for gamma in [0.2, 0.5, 0.9]:
        yield from [("cpm", cpm, gamma), ("modularity", qmod, gamma)]


def test_valid_partition(G):
    partition = comm.leiden_communities(G, resolution=0.1, seed=10)
    assert comm.is_partition(G, partition)


def test_partitions_yields_copy():
    G = nx.path_graph(15)
    parts_iter = comm.leiden_partitions(G, resolution=0.2, seed=42)
    first_part = next(parts_iter)
    first_copy = [s.copy() for s in first_part]

    # check 1st part stays fixed even after 2nd iteration (like gh-5901 in louvain)
    assert first_copy[0] == first_part[0]
    second_part = next(parts_iter)
    assert first_copy[0] == first_part[0]


def test_empty_graph():
    G = nx.Graph()
    G.add_nodes_from(range(5))
    expected = [{0}, {1}, {2}, {3}, {4}]
    assert comm.leiden_communities(G) == expected


@pytest.mark.parametrize("metric, Q_func, gamma", _quality())
def test_overall_increase(metric, Q_func, gamma):
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    singletons = [{n} for n in G]

    Q = Q_func(G, singletons)
    new_P = comm.leiden_communities(G, metric=metric, resolution=gamma, seed=42)
    new_Q = Q_func(G, new_P)
    assert new_Q > Q


@pytest.mark.parametrize("metric", _metrics())
def test_coverage_up_with_leiden_metrics(G, singletons, metric):
    # check that `partition_quality` coverage increases for all metrics
    # even though they are not optimizing coverage. Also that coverage > 45%
    partition = comm.leiden_communities(G, metric=metric, resolution=0.01, seed=10)
    coverage = comm.partition_quality(G, partition)[0]  # 0th return is coverage
    assert coverage >= 0.45
    assert coverage > comm.partition_quality(G, singletons)[0]


def test_weight_kwarg():
    G = nx.karate_club_graph()
    nx.set_edge_attributes(
        G, {edge: i * i for i, edge in enumerate(G.edges)}, name="foo"
    )

    partition1 = comm.leiden_communities(G, weight=None, seed=2)
    partition2 = comm.leiden_communities(G, weight="foo", seed=2)
    partition3 = comm.leiden_communities(G, weight="weight", seed=2)

    assert partition1 != partition2
    assert partition2 != partition3
    assert partition1 != partition3


def test_resolution_kwarg_cpm(G):
    P1 = comm.leiden_communities(G, resolution=0.05, seed=12)
    P2 = comm.leiden_communities(G, resolution=0.10, seed=12)
    P3 = comm.leiden_communities(G, resolution=0.5, seed=12)
    P4 = comm.leiden_communities(G, resolution=0.7, seed=12)
    P5 = comm.leiden_communities(G, resolution=1.5, seed=12)
    assert len(P1) < len(P2) < len(P3) < len(P4) < len(P5)


def test_resolution_kwarg_mod(G):
    qmod = "modularity"
    # Only three sizes of partitions: 2, 21, 77. Changes at r=0 and r=6.83
    if G.is_multigraph():
        P1 = comm.leiden_communities(G, metric=qmod, resolution=1, seed=12)
        P2 = comm.leiden_communities(G, metric=qmod, resolution=2, seed=12)
        P10 = comm.leiden_communities(G, metric=qmod, resolution=10, seed=12)
        assert len(P1) < len(P2) < len(P10)
    else:
        P1 = comm.leiden_communities(G, metric=qmod, resolution=0.0, seed=12)
        P2 = comm.leiden_communities(G, metric=qmod, resolution=1.0, seed=12)
        P3 = comm.leiden_communities(G, metric=qmod, resolution=7.0, seed=12)
        assert len(P1) < len(P2) < len(P3), f"{len(P1)=} {len(P2)=} {len(P3)=}"


def test_LFR_communities_across_algos():
    # same graph as for fixture G, but not multigraph (it'd need other seeds)
    G = nx.LFR_benchmark_graph(
        250, 3, 1.5, 0.009, average_degree=5, min_community=20, seed=10
    )
    # Results are random, but Louvain is consistent across seed.
    # Resolution differs to get 3 communities.
    # The LFR example constructs G to have 3 communities.
    # So comparison is really about the nodes in the 3 communities being the same
    # That works for all with correct choices of seed
    C = nx.get_node_attributes(G, "community").values()
    LFR_comm = {frozenset(c) for c in C}  # remove duplicate entries

    C = comm.louvain_communities(G, resolution=0.5, seed=10)
    louvain_comm = {frozenset(c) for c in C}

    C = comm.leiden_communities(G, metric="cpm", resolution=0.001, seed=45)
    cpm_comm = {frozenset(c) for c in C}

    C = comm.leiden_communities(G, metric="modularity", resolution=0.3, seed=24)
    mod_comm = {frozenset(c) for c in C}

    assert louvain_comm == cpm_comm == LFR_comm == mod_comm


def test_barbell_communities_across_algos():
    G = nx.barbell_graph(5, 3)
    seed = 42

    # seed doesn't seem to matter for this example. Resolution does.
    louvain_comm = comm.louvain_communities(G, resolution=1)
    mod_comm = comm.leiden_communities(G, metric="modularity", resolution=1, seed=seed)
    cpm_comm = comm.leiden_communities(G, metric="cpm", resolution=0.3, seed=seed)

    assert {frozenset(C) for C in louvain_comm} == {frozenset(C) for C in mod_comm}
    assert {frozenset(C) for C in louvain_comm} == {frozenset(C) for C in cpm_comm}


@pytest.mark.parametrize("metric", _metrics())
def test_max_level_kwarg(small_G, metric):
    P_iter = comm.leiden_partitions(small_G, resolution=0.1, seed=42, metric=metric)
    for max_level, expected in enumerate(P_iter, start=1):
        P = comm.leiden_communities(
            small_G, max_level=max_level, resolution=0.1, seed=42, metric=metric
        )
        assert P == expected
    assert max_level > 1  # Ensure we are actually testing max_level

    # max_level is an upper limit; it's okay if we stop before it's hit.
    P = comm.leiden_communities(
        small_G, max_level=max_level + 1, resolution=0.1, seed=42, metric=metric
    )
    assert P == expected

    with pytest.raises(ValueError, match="max_level argument must be.* positive"):
        comm.leiden_communities(small_G, max_level=0)


def test_communities_connected(G):
    partition = comm.leiden.leiden_communities(
        G, weight=None, resolution=0.3, theta=0.1, seed=10
    )
    for C in partition:
        assert nx.is_connected(G.subgraph(C).copy())


def test_mispelled_metric():
    G = nx.karate_club_graph()
    with pytest.raises(nx.NetworkXError):
        comm.leiden_communities(G, metric="bad_metric")


def test_expected_stable_across_code_changes_cpm():
    G = nx.karate_club_graph()
    P = comm.leiden_communities(G, resolution=0.2, seed=3)
    P_expected = [
        {0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21},
        {16, 4, 5, 6, 10},
        {9},
        {8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33},
    ]
    assert {frozenset(C) for C in P} == {frozenset(C) for C in P_expected}

    G = nx.karate_club_graph()
    P = comm.leiden_communities(G, weight=None, resolution=0.2, seed=170)
    P_expected = [
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
    assert {frozenset(C) for C in P} == {frozenset(C) for C in P_expected}


def test_expected_stable_across_code_changes_qmod():
    qmod = "modularity"
    G = nx.karate_club_graph()
    P = comm.leiden_communities(G, resolution=0.2, seed=22, metric=qmod)
    P_expected = [
        {0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21},
        {16, 4, 5, 6, 10},
        {32, 33, 8, 9, 14, 15, 18, 20, 22, 23, 26, 27, 29, 30},
        {24, 25, 28, 31},
    ]
    assert {frozenset(C) for C in P} == {frozenset(C) for C in P_expected}

    G = nx.karate_club_graph()
    P = comm.leiden_communities(G, weight=None, resolution=0.4, seed=100, metric=qmod)
    P_expected = [
        {0, 1, 2, 3, 7, 9, 11, 12, 13, 17, 19, 21},
        {16, 4, 5, 6, 10},
        {8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33},
    ]
    assert {frozenset(C) for C in P} == {frozenset(C) for C in P_expected}


def test_connected_communities():
    G = nx.karate_club_graph()
    n = 42
    r = 0.2
    part = comm.leiden_communities(G, resolution=r, seed=n)
    for C in part:
        assert nx.is_connected(G.subgraph(C).copy())

    part = comm.leiden_communities(G, resolution=r, seed=n, metric="modularity")
    for C in part:
        assert nx.is_connected(G.subgraph(C).copy())


def test_connected_communities_no_weights():
    G = nx.karate_club_graph()
    r = 0.3
    part = comm.leiden_communities(G, weight=None, resolution=r, seed=111)
    for C in part:
        assert nx.is_connected(G.subgraph(C).copy())


@pytest.mark.parametrize("metric", _metrics())
def test_directed_graphs_modularity(metric):
    G = nx.gn_graph(n=100, seed=11)
    G.add_edges_from([(1, 2), (2, 1)])  # ensure one node-pair has both directions
    assert nx.is_directed(G)
    comm.leiden_communities(G, metric=metric, weight=None, resolution=0.2, seed=11)


def test_bipartite_graphs_modularity():
    G = nx.bipartite.random_graph(10, 20, 0.2, seed=11)
    with pytest.raises(nx.NetworkXError):
        comm.leiden_communities(G, metric="barber_modularity", resolution=0.2, seed=1)


def test_bipartite_graphs_modularity_directed():
    G = nx.bipartite.random_graph(10, 20, 0.2, directed=True, seed=11)
    with pytest.raises(nx.NetworkXError):
        comm.leiden_communities(G, metric="barber_modularity", resolution=0.2, seed=1)


def test_comms_change_after_aggregation():
    LP = comm.leiden_partitions
    PG = nx.path_graph(15)
    DPG = nx.DiGraph(PG.edges)

    result = list(LP(PG, resolution=0.2, seed=1))
    assert len(result[0]) != len(result[1])
    result = list(LP(DPG, resolution=0.2, seed=1))
    assert len(result[0]) != len(result[1])

    result = list(LP(PG, metric="modularity", resolution=0.2, seed=1))
    assert len(result[0]) != len(result[1])
    result = list(LP(DPG, metric="modularity", resolution=0.02, seed=1))
    assert len(result[0]) != len(result[1])


@pytest.mark.parametrize("m", _metrics())
def test_weights_matter(m):
    G = nx.path_graph(15)
    no_weights = list(comm.leiden_partitions(G, metric=m, resolution=2, seed=42637))

    G.add_weighted_edges_from((u, v, (u + 1) * v) for u, v in G.edges())

    with_weights = list(comm.leiden_partitions(G, metric=m, resolution=2, seed=40))
    fewer_comms = len(no_weights[0]) > len(with_weights[0])
    big_comms_bigger = len(no_weights[0][3]) < len(with_weights[0][3])
    assert fewer_comms or big_comms_bigger
    no_w, with_w = no_weights[-1], with_weights[-1]
    assert (len(no_w) > len(with_w)) or (len(no_w[0]) < len(with_w[0]))

    big_weights = list(comm.leiden_partitions(G, metric=m, resolution=2, seed=40))
    part_with_3 = [i for i, c in enumerate(big_weights[-1]) if 3 in c][0]
    assert 4 in big_weights[-1][part_with_3]


@pytest.mark.parametrize("m", _metrics())
def test_directed_weights_matter(m):
    r = 2
    s = 42637
    G = nx.DiGraph(nx.path_graph(15).edges())
    no_weights = list(comm.leiden_partitions(G, metric=m, resolution=r, seed=s))

    G.add_weighted_edges_from((u, v, (u + 1) * v) for u, v in G.edges())
    with_weights = list(comm.leiden_partitions(G, metric=m, resolution=r, seed=s))
    assert len(no_weights[0]) > len(with_weights[0])
    assert len(no_weights[-1][-1]) < len(with_weights[-1][-1])
    part_with_3 = [i for i, c in enumerate(with_weights[-1]) if 3 in c][0]
    assert 4 not in with_weights[-1][part_with_3]

    G.edges[(3, 4)]["weight"] = 1000
    big_weights = list(comm.leiden_partitions(G, metric=m, resolution=r, seed=s))
    part_with_3 = [i for i, c in enumerate(big_weights[-1]) if 3 in c][0]
    assert 4 in big_weights[-1][part_with_3]
