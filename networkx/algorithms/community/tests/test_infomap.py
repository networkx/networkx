import pytest

import networkx as nx
from networkx.algorithms.community import infomap_communities


def test_valid_partition():
    G = nx.karate_club_graph()
    partition = nx.community.infomap_communities(G)
    assert nx.community.is_partition(G, partition)


def test_labels_preserved():
    G = nx.karate_club_graph()
    partition = nx.community.infomap_communities(G)
    assert set().union(*partition) == set(G.nodes())


def test_directed():
    # Infomap is flow-based and supports directed graphs.
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    G = nx.gnc_graph(50, seed=42)
    partition = nx.community.infomap_communities(G)
    assert nx.community.is_partition(G, partition)


def test_directedness_from_graph_not_flow_symmetry():
    """A symmetric directed graph (reciprocal equal-weight links) has symmetric
    flow, yet Infomap must still treat it as directed. The optimizer takes
    directedness from the graph, not by inferring it from flow symmetry."""
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    import random

    from networkx.algorithms.community.infomap import _CoreOptimizer
    from networkx.algorithms.community.quality import _flow

    edges = [(0, 1), (1, 2), (2, 0)]
    DG = nx.DiGraph()
    for u, v in edges:
        DG.add_edge(u, v)
        DG.add_edge(v, u)  # reciprocal, equal weight -> symmetric flow
    flow, links = _flow(DG, "weight")
    opt = _CoreOptimizer(
        dict(flow), list(links), {n: 0 for n in DG}, random.Random(0), DG.is_directed()
    )
    assert opt.directed is True

    UG = nx.Graph(edges)
    uflow, ulinks = _flow(UG, "weight")
    uopt = _CoreOptimizer(
        dict(uflow),
        list(ulinks),
        {n: 0 for n in UG},
        random.Random(0),
        UG.is_directed(),
    )
    assert uopt.directed is False


def test_isolated_nodes():
    G = nx.karate_club_graph()
    G.add_node("isolated")
    partition = nx.community.infomap_communities(G)
    assert {"isolated"} in partition


def test_weight_param():
    G = nx.karate_club_graph()
    nx.set_edge_attributes(
        G, {edge: i * i for i, edge in enumerate(G.edges)}, name="foo"
    )
    partition_none = nx.community.infomap_communities(G, weight=None, seed=2)
    partition_foo = nx.community.infomap_communities(G, weight="foo", seed=2)

    assert nx.community.is_partition(G, partition_none)
    assert nx.community.is_partition(G, partition_foo)
    # The weight attribute is actually honored: weighting changes the partition,
    # so the test would fail if `weight` were silently ignored.
    assert sorted(map(sorted, partition_none)) != sorted(map(sorted, partition_foo))


def test_seed_reproducible():
    G = nx.karate_club_graph()
    p1 = nx.community.infomap_communities(G, seed=42)
    p2 = nx.community.infomap_communities(G, seed=42)
    assert sorted(map(sorted, p1)) == sorted(map(sorted, p2))


def test_infomap_native_matches_cpp_codelength_barbell():
    """The native optimizer should reach the same two-level optimum as the
    reference C++ Infomap on a clear two-clique structure."""
    infomap = pytest.importorskip("infomap")
    from networkx.algorithms.community.quality import map_equation

    G = nx.barbell_graph(5, 0)
    partition = nx.community.infomap_communities(G, seed=42)
    assert nx.community.is_partition(G, partition)

    im = infomap.Infomap(two_level=True, silent=True, seed=42)
    for u, v in G.edges():
        im.add_link(u, v)
    im.run()
    assert map_equation(G, partition) == pytest.approx(im.codelength, abs=1e-9)


