"""
Testing the :mod:`networkx.algorithms.community.community_formation` module.

Which is the implementation of the Social Aware Assignment of Passengers in Ridesharing
The social aware assignment problem belongs to the field of community formation, which is an important research branch 
within multiagent systems. It analyses the outcome that results when a set of agents is partitioned into communities.
Actually, Match_And_Merge model is a special case of simple Additively Separable Hedonic Games (ASHGs).

Which was described in the article:
Levinger C., Hazon N., Azaria A. Social Aware Assignment of Passengers in Ridesharing. - 2022, https://github.com/VictoKu1/ResearchAlgorithmsCourse1/raw/main/Article/2022%2C%20Chaya%20Amos%20Noam%2C%20Socially%20aware%20assignment%20of%20passengers%20in%20ride%20sharing.pdf.

The match_and_merge algorithm is based on the pseudocode from the article
which is written (as well as the tests) by Victor Kushnir.
"""
import math
import random

import pytest

import networkx as nx
from networkx.algorithms.community.community_formation import match_and_merge


def small_chain_graph():
    G = nx.Graph()
    list_of_edges = [(1, 2), (2, 3), (3, 4), (4, 5), (4, 6)]
    G.add_edges_from(list_of_edges)
    return G


def clique_graph_of_size_3():
    G = nx.Graph()
    list_of_edges = [(1, 2), (2, 3), (3, 1)]
    G.add_edges_from(list_of_edges)
    return G


class Test_community_formation:
    def test_empty_graph_returns_empty_list(self):
        G_empty = nx.Graph()
        assert match_and_merge(G_empty, k=0) == []

    def test_small_chain_graph_with_k_4_returns_correct_partition(self):
        G_1 = small_chain_graph()
        assert match_and_merge(G_1, k=4) == [[1, 2], [3, 4, 5, 6]]

    def test_small_chain_graph_with_k_3_returns_correct_partition(self):
        G_1 = small_chain_graph()
        assert match_and_merge(G_1, k=3) == [[1, 2], [3, 4, 6], [5]]

    def test_small_chain_graph_with_k_2_returns_correct_partition(self):
        G_1 = small_chain_graph()
        assert match_and_merge(G_1, k=2) == [[1, 2], [3, 4], [5], [6]]

    def test_clique_graph_of_size_3_with_k_3_returns_correct_partition(self):
        G_clique_3 = clique_graph_of_size_3()
        assert match_and_merge(G_clique_3, k=3) == [[1, 2, 3]]

    def test_approximation_ratio(self):
        # For each n between 5 and 15, generate a clique graph with n nodes and check for 5<k≤15
        for n in range(5, 69):
            G = nx.complete_graph(n)
            P = match_and_merge(G, 2)
            value_of_P = sum(
                len([(u, v) for u, v in G.edges() if u in S and v in S]) for S in P
            )
            optimal_value = len(nx.algorithms.max_weight_matching(G, weight=1))
            approximation_ratio = value_of_P / optimal_value
            assert approximation_ratio >= 0.99999

    def test_clique_graph_with_k_in_range_every_node_in_exactly_one_partition(self):
        # Check that every node is in exactly one partition
        for n in range(5, 15):
            G = nx.complete_graph(n)
            for k in range(5, 15):
                if k <= n:
                    P = match_and_merge(G, k)
                    assert [len([p for p in P if n in p]) == 1 for n in G.nodes()]

    def test_clique_graph_with_k_in_range_number_of_partitions_at_most_ceil_n_2(self):
        # Check that the number of partitions is at most ceil(n/2)
        for n in range(5, 15):
            G = nx.complete_graph(n)
            for k in range(5, 15):
                if k <= n:
                    P = match_and_merge(G, k)
                    assert len(P) <= math.ceil(G.number_of_nodes() / 2)

    def test_k_greater_than_n_raises_error(self):
        # Check that it raises an error when k>n
        for n in range(5, 15):
            G = nx.complete_graph(n)
            for k in range(5, 15):
                if k > n:
                    with pytest.raises(nx.NetworkXError):
                        match_and_merge(G, k)

    def test_random_graph_with_k_in_range_returns_correct_partition(self):
        # For each n between 5 and 15 (inclusive), generate a random graph with n nodes and check for 5<k≤15
        for n in range(5, 15):
            p = 0.5
            G = nx.gnp_random_graph(n, p)
            for k in range(5, 15):
                if k <= n:
                    P = match_and_merge(G, k)
                    assert [len(p) <= k for p in P]

    def test_random_graph_with_k_in_range_every_node_in_exactly_one_partition(self):
        # Check that every node is in exactly one partition
        for n in range(5, 15):
            p = 0.5
            G = nx.gnp_random_graph(n, p)
            for k in range(5, 15):
                if k <= n:
                    P = match_and_merge(G, k)
                    assert [len([p for p in P if n in p]) == 1 for n in G.nodes()]

    def test_maximum_matching(self):
        # Check that the maximum matching is a partition
        for n in range(5, 15):
            p = 0.5
            G = nx.gnp_random_graph(n, p)
            P = [tuple(p) for p in match_and_merge(G, 2) if len(p) > 1]
            G_test = nx.Graph()
            G_test.add_nodes_from(sorted((G.nodes()), reverse=True))
            G_test.add_edges_from(sorted((G.edges()), reverse=True))
            assert len(P) == len(
                [
                    tuple(sorted(p))
                    for p in sorted(nx.max_weight_matching(G_test, weight=1))
                ]
            )

    def test_partition_is_a_social_aware_assignment_check_size_of_subset(self):
        for n in range(5, 15):
            p = 0.5
            G = nx.gnp_random_graph(n, p)
            for k in range(5, n):
                P = match_and_merge(G, k)
                # Check that every partition has at most k nodes
                assert [len(p) <= k for p in P]

    def test_partition_is_a_social_aware_assignment_V_P(self):
        for n in range(5, 15):
            p = 0.5
            G = nx.gnp_random_graph(n, p)
            P = match_and_merge(G, 2)
            # Check that the value of V_P is maximized
            V_P = 0
            for p in P:
                for i in p:
                    for j in p:
                        if G.has_edge(i, j):
                            V_P += 1
            assert V_P >= len(
                [tuple(sorted(p)) for p in sorted(nx.max_weight_matching(G, weight=1))]
            )

    def test_disconnected_components_weighted_graph_with_k_5_returns_correct_partition(
        self,
    ):
        # Check that the partition of graph G is correct for a disconnected graph
        G = small_chain_graph()
        G.add_edges_from([(7, 8), (8, 9), (9, 7)])
        # Add random weights to the edges
        for u, v in G.edges():
            G[u][v]["weight"] = random.randint(1, 205)
        assert match_and_merge(G, k=5) == [[1, 2], [3, 4, 5, 6], [7, 8, 9]]
