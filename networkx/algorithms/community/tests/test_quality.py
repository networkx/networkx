"""Unit tests for the :mod:`networkx.algorithms.community.quality`
module.

"""

from typing import NamedTuple

import pytest

import networkx as nx
from networkx import barbell_graph
from networkx.algorithms.community import (
    constant_potts_model,
    map_equation,
    modularity,
    overlapping_modularity,
    partition_quality,
)
from networkx.algorithms.community.quality import (
    _quality_delta_cpm_directed,
    _quality_delta_cpm_undirected,
    inter_community_edges,
)


class TestPerformance:
    """Unit tests for the :func:`performance` function."""

    def test_bad_partition(self):
        """Tests that a poor partition has a low performance measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 4}, {2, 3, 5}]
        assert 8 / 15 == pytest.approx(partition_quality(G, partition)[1], abs=1e-7)

    def test_good_partition(self):
        """Tests that a good partition has a high performance measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 2}, {3, 4, 5}]
        assert 14 / 15 == pytest.approx(partition_quality(G, partition)[1], abs=1e-7)


class TestCoverage:
    """Unit tests for the :func:`coverage` function."""

    def test_bad_partition(self):
        """Tests that a poor partition has a low coverage measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 4}, {2, 3, 5}]
        assert 3 / 7 == pytest.approx(partition_quality(G, partition)[0], abs=1e-7)

    def test_good_partition(self):
        """Tests that a good partition has a high coverage measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 2}, {3, 4, 5}]
        assert 6 / 7 == pytest.approx(partition_quality(G, partition)[0], abs=1e-7)