def test_infomap_native_matches_cpp_codelength_karate():
    """With aggregation and several trials, the native optimizer should reach
    the same two-level optimum as the reference C++ Infomap on karate."""
    infomap = pytest.importorskip("infomap")
    from networkx.algorithms.community.quality import map_equation

    G = nx.karate_club_graph()
    partition = nx.community.infomap_communities(G, seed=42, num_trials=20)

    im = infomap.Infomap(two_level=True, silent=True, seed=42, num_trials=50)
    for u, v, w in G.edges(data="weight", default=1):
        im.add_link(u, v, w)
    im.run()
    assert map_equation(G, partition) == pytest.approx(im.codelength, abs=1e-9)


def test_infomap_native_matches_cpp_directed_dag():
    """On a directed growing DAG (a hard case for greedy search), the optimizer
    should reach the C++ reference two-level codelength given enough trials."""
    infomap = pytest.importorskip("infomap")
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    from networkx.algorithms.community.quality import map_equation

    G = nx.gnc_graph(40, seed=3)
    partition = nx.community.infomap_communities(G, seed=1, num_trials=20)
    assert nx.community.is_partition(G, partition)

    im = infomap.Infomap(
        directed=True, two_level=True, silent=True, seed=42, num_trials=100
    )
    for u, v in G.edges():
        im.add_link(u, v)
    im.run()
    assert map_equation(G, partition, weight=None) <= im.codelength + 1e-6


def test_infomap_communities_two_level_matches_cpp_ring_of_cliques():
    """On a genuinely multilevel graph, infomap_communities (two-level) reaches
    the same two-level optimum as the reference C++ Infomap run with
    two_level=True -- not the coarser hierarchy top it used to return."""
    infomap = pytest.importorskip("infomap")
    from networkx.algorithms.community.quality import map_equation

    G = nx.ring_of_cliques(12, 6)
    partition = nx.community.infomap_communities(G, weight=None, seed=42, num_trials=20)

    im = infomap.Infomap(two_level=True, silent=True, seed=42, num_trials=50)
    for u, v in G.edges():
        im.add_link(u, v)
    im.run()
    assert map_equation(G, partition, weight=None) == pytest.approx(
        im.codelength, abs=1e-6
    )


def test_hierarchical_codelength_matches_cpp_multilevel():
    """The multilevel (hierarchical) codelength must match the C++ reference
    on a graph where Infomap finds a >2-level hierarchy."""
    infomap = pytest.importorskip("infomap")
    from networkx.algorithms.community.infomap import _hierarchical_codelength
    from networkx.algorithms.community.quality import _flow

    G = nx.ring_of_cliques(12, 6)

    im = infomap.Infomap(silent=True, seed=42, num_trials=50)
    for u, v in G.edges():
        im.add_link(u, v)
    im.run()
    assert im.num_levels >= 3  # genuinely multilevel

    flow, links = _flow(G, None)
    path = {
        node: tuple(modules) for node, modules in im.get_multilevel_modules().items()
    }
    assert _hierarchical_codelength(dict(flow), links, path) == pytest.approx(
        im.codelength, abs=1e-9
    )


def test_infomap_multilevel_matches_cpp_ring_of_cliques():
    """The multilevel optimizer should reach the C++ reference hierarchical
    codelength on a genuinely 3-level structure (ring of cliques)."""
    import random

    infomap = pytest.importorskip("infomap")
    from networkx.algorithms.community.infomap import (
        _build_hierarchy,
        _hierarchical_codelength,
    )
    from networkx.algorithms.community.quality import _flow

    G = nx.ring_of_cliques(12, 6)
    im = infomap.Infomap(silent=True, seed=42, num_trials=80)
    for u, v in G.edges():
        im.add_link(u, v)
    im.run()
    assert im.num_levels >= 3

    flow, links = _flow(G, None)
    flow = dict(flow)
    best_path = min(
        (
            _build_hierarchy(flow, links, random.Random(s), G.is_directed())
            for s in range(15)
        ),
        key=lambda p: _hierarchical_codelength(flow, links, p),
    )
    depth = max(len(p) for p in best_path.values())
    assert depth >= 2  # genuinely multilevel (>= 2 module levels)
    assert _hierarchical_codelength(flow, links, best_path) == pytest.approx(
        im.codelength, abs=1e-6
    )


