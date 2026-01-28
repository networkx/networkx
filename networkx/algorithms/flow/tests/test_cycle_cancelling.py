import random

import pytest

import networkx as nx

# -------------------------
# Helpers
# -------------------------


def _assert_flow_conservation(flow, s, t):
    """
    For an s-t flow dict {u:{v:f}}, check flow conservation at internal nodes:
    inflow == outflow for all nodes except s and t.
    """
    nodes = set(flow.keys())
    for u in flow:
        nodes.update(flow[u].keys())

    # Compute net flow: out - in
    net = {v: 0 for v in nodes}
    for u, nbrs in flow.items():
        for v, f in nbrs.items():
            net[u] += f
            net[v] -= f

    for v in nodes:
        if v in (s, t):
            continue
        assert net[v] == 0, f"Flow conservation violated at node {v}: net={net[v]}"


def _assert_capacity_constraints(G, flow, capacity="capacity"):
    """
    Check 0 <= f(u,v) <= cap(u,v) for all original edges in G.
    Also ensure no flow on non-edges.
    """
    for u, nbrs in flow.items():
        for v, f in nbrs.items():
            # In many flow dicts, neighbors include only edges that exist in G.
            assert G.has_edge(u, v), f"Flow has value on non-edge ({u},{v})"
            cap = G[u][v].get(capacity, None)
            assert cap is not None, f"Missing capacity attribute on edge ({u},{v})"
            assert 0 <= f <= cap, f"Capacity violated on ({u},{v}): f={f}, cap={cap}"


def _flow_value(flow, s):
    """
    Total flow sent out of s in a flow dict.
    """
    return sum(flow.get(s, {}).values())


# -------------------------
# Deterministic graph builders
# -------------------------


def build_graph_small_1():
    """
    A small graph with multiple s-t paths and differing costs.
    """
    G = nx.DiGraph()
    # Two main routes: 0-1-3 and 0-2-3
    G.add_edge(0, 1, capacity=3, weight=1)
    G.add_edge(1, 3, capacity=3, weight=1)

    G.add_edge(0, 2, capacity=3, weight=5)
    G.add_edge(2, 3, capacity=3, weight=1)

    # Cross edge allows mixing
    G.add_edge(1, 2, capacity=2, weight=0)
    return G, 0, 3


def build_graph_small_2_with_negative_cycle_in_residual():
    """
    A graph where cycle-canceling may encounter negative cycles in the *residual*.
    (This can happen after sending some flow.)
    Still, the optimal min-cost max-flow should match NetworkX.

    Structure:
      0 -> 1 -> 3
      0 -> 2 -> 3
      1 -> 2 cheap edge, 2 -> 1 expensive edge (creates potential for residual negative cycle adjustments)
    """
    G = nx.DiGraph()
    G.add_edge(0, 1, capacity=2, weight=2)
    G.add_edge(1, 3, capacity=2, weight=2)

    G.add_edge(0, 2, capacity=2, weight=2)
    G.add_edge(2, 3, capacity=2, weight=2)

    G.add_edge(1, 2, capacity=2, weight=-5)
    G.add_edge(2, 1, capacity=2, weight=10)
    return G, 0, 3


def build_graph_parallel_edges_multidigraph():
    """
    MultiDiGraph with parallel edges; your Karp preprocessing keeps min-weight per (u,v).
    For cycle-cancelling, you likely convert residual MultiDiGraph to DiGraph for Karp,
    so we test that the algorithm still matches NetworkX on the original simple DiGraph.

    For fairness, we define both:
      - MG: MultiDiGraph for your algorithm (if you support it)
      - G_ref: DiGraph oracle used by NetworkX max_flow_min_cost
    """
    MG = nx.MultiDiGraph()
    # parallel edges 0->1: choose cheaper (weight=1) effectively
    MG.add_edge(0, 1, capacity=2, weight=7)
    MG.add_edge(0, 1, capacity=2, weight=1)
    MG.add_edge(1, 2, capacity=2, weight=1)

    MG.add_edge(0, 2, capacity=2, weight=10)

    # Reference simple graph: keep min weight per direction
    G_ref = nx.DiGraph()
    G_ref.add_edge(0, 1, capacity=2, weight=1)
    G_ref.add_edge(1, 2, capacity=2, weight=1)
    G_ref.add_edge(0, 2, capacity=2, weight=10)

    return MG, G_ref, 0, 2


# -------------------------
# Tests
# -------------------------


