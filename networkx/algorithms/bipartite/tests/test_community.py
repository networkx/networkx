"""Tests for bipartite community detection and quality functions."""

import pytest

import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms.bipartite.community import (
    _bipartite_modularity_merge_delta,
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

    def test_multigraph(self):
        # MultiGraph with parallel edges: each parallel edge is counted
        # separately in both the degree sums and L_c. Two parallel (0, 2)
        # edges plus one (1, 3). Degrees: deg(0)=2, deg(1)=1, deg(2)=2,
        # deg(3)=1. m = 3.
        #   {0, 2}: L=2, k=2, d=2 -> 2/3 - 4/9 = 2/9
        #   {1, 3}: L=1, k=1, d=1 -> 1/3 - 1/9 = 2/9
        # Total Q = 4/9.
        G = nx.MultiGraph()
        G.add_edges_from([(0, 2), (0, 2), (1, 3)])
        red = {0, 1}
        communities = [{0, 2}, {1, 3}]
        assert bipartite.modularity(G, communities, red) == pytest.approx(4 / 9)


def _compute_m(G, red, weight="weight"):
    """Compute total edge weight the same way bipartite.modularity does."""
    return sum(G.degree(v, weight=weight) for v in red)


def _set_bipartite_degree_attrs(G, red, weight="weight"):
    """Set red_degree / blue_degree attributes on a leaf bipartite graph.

    Red nodes get red_degree = deg(v), blue_degree = 0.
    Blue nodes get red_degree = 0, blue_degree = deg(v).
    """
    for v in G:
        deg = G.degree(v, weight=weight)
        if v in red:
            G.nodes[v]["red_degree"] = deg
            G.nodes[v]["blue_degree"] = 0
        else:
            G.nodes[v]["red_degree"] = 0
            G.nodes[v]["blue_degree"] = deg


def _q_merge_delta_via_full_eval(G, C_a, C_b, rest, red, resolution=1, weight="weight"):
    """Reference merge delta: compute Q_B before/after merging C_a and C_b."""
    before = [C_a, C_b] + rest
    after = [C_a | C_b] + rest
    q_before = bipartite.modularity(
        G, before, red, weight=weight, resolution=resolution
    )
    q_after = bipartite.modularity(G, after, red, weight=weight, resolution=resolution)
    return q_after - q_before


class TestBipartiteModularityMergeDelta:
    def test_singleton_move_red(self):
        # Moving red node 0 from A to B on two disjoint K_{2,2}.
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        _set_bipartite_degree_attrs(G, red)
        m = _compute_m(G, red)
        u = 0
        B = {4, 5, 6, 7}
        q_merge = _bipartite_modularity_merge_delta(G, {u}, B, 1, m=m)
        q_delta = _q_merge_delta_via_full_eval(G, {u}, B, [{1, 2, 3}], red)
        assert q_merge == pytest.approx(q_delta)

    def test_singleton_move_blue(self):
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        _set_bipartite_degree_attrs(G, red)
        m = _compute_m(G, red)
        u = 2  # blue
        B = {4, 5, 6, 7}
        q_merge = _bipartite_modularity_merge_delta(G, {u}, B, 1, m=m)
        q_delta = _q_merge_delta_via_full_eval(G, {u}, B, [{0, 1, 3}], red)
        assert q_merge == pytest.approx(q_delta)

    def test_two_k22_merge(self):
        # Two disjoint K_{2,2}. Merging the two components drops Q_B from
        # 0.5 to 0 (merged partition is a single community covering the
        # whole graph).
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        _set_bipartite_degree_attrs(G, red)
        m = _compute_m(G, red)
        A = {0, 1, 2, 3}
        B = {4, 5, 6, 7}

        q_merge = _bipartite_modularity_merge_delta(G, A, B, 1, m=m)
        q_delta = _q_merge_delta_via_full_eval(G, A, B, [], red)
        assert q_merge == pytest.approx(q_delta)
        assert q_merge == pytest.approx(-0.5)

    def test_weighted_merge(self):
        G = nx.Graph()
        G.add_edge(0, 2, weight=3)
        G.add_edge(0, 3, weight=1)
        G.add_edge(1, 2, weight=2)
        G.add_edge(1, 3, weight=5)
        red = {0, 1}
        _set_bipartite_degree_attrs(G, red)
        m = _compute_m(G, red)
        A = {0, 2}
        B = {1, 3}

        q_merge = _bipartite_modularity_merge_delta(G, A, B, 1, m=m)
        q_delta = _q_merge_delta_via_full_eval(G, A, B, [], red)
        assert q_merge == pytest.approx(q_delta)

    def test_resolution_parameter(self):
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        red = {0, 1, 4, 5}
        _set_bipartite_degree_attrs(G, red)
        m = _compute_m(G, red)
        A = {0, 1, 2, 3}
        B = {4, 5, 6, 7}

        for gamma in (0.5, 1.0, 2.0):
            q_merge = _bipartite_modularity_merge_delta(G, A, B, gamma, m=m)
            q_delta = _q_merge_delta_via_full_eval(G, A, B, [], red, resolution=gamma)
            assert q_merge == pytest.approx(q_delta)

    def test_random_graph_all_pairs(self):
        # Fuzz test: every ordered pair of three communities on a random
        # bipartite graph, verified against the full quality function.
        G = nx.bipartite.random_graph(6, 8, 0.5, seed=42)
        red = {n for n, d in G.nodes(data=True) if d["bipartite"] == 0}
        _set_bipartite_degree_attrs(G, red)
        m = _compute_m(G, red)

        all_nodes = sorted(G)
        third = len(all_nodes) // 3
        C1 = set(all_nodes[:third])
        C2 = set(all_nodes[third : 2 * third])
        C3 = set(all_nodes[2 * third :])

        pairs = [(C1, C2, [C3]), (C1, C3, [C2]), (C2, C3, [C1])]
        for A, B, rest in pairs:
            q_merge = _bipartite_modularity_merge_delta(G, A, B, 1, m=m)
            q_delta = _q_merge_delta_via_full_eval(G, A, B, rest, red)
            assert q_merge == pytest.approx(q_delta)

    def test_multigraph(self):
        # Parallel edges must be reflected in both the red/blue degree
        # attributes and in E(A, B). Edges: (0, 2) x 2, (1, 2), (1, 3).
        # Degrees: deg(0)=2, deg(1)=2, deg(2)=3, deg(3)=1. m = 4.
        # Merging A={0, 3} with B={1, 2}:
        #   k_A = 2, d_A = 1, k_B = 2, d_B = 3
        #   E(A, B) = 2 (parallel 0-2) + 1 (1-3) = 3
        # merge_delta = 3/4 - (2*3 + 2*1)/16 = 3/4 - 1/2 = 1/4.
        G = nx.MultiGraph()
        G.add_edges_from([(0, 2), (0, 2), (1, 2), (1, 3)])
        red = {0, 1}
        _set_bipartite_degree_attrs(G, red)
        m = _compute_m(G, red)

        A = {0, 3}
        B = {1, 2}
        q_merge = _bipartite_modularity_merge_delta(G, A, B, 1, m=m)
        q_delta = _q_merge_delta_via_full_eval(G, A, B, [], red)
        assert q_merge == pytest.approx(q_delta)
        assert q_merge == pytest.approx(0.25)

    def test_aggregated_supernode_graph(self):
        # Construct an aggregated graph where each super-node carries the
        # red/blue degree sums of its constituent community, and self-loops
        # encode intra-community edge weights. Verify merge_delta on the
        # aggregate equals merge_delta on the original for the same merge
        # operation.
        #
        # Original: two disjoint K_{2,2} on nodes {0,1,2,3} and {4,5,6,7},
        # with one extra cross-edge (1, 6) to give the merge a nonzero
        # E(A, B).
        G = nx.Graph()
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        G.add_edge(1, 6)  # cross edge so E(A, B) != 0
        red = {0, 1, 4, 5}
        _set_bipartite_degree_attrs(G, red)
        m = _compute_m(G, red)

        A = {0, 1, 2, 3}
        B = {4, 5, 6, 7}
        q_merge_leaf = _bipartite_modularity_merge_delta(G, A, B, 1, m=m)

        # Aggregated graph: community A -> super-node "a", B -> "b".
        # k_a = sum of red degrees in A, etc. Self-loop weight on "a" is
        # the intra-A edge weight total (L_A); likewise for "b". Edge
        # ("a", "b") has weight E(A, B).
        k_A = sum(G.nodes[v]["red_degree"] for v in A)
        d_A = sum(G.nodes[v]["blue_degree"] for v in A)
        k_B = sum(G.nodes[v]["red_degree"] for v in B)
        d_B = sum(G.nodes[v]["blue_degree"] for v in B)
        L_A = sum(1 for u, v in G.edges() if u in A and v in A)
        L_B = sum(1 for u, v in G.edges() if u in B and v in B)
        E_AB = sum(
            1 for u, v in G.edges() if (u in A and v in B) or (u in B and v in A)
        )

        H = nx.Graph()
        H.add_node("a", red_degree=k_A, blue_degree=d_A)
        H.add_node("b", red_degree=k_B, blue_degree=d_B)
        H.add_edge("a", "a", weight=L_A)
        H.add_edge("b", "b", weight=L_B)
        H.add_edge("a", "b", weight=E_AB)

        # m is preserved across aggregation.
        q_merge_agg = _bipartite_modularity_merge_delta(H, {"a"}, {"b"}, 1, m=m)

        assert q_merge_leaf == pytest.approx(q_merge_agg)
