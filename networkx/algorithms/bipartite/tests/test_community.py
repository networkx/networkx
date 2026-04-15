"""Tests for bipartite community detection and quality functions."""

import pytest

import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms.bipartite.community import (
    _bipartite_modularity_delta_partial_eval_add,
    _bipartite_modularity_delta_partial_eval_remove,
)
from networkx.algorithms.community.quality import NotAPartition


class TestBipartiteModularity:
    def test_complete_bipartite_no_structure(self):
        # K_{2,2} has no community structure: every red connects to
        # every blue, so any split gives Q_B = 0.
        G = nx.complete_bipartite_graph(2, 2)
        red = {0, 1}
        communities = [{0, 2}, {1, 3}]
        assert bipartite.modularity(G, communities, red) == pytest.approx(0.0)

    def test_two_disjoint_edges(self):
        # Two disconnected edges form two perfect bipartite communities.
        G = nx.Graph([(0, 2), (1, 3)])
        red = {0, 1}
        communities = [{0, 2}, {1, 3}]
        # m = 2; each community: L_c=1, k_c=1, d_c=1
        # contribution = 1/2 - 1*1/4 = 1/4; total = 1/2
        assert bipartite.modularity(G, communities, red) == pytest.approx(0.5)

    def test_single_community(self):
        G = nx.complete_bipartite_graph(3, 4)
        red = set(range(3))
        communities = [set(G)]
        assert bipartite.modularity(G, communities, red) == pytest.approx(0.0)

    def test_singleton_communities(self):
        G = nx.complete_bipartite_graph(3, 4)
        red = set(range(3))
        communities = [{n} for n in G]
        assert bipartite.modularity(G, communities, red) == pytest.approx(0.0)

    def test_weighted(self):
        G = nx.Graph()
        G.add_edge(0, 2, weight=3)
        G.add_edge(1, 3, weight=1)
        red = {0, 1}
        communities = [{0, 2}, {1, 3}]
        # m = 4
        # {0,2}: L_c=3, k_c=3, d_c=3  -> 3/4 - 9/16 = 3/16
        # {1,3}: L_c=1, k_c=1, d_c=1  -> 1/4 - 1/16 = 3/16
        # total = 6/16 = 0.375
        assert bipartite.modularity(G, communities, red) == pytest.approx(0.375)

    def test_weight_none_ignores_attribute(self):
        G = nx.Graph()
        G.add_edge(0, 2, weight=3)
        G.add_edge(1, 3, weight=1)
        red = {0, 1}
        communities = [{0, 2}, {1, 3}]
        # With weight=None, both edges have weight 1. m = 2.
        # Each community contributes 1/2 - 1/4 = 1/4 -> total 0.5
        assert bipartite.modularity(G, communities, red, weight=None) == pytest.approx(
            0.5
        )

    def test_resolution_scales_null_model(self):
        G = nx.Graph([(0, 2), (1, 3)])
        red = {0, 1}
        communities = [{0, 2}, {1, 3}]
        q1 = bipartite.modularity(G, communities, red, resolution=1)
        q_low = bipartite.modularity(G, communities, red, resolution=0.5)
        q_high = bipartite.modularity(G, communities, red, resolution=2)
        assert q_low > q1 > q_high
        # Explicit values (m=2): per-community L_c/m - res*k_c*d_c/m^2
        # res=0.5: 2 * (1/2 - 0.5 * 1/4) = 0.75
        # res=2.0: 2 * (1/2 - 2   * 1/4) = 0
        assert q_low == pytest.approx(0.75)
        assert q_high == pytest.approx(0.0)

    def test_iterable_of_communities_is_accepted(self):
        G = nx.Graph([(0, 2), (1, 3)])
        red = {0, 1}
        communities = iter([{0, 2}, {1, 3}])
        assert bipartite.modularity(G, communities, red) == pytest.approx(0.5)

    def test_empty_graph(self):
        G = nx.Graph()
        assert bipartite.modularity(G, [], set()) == pytest.approx(0.0)

    def test_not_a_partition_raises(self):
        G = nx.complete_bipartite_graph(2, 2)
        red = {0, 1}
        # Missing node 3
        with pytest.raises(NotAPartition):
            bipartite.modularity(G, [{0, 2}, {1}], red)
        # Overlapping
        with pytest.raises(NotAPartition):
            bipartite.modularity(G, [{0, 1, 2}, {1, 3}], red)

    def test_directed_not_implemented(self):
        G = nx.DiGraph([(0, 2), (1, 3)])
        with pytest.raises(nx.NetworkXNotImplemented):
            bipartite.modularity(G, [{0, 2}, {1, 3}], {0, 1})

    def test_communities_with_single_side_contribute_zero(self):
        # A community containing only red (or only blue) nodes has L_c=0
        # and one of k_c, d_c = 0, so its contribution is 0.
        G = nx.complete_bipartite_graph(2, 2)
        red = {0, 1}
        communities = [{0, 1}, {2, 3}]
        assert bipartite.modularity(G, communities, red) == pytest.approx(0.0)

    def test_southern_women_trivial_partitions(self):
        G = nx.davis_southern_women_graph()
        women = {n for n, d in G.nodes(data=True) if d["bipartite"] == 0}
        assert bipartite.modularity(G, [set(G)], women) == pytest.approx(0.0)
        assert bipartite.modularity(G, [{n} for n in G], women) == pytest.approx(0.0)

    def test_disjoint_bipartite_components_positive(self):
        # Two disjoint K_{2,2} components; grouping each component as a
        # community gives strong bipartite modularity.
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        communities = [{0, 1, 2, 3}, {4, 5, 6, 7}]
        q = bipartite.modularity(G, communities, red)
        assert q > 0
        # Hand calc: m = 8. For each component L_c=4, k_c=4, d_c=4.
        # contribution = 4/8 - 16/64 = 0.5 - 0.25 = 0.25; total = 0.5
        assert q == pytest.approx(0.5)

    def test_random_bipartite_trivial_partitions(self):
        G = nx.bipartite.random_graph(6, 8, 0.5, seed=42)
        red = {n for n, d in G.nodes(data=True) if d["bipartite"] == 0}
        assert bipartite.modularity(G, [set(G)], red) == pytest.approx(0.0)
        assert bipartite.modularity(G, [{n} for n in G], red) == pytest.approx(0.0)

    def test_nodes_as_iterable(self):
        G = nx.complete_bipartite_graph(2, 2)
        # Pass nodes as list rather than set; function should accept any
        # iterable and convert internally.
        communities = [{0, 2}, {1, 3}]
        assert bipartite.modularity(G, communities, [0, 1]) == pytest.approx(0.0)


