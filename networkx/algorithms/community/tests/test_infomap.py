from typing import NamedTuple

import pytest

import networkx as nx


def test_valid_partition():
    G = nx.karate_club_graph()
    partition = nx.community.infomap_communities(G)
    assert nx.community.is_partition(G, partition)


def test_labels_preserved():
    # String labels: an accidental relabel-to-index bug cannot hide.
    G = nx.relabel_nodes(nx.karate_club_graph(), lambda n: f"v{n}")
    partition = nx.community.infomap_communities(G)
    assert set().union(*partition) == set(G.nodes())


def test_directed():
    # Infomap is flow-based and supports directed graphs.
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    G = nx.gnc_graph(50, seed=42)
    partition = nx.community.infomap_communities(G)
    assert nx.community.is_partition(G, partition)


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


def test_hierarchical_codelength_matches_cpp_multilevel():
    """The multilevel (hierarchical) codelength must match the C++ reference
    on a graph where Infomap finds a >2-level hierarchy."""
    infomap = pytest.importorskip("infomap", minversion="2.14")
    from networkx.algorithms.community.infomap import _hierarchical_codelength
    from networkx.algorithms.community.quality import _flow

    G = nx.ring_of_cliques(12, 6)

    im = infomap.Infomap(silent=True, seed=42, num_trials=50)
    for u, v in G.edges():
        im.add_link(u, v)
    result = im.run()
    assert result.num_levels >= 3  # genuinely multilevel

    flow, links = _flow(G, None)
    path = {
        node: tuple(modules) for node, modules in result.multilevel_modules().items()
    }
    assert _hierarchical_codelength(dict(flow), links, path) == pytest.approx(
        result.codelength, abs=1e-9
    )


# --- Single recorded values, kept out of the case table below because each
# --- checks one specific path rather than the optimizer's usual entry points ---


def test_map_equation_directed_cycle_known_value():
    # Two directed triangles bridged; codelength from the C++ reference.
    pytest.importorskip("scipy")  # directed flow uses nx.pagerank

    G = nx.DiGraph([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3), (0, 4)])
    partition = [{0, 1, 2}, {3, 4, 5}]
    assert nx.community.map_equation(G, partition) == pytest.approx(1.772891, abs=1e-5)


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


# --- Structural properties of the result ---


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
    for coarse, fine in nx.utils.pairwise(levels):
        for community in fine:
            assert any(community <= parent for parent in coarse)


def test_infomap_communities_optimizes_two_level_objective():
    """infomap_communities returns the two-level optimum, not the coarsest level
    of the multilevel hierarchy. On a genuinely hierarchical graph the two-level
    optimum compresses strictly better, in two-level terms, than the hierarchy's
    top level (which infomap_partitions yields first)."""
    G = nx.ring_of_cliques(12, 6)
    communities = nx.community.infomap_communities(G, seed=0, num_trials=10)
    hierarchy_top = next(
        iter(nx.community.infomap_partitions(G, seed=0, num_trials=10))
    )
    assert (
        nx.community.map_equation(G, communities)
        < nx.community.map_equation(G, hierarchy_top) - 1e-9
    )


def test_infomap_partitions_empty_graph():
    # One empty level, matching louvain_partitions / leiden_partitions.
    assert list(nx.community.infomap_partitions(nx.Graph())) == [[]]


def test_infomap_handles_multigraph_as_summed_weights():
    """Parallel edges are summed, matching the equivalent weighted simple graph
    (as Louvain does), so multigraphs are handled rather than rejected."""
    MG = nx.MultiGraph([(0, 1), (0, 1), (1, 2), (2, 0)])
    SG = nx.Graph()
    SG.add_weighted_edges_from([(0, 1, 2), (1, 2, 1), (2, 0, 1)])
    partition = [{0, 1, 2}]
    assert nx.community.map_equation(MG, partition, weight=None) == pytest.approx(
        nx.community.map_equation(SG, partition)
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


def test_infomap_rejects_invalid_num_trials():
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
    G = nx.planted_partition_graph(5, 12, 0.3, 0.05, seed=4)
    c1 = nx.community.map_equation(
        G, nx.community.infomap_communities(G, weight=None, seed=0, num_trials=1)
    )
    c20 = nx.community.map_equation(
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
        nx.Graph([(0, 0), (0, 1), (1, 1)]),
    ],
    ids=["empty", "single-node", "edgeless", "single-edge", "self-loops"],
)
def test_infomap_degenerate_graphs(G):
    """Empty, single-node, edgeless, single-edge, and self-loop graphs return a
    valid partition (or [] for the empty graph) without crashing."""
    partition = nx.community.infomap_communities(G, seed=0)
    if len(G) == 0:
        assert partition == []
    else:
        assert nx.community.is_partition(G, partition)