def test_cycle_cancelling_matches_networkx_on_small_graph_1():
    G, s, t = build_graph_small_1()

    # Oracle: NetworkX min-cost max-flow for single-source/single-sink
    flow_ref = nx.max_flow_min_cost(G, s, t, capacity="capacity", weight="weight")
    cost_ref = nx.cost_of_flow(G, flow_ref, weight="weight")
    val_ref = _flow_value(flow_ref, s)

    flow_cc, cost_cc = nx.cycle_cancelling(
        G.copy(), s, t, capacity="capacity", weight="weight"
    )

    assert cost_cc == cost_ref
    assert _flow_value(flow_cc, s) == val_ref
    _assert_flow_conservation(flow_cc, s, t)
    _assert_capacity_constraints(G, flow_cc, capacity="capacity")


def test_cycle_cancelling_matches_networkx_on_small_graph_2():
    G, s, t = build_graph_small_2_with_negative_cycle_in_residual()

    flow_ref = nx.max_flow_min_cost(G, s, t, capacity="capacity", weight="weight")
    cost_ref = nx.cost_of_flow(G, flow_ref, weight="weight")
    val_ref = _flow_value(flow_ref, s)

    flow_cc, cost_cc = nx.cycle_cancelling(
        G.copy(), s, t, capacity="capacity", weight="weight"
    )

    assert cost_cc == cost_ref
    assert _flow_value(flow_cc, s) == val_ref
    _assert_flow_conservation(flow_cc, s, t)
    _assert_capacity_constraints(G, flow_cc, capacity="capacity")


def test_cycle_cancelling_rejects_non_digraph():
    UG = nx.Graph()
    UG.add_edge(0, 1, capacity=1, weight=1)
    with pytest.raises((TypeError, nx.NetworkXError)):
        nx.cycle_cancelling(UG, 0, 1, capacity="capacity", weight="weight")


def test_cycle_cancelling_raises_on_missing_capacity():
    G = nx.DiGraph()
    G.add_edge(0, 1, weight=1)  # missing capacity
    with pytest.raises((ValueError, nx.NetworkXError, KeyError)):
        nx.cycle_cancelling(G, 0, 1, capacity="capacity", weight="weight")


def test_cycle_cancelling_raises_on_missing_weight():
    G = nx.DiGraph()
    G.add_edge(0, 1, capacity=1)  # missing weight
    with pytest.raises((ValueError, nx.NetworkXError, KeyError)):
        nx.cycle_cancelling(G, 0, 1, capacity="capacity", weight="weight")


def test_cycle_cancelling_multidigraph_parallel_edges_matches_reference():
    MG, G_ref, s, t = build_graph_parallel_edges_multidigraph()

    # Oracle on the reference DiGraph
    flow_ref = nx.max_flow_min_cost(G_ref, s, t, capacity="capacity", weight="weight")
    cost_ref = nx.cost_of_flow(G_ref, flow_ref, weight="weight")
    val_ref = _flow_value(flow_ref, s)

    # Your algorithm run on MultiDiGraph (if supported). If not supported, change to expect TypeError.
    flow_cc, cost_cc = nx.cycle_cancelling(
        MG.copy(), s, t, capacity="capacity", weight="weight"
    )

    assert cost_cc == cost_ref
    assert _flow_value(flow_cc, s) == val_ref


def test_cycle_cancelling_random_small_fixed_seed_matches_networkx():
    """
    Small randomized regression test with fixed seed.
    Keep it small to avoid flaky/slow tests in CI.
    """
    rng = random.Random(12345)

    for _ in range(10):
        n = 6
        s, t = 0, n - 1
        G = nx.DiGraph()

        # Build a sparse-ish random digraph with guaranteed s->t path
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if rng.random() < 0.25:
                    G.add_edge(
                        u,
                        v,
                        capacity=rng.randint(1, 5),
                        weight=rng.randint(-3, 6),
                    )

        # Ensure at least one simple s->t chain
        chain = [0, 2, 4, 5]
        for u, v in zip(chain, chain[1:]):
            if not G.has_edge(u, v):
                G.add_edge(u, v, capacity=rng.randint(1, 5), weight=rng.randint(-3, 6))

        flow_ref = nx.max_flow_min_cost(G, s, t, capacity="capacity", weight="weight")
        cost_ref = nx.cost_of_flow(G, flow_ref, weight="weight")
        val_ref = _flow_value(flow_ref, s)

        flow_cc, cost_cc = nx.cycle_cancelling(
            G.copy(), s, t, capacity="capacity", weight="weight"
        )

        assert cost_cc == cost_ref
        assert _flow_value(flow_cc, s) == val_ref
        _assert_flow_conservation(flow_cc, s, t)
        _assert_capacity_constraints(G, flow_cc, capacity="capacity")
