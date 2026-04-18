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


# ---------------------------------------------------------------------------
# Tests for butterflies()
# ---------------------------------------------------------------------------


class TestButterflies:
    """Tests for bipartite.butterflies()."""

    def make(self, left, right, edges):
        G = nx.Graph()
        G.add_nodes_from(left, bipartite=0)
        G.add_nodes_from(right, bipartite=1)
        G.add_edges_from(edges)
        return G

    # -- total count (sum // 4) ---------------------------------------------

    def test_k22_total(self):
        G = self.make([0, 1], [2, 3], [(0, 2), (0, 3), (1, 2), (1, 3)])
        assert sum(bipartite.butterflies(G).values()) // 4 == 1

    def test_k33_total(self):
        G = nx.complete_bipartite_graph(3, 3)
        assert sum(bipartite.butterflies(G).values()) // 4 == 9

    def test_k44_total(self):
        G = nx.complete_bipartite_graph(4, 4)
        assert sum(bipartite.butterflies(G).values()) // 4 == 36

    def test_k55_total(self):
        G = nx.complete_bipartite_graph(5, 5)
        assert sum(bipartite.butterflies(G).values()) // 4 == 100

    def test_empty_graph(self):
        G = self.make([0, 1], [2, 3], [])
        assert all(v == 0 for v in bipartite.butterflies(G).values())

    def test_single_edge(self):
        G = self.make([0], [1], [(0, 1)])
        assert sum(bipartite.butterflies(G).values()) == 0

    def test_path_no_butterfly(self):
        G = self.make([0, 1], [2, 3], [(0, 2), (1, 2), (1, 3)])
        assert sum(bipartite.butterflies(G).values()) // 4 == 0

    def test_star_no_butterfly(self):
        G = self.make([0], [1, 2, 3, 4], [(0, 1), (0, 2), (0, 3), (0, 4)])
        assert sum(bipartite.butterflies(G).values()) // 4 == 0

    def test_two_disjoint_k22(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1, 4, 5], bipartite=0)
        G.add_nodes_from([2, 3, 6, 7], bipartite=1)
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        assert sum(bipartite.butterflies(G).values()) // 4 == 2

    def test_three_shared_neighbours(self):
        G = self.make(
            [0, 1, 2],
            [3, 4],
            [(0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4)],
        )
        assert sum(bipartite.butterflies(G).values()) // 4 == 3

    # -- per-node counts ----------------------------------------------------

    def test_k22_per_node(self):
        G = self.make([0, 1], [2, 3], [(0, 2), (0, 3), (1, 2), (1, 3)])
        assert bipartite.butterflies(G) == {0: 1, 1: 1, 2: 1, 3: 1}

    def test_k33_per_node(self):
        G = nx.complete_bipartite_graph(3, 3)
        bt = bipartite.butterflies(G)
        assert all(v == 6 for v in bt.values())

    def test_per_node_sum_divisible_by_four(self):
        # Each butterfly contributes to exactly 4 nodes, so sum is divisible by 4.
        G = nx.complete_bipartite_graph(4, 4)
        bt = bipartite.butterflies(G)
        assert sum(bt.values()) % 4 == 0

    def test_isolated_node_zero(self):
        G = self.make([0, 1, 99], [2, 3], [(0, 2), (0, 3), (1, 2), (1, 3)])
        assert bipartite.butterflies(G)[99] == 0

    def test_all_nodes_in_result(self):
        G = self.make([0, 1], [2, 3], [(0, 2), (0, 3), (1, 2), (1, 3)])
        assert set(bipartite.butterflies(G).keys()) == set(G.nodes())

    # -- nodes= parameter ---------------------------------------------------

    def test_nodes_param_keys(self):
        G = self.make([0, 1], [2, 3], [(0, 2), (0, 3), (1, 2), (1, 3)])
        bt = bipartite.butterflies(G, nodes=[0, 1])
        assert set(bt.keys()) == {0, 1}

    def test_nodes_param_correct_count(self):
        # nodes= filters the output dict but does not affect the computation.
        # Counts must match the full-graph result, matching nx.triangles() convention.
        G = self.make([0, 1], [2, 3], [(0, 2), (0, 3), (1, 2), (1, 3)])
        bt_full = bipartite.butterflies(G)
        bt_sub = bipartite.butterflies(G, nodes=[0, 1])
        assert bt_sub[0] == bt_full[0]
        assert bt_sub[1] == bt_full[1]

    def test_nodes_param_absent_node_ignored(self):
        # A node not in G should be silently ignored, matching nx.triangles() behaviour.
        G = self.make([0, 1], [2, 3], [(0, 2), (0, 3), (1, 2), (1, 3)])
        bt = bipartite.butterflies(G, nodes=[0, 99])
        assert set(bt.keys()) == {0}
        assert bt[0] == 1

    # -- error handling -----------------------------------------------------

    def test_not_bipartite_raises(self):
        with pytest.raises(nx.NetworkXError):
            bipartite.butterflies(nx.complete_graph(4))

    def test_disconnected_no_raise(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1, 4, 5], bipartite=0)
        G.add_nodes_from([2, 3, 6, 7], bipartite=1)
        G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3)])
        G.add_edges_from([(4, 6), (4, 7), (5, 6), (5, 7)])
        bt = bipartite.butterflies(G)  # must not raise AmbiguousSolution
        assert sum(bt.values()) // 4 == 2
