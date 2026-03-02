import math

import pytest

import networkx as nx

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_edge(G, u, v, capacity, weight):
    G.add_edge(u, v, capacity=capacity, weight=weight)


def total_flow_out(flow_dict, s):
    """Sum of flow leaving source s."""
    return sum(flow_dict.get(s, {}).values())


def assert_flow_conservation(flow_dict, G, s, t):
    """
    For every node except s and t: flow_in == flow_out.
    For s: net flow out >= 0.
    For t: net flow in >= 0.
    """
    for node in G.nodes():
        if node in (s, t):
            continue
        flow_in = sum(flow_dict.get(u, {}).get(node, 0) for u in G.nodes())
        flow_out = sum(flow_dict.get(node, {}).values())
        assert flow_in == flow_out, (
            f"Flow conservation violated at node {node}: in={flow_in}, out={flow_out}"
        )


def assert_capacity_respected(flow_dict, G, capacity="capacity"):
    """Every edge flow must be >= 0 and <= its capacity."""
    for u, v, data in G.edges(data=True):
        f = flow_dict.get(u, {}).get(v, 0)
        assert f >= 0, f"Negative flow on edge ({u},{v}): {f}"
        assert f <= data[capacity], (
            f"Flow {f} exceeds capacity {data[capacity]} on edge ({u},{v})"
        )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCycleCancellingInputValidation:
    """Tests for parameter validation — all should raise before doing any work."""

    def test_raises_on_undirected_graph(self):
        G = nx.Graph()
        G.add_edge(0, 1, capacity=5, weight=1)
        with pytest.raises(TypeError, match="directed"):
            nx.cycle_cancelling(G, 0, 1)

    def test_raises_on_missing_source(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, capacity=5, weight=1)
        with pytest.raises(ValueError, match="Source"):
            nx.cycle_cancelling(G, 99, 1)

    def test_raises_on_missing_target(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, capacity=5, weight=1)
        with pytest.raises(ValueError, match="Target"):
            nx.cycle_cancelling(G, 0, 99)

    def test_raises_on_missing_capacity_attribute(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=1)  # no capacity
        G.add_node(1)
        with pytest.raises(ValueError, match="capacity"):
            nx.cycle_cancelling(G, 0, 1)

    def test_raises_on_missing_weight_attribute(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, capacity=5)  # no weight
        G.add_node(1)
        with pytest.raises(ValueError, match="weight"):
            nx.cycle_cancelling(G, 0, 1)

    def test_raises_on_negative_capacity(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, capacity=-1, weight=1)
        G.add_node(1)
        with pytest.raises(ValueError, match="capacity"):
            nx.cycle_cancelling(G, 0, 1)

    def test_raises_on_non_callable_negative_cycle_func(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, capacity=5, weight=1)
        with pytest.raises(nx.NetworkXError, match="callable"):
            nx.cycle_cancelling(G, 0, 1, negative_cycle_func="not_a_function")


class TestCycleCancellingReturnStructure:
    """Tests that verify the shape and type of what is returned."""

    def test_returns_tuple_of_two(self):
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=10, weight=2)
        result = nx.cycle_cancelling(G, 0, 1)
        assert isinstance(result, tuple) and len(result) == 2

    def test_flow_dict_is_dict(self):
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=10, weight=2)
        flow_dict, _ = nx.cycle_cancelling(G, 0, 1)
        assert isinstance(flow_dict, dict)

    def test_min_cost_is_numeric(self):
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=10, weight=2)
        _, cost = nx.cycle_cancelling(G, 0, 1)
        assert isinstance(cost, int | float)

    def test_min_cost_non_negative(self):
        """With non-negative weights, min cost must be >= 0."""
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=5, weight=3)
        make_edge(G, 0, 1, capacity=3, weight=7)
        _, cost = nx.cycle_cancelling(G, 0, 1)
        assert cost >= 0