def test_modularity():
    G = nx.barbell_graph(3, 0)
    C = [{0, 1, 4}, {2, 3, 5}]
    assert (-16 / (14**2)) == pytest.approx(modularity(G, C), abs=1e-7)
    C = [{0, 1, 2}, {3, 4, 5}]
    assert (35 * 2) / (14**2) == pytest.approx(modularity(G, C), abs=1e-7)

    n = 1000
    G = nx.erdos_renyi_graph(n, 0.09, seed=42, directed=True)
    C = [set(range(n // 2)), set(range(n // 2, n))]
    assert 0.00017154251389292754 == pytest.approx(modularity(G, C), abs=1e-7)

    G = nx.margulis_gabber_galil_graph(10)
    mid_value = G.number_of_nodes() // 2
    nodes = list(G.nodes)
    C = [set(nodes[:mid_value]), set(nodes[mid_value:])]
    assert 0.13 == pytest.approx(modularity(G, C), abs=1e-7)

    G = nx.DiGraph()
    G.add_edges_from([(2, 1), (2, 3), (3, 4)])
    C = [{1, 2}, {3, 4}]
    assert 2 / 9 == pytest.approx(modularity(G, C), abs=1e-7)


def _validate_quality_delta(G, u, A, B, quality_func, delta_func, resolution):
    all_nodes = set(G.nodes)
    C = all_nodes - (A.union(B))
    if C:
        P = [A, B, C]
    else:
        P = [A, B]

    A_prime = A - {u}
    B_prime = B.union({u})

    if C:
        P_prime = [A_prime, B_prime, C]
    else:
        P_prime = [A_prime, B_prime]

    Q_before = quality_func(G, P, resolution)
    Q_after = quality_func(G, P_prime, resolution)
    Q_delta = Q_after - Q_before

    Q_fast_delta_rem = delta_func(G, {u}, A, resolution)
    Q_fast_delta_add = delta_func(G, {u}, B, resolution)
    Q_fast_delta = Q_fast_delta_add - Q_fast_delta_rem

    return (Q_delta - Q_fast_delta) < 0.000000001


def test_cpm_delta_undirected():
    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4}, {5}]
    nx.set_node_attributes(G, 1, "node_weight")
    nx.set_edge_attributes(G, 1, "weight")
    r = 0.5

    u = 0
    A = partition[0]
    B = partition[1]

    assert _validate_quality_delta(
        G, u, A, B, constant_potts_model, _quality_delta_cpm_undirected, r
    )


def test_cpm_delta_directed():
    G = nx.barbell_graph(3, 0)
    G = nx.to_directed(G)

    partition = [{0, 1, 2}, {3, 4, 5}]
    nx.set_node_attributes(G, 1, "node_weight")
    nx.set_edge_attributes(G, 1, "weight")
    r = 0.5

    u = 0
    A = partition[0]
    B = partition[1]
    r = 0.5

    assert _validate_quality_delta(
        G, u, A, B, constant_potts_model, _quality_delta_cpm_directed, r
    )


def test_cpm_delta_undirected_weights():
    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    G.nodes[0]["node_weight"] = 1
    G.nodes[1]["node_weight"] = 2
    G.nodes[2]["node_weight"] = 3
    G.nodes[3]["node_weight"] = 4
    G.nodes[4]["node_weight"] = 5
    G.nodes[5]["node_weight"] = 6

    # the add and remove functions should cancel terms which come from
    # self-loops and hence we add some weighted self-loops
    for i in range(6):
        G.add_edge(i, i)
        G.edges[(i, i)]["weight"] = i + 2

    G.edges[(0, 1)]["weight"] = 1
    G.edges[(0, 2)]["weight"] = 2
    G.edges[(1, 2)]["weight"] = 3
    G.edges[(2, 3)]["weight"] = 4
    G.edges[(3, 4)]["weight"] = 5
    G.edges[(3, 5)]["weight"] = 6
    G.edges[(4, 5)]["weight"] = 7

    u = 0
    A = partition[0]
    B = partition[1]
    r = 0.5

    assert _validate_quality_delta(
        G, u, A, B, constant_potts_model, _quality_delta_cpm_undirected, r
    )


def test_cpm_delta_directed_weights():
    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    G.nodes[0]["node_weight"] = 1
    G.nodes[1]["node_weight"] = 2
    G.nodes[2]["node_weight"] = 3
    G.nodes[3]["node_weight"] = 4
    G.nodes[4]["node_weight"] = 5
    G.nodes[5]["node_weight"] = 6

    # the add and remove functions should cancel terms which come from
    # self-loops and hence we add some weighted self-loops
    for i in range(6):
        G.add_edge(i, i)
        G.edges[(i, i)]["weight"] = i + 2

    G = nx.to_directed(G)

    G.edges[(0, 1)]["weight"] = 1
    G.edges[(0, 2)]["weight"] = 2
    G.edges[(1, 2)]["weight"] = 3
    G.edges[(2, 3)]["weight"] = 4
    G.edges[(3, 4)]["weight"] = 5
    G.edges[(3, 5)]["weight"] = 6
    G.edges[(4, 5)]["weight"] = 7

    G.edges[(1, 0)]["weight"] = 1
    G.edges[(2, 0)]["weight"] = 2
    G.edges[(2, 1)]["weight"] = 3
    G.edges[(3, 2)]["weight"] = 4
    G.edges[(4, 3)]["weight"] = 5
    G.edges[(5, 3)]["weight"] = 6
    G.edges[(5, 4)]["weight"] = 7

    u = 0
    A = partition[0]
    B = partition[1]
    r = 0.5

    assert _validate_quality_delta(
        G, u, A, B, constant_potts_model, _quality_delta_cpm_directed, r
    )


def test_cpm_undirected():
    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    gamma = 0.1
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert 3 - (gamma * 3**2) / 2 + 3 - (gamma * 3**2) / 2 == cpm

    partition = [{0, 1, 2}, {3, 4, 5}]
    gamma = 1
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert 3 - (gamma * 3**2) / 2 + 3 - (gamma * 3**2) / 2 == cpm

    partition = [{i} for i in G]
    gamma = 1
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert -6 * gamma / 2 == cpm

    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    G.nodes[0]["foo"] = 2
    G.nodes[1]["foo"] = 3
    G.nodes[2]["foo"] = 4
    G.nodes[3]["foo"] = 2
    G.nodes[4]["foo"] = 8
    G.nodes[5]["foo"] = 10

    G.edges[(0, 1)]["bar"] = 1
    G.edges[(0, 2)]["bar"] = 2
    G.edges[(1, 2)]["bar"] = 3
    G.edges[(2, 3)]["bar"] = 4
    G.edges[(3, 4)]["bar"] = 3
    G.edges[(3, 5)]["bar"] = 2
    G.edges[(4, 5)]["bar"] = 1

    gamma = 1
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert 3 - (gamma * 3**2) / 2 + 3 - (gamma * 3**2) / 2 == cpm
    cpm = constant_potts_model(
        G, partition, weight="bar", node_weight="foo", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert 6 - (gamma * 9**2) / 2 + 6 - (gamma * 20**2) / 2 == cpm

    gamma = 0.2
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert 3 - (gamma * 3**2) / 2 + 3 - (gamma * 3**2) / 2 - cpm < 0.000000000001

    cpm = constant_potts_model(
        G, partition, weight="bar", node_weight="foo", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert 6 - (gamma * 9**2) / 2 + 6 - (gamma * 20**2) / 2 == cpm

    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    G.nodes[0]["node_weight"] = 2
    G.nodes[1]["node_weight"] = 3
    G.nodes[2]["node_weight"] = 4
    G.nodes[3]["node_weight"] = 2
    G.nodes[4]["node_weight"] = 8
    G.nodes[5]["node_weight"] = 10

    G.edges[(0, 1)]["weight"] = 1
    G.edges[(0, 2)]["weight"] = 2
    G.edges[(1, 2)]["weight"] = 3
    G.edges[(2, 3)]["weight"] = 4
    G.edges[(3, 4)]["weight"] = 3
    G.edges[(3, 5)]["weight"] = 2
    G.edges[(4, 5)]["weight"] = 1

    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert 6 - (gamma * 9**2) / 2 + 6 - (gamma * 20**2) / 2 == cpm


def test_modularity_resolution():
    G = nx.barbell_graph(3, 0)
    C = [{0, 1, 4}, {2, 3, 5}]
    assert modularity(G, C) == pytest.approx(3 / 7 - 100 / 14**2)
    gamma = 2
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx(3 / 7 - gamma * 100 / 14**2)
    gamma = 0.2
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx(3 / 7 - gamma * 100 / 14**2)

    C = [{0, 1, 2}, {3, 4, 5}]
    assert modularity(G, C) == pytest.approx(6 / 7 - 98 / 14**2)
    gamma = 2
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx(6 / 7 - gamma * 98 / 14**2)
    gamma = 0.2
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx(6 / 7 - gamma * 98 / 14**2)

    G = nx.barbell_graph(5, 3)
    C = [frozenset(range(5)), frozenset(range(8, 13)), frozenset(range(5, 8))]
    gamma = 1
    result = modularity(G, C, resolution=gamma)
    # This C is maximal for gamma=1:  modularity = 0.518229
    assert result == pytest.approx((22 / 24) - gamma * (918 / (48**2)))
    gamma = 2
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx((22 / 24) - gamma * (918 / (48**2)))
    gamma = 0.2
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx((22 / 24) - gamma * (918 / (48**2)))

    C = [{0, 1, 2, 3}, {9, 10, 11, 12}, {5, 6, 7}, {4}, {8}]
    gamma = 1
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx((14 / 24) - gamma * (598 / (48**2)))
    gamma = 2.5
    result = modularity(G, C, resolution=gamma)
    # This C is maximal for gamma=2.5:  modularity = -0.06553819
    assert result == pytest.approx((14 / 24) - gamma * (598 / (48**2)))
    gamma = 0.2
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx((14 / 24) - gamma * (598 / (48**2)))

    C = [frozenset(range(8)), frozenset(range(8, 13))]
    gamma = 1
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx((23 / 24) - gamma * (1170 / (48**2)))
    gamma = 2
    result = modularity(G, C, resolution=gamma)
    assert result == pytest.approx((23 / 24) - gamma * (1170 / (48**2)))
    gamma = 0.3
    result = modularity(G, C, resolution=gamma)
    # This C is maximal for gamma=0.3:  modularity = 0.805990
    assert result == pytest.approx((23 / 24) - gamma * (1170 / (48**2)))


class TestOverlappingModularity:
    """Tests for :func:`overlapping_modularity` (Shen et al.'s EQ)."""

    def test_equivalence_with_modularity_on_partition(self):
        # When the cover is actually a partition, EQ must equal Q.
        G = nx.barbell_graph(3, 0)
        partition = [{0, 1, 2}, {3, 4, 5}]
        assert overlapping_modularity(G, partition) == pytest.approx(
            modularity(G, partition)
        )

    def test_equivalence_on_karate_club(self):
        G = nx.karate_club_graph()
        partition = list(nx.community.label_propagation_communities(G))
        assert overlapping_modularity(G, partition) == pytest.approx(
            modularity(G, partition)
        )

    def test_triangle_two_overlapping_communities(self):
        # Triangle (0,1,2), cover [{0,1}, {1,2}]. Hand-calculated EQ = -1/6.
        G = nx.cycle_graph(3)
        cover = [{0, 1}, {1, 2}]
        assert overlapping_modularity(G, cover) == pytest.approx(-1 / 6)

    def test_triangle_all_pairs_cover(self):
        # Triangle, cover [{0,1}, {1,2}, {0,2}]. Hand-calculated EQ = -1/12.
        G = nx.cycle_graph(3)
        cover = [{0, 1}, {1, 2}, {0, 2}]
        assert overlapping_modularity(G, cover) == pytest.approx(-1 / 12)

    def test_single_community_is_zero(self):
        # Shen page 4: EQ = 0 when all nodes are in a single community.
        G = nx.karate_club_graph()
        assert overlapping_modularity(G, [set(G)]) == pytest.approx(0.0)

    def test_resolution_monotonicity(self):
        # For a fixed cover, higher resolution -> lower EQ
        # (the null-model term grows with gamma).
        G = nx.barbell_graph(3, 0)
        cover = [{0, 1, 2}, {3, 4, 5}]
        eq_low = overlapping_modularity(G, cover, resolution=0.5)
        eq_one = overlapping_modularity(G, cover, resolution=1)
        eq_high = overlapping_modularity(G, cover, resolution=2)
        assert eq_low > eq_one > eq_high

    def test_kclique_communities_integration(self):
        # Output of k_clique_communities should feed directly to
        # overlapping_modularity without raising.
        G = nx.complete_graph(5)
        H = nx.relabel_nodes(nx.complete_graph(5), {i: i + 3 for i in range(5)})
        G.add_edges_from(H.edges())
        cover = list(nx.community.k_clique_communities(G, 4))
        # All nodes should be covered (each appears in some maximal clique
        # community), so this should not raise.
        eq = overlapping_modularity(G, cover)
        assert isinstance(eq, float)

    def test_invalid_cover_raises(self):
        G = nx.path_graph(4)
        with pytest.raises(nx.NetworkXError):
            overlapping_modularity(G, [{0, 1}])  # nodes 2, 3 uncovered

    def test_directed_not_implemented(self):
        G = nx.DiGraph([(0, 1), (1, 2)])
        with pytest.raises(nx.NetworkXNotImplemented):
            overlapping_modularity(G, [{0, 1, 2}])

    def test_empty_graph(self):
        assert overlapping_modularity(nx.Graph(), []) == 0.0

    def test_weighted_reduces_to_unweighted_when_uniform(self):
        # When all edge weights are 1, the weighted result matches the
        # unweighted-default result.
        G = nx.cycle_graph(4)
        for u, v in G.edges():
            G[u][v]["weight"] = 1.0
        cover = [{0, 1, 2}, {2, 3, 0}]
        assert overlapping_modularity(G, cover) == pytest.approx(
            overlapping_modularity(G, cover, weight=None)
        )

    def test_weight_none_ignores_edge_weights(self):
        # weight=None must treat the graph as unweighted regardless of
        # actual edge weights.
        G = nx.cycle_graph(4)
        for u, v in G.edges():
            G[u][v]["weight"] = 99.0
        Gp = nx.cycle_graph(4)  # no weights
        cover = [{0, 1, 2}, {2, 3, 0}]
        assert overlapping_modularity(G, cover, weight=None) == pytest.approx(
            overlapping_modularity(Gp, cover, weight=None)
        )

    def test_resolution_partition_matches_modularity(self):
        # On a partition input, EQ(gamma) must equal Q(gamma) for any gamma.
        G = nx.barbell_graph(3, 0)
        partition = [{0, 1, 2}, {3, 4, 5}]
        for gamma in (0.3, 1.0, 2.5):
            assert overlapping_modularity(
                G, partition, resolution=gamma
            ) == pytest.approx(modularity(G, partition, resolution=gamma))

    def test_weighted_triangle_hand_calc(self):
        # Triangle with non-uniform edge weights:
        #   (0,1)=2, (1,2)=3, (0,2)=1
        # Weighted degrees: k_0=3, k_1=5, k_2=4; 2m=12.
        # Cover [{0,1}, {1,2}]; O_0=1, O_1=2, O_2=1.
        # Community {0,1}: L_tilde=2/(1*2)=1, k_tilde=3+5/2=5.5
        #   contribution = 2*1/12 - (5.5/12)**2 = -25/576
        # Community {1,2}: L_tilde=3/(2*1)=1.5, k_tilde=5/2+4=6.5
        #   contribution = 2*1.5/12 - (6.5/12)**2 = -25/576
        # EQ = -50/576 = -25/288.
        G = nx.Graph()
        G.add_weighted_edges_from([(0, 1, 2), (1, 2, 3), (0, 2, 1)])
        cover = [{0, 1}, {1, 2}]
        assert overlapping_modularity(G, cover) == pytest.approx(-25 / 288)

    def test_multigraph(self):
        # Round-tripping a simple graph through MultiGraph gives the same
        # EQ; adding a parallel edge then changes the value, confirming
        # parallel edges contribute to both the null-model and the
        # overlap-discounted edge sums.
        G = nx.barbell_graph(3, 0)
        H = nx.MultiGraph(G)
        cover = [{0, 1, 2, 3}, {2, 3, 4, 5}]  # bridge nodes 2, 3 overlap

        assert overlapping_modularity(H, cover) == pytest.approx(
            overlapping_modularity(G, cover)
        )

        H.add_edge(0, 1)  # parallel edge in H, no equivalent in G
        assert overlapping_modularity(H, cover) != pytest.approx(
            overlapping_modularity(G, cover)
        )


def test_inter_community_edges_with_digraphs():
    G = nx.complete_graph(2, create_using=nx.DiGraph())
    partition = [{0}, {1}]
    assert inter_community_edges(G, partition) == 2

    G = nx.complete_graph(10, create_using=nx.DiGraph())
    partition = [{0}, {1, 2}, {3, 4, 5}, {6, 7, 8, 9}]
    assert inter_community_edges(G, partition) == 70

    G = nx.cycle_graph(4, create_using=nx.DiGraph())
    partition = [{0, 1}, {2, 3}]
    assert inter_community_edges(G, partition) == 2


def test_map_equation_single_module_equals_visit_rate_entropy():
    """With every node in one module, the two-level map equation reduces to
    the entropy of the node visit rates. For the undirected path 0-1-2 the
    (weighted) degrees are 1, 2, 1 so the stationary visit rates are
    1/4, 1/2, 1/4, giving H = -(2*0.25*log2(0.25) + 0.5*log2(0.5)) = 1.5 bits.
    """
    G = nx.path_graph(3)  # edges (0,1), (1,2)
    codelength = map_equation(G, [{0, 1, 2}])
    assert codelength == pytest.approx(1.5)


def test_map_equation_two_triangles_hand_calculated():
    """The smallest clean two-module example: two triangles joined by a single
    edge. With one triangle per module the walker crosses between modules only
    on the bridge, so the index codebook is used at rate
    q = 2/14 = 1/7 with two equally likely symbols: index term (1/7) * 1 bit.
    Each module codebook is used at rate 4/7 (visit rate 1/2 plus exit rate
    1/14) with symbol frequencies 1/8 (exit), 1/4, 1/4, 3/8:
    L = 1/7 + 2 * (4/7) * H(1/8, 1/4, 1/4, 3/8) = 2.320730 bits."""
    G = nx.barbell_graph(3, 0)  # two triangles joined by one edge
    partition = [{0, 1, 2}, {3, 4, 5}]
    assert map_equation(G, partition) == pytest.approx(2.320730, abs=1e-5)


def test_map_equation_not_a_partition():
    """`communities` must partition the nodes. An uncovered node, an
    overlapping node and a node listed twice within one community all raise,
    matching what modularity rejects for the same input."""
    G = nx.barbell_graph(3, 0)
    missing_node = [{0, 1, 2}, {3, 4}]
    overlapping = [{0, 1, 2, 3}, {3, 4, 5}]
    duplicated = [[0, 0, 1, 2], [3, 4, 5]]
    for communities in (missing_node, overlapping, duplicated):
        with pytest.raises(nx.NetworkXError, match="not a valid partition"):
            map_equation(G, communities)
        with pytest.raises(nx.NetworkXError, match="not a valid partition"):
            modularity(G, communities)


def test_map_equation_undirected_self_loop_known_value():
    """A self-loop is one transition that keeps the walker in place, so it
    counts once toward the visit rate (Infomap's undirected normalization
    ``2*sum_w - sum_self``). For the 4-cycle 0-1-2-3-0 with a weight-3 self-loop
    on node 0, the visit rates are 5/11, 2/11, 2/11, 2/11, so in a single module
    the codelength is their entropy. Value validated against the C++ reference.
    """
    G = nx.Graph()
    G.add_weighted_edges_from([(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1), (0, 0, 3)])
    assert map_equation(G, [{0, 1, 2, 3}]) == pytest.approx(1.858555, abs=1e-5)


def test_map_equation_directed_without_flow_is_zero():
    """A directed graph whose links carry no weight has no recorded flow, so
    there is nothing to code and the codelength is 0. Uniform visit rates would
    give log2(n) instead. Value validated against the C++ reference, which
    reports 0 both with no links at all and with a single zero-weight link.
    """
    G = nx.DiGraph()
    G.add_nodes_from([0, 1])
    assert map_equation(G, [set(G)]) == 0.0

    G.add_edge(0, 1, weight=0.0)
    assert map_equation(G, [set(G)]) == 0.0


# --- Ground-truth codelengths -------------------------------------------------
#
# Each case records a graph, a partition, and the codelength the reference C++
# Infomap reports for it. networkx is checked against the recorded number, so
# these tests run whether or not the `infomap` package is installed and do not
# move when it changes. A second, skippable test re-derives the same numbers
# from the C++ implementation, which is what catches drift between the two.


class _MapEquationCase(NamedTuple):
    id: str
    build: object  # () -> graph
    communities: list
    codelength: float
    weight: str | None = "weight"
    teleportation_probability: float = 0.15
    directed: bool = False
    num_trials: int = 1


def _directed_cycles():
    return nx.DiGraph([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3), (0, 4)])


def _undirected_self_loops():
    G = nx.Graph()
    G.add_weighted_edges_from(
        [(0, 1, 1), (1, 2, 1), (2, 0, 1), (3, 4, 1), (4, 5, 1), (5, 3, 1), (2, 3, 1)]
        + [(0, 0, 2), (4, 4, 3)]
    )
    return G


_MAP_EQUATION_CASES = [
    _MapEquationCase(
        "karate",
        nx.karate_club_graph,
        [
            {0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21},
            {4, 5, 6, 10, 16},
            {8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33},
        ],
        4.087423158819623,
    ),
    _MapEquationCase(
        "directed-cycles",
        _directed_cycles,
        [{0, 1, 2}, {3, 4, 5}],
        1.77289125575288,
        directed=True,
    ),
    _MapEquationCase(
        "directed-dangling",
        lambda: nx.DiGraph([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (0, 4)]),
        [{0, 1, 2}, {3, 4}],
        1.9850494902284956,
        directed=True,
    ),
    _MapEquationCase(
        # A growing DAG: enter and exit flow differ per module, which is what
        # exercises the directed index term.
        "gnc-dag",
        lambda: nx.gnc_graph(40, seed=3),
        [
            {0, 1, 3, 4, 6, 10, 13, 20, 23, 32},
            {2, 26},
            {5, 27, 36, 38},
            {7, 9, 15, 16, 19, 21, 24, 25, 28, 31, 35, 37, 39},
            {8, 11, 14},
            {12, 17, 22, 33},
            {18, 29},
            {30, 34},
        ],
        2.3493511266833416,
        weight=None,
        directed=True,
        num_trials=50,
    ),
    _MapEquationCase(
        "directed-teleportation-0.5",
        _directed_cycles,
        [{0, 1, 2}, {3, 4, 5}],
        2.008314883625276,
        teleportation_probability=0.5,
        directed=True,
    ),
    _MapEquationCase(
        "undirected-self-loops",
        _undirected_self_loops,
        [{0, 1, 2}, {3, 4, 5}],
        2.1133480671115863,
    ),
    _MapEquationCase(
        "directed-self-loops",
        lambda: nx.DiGraph(
            [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3), (0, 4), (0, 0)]
            + [(4, 4)]
        ),
        [{0, 1, 2}, {3, 4, 5}],
        1.6879974334326313,
        weight=None,
        directed=True,
    ),
]


def _cpp_codelength(case):
    """Codelength the reference C++ Infomap reports for `case`, or skip."""
    infomap = pytest.importorskip("infomap", minversion="2.14")
    G = case.build()
    network = infomap.Network()
    for u, v, wt in G.edges(data=case.weight, default=1):
        network.add_link(u, v, wt)
    return network.run(
        options=infomap.Options(
            two_level=True,
            silent=True,
            seed=42,
            directed=case.directed,
            num_trials=case.num_trials,
            teleportation_probability=case.teleportation_probability,
        )
    ).codelength


@pytest.mark.parametrize("case", _MAP_EQUATION_CASES, ids=lambda c: c.id)
def test_map_equation_matches_ground_truth(case):
    """map_equation reproduces the recorded codelength. Runs with or without
    the `infomap` package, so a break here is a break in networkx."""
    if case.directed:
        pytest.importorskip("scipy")  # directed flow uses nx.pagerank
    codelength = map_equation(
        case.build(),
        case.communities,
        weight=case.weight,
        teleportation_probability=case.teleportation_probability,
    )
    assert codelength == pytest.approx(case.codelength, abs=1e-9)


@pytest.mark.parametrize("case", _MAP_EQUATION_CASES, ids=lambda c: c.id)
def test_map_equation_ground_truth_matches_cpp(case):
    """The recorded codelengths still agree with the reference C++ Infomap.
    Skipped when the `infomap` package is missing, so an unavailable or changed
    upstream stops guarding against drift rather than failing the suite."""
    assert _cpp_codelength(case) == pytest.approx(case.codelength, abs=1e-9)