# --- Recorded optima ----------------------------------------------------------
#
# Each case records a graph and the two-level codelength the reference C++
# Infomap reports as its optimum. The optimizer here is checked against the
# recorded number, so these tests run whether or not the `infomap` package is
# installed and do not move when it changes. A second, skippable test re-derives
# the same numbers from C++, which is what catches drift between the two.


class _OptimumCase(NamedTuple):
    id: str
    build: object  # () -> graph
    codelength: float
    weight: str | None = "weight"
    seeds: tuple = (0,)
    num_trials: int = 10
    teleportation_probability: float = 0.15
    directed: bool = False
    cpp_trials: int = 50


def _reciprocal_triangles():
    return nx.DiGraph(
        [(0, 1), (1, 0), (1, 2), (2, 1), (2, 0), (0, 2)]
        + [(3, 4), (4, 3), (4, 5), (5, 4), (5, 3), (3, 5), (2, 3)]
    )


_OPTIMUM_CASES = [
    _OptimumCase("barbell", lambda: nx.barbell_graph(5, 0), 2.6427550064563676),
    _OptimumCase("karate", nx.karate_club_graph, 4.087423158819623, num_trials=20),
    _OptimumCase(
        "caveman",
        lambda: nx.connected_caveman_graph(5, 6),
        3.089850642923342,
        weight=None,
    ),
    _OptimumCase(
        # Genuinely multilevel, so this pins the two-level optimum rather than
        # the coarsest level of the hierarchy.
        "ring-of-cliques",
        lambda: nx.ring_of_cliques(12, 6),
        3.146423428048501,
        weight=None,
        seeds=(42,),
        num_trials=20,
    ),
    _OptimumCase(
        # Growing DAGs are the hard case for the greedy search.
        "gnc-dag-80",
        lambda: nx.gnc_graph(80, seed=7),
        2.0203742478586735,
        weight=None,
        seeds=(0, 1, 2),
        num_trials=15,
        directed=True,
        cpp_trials=100,
    ),
    _OptimumCase(
        "gnc-dag-40",
        lambda: nx.gnc_graph(40, seed=3),
        2.3493511266833416,
        weight=None,
        seeds=(0, 1, 2),
        num_trials=15,
        directed=True,
        cpp_trials=100,
    ),
    _OptimumCase(
        # At tau=0.85 the optimum is a different partition than at the default,
        # so this fails if teleportation_probability stops reaching the flow.
        "gnc-dag-40-teleportation-0.85",
        lambda: nx.gnc_graph(40, seed=3),
        2.7403670603341608,
        weight=None,
        seeds=(0, 1, 2),
        num_trials=15,
        teleportation_probability=0.85,
        directed=True,
        cpp_trials=100,
    ),
    _OptimumCase(
        # Reciprocal links make the flow symmetric while the graph stays
        # directed, which exercises the directed leftover-move rule.
        "directed-reciprocal",
        _reciprocal_triangles,
        1.754327284932079,
        weight=None,
        seeds=tuple(range(8)),
        directed=True,
        cpp_trials=80,
    ),
]


def _best_codelength(case):
    """Lowest codelength this implementation reaches over the case's seeds."""
    G = case.build()
    return min(
        nx.community.map_equation(
            G,
            nx.community.infomap_communities(
                G,
                weight=case.weight,
                seed=seed,
                num_trials=case.num_trials,
                teleportation_probability=case.teleportation_probability,
            ),
            weight=case.weight,
            teleportation_probability=case.teleportation_probability,
        )
        for seed in case.seeds
    )


def _cpp_codelength(case, *, two_level=True, num_trials=None):
    """Codelength the reference C++ Infomap reaches, or skip if it is absent."""
    infomap = pytest.importorskip("infomap", minversion="2.14")
    G = case.build()
    network = infomap.Network()
    for u, v, wt in G.edges(data=case.weight, default=1):
        network.add_link(u, v, wt)
    return network.run(
        options=infomap.Options(
            two_level=two_level,
            silent=True,
            seed=42,
            directed=case.directed,
            num_trials=case.cpp_trials if num_trials is None else num_trials,
            teleportation_probability=case.teleportation_probability,
        )
    ).codelength


@pytest.mark.parametrize("case", _OPTIMUM_CASES, ids=lambda c: c.id)
def test_infomap_reaches_recorded_optimum(case):
    """The optimizer reaches the recorded optimum. Runs with or without the
    `infomap` package, so a break here is a break in networkx."""
    if case.directed:
        pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    assert _best_codelength(case) == pytest.approx(case.codelength, abs=1e-9)


