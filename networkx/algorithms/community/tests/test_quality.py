"""Unit tests for the :mod:`networkx.algorithms.community.quality`
module.

"""

import pytest

import networkx as nx
from networkx import barbell_graph
from networkx.algorithms.community import (
    constant_potts_model,
    modularity,
    partition_quality,
)
from networkx.algorithms.community.quality import (
    _cpm_delta_partial_eval_add,
    _cpm_delta_partial_eval_remove,
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


def test_cpm():
    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    gamma = 0.1
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert (3 - gamma * 3**2) + (3 - gamma * 3**2) == cpm

    partition = [{0, 1, 2}, {3, 4, 5}]
    gamma = 1
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert (3 - gamma * 3**2) + (3 - gamma * 3**2) == cpm

    partition = [{i} for i in G]
    gamma = 1
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert -6 * gamma == cpm

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
    assert (3 - gamma * 3**2) + (3 - gamma * 3**2) == cpm
    cpm = constant_potts_model(
        G, partition, weight="bar", node_weight="foo", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert (6 - gamma * 9**2) + (6 - gamma * 20**2) == cpm

    gamma = 0.2
    cpm = constant_potts_model(
        G, partition, weight="weight", node_weight="node_weight", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert (3 - gamma * 3**2) + (3 - gamma * 3**2) == cpm

    cpm = constant_potts_model(
        G, partition, weight="bar", node_weight="foo", resolution=gamma
    )
    # compare cpm against the value computed by hand using the
    # formula stated in the definition of constant_potts_model
    assert (6 - gamma * 9**2) + (6 - gamma * 20**2) == cpm

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
    assert (6 - gamma * 9**2) + (6 - gamma * 20**2) == cpm


def test_cpm_add_remove_total_cost():
    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    nx.set_node_attributes(G, 1, "node_weight")
    nx.set_edge_attributes(G, 1, "weight")
    r = 0.5

    u = 0
    A = partition[0]
    B = partition[1]
    qA = _cpm_delta_partial_eval_remove(G, node=u, community=A, resolution=r)
    qB = _cpm_delta_partial_eval_add(G, node=u, community=B, resolution=r)

    q_after = constant_potts_model(
        G,
        [A - {u}, B.union({u})],
        weight="weight",
        node_weight="node_weight",
        resolution=r,
    )
    q_before = constant_potts_model(
        G, [A, B], weight="weight", node_weight="node_weight", resolution=r
    )
    q_delta = q_after - q_before
    assert qA + qB == q_delta


def test_cpm_add_remove_total_cost_weights():
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

    r = 0.5

    u = 0
    A = partition[0]
    B = partition[1]
    qA = _cpm_delta_partial_eval_remove(G, node=u, community=A, resolution=r)
    qB = _cpm_delta_partial_eval_add(G, node=u, community=B, resolution=r)

    q_after = constant_potts_model(
        G,
        [A - {u}, B.union({u})],
        weight="weight",
        node_weight="node_weight",
        resolution=r,
    )
    q_before = constant_potts_model(
        G, [A, B], weight="weight", node_weight="node_weight", resolution=r
    )
    q_delta = q_after - q_before
    assert qA + qB == q_delta


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
