import math

import pytest

import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms.bipartite.cluster import cc_dot, cc_max, cc_min


def test_pairwise_bipartite_cc_functions():
    # Test functions for different kinds of bipartite clustering coefficients
    # between pairs of nodes using 3 example graphs from figure 5 p. 40
    # Latapy et al (2008)
    G1 = nx.Graph([(0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 5), (1, 6), (1, 7)])
    G2 = nx.Graph([(0, 2), (0, 3), (0, 4), (1, 3), (1, 4), (1, 5)])
    G3 = nx.Graph(
        [(0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9)]
    )
    result = {
        0: [1 / 3.0, 2 / 3.0, 2 / 5.0],
        1: [1 / 2.0, 2 / 3.0, 2 / 3.0],
        2: [2 / 8.0, 2 / 5.0, 2 / 5.0],
    }
    for i, G in enumerate([G1, G2, G3]):
        assert bipartite.is_bipartite(G)
        assert cc_dot(set(G[0]), set(G[1])) == result[i][0]
        assert cc_min(set(G[0]), set(G[1])) == result[i][1]
        assert cc_max(set(G[0]), set(G[1])) == result[i][2]


def test_star_graph():
    G = nx.star_graph(3)
    # all modes are the same
    answer = {0: 0, 1: 1, 2: 1, 3: 1}
    assert bipartite.clustering(G, mode="dot") == answer
    assert bipartite.clustering(G, mode="min") == answer
    assert bipartite.clustering(G, mode="max") == answer


def test_not_bipartite():
    with pytest.raises(nx.NetworkXError):
        bipartite.clustering(nx.complete_graph(4))


def test_bad_mode():
    with pytest.raises(nx.NetworkXError):
        bipartite.clustering(nx.path_graph(4), mode="foo")


def test_path_graph():
    G = nx.path_graph(4)
    answer = {0: 0.5, 1: 0.5, 2: 0.5, 3: 0.5}
    assert bipartite.clustering(G, mode="dot") == answer
    assert bipartite.clustering(G, mode="max") == answer
    answer = {0: 1, 1: 1, 2: 1, 3: 1}
    assert bipartite.clustering(G, mode="min") == answer


def test_average_path_graph():
    G = nx.path_graph(4)
    assert bipartite.average_clustering(G, mode="dot") == 0.5
    assert bipartite.average_clustering(G, mode="max") == 0.5
    assert bipartite.average_clustering(G, mode="min") == 1


def test_ra_clustering_davis():
    G = nx.davis_southern_women_graph()
    cc4 = round(bipartite.robins_alexander_clustering(G), 3)
    assert cc4 == 0.468


def test_ra_clustering_square():
    G = nx.path_graph(4)
    G.add_edge(0, 3)
    assert bipartite.robins_alexander_clustering(G) == 1.0


def test_ra_clustering_zero():
    G = nx.Graph()
    assert bipartite.robins_alexander_clustering(G) == 0
    G.add_nodes_from(range(4))
    assert bipartite.robins_alexander_clustering(G) == 0
    G.add_edges_from([(0, 1), (2, 3), (3, 4)])
    assert bipartite.robins_alexander_clustering(G) == 0
    G.add_edge(1, 2)
    assert bipartite.robins_alexander_clustering(G) == 0


class TestButterflies:
    @pytest.mark.parametrize("n", range(2, 6))
    @pytest.mark.parametrize("nodes", (None, [0, 1], {0, 1}, [0, 1, 2]))
    def test_complete_bipartite_graph_equipartition(self, n, nodes):
        """For the complete bipartite graph K_mn with m == n, the total number
        of butterflies == (n choose 2) ** 2 and the number of
        butterflies-per-node is (n choose 2) * (n - 1)"""
        G = nx.complete_bipartite_graph(n, n)
        butterflies = nx.bipartite.butterflies(G, nodes=nodes)

        expected_per_node = math.comb(n, 2) * (n - 1)
        nodes_expected_in_result = set(G) if nodes is None else set(nodes)
        assert set(butterflies) == nodes_expected_in_result
        assert all(v == expected_per_node for v in butterflies.values())
        if nodes is None:
            expected_total = math.comb(n, 2) ** 2
            assert sum(butterflies.values()) // 4 == expected_total

    @pytest.mark.parametrize(
        "G", [nx.empty_graph(4), nx.Graph([(0, 1)]), nx.path_graph(4), nx.star_graph(4)]
    )
    def test_no_butterflies(self, G):
        assert all(v == 0 for v in bipartite.butterflies(G).values())

    def test_two_disjoint_k22(self):
        # Expect sum of butterflies from each component
        G = nx.Graph()
        G.add_nodes_from([0, 1, 4, 5], bipartite=0)
        G.add_nodes_from([2, 3, 6, 7], bipartite=1)
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        assert sum(bipartite.butterflies(G).values()) // 4 == 2

    def test_different_sized_partitions(self):
        G = nx.complete_bipartite_graph(3, 2)
        assert sum(bipartite.butterflies(G).values()) // 4 == 3

    def test_isolated_node_zero(self):
        G = nx.complete_bipartite_graph(2, 2)
        G.add_node(99)
        assert nx.bipartite.butterflies(G) == {0: 1, 1: 1, 2: 1, 3: 1, 99: 0}

    def test_nodes_param_absent_node_ignored(self):
        # Nodes not in G are silently ignored, matching nx.triangles() behavior
        G = nx.complete_bipartite_graph(2, 2)
        bt = bipartite.butterflies(G, nodes=[0, 99])
        assert set(bt.keys()) == {0}
        assert bt[0] == 1

    def test_directed_raises(self):
        with pytest.raises(nx.NetworkXNotImplemented):
            bipartite.butterflies(nx.DiGraph([(0, 1), (1, 2)]))
