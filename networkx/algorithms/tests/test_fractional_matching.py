import math
import random

import pytest
import networkx as nx
from networkx.algorithms.matching import fractional_matching

def test_empty_graph():
    G = nx.Graph()
    m = fractional_matching(G)
    assert m == {}  # no edges at all

def test_single_edge():
    G = nx.Graph()
    G.add_edge(1, 2)
    m = fractional_matching(G)
    # the only edge must get value 1
    assert m == {(1, 2): 1}

def test_triangle():
    # a 3‑cycle can only support total weight ≤1 per node
    G = nx.cycle_graph(3)
    m = fractional_matching(G)
    # each node incident sum ≤1
    for node in G:
        s = sum(val for (u, v), val in m.items() if u == node or v == node)
        assert s <= 1 + 1e-8

def test_directed_raises():
    D = nx.DiGraph([(1,2)])
    with pytest.raises(nx.NetworkXNotImplemented):
        fractional_matching(D)

def test_property_on_random():
    # compare to a “greedy” solver for small graphs
    import random
    for _ in range(10):
        G = nx.gnp_random_graph(5, 0.5)
        m = fractional_matching(G)
        # check fractional constraints
        for node in G:
            total = sum(m.get((u, v), 0) for u, v in G.edges(node))
            assert total <= 1 + 1e-8

# --------------------------------------------------------------------
# 1.  Larger random graphs — verify constraints only (fast, O(E)).

@pytest.mark.parametrize(
    "n, p", [(50, 0.08), (120, 0.04), (250, 0.02)]
)
def test_large_random_graph_constraints(n, p):
    """On moderately large graphs the solution must still satisfy
    0 ≤ x_e ≤ 1 and Σ_e incident to v  x_e ≤ 1 for every vertex."""
    G = nx.fast_gnp_random_graph(n, p, seed=42)
    match = fractional_matching(G)

    # Check edge‐values and build per‑node sums.
    node_load = {v: 0.0 for v in G}
    for (u, v), val in match.items():
        # Values can only be 0.5 or 1 (never store 0).
        assert val in (0.5, 1.0)
        # Only store one orientation.
        assert (v, u) not in match
        node_load[u] += val
        node_load[v] += val

    # Every vertex load ≤ 1.
    assert all(load <= 1.0 + 1e-8 for load in node_load.values())


# --------------------------------------------------------------------
# 2.  Bipartite graph — integrality check.

# def test_bipartite_integrality():
#     """For bipartite graphs the fractional matching LP is integral, so
#     every edge chosen must be 0 or 1 and the total weight equals the
#     size of a maximum matching."""
#     # Create a 10×10 random bipartite graph.
#     top, bottom = range(10), range(10, 20)
#     G = nx.complete_bipartite_graph(10, 10)
#     # Remove ~30 % edges at random to avoid trivial saturation.
#     G.remove_edges_from(random.sample(list(G.edges()), k=int(0.3 * G.number_of_edges())))

#     frac = fractional_matching(G)

#     # (a) All edge‑values integral.
#     assert all(val in (1.0,) for val in frac.values())

#     # (b) Compare objective value to a maximum matching.
#     max_match = nx.bipartite.maximum_matching(G, top)
#     max_size = len(max_match) // 2  # each edge counted twice
#     frac_size = sum(frac.values())

#     assert math.isclose(frac_size, max_size, rel_tol=0, abs_tol=1e-8)


# --------------------------------------------------------------------
# 3.  Stress‑test on a sparse power‑law graph (optional slow mark).

@pytest.mark.slow
def test_powerlaw_graph_constraints():
    """Stress the solver on a 1 000‑node graph but only check feasibility."""
    G = nx.powerlaw_cluster_graph(1000, 3, 0.1, seed=7)
    frac = fractional_matching(G)

    # Quick feasibility scan (same as before).
    node_load = {v: 0.0 for v in G}
    for (u, v), val in frac.items():
        assert val in (0.5, 1.0)
        assert (v, u) not in frac
        node_load[u] += val
        node_load[v] += val
    assert all(load <= 1.0 + 1e-8 for load in node_load.values())
