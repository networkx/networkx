import math

import pytest

import networkx as nx

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def mean_cycle_weight(G, cycle, weight="weight"):
    """
    Compute mean edge weight for a closed cycle [a, b, ..., a].
    For MultiDiGraph uses the minimum-weight parallel edge (mirrors karp internals).
    """
    if len(cycle) < 2:
        raise ValueError("Cycle too short")
    total = 0.0
    for u, v in zip(cycle, cycle[1:]):
        if isinstance(G, nx.MultiDiGraph):
            total += min(d.get(weight, 0) for d in G[u][v].values())
        else:
            total += G[u][v].get(weight, 0)
    return total / (len(cycle) - 1)


def assert_valid_cycle(G, cycle):
    """Assert that cycle is closed and every edge exists in G."""
    assert len(cycle) >= 2, "Cycle must have at least 2 nodes"
    assert cycle[0] == cycle[-1], "Cycle must be closed (first == last node)"
    for u, v in zip(cycle, cycle[1:]):
        assert G.has_edge(u, v), f"Edge ({u}, {v}) not in graph"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestKarp:
    # --- Input validation ---------------------------------------------------

    def test_raises_on_empty_graph(self):
        """karp raises NetworkXError on a graph with no nodes."""
        G = nx.DiGraph()
        with pytest.raises(nx.NetworkXError, match="Empty graph"):
            nx.karp(G)

    def test_raises_on_undirected_graph(self):
        """karp raises TypeError for undirected graphs."""
        G = nx.Graph()
        G.add_edge(0, 1, weight=-1)
        with pytest.raises(TypeError):
            nx.karp(G)

    def test_raises_when_no_negative_mean_cycle(self):
        """karp raises NetworkXError when all cycles have non-negative mean."""
        G = nx.DiGraph()
        G.add_weighted_edges_from([(0, 1, 1), (1, 2, 1), (2, 0, 1)])
        with pytest.raises(nx.NetworkXError, match="No negative mean cycle found"):
            nx.karp(G)

    def test_raises_on_dag_no_cycle(self):
        """karp raises when there are no cycles at all (DAG)."""
        G = nx.DiGraph()
        G.add_weighted_edges_from([(0, 1, -5), (1, 2, -5)])
        with pytest.raises(nx.NetworkXError):
            nx.karp(G)

    # --- Correctness: cycle properties --------------------------------------

    def test_negative_self_loop(self):
        """A negative self-loop is a valid negative mean cycle."""
        G = nx.DiGraph()
        G.add_edge("A", "A", weight=-2)
        cycle = nx.karp(G)
        assert_valid_cycle(G, cycle)
        assert mean_cycle_weight(G, cycle) < 0

    def test_simple_two_node_negative_cycle(self):
        """A 2-node cycle with negative total weight is detected."""
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=-3)
        G.add_edge(1, 0, weight=1)
        cycle = nx.karp(G)
        assert_valid_cycle(G, cycle)
        assert mean_cycle_weight(G, cycle) < 0

    def test_cycle_is_closed(self):
        """Returned cycle always starts and ends at the same node."""
        G = nx.DiGraph()
        G.add_weighted_edges_from([(0, 1, -1), (1, 2, -1), (2, 0, -1)])
        cycle = nx.karp(G)
        assert cycle[0] == cycle[-1]

    def test_all_edges_exist_in_graph(self):
        """Every consecutive pair in the returned cycle must be an edge in G."""
        G = nx.DiGraph()
        G.add_weighted_edges_from([(0, 1, 2), (1, 2, -10), (2, 0, 1)])
        cycle = nx.karp(G)
        assert_valid_cycle(G, cycle)

    # --- Minimum mean selection ---------------------------------------------

    def test_prefers_more_negative_mean_among_multiple_cycles(self):
        """
        With two disjoint negative cycles, karp returns the one with smaller mean.
        Cycle 1: (a->b->a) mean = (-2 + 0) / 2 = -1.0
        Cycle 2: (x->y->x) mean = (-10 + 1) / 2 = -4.5  ← more negative
        """
        G = nx.DiGraph()
        G.add_edge("a", "b", weight=-2)
        G.add_edge("b", "a", weight=0)
        G.add_edge("x", "y", weight=-10)
        G.add_edge("y", "x", weight=1)
        cycle = nx.karp(G)
        assert_valid_cycle(G, cycle)
        mu = mean_cycle_weight(G, cycle)
        assert math.isclose(mu, -4.5, rel_tol=0, abs_tol=1e-9)

    @pytest.mark.parametrize(
        "neg_weight,pos_weight,expected_mean",
        [
            (-4, 2, -1.0),
            (-10, 4, -3.0),
            (-1, 0, -0.5),
        ],
    )
    def test_mean_value_correctness(self, neg_weight, pos_weight, expected_mean):
        """Mean of the found cycle matches the analytically computed value."""
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=neg_weight)
        G.add_edge(1, 0, weight=pos_weight)
        cycle = nx.karp(G)
        assert_valid_cycle(G, cycle)
        mu = mean_cycle_weight(G, cycle)
        assert math.isclose(mu, expected_mean, rel_tol=0, abs_tol=1e-9)

    # --- MultiDiGraph support -----------------------------------------------

    def test_multigraph_uses_min_weight_parallel_edge(self):
        """
        For MultiDiGraph with parallel edges u->v, karp picks the min-weight one.
        Edges: u->v (weight=5), u->v (weight=-10), v->u (weight=1)
        Effective cycle mean: (-10 + 1) / 2 = -4.5
        """
        MG = nx.MultiDiGraph()
        MG.add_edge("u", "v", weight=5)
        MG.add_edge("u", "v", weight=-10)
        MG.add_edge("v", "u", weight=1)
        cycle = nx.karp(MG)
        # Validate against the original multigraph
        assert_valid_cycle(MG, cycle)
        mu = mean_cycle_weight(MG, cycle)
        assert math.isclose(mu, -4.5, rel_tol=0, abs_tol=1e-9)

    def test_multigraph_single_negative_edge(self):
        """MultiDiGraph with one negative and one positive parallel edge finds negative cycle."""
        MG = nx.MultiDiGraph()
        MG.add_edge(0, 1, weight=100)
        MG.add_edge(0, 1, weight=-5)
        MG.add_edge(1, 0, weight=2)
        cycle = nx.karp(MG)
        assert_valid_cycle(MG, cycle)
        assert mean_cycle_weight(MG, cycle) < 0

    # --- Custom weight attribute --------------------------------------------

    def test_custom_weight_attribute(self):
        """karp respects a non-default weight attribute name."""
        G = nx.DiGraph()
        G.add_edge(0, 1, cost=-3)
        G.add_edge(1, 0, cost=-1)
        cycle = nx.karp(G, weight="cost")
        assert_valid_cycle(G, cycle)
        mu = mean_cycle_weight(G, cycle, weight="cost")
        assert mu < 0

    # --- Graph structure edge cases -----------------------------------------

    def test_larger_cycle(self):
        """karp detects a negative cycle in a longer path-structured graph."""
        G = nx.DiGraph()
        # Positive path: 0→1→2→3→4
        G.add_weighted_edges_from([(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1)])
        # Negative back-edge that creates a cycle: 4→2 (mean of 2→3→4→2 = (1+1-5)/3)
        G.add_edge(4, 2, weight=-5)
        cycle = nx.karp(G)
        assert_valid_cycle(G, cycle)
        assert mean_cycle_weight(G, cycle) < 0

    @pytest.mark.parametrize("n", [3, 5, 10])
    def test_negative_n_cycle(self, n):
        """A directed n-cycle with all-negative weights is always detected."""
        G = nx.cycle_graph(n, create_using=nx.DiGraph())
        for u, v in G.edges():
            G[u][v]["weight"] = -1
        cycle = nx.karp(G)
        assert_valid_cycle(G, cycle)
        assert mean_cycle_weight(G, cycle) < 0