class TestCycleCancellingFlowProperties:
    """Tests that verify flow conservation and capacity constraints."""

    def test_flow_conservation_simple(self):
        """On a simple path graph, flow is conserved at every internal node."""
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=10, weight=1)
        make_edge(G, 1, 2, capacity=10, weight=1)
        flow_dict, _ = nx.cycle_cancelling(G, 0, 2)
        assert_flow_conservation(flow_dict, G, 0, 2)

    def test_capacity_respected_simple(self):
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=5, weight=2)
        flow_dict, _ = nx.cycle_cancelling(G, 0, 1)
        assert_capacity_respected(flow_dict, G)

    def test_flow_conservation_diamond(self):
        """Diamond graph: two parallel paths from s to t."""
        G = nx.DiGraph()
        make_edge(G, "s", "a", capacity=4, weight=1)
        make_edge(G, "s", "b", capacity=6, weight=2)
        make_edge(G, "a", "t", capacity=4, weight=1)
        make_edge(G, "b", "t", capacity=6, weight=2)
        flow_dict, _ = nx.cycle_cancelling(G, "s", "t")
        assert_flow_conservation(flow_dict, G, "s", "t")
        assert_capacity_respected(flow_dict, G)

    def test_flow_conservation_with_internal_nodes(self):
        """Multi-hop path: every intermediate node must conserve flow."""
        G = nx.DiGraph()
        for u, v in [(0, 1), (1, 2), (2, 3), (3, 4)]:
            make_edge(G, u, v, capacity=8, weight=1)
        flow_dict, _ = nx.cycle_cancelling(G, 0, 4)
        assert_flow_conservation(flow_dict, G, 0, 4)
        assert_capacity_respected(flow_dict, G)


class TestCycleCancellingCostCorrectness:
    """Tests that verify the minimum cost is computed correctly."""

    def test_single_edge_cost(self):
        """
        Single edge s→t with capacity 5, weight 3.
        Max flow = 5, min cost = 5 * 3 = 15.
        """
        G = nx.DiGraph()
        make_edge(G, "s", "t", capacity=5, weight=3)
        flow_dict, cost = nx.cycle_cancelling(G, "s", "t")
        assert cost == 15
        assert flow_dict["s"]["t"] == 5

    def test_two_parallel_paths_picks_cheaper(self):
        """
        s→a→t (weight 1+1=2 per unit) vs s→b→t (weight 10+10=20 per unit).
        Both have capacity 5. Algorithm must route as much as possible through cheap path.
        Min cost flow = 5*2 + 5*20 = 110  (max flow uses both).
        """
        G = nx.DiGraph()
        make_edge(G, "s", "a", capacity=5, weight=1)
        make_edge(G, "a", "t", capacity=5, weight=1)
        make_edge(G, "s", "b", capacity=5, weight=10)
        make_edge(G, "b", "t", capacity=5, weight=10)
        _, cost = nx.cycle_cancelling(G, "s", "t")
        # Total flow = 10 (max), cheapest split: all 5 via a, all 5 via b
        assert cost == 5 * 2 + 5 * 20

    def test_bottleneck_capacity_limits_flow(self):
        """
        s→m (cap=2) → t (cap=10). Bottleneck is 2.
        Cost = 2 * (weight_sm + weight_mt).
        """
        G = nx.DiGraph()
        make_edge(G, "s", "m", capacity=2, weight=3)
        make_edge(G, "m", "t", capacity=10, weight=4)
        flow_dict, cost = nx.cycle_cancelling(G, "s", "t")
        assert flow_dict.get("s", {}).get("m", 0) == 2
        assert cost == 2 * (3 + 4)

    def test_zero_capacity_edge_carries_no_flow(self):
        """An edge with capacity=0 should carry 0 flow."""
        G = nx.DiGraph()
        make_edge(G, "s", "a", capacity=0, weight=1)
        make_edge(G, "s", "t", capacity=5, weight=2)
        flow_dict, cost = nx.cycle_cancelling(G, "s", "t")
        assert flow_dict.get("s", {}).get("a", 0) == 0
        assert cost == 5 * 2

    def test_cost_equals_sum_of_flow_times_weight(self):
        """Verify returned cost matches manually computed flow * weight sum."""
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=3, weight=2)
        make_edge(G, 0, 2, capacity=4, weight=5)
        make_edge(G, 1, 3, capacity=3, weight=1)
        make_edge(G, 2, 3, capacity=4, weight=2)
        flow_dict, cost = nx.cycle_cancelling(G, 0, 3)
        manual_cost = sum(
            flow_dict.get(u, {}).get(v, 0) * G[u][v]["weight"]
            for u, v in G.edges()
            if flow_dict.get(u, {}).get(v, 0) > 0
        )
        assert cost == manual_cost