@pytest.mark.parametrize("case", _OPTIMUM_CASES, ids=lambda c: c.id)
def test_recorded_optimum_matches_cpp(case):
    """The recorded optima still agree with the reference C++ Infomap. Skipped
    when the package is missing, so an unavailable or changed upstream stops
    guarding against drift rather than failing the suite."""
    assert _cpp_codelength(case) == pytest.approx(case.codelength, abs=1e-9)


def test_recorded_multilevel_optimum_matches_cpp():
    """Companion to test_infomap_multilevel_reaches_known_optimum_no_dep: the
    recorded hierarchical optimum still agrees with the C++ reference."""
    case = next(c for c in _OPTIMUM_CASES if c.id == "ring-of-cliques")
    assert _cpp_codelength(case, two_level=False, num_trials=50) == pytest.approx(
        3.128528943240294, abs=1e-9
    )


# --- Robustness: termination, graph flavours, and the no-mutation contract ---


def test_infomap_terminates_on_every_atlas_graph():
    """Both entry points terminate and return a valid partition for all 1252
    graphs in the atlas. Louvain had an infinite loop on one of them (gh-8739)
    from floating-point ties, and the search here alternates fine- and
    coarse-tuning under similar thresholds, so the whole atlas is swept rather
    than one graph pinned."""
    from networkx.generators.atlas import graph_atlas_g

    for G in graph_atlas_g():
        if len(G) == 0:
            continue
        assert nx.community.is_partition(
            G, nx.community.infomap_communities(G, seed=123)
        )
        levels = list(nx.community.infomap_partitions(G, seed=123))
        for partition in levels:
            assert nx.community.is_partition(G, partition)
        # Levels must nest, at every graph, not just the hierarchical ones.
        for coarse, fine in nx.utils.pairwise(levels):
            assert all(any(c <= parent for parent in coarse) for c in fine)


@pytest.mark.parametrize(
    "build",
    [
        lambda: nx.MultiDiGraph(nx.gnc_graph(30, seed=2)),
        lambda: nx.freeze(nx.karate_club_graph()),
        lambda: nx.karate_club_graph().subgraph(range(12)),
        lambda: nx.reverse_view(nx.gnc_graph(30, seed=2)),
        # Any hashable is a node, and nothing here orders them.
        lambda: nx.Graph([(0, "a"), ("a", (1, 2)), ((1, 2), 0), (0, frozenset({1}))]),
    ],
    ids=["multidigraph", "frozen", "subgraph-view", "reverse-view", "mixed-node-types"],
)
def test_infomap_accepts_every_graph_flavour(build):
    """Graph classes and node types beyond the plain Graph/DiGraph pair: Louvain
    covers MultiDiGraph the same way, views must not need copying, and node
    labels are only ever hashed, never ordered."""
    G = build()
    if G.is_directed():
        pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    assert nx.community.is_partition(G, nx.community.infomap_communities(G, seed=1))


def test_infomap_leaves_the_graph_untouched():
    """None of the three entry points may modify the graph they are given."""
    G = nx.karate_club_graph()
    before = (dict(G.nodes(data=True)), sorted(G.edges(data=True)))
    nx.community.infomap_communities(G, seed=1)
    list(nx.community.infomap_partitions(G, seed=1))
    nx.community.map_equation(G, [set(G)])
    assert (dict(G.nodes(data=True)), sorted(G.edges(data=True))) == before


# --- Optimizer internals ---


def test_core_optimizer_cached_module_codelength_stays_exact():
    """The optimizer caches each module's own codelength contribution and
    updates it per move. Drift there would bias every later move, so check it
    against a fresh recomputation once the search has finished."""
    import random

    from networkx.algorithms.community.infomap import _CoreOptimizer, _module_codelength
    from networkx.algorithms.community.quality import _flow

    G = nx.karate_club_graph()
    flow, links = _flow(G, "weight")
    singletons = {node: i for i, node in enumerate(flow)}
    optimizer = _CoreOptimizer(flow, links, singletons, random.Random(7), False)
    optimizer.optimize(False, 10)

    for module in set(optimizer.module_of.values()):
        assert optimizer.module_codelength[module] == _module_codelength(
            optimizer.module_enter[module],
            optimizer.module_exit[module],
            optimizer.module_exit[module] + optimizer.module_flow[module],
        )
    # ...and the running codelength still agrees with the public quality function.
    communities = list(nx.utils.groups(optimizer.module_of).values())
    assert optimizer.codelength() == pytest.approx(
        nx.community.map_equation(G, communities), abs=1e-12
    )