# --- NetworkX-native parity tests (hardcoded codelengths validated against the
# --- reference C++ Infomap; no dependency on the `infomap` package) ---


def test_infomap_reaches_known_optimum_barbell():
    from networkx.algorithms.community.quality import map_equation

    G = nx.barbell_graph(5, 0)
    partition = nx.community.infomap_communities(G, seed=0, num_trials=10)
    assert nx.community.is_partition(G, partition)
    # Two-level optimum found by the C++ reference for two K5 joined by an edge.
    assert map_equation(G, partition) == pytest.approx(2.642755, abs=1e-5)


def test_infomap_reaches_known_optimum_karate():
    from networkx.algorithms.community.quality import map_equation

    G = nx.karate_club_graph()  # weighted (Zachary)
    partition = nx.community.infomap_communities(G, seed=0, num_trials=20)
    assert nx.community.is_partition(G, partition)
    assert map_equation(G, partition) == pytest.approx(4.087423, abs=1e-5)


def test_infomap_reaches_known_optimum_caveman():
    from networkx.algorithms.community.quality import map_equation

    G = nx.connected_caveman_graph(5, 6)
    partition = nx.community.infomap_communities(G, weight=None, seed=0, num_trials=10)
    assert map_equation(G, partition, weight=None) == pytest.approx(3.089847, abs=1e-5)


def test_map_equation_directed_cycle_known_value():
    # Two directed triangles bridged; codelength from the C++ reference.
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    from networkx.algorithms.community.quality import map_equation

    G = nx.DiGraph([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3), (0, 4)])
    partition = [{0, 1, 2}, {3, 4, 5}]
    assert map_equation(G, partition) == pytest.approx(1.772891, abs=1e-5)


def test_infomap_reaches_known_optimum_gnc_dag():
    """Growing DAGs are the hard case where Infomap's move heuristics matter
    most; the optimizer must still reach the C++ two-level optimum. Best over a
    few seeds keeps this robust against per-trial stochasticity."""
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    from networkx.algorithms.community.quality import map_equation

    G = nx.gnc_graph(80, seed=7)
    best = min(
        map_equation(
            G,
            nx.community.infomap_communities(G, weight=None, seed=s, num_trials=15),
            weight=None,
        )
        for s in range(3)
    )
    assert best == pytest.approx(2.020374, abs=1e-5)


def test_infomap_multilevel_reaches_known_optimum_no_dep():
    """Multilevel build reaches the known C++ hierarchical optimum on a 3-level
    ring of cliques (hardcoded; no dependency on the infomap package)."""
    import random

    from networkx.algorithms.community.infomap import (
        _build_hierarchy,
        _hierarchical_codelength,
    )
    from networkx.algorithms.community.quality import _flow

    G = nx.ring_of_cliques(12, 6)
    flow, links = _flow(G, None)
    flow = dict(flow)
    best = min(
        _hierarchical_codelength(
            flow,
            links,
            _build_hierarchy(flow, links, random.Random(s), G.is_directed()),
        )
        for s in range(6)
    )
    assert best == pytest.approx(3.128529, abs=1e-5)


def test_infomap_partitions_yields_nested_levels():
    """infomap_partitions yields a valid partition per hierarchy level, coarsest
    first, with each level at least as fine as the previous (a refinement)."""
    G = nx.ring_of_cliques(12, 6)
    levels = list(nx.community.infomap_partitions(G, seed=0, num_trials=10))
    assert len(levels) >= 2  # ring of cliques is genuinely multilevel
    for partition in levels:
        assert nx.community.is_partition(G, partition)
    # Coarsest first: each subsequent level has at least as many communities.
    assert [len(p) for p in levels] == sorted(len(p) for p in levels)
    # ...and the levels genuinely nest: every community of a finer level is a
    # subset of some community one level coarser (a true refinement, not a
    # reshuffle that merely happens to have more parts).
    for coarse, fine in zip(levels, levels[1:]):
        for community in fine:
            assert any(community <= parent for parent in coarse)


