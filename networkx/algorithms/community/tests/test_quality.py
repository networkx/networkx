"""Unit tests for the :mod:`networkx.algorithms.community.quality`
module.

"""

import pytest

import networkx as nx
from networkx import barbell_graph
from networkx.algorithms.community import (
    constant_potts_model,
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