def _q_delta_via_full_eval(G, u, A, B, rest, red, resolution=1, weight="weight"):
    """Reference delta: compute Q_B on the before/after partitions."""
    before = [A, B] + rest
    after = [A - {u}, B | {u}] + rest
    q_before = bipartite.modularity(
        G, before, red, weight=weight, resolution=resolution
    )
    q_after = bipartite.modularity(G, after, red, weight=weight, resolution=resolution)
    return q_after - q_before


def _compute_m(G, red, weight="weight"):
    """Compute total edge weight the same way bipartite.modularity does."""
    return sum(G.degree(v, weight=weight) for v in red)


class TestBipartiteModularityDelta:
    def test_red_node_move_unweighted(self):
        # Two disjoint K_{2,2} components. Move red node 0 from its
        # community to the other.
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        A = {0, 1, 2, 3}
        B = {4, 5, 6, 7}
        u = 0  # red node
        m = _compute_m(G, red)

        q_rem = _bipartite_modularity_delta_partial_eval_remove(
            G, u, A, 1, nodes=red, m=m
        )
        q_add = _bipartite_modularity_delta_partial_eval_add(G, u, B, 1, nodes=red, m=m)
        q_delta = _q_delta_via_full_eval(G, u, A, B, [], red)
        assert q_rem + q_add == pytest.approx(q_delta)

    def test_blue_node_move_unweighted(self):
        # Same graph, move blue node 2.
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        A = {0, 1, 2, 3}
        B = {4, 5, 6, 7}
        u = 2  # blue node
        m = _compute_m(G, red)

        q_rem = _bipartite_modularity_delta_partial_eval_remove(
            G, u, A, 1, nodes=red, m=m
        )
        q_add = _bipartite_modularity_delta_partial_eval_add(G, u, B, 1, nodes=red, m=m)
        q_delta = _q_delta_via_full_eval(G, u, A, B, [], red)
        assert q_rem + q_add == pytest.approx(q_delta)

    def test_weighted_edges(self):
        G = nx.Graph()
        G.add_edge(0, 2, weight=3)
        G.add_edge(0, 3, weight=1)
        G.add_edge(1, 2, weight=2)
        G.add_edge(1, 3, weight=5)
        red = {0, 1}
        A = {0, 2}
        B = {1, 3}
        u = 0
        m = _compute_m(G, red)

        q_rem = _bipartite_modularity_delta_partial_eval_remove(
            G, u, A, 1, nodes=red, m=m
        )
        q_add = _bipartite_modularity_delta_partial_eval_add(G, u, B, 1, nodes=red, m=m)
        q_delta = _q_delta_via_full_eval(G, u, A, B, [], red)
        assert q_rem + q_add == pytest.approx(q_delta)

    def test_resolution_parameter(self):
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        A = {0, 1, 2, 3}
        B = {4, 5, 6, 7}
        u = 0
        m = _compute_m(G, red)

        for gamma in (0.5, 1.0, 2.0):
            q_rem = _bipartite_modularity_delta_partial_eval_remove(
                G, u, A, gamma, nodes=red, m=m
            )
            q_add = _bipartite_modularity_delta_partial_eval_add(
                G, u, B, gamma, nodes=red, m=m
            )
            q_delta = _q_delta_via_full_eval(G, u, A, B, [], red, resolution=gamma)
            assert q_rem + q_add == pytest.approx(q_delta)

    def test_composition_property(self):
        # Verify that remove(u, A) == -add(u, A\{u}), i.e. the remove/add
        # pair composes into the single quality_delta pattern used by #8509.
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        A = {0, 1, 2, 3}
        u = 0
        m = _compute_m(G, red)

        q_rem = _bipartite_modularity_delta_partial_eval_remove(
            G, u, A, 1, nodes=red, m=m
        )
        q_add_neg = _bipartite_modularity_delta_partial_eval_add(
            G, u, A - {u}, 1, nodes=red, m=m
        )
        assert q_rem == pytest.approx(-q_add_neg)

    def test_random_graph_all_moves(self):
        # Fuzz test: for every possible single-node move on a random
        # bipartite graph, verify the delta invariant.
        G = nx.bipartite.random_graph(6, 8, 0.5, seed=42)
        red = {n for n, d in G.nodes(data=True) if d["bipartite"] == 0}
        m = _compute_m(G, red)

        # Start with a two-community partition.
        comm_a = {n for n in G if n < 7}
        comm_b = set(G) - comm_a
        partition = [comm_a, comm_b]

        for u in G:
            if u in comm_a:
                A, B, rest = comm_a, comm_b, []
            else:
                A, B, rest = comm_b, comm_a, []

            q_rem = _bipartite_modularity_delta_partial_eval_remove(
                G, u, A, 1, nodes=red, m=m
            )
            q_add = _bipartite_modularity_delta_partial_eval_add(
                G, u, B, 1, nodes=red, m=m
            )
            q_delta = _q_delta_via_full_eval(G, u, A, B, rest, red)
            assert q_rem + q_add == pytest.approx(q_delta)