def test_infomap_communities_optimizes_two_level_objective():
    """infomap_communities returns the two-level optimum, not the coarsest level
    of the multilevel hierarchy. On a genuinely hierarchical graph the two-level
    optimum compresses strictly better, in two-level terms, than the hierarchy's
    top level (which infomap_partitions yields first)."""
    from networkx.algorithms.community.quality import map_equation

    G = nx.ring_of_cliques(12, 6)
    communities = nx.community.infomap_communities(G, seed=0, num_trials=10)
    hierarchy_top = next(
        iter(nx.community.infomap_partitions(G, seed=0, num_trials=10))
    )
    assert map_equation(G, communities) < map_equation(G, hierarchy_top) - 1e-9


def test_infomap_partitions_empty_graph():
    # One empty level, matching louvain_partitions / leiden_partitions.
    assert list(nx.community.infomap_partitions(nx.Graph())) == [[]]


def test_infomap_invalid_num_trials():
    G = nx.karate_club_graph()
    with pytest.raises(ValueError, match="num_trials"):
        nx.community.infomap_communities(G, num_trials=0)


def test_infomap_handles_multigraph_as_summed_weights():
    """Parallel edges are summed, matching the equivalent weighted simple graph
    (as Louvain does), so multigraphs are handled rather than rejected."""
    from networkx.algorithms.community.quality import map_equation

    MG = nx.MultiGraph([(0, 1), (0, 1), (1, 2), (2, 0)])
    SG = nx.Graph()
    SG.add_weighted_edges_from([(0, 1, 2), (1, 2, 1), (2, 0, 1)])
    partition = [{0, 1, 2}]
    assert map_equation(MG, partition, weight=None) == pytest.approx(
        map_equation(SG, partition)
    )
    assert nx.community.is_partition(MG, nx.community.infomap_communities(MG))


# --- Input validation, determinism, and degenerate-input correctness ---


def test_infomap_directed_zero_weight_edges():
    """A dangling source (zero out-strength, e.g. only a zero-weight out-edge)
    must not crash the directed flow: its flow is redistributed by teleportation
    and its links carry none, rather than dividing by a zero out-strength."""
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    G = nx.DiGraph()
    G.add_edge(0, 1, weight=0.0)
    G.add_edge(1, 2, weight=3.0)
    assert nx.community.is_partition(G, nx.community.infomap_communities(G, seed=1))
    assert all(
        nx.community.is_partition(G, p)
        for p in nx.community.infomap_partitions(G, seed=1)
    )


def test_infomap_invalid_num_trials_type():
    """num_trials must be a positive integer; 0, negatives, and non-ints all
    raise ValueError (not a bare TypeError) per the documented contract."""
    G = nx.karate_club_graph()
    for bad in (0, -1, 1.5, "3"):
        with pytest.raises(ValueError, match="num_trials"):
            nx.community.infomap_communities(G, num_trials=bad)


def test_infomap_partitions_validates_num_trials_eagerly():
    """infomap_partitions wraps a generator, so a bad num_trials must raise on
    the call itself, not only once the result is iterated."""
    G = nx.karate_club_graph()
    for bad in (0, 1.5):
        with pytest.raises(ValueError, match="num_trials"):
            nx.community.infomap_partitions(G, num_trials=bad)


def test_infomap_rejects_invalid_weights():
    """Flow is a probability distribution, so negative or non-finite weights are
    rejected rather than silently producing a meaningless codelength."""
    for bad in (-1.0, float("nan"), float("inf")):
        G = nx.Graph()
        G.add_edge(0, 1, weight=bad)
        G.add_edge(1, 2, weight=2.0)
        with pytest.raises(ValueError, match="non-negative"):
            nx.community.infomap_communities(G)


