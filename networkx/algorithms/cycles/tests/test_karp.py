import math

import pytest

import networkx as nx
from networkx.algorithms.cycles.mean_cycle import karp


def mean_cycle_weight(G, cycle, weight="weight"):
    """
    Helper: compute mean edge weight for a cycle returned as a node list
    that includes the closing node (e.g., [a,b,c,a]).
    """
    if len(cycle) < 2:
        raise ValueError("Cycle too short")
    total = 0.0
    m = 0
    for u, v in zip(cycle, cycle[1:]):
        total += G[u][v].get(weight, 0)
        m += 1
    return total / m


def test_karp_raises_on_empty_graph():
    G = nx.DiGraph()
    with pytest.raises(nx.NetworkXError, match="Empty graph"):
        karp(G)


def test_karp_finds_negative_self_loop():
    # Negative self-loop is a negative mean cycle with mean = weight itself.
    G = nx.DiGraph()
    G.add_edge("A", "A", weight=-2)

    cycle = karp(G)
    assert cycle[0] == "A" and cycle[-1] == "A"
    assert len(cycle) == 2  # ["A","A"]

    mu = mean_cycle_weight(G, cycle)
    assert mu < 0
    assert math.isclose(mu, -2.0, rel_tol=0, abs_tol=1e-12)


def test_karp_raises_when_no_negative_mean_cycle():
    # Simple directed 3-cycle with positive mean
    G = nx.DiGraph()
    G.add_weighted_edges_from([(0, 1, 1), (1, 2, 1), (2, 0, 1)], weight="weight")

    with pytest.raises(nx.NetworkXError, match="No negative mean cycle found"):
        karp(G)


def test_karp_multidigraph_keeps_min_weight_parallel_edge():
    # MultiDiGraph with two parallel edges u->v; preprocessing should keep the cheapest one.
    MG = nx.MultiDiGraph()
    MG.add_edge("u", "v", weight=5)  # expensive
    MG.add_edge("u", "v", weight=-10)  # cheap
    MG.add_edge(
        "v", "u", weight=1
    )  # completes a cycle: u->v->u mean = (-10 + 1)/2 = -4.5

    cycle = karp(MG)
    # After preprocessing, cycle should exist and be negative
    # Convert to simple DiGraph with min edge chosen to compute mean:
    G = nx.DiGraph()
    for u, v, data in MG.edges(data=True):
        w = data.get("weight", 0)
        if G.has_edge(u, v):
            G[u][v]["weight"] = min(G[u][v]["weight"], w)
        else:
            G.add_edge(u, v, weight=w)

    mu = mean_cycle_weight(G, cycle)
    assert mu < 0
    assert math.isclose(mu, (-10 + 1) / 2, rel_tol=0, abs_tol=1e-12)


def test_karp_prefers_more_negative_mean_among_multiple_cycles():
    # Two disjoint negative cycles; algorithm should return the one with smaller (more negative) mean.
    G = nx.DiGraph()

    # Cycle 1: mean = (-2 + 0)/2 = -1
    G.add_edge("a", "b", weight=-2)
    G.add_edge("b", "a", weight=0)

    # Cycle 2: mean = (-10 + 1)/2 = -4.5  (more negative)
    G.add_edge("x", "y", weight=-10)
    G.add_edge("y", "x", weight=1)

    cycle = karp(G)
    mu = mean_cycle_weight(G, cycle)

    # Should pick the more negative mean cycle
    assert mu < -2  # weaker but robust: ensures it's not the -1 cycle
    assert math.isclose(mu, (-10 + 1) / 2, rel_tol=0, abs_tol=1e-12)