class TestCycleCancellingKnownAnswers:
    """
    Tests against textbook examples with known optimal costs.
    These are the most important correctness tests for a contribution.
    """

    def test_simple_known_optimal(self):
        """
        s→a (cap=10, w=2), a→t (cap=10, w=3).
        Only path: cost = 10 * (2+3) = 50.
        """
        G = nx.DiGraph()
        make_edge(G, "s", "a", capacity=10, weight=2)
        make_edge(G, "a", "t", capacity=10, weight=3)
        _, cost = nx.cycle_cancelling(G, "s", "t")
        assert cost == 50

    def test_two_node_graph(self):
        """Minimal graph: just s and t connected by one edge."""
        G = nx.DiGraph()
        make_edge(G, "s", "t", capacity=7, weight=4)
        flow_dict, cost = nx.cycle_cancelling(G, "s", "t")
        assert flow_dict["s"]["t"] == 7
        assert cost == 28

    @pytest.mark.parametrize("cap,w", [(1, 1), (5, 3), (10, 7), (100, 2)])
    def test_single_edge_parametrized(self, cap, w):
        """Single edge cost always equals capacity * weight."""
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=cap, weight=w)
        _, cost = nx.cycle_cancelling(G, 0, 1)
        assert cost == cap * w


class TestCycleCancellingCustomParameters:
    """Tests for optional parameters: weight, capacity, negative_cycle_func."""

    def test_custom_weight_attribute(self):
        """cycle_cancelling respects a custom weight attribute name."""
        G = nx.DiGraph()
        G.add_edge(0, 1, capacity=5, cost=3)
        _, cost = nx.cycle_cancelling(G, 0, 1, weight="cost")
        assert cost == 15

    def test_custom_capacity_attribute(self):
        """cycle_cancelling respects a custom capacity attribute name."""
        G = nx.DiGraph()
        G.add_edge(0, 1, cap=4, weight=2)
        _, cost = nx.cycle_cancelling(G, 0, 1, capacity="cap")
        assert cost == 8

    def test_custom_negative_cycle_func_is_called(self):
        """A custom negative_cycle_func is actually used when provided."""
        called = {"count": 0}
        from karp import karp as real_karp

        def tracking_karp(G, *args, **kwargs):
            called["count"] += 1
            return real_karp(G, *args, **kwargs)

        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=5, weight=1)
        nx.cycle_cancelling(G, 0, 1, negative_cycle_func=tracking_karp)
        assert called["count"] >= 1

    def test_default_negative_cycle_func_is_karp(self):
        """When no negative_cycle_func is provided, karp is used by default."""
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=3, weight=2)
        # Should not raise — karp is the default and handles this graph
        flow_dict, cost = nx.cycle_cancelling(G, 0, 1)
        assert cost == 6


class TestCycleCancellingEdgeCases:
    """Edge cases and boundary conditions."""

    def test_large_capacity_single_edge(self):
        """Large capacity should not cause overflow or correctness issues."""
        G = nx.DiGraph()
        make_edge(G, 0, 1, capacity=10_000, weight=1)
        _, cost = nx.cycle_cancelling(G, 0, 1)
        assert cost == 10_000

    def test_string_node_labels(self):
        """Graph with string node labels works correctly."""
        G = nx.DiGraph()
        make_edge(G, "source", "sink", capacity=5, weight=3)
        flow_dict, cost = nx.cycle_cancelling(G, "source", "sink")
        assert cost == 15

    def test_integer_and_float_weights(self):
        """Float weights are handled without error."""
        G = nx.DiGraph()
        G.add_edge(0, 1, capacity=4, weight=1.5)
        _, cost = nx.cycle_cancelling(G, 0, 1)
        assert math.isclose(cost, 6.0, rel_tol=1e-9)