def test_infomap_seed_int_and_random_state_agree():
    """An int seed and a random.Random with the same seed give the identical
    partition (the @py_random_state contract)."""
    import random

    G = nx.karate_club_graph()
    p_int = nx.community.infomap_communities(G, seed=42)
    p_rs = nx.community.infomap_communities(G, seed=random.Random(42))
    assert sorted(map(sorted, p_int)) == sorted(map(sorted, p_rs))


def test_infomap_different_seeds_vary_partition():
    """The search is stochastic: on a graph without one dominant optimum,
    different seeds explore different partitions -- guards against the seed
    being silently ignored."""
    G = nx.planted_partition_graph(5, 12, 0.3, 0.05, seed=3)
    seen = {
        tuple(sorted(tuple(sorted(c)) for c in p))
        for p in (
            nx.community.infomap_communities(G, weight=None, seed=s) for s in range(10)
        )
    }
    assert len(seen) > 1


def test_infomap_structureless_graph_is_one_module():
    """A graph with no community structure collapses to a single module: the map
    equation never does worse than coding the whole walk in one codebook. Guards
    the one-level fallback in _partition."""
    for G in (nx.complete_graph(10), nx.gnp_random_graph(20, 0.9, seed=2)):
        partition = nx.community.infomap_communities(G, seed=0, num_trials=5)
        assert partition == [set(G)]


def test_infomap_disconnected_components_not_merged():
    """Two disjoint cliques never share a module: no flow crosses the gap."""
    G = nx.disjoint_union(nx.complete_graph(5), nx.complete_graph(5))
    partition = nx.community.infomap_communities(G, seed=0, num_trials=5)
    assert nx.community.is_partition(G, partition)
    left, right = set(range(5)), set(range(5, 10))
    assert all(c <= left or c <= right for c in partition)


def test_infomap_num_trials_improves_codelength():
    """More restarts can only keep or lower the best codelength found -- the
    first trial of an N-trial run reuses the single-trial seed stream."""
    from networkx.algorithms.community.quality import map_equation

    G = nx.planted_partition_graph(5, 12, 0.3, 0.05, seed=4)
    c1 = map_equation(
        G, nx.community.infomap_communities(G, weight=None, seed=0, num_trials=1)
    )
    c20 = map_equation(
        G, nx.community.infomap_communities(G, weight=None, seed=0, num_trials=20)
    )
    assert c20 <= c1 + 1e-9


@pytest.mark.parametrize(
    "G",
    [
        nx.empty_graph(0),
        nx.empty_graph(1),
        nx.empty_graph(5),
        nx.path_graph(2),
        nx.Graph([(0, 0), (0, 1), (1, 1)]),  # self-loops
    ],
)
def test_infomap_degenerate_graphs(G):
    """Empty, single-node, edgeless, and self-loop graphs return a valid
    partition (or [] for the empty graph) without crashing."""
    partition = nx.community.infomap_communities(G, seed=0)
    if len(G) == 0:
        assert partition == []
    else:
        assert nx.community.is_partition(G, partition)


def test_infomap_directed_reciprocal_matches_cpp():
    """Directed graphs with reciprocal edges exercise the link-counting leftover
    rule and the strongest-connected tie-break; the optimizer must still reach
    the reference C++ two-level optimum."""
    infomap = pytest.importorskip("infomap")
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    from networkx.algorithms.community.quality import map_equation

    G = nx.DiGraph(
        [
            (0, 1),
            (1, 0),
            (1, 2),
            (2, 1),
            (2, 0),
            (0, 2),
            (3, 4),
            (4, 3),
            (4, 5),
            (5, 4),
            (5, 3),
            (3, 5),
            (2, 3),
        ]
    )
    best = min(
        map_equation(
            G, nx.community.infomap_communities(G, weight=None, seed=s, num_trials=10)
        )
        for s in range(8)
    )
    im = infomap.Infomap(
        directed=True, two_level=True, silent=True, seed=42, num_trials=80
    )
    for u, v in G.edges():
        im.add_link(u, v)
    im.run()
    assert best == pytest.approx(im.codelength, abs=1e-6)
