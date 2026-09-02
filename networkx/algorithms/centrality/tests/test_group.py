"""
Tests for Group Centrality Measures
"""

import pytest

import networkx as nx


class TestGroupBetweennessCentrality:
    def test_group_betweenness_single_node(self):
        """
        Group betweenness centrality for single node group
        """
        G = nx.path_graph(5)
        C = [1]
        b = nx.group_betweenness_centrality(
            G, C, weight=None, normalized=False, endpoints=False
        )
        b_answer = 3.0
        assert b == b_answer

    def test_group_betweenness_guard_against_keyerror(self):
        """
        Check for KeyErrors in D[u][v] inside group_betweenness_centrality
        """
        G = nx.path_graph(6, create_using=nx.DiGraph)
        # y_in_Dx is enforced by the loop bounds. (KeyError if not enforced)
        # Also checks v_in_Dy, y_in_Dv, x_in_Dv and v_in_Dx. Note: do not need x_in_Dy
        assert 2 == nx.group_betweenness_centrality(G, [2, 3, 4], normalized=False)

    def test_group_betweenness_with_endpoints(self):
        """
        Group betweenness centrality for single node group
        """
        G = nx.path_graph(5)
        C = [1]
        b = nx.group_betweenness_centrality(
            G, C, weight=None, normalized=False, endpoints=True
        )
        b_answer = 7.0
        assert b == b_answer

    def test_group_betweenness_normalized(self):
        """
        Group betweenness centrality for group with more than
        1 node and normalized
        """
        G = nx.path_graph(5)
        C = [1, 3]
        b = nx.group_betweenness_centrality(
            G, C, weight=None, normalized=True, endpoints=False
        )
        b_answer = 1.0
        assert b == b_answer

    def test_two_group_betweenness_value_zero(self):
        """
        Group betweenness centrality value of 0
        """
        G = nx.cycle_graph(7)
        C = [[0, 1, 6], [0, 1, 5]]
        b = nx.group_betweenness_centrality(G, C, weight=None, normalized=False)
        b_answer = [0.0, 3.0]
        assert b == b_answer

    def test_group_betweenness_value_zero(self):
        """
        Group betweenness centrality value of 0
        """
        G = nx.cycle_graph(6)
        C = [0, 1, 5]
        b = nx.group_betweenness_centrality(G, C, weight=None, normalized=False)
        b_answer = 0.0
        assert b == b_answer

    def test_group_betweenness_many_groups(self):
        """
        Group betweenness centrality with single graph over many groups.
        Also checks that singleton groups equal regular betweenness values.
        """
        G = nx.path_graph(5)
        G.remove_edge(0, 1)

        bc = nx.betweenness_centrality(G, normalized=False)
        gbc_singletons = [0, 0, 2, 2, 0]
        assert list(bc.values()) == gbc_singletons

        many_groups = [[node] for node in G]
        results = nx.group_betweenness_centrality(G, many_groups, normalized=False)
        assert results == gbc_singletons

    def test_group_betweenness_disconnected_graph(self):
        """
        Group betweenness centrality in a disconnected graph
        """
        G = nx.path_graph(5)
        G.remove_edge(0, 1)
        C = [1]
        b = nx.group_betweenness_centrality(G, C, weight=None, normalized=False)
        b_answer = 0.0
        assert b == b_answer

    def test_group_betweenness_many_groups_directed_graph(self):
        """
        Group betweenness centrality with directed graph over many groups.
        Also checks that singleton groups equal regular betweenness values.
        """
        G = nx.path_graph(5, create_using=nx.DiGraph)
        G.remove_edge(0, 1)

        bc = nx.betweenness_centrality(G, normalized=False)
        gbc_singletons = [0, 0, 2, 2, 0]
        assert list(bc.values()) == gbc_singletons

        many_groups = [[node] for node in G]
        results = nx.group_betweenness_centrality(G, many_groups, normalized=False)
        assert results == gbc_singletons

    def test_group_betweenness_node_not_in_graph(self):
        """
        Node(s) in C not in graph, raises NodeNotFound exception
        """
        with pytest.raises(nx.NodeNotFound):
            nx.group_betweenness_centrality(nx.path_graph(5), [4, 7, 8])

    def test_group_betweenness_directed_weighted(self):
        """
        Group betweenness centrality in a directed and weighted graph
        """
        G = nx.DiGraph()
        G.add_edge(1, 0, weight=1)
        G.add_edge(0, 2, weight=2)
        G.add_edge(1, 2, weight=3)
        G.add_edge(3, 1, weight=4)
        G.add_edge(2, 3, weight=1)
        G.add_edge(4, 3, weight=6)
        G.add_edge(2, 4, weight=7)
        C = [1, 2]
        b = nx.group_betweenness_centrality(G, C, weight="weight", normalized=False)
        b_answer = 5.0
        assert b == b_answer

    def test_group_betweenness_disconnected_directed_graph(self):
        """
        GBC check of disconnected directed graph (from gh-8666 comment)
        """
        # unweighted version
        G = nx.DiGraph([(1, 0), (1, 5), (2, 0), (2, 3), (3, 2), (5, 3)])
        G.add_node(4)
        C = [3, 4, 2]
        assert 1 == nx.group_betweenness_centrality(G, C, normalized=False)

        # weighted version
        G = nx.DiGraph()
        G.add_node(4)
        G.add_weighted_edges_from(
            [(1, 0, 2), (1, 5, 4), (2, 0, 1), (2, 3, 5), (3, 2, 2), (5, 3, 3)]
        )
        ans = nx.group_betweenness_centrality(G, C, weight="weight", normalized=False)
        assert ans == 1

    def test_group_betweenness_no_paths_through_group(self):
        """
        GBC sanity check when no paths pass through group (regression test for gh-8827)
        """
        # The non-group nodes 3, 4 and 5 have no shortest path between them that also
        # has an interior node in C, so the group betweenness is 0.
        G = nx.Graph([(0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 3), (3, 4), (4, 5)])
        assert 0 == nx.group_betweenness_centrality(G, [0, 1, 2], normalized=False)

    def test_group_betweenness_directed_ground_truth(self):
        """
        GBC check against exhaustive counting for directed graph (see gh-8827)
        """
        G = nx.DiGraph(
            [
                (0, 6),
                (1, 3),
                (1, 6),
                (2, 5),
                (2, 6),
                (2, 7),
                (3, 1),
                (3, 4),
                (4, 0),
                (4, 2),
                (4, 5),
                (4, 7),
                (5, 1),
                (5, 7),
                (6, 0),
                (6, 1),
                (6, 7),
                (7, 2),
                (7, 4),
                (7, 6),
            ]
        )

        b = nx.group_betweenness_centrality(G, [1, 2, 3], normalized=False)
        assert b == pytest.approx(8 / 3)


class TestProminentGroup:
    np = pytest.importorskip("numpy")
    pd = pytest.importorskip("pandas")

    def test_prominent_group_single_node(self):
        """
        Prominent group for single node
        """
        G = nx.path_graph(5)
        k = 1
        b, g = nx.prominent_group(G, k, normalized=False, endpoints=False)
        b_answer, g_answer = 4.0, [2]
        assert b == b_answer and g == g_answer

    def test_prominent_group_with_c(self):
        """
        Prominent group without some nodes
        """
        G = nx.path_graph(5)
        k = 1
        b, g = nx.prominent_group(G, k, normalized=False, C=[2])
        b_answer, g_answer = 3.0, [1]
        assert b == b_answer and g == g_answer

    def test_prominent_group_normalized_endpoints(self):
        """
        Prominent group with normalized result, with endpoints
        """
        G = nx.cycle_graph(7)
        k = 2
        b, g = nx.prominent_group(G, k, normalized=True, endpoints=True)
        b_answer, g_answer = 1.7, [2, 5]
        assert b == b_answer and g == g_answer

    def test_prominent_group_disconnected_graph(self):
        """
        Prominent group of disconnected graph
        """
        G = nx.path_graph(6)
        G.remove_edge(0, 1)
        k = 1
        b, g = nx.prominent_group(G, k, weight=None, normalized=False)
        b_answer, g_answer = 4.0, [3]
        assert b == b_answer and g == g_answer

    def test_prominent_group_node_not_in_graph(self):
        """
        Node(s) in C not in graph, raises NodeNotFound exception
        """
        with pytest.raises(nx.NodeNotFound):
            nx.prominent_group(nx.path_graph(5), 1, C=[10])

    def test_group_betweenness_directed_weighted(self):
        """
        Group betweenness centrality in a directed and weighted graph
        """
        G = nx.DiGraph()
        G.add_edge(1, 0, weight=1)
        G.add_edge(0, 2, weight=2)
        G.add_edge(1, 2, weight=3)
        G.add_edge(3, 1, weight=4)
        G.add_edge(2, 3, weight=1)
        G.add_edge(4, 3, weight=6)
        G.add_edge(2, 4, weight=7)
        k = 2
        b, g = nx.prominent_group(G, k, weight="weight", normalized=False)
        b_answer, g_answer = 5.0, [1, 2]
        assert b == b_answer and g == g_answer

    def test_prominent_group_greedy_algorithm(self):
        """
        Group betweenness centrality in a greedy algorithm
        """
        G = nx.cycle_graph(7)
        k = 2
        b, g = nx.prominent_group(G, k, normalized=True, endpoints=True, greedy=True)
        b_answer, g_answer = 1.7, [6, 3]
        assert b == b_answer and g == g_answer


class TestGroupClosenessCentrality:
    def test_group_closeness_single_node(self):
        """
        Group closeness centrality for a single node group
        """
        G = nx.path_graph(5)
        c = nx.group_closeness_centrality(G, [1])
        c_answer = nx.closeness_centrality(G, 1)
        assert c == c_answer

    def test_group_closeness_disconnected(self):
        """
        Group closeness centrality for a disconnected graph
        """
        G = nx.Graph()
        G.add_nodes_from([1, 2, 3, 4])
        c = nx.group_closeness_centrality(G, [1, 2])
        c_answer = 0
        assert c == c_answer

    def test_group_closeness_multiple_node(self):
        """
        Group closeness centrality for a group with more than
        1 node
        """
        G = nx.path_graph(4)
        c = nx.group_closeness_centrality(G, [1, 2])
        c_answer = 1
        assert c == c_answer

    def test_group_closeness_node_not_in_graph(self):
        """
        Node(s) in S not in graph, raises NodeNotFound exception
        """
        with pytest.raises(nx.NodeNotFound):
            nx.group_closeness_centrality(nx.path_graph(5), [6, 7, 8])


class TestGroupDegreeCentrality:
    def test_group_degree_centrality_single_node(self):
        """
        Group degree centrality for a single node group
        """
        G = nx.path_graph(4)
        d = nx.group_degree_centrality(G, [1])
        d_answer = nx.degree_centrality(G)[1]
        assert d == d_answer

    def test_group_degree_centrality_multiple_node(self):
        """
        Group degree centrality for group with more than
        1 node
        """
        G = nx.Graph()
        G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
        G.add_edges_from(
            [(1, 2), (1, 3), (1, 6), (1, 7), (1, 8), (2, 3), (2, 4), (2, 5)]
        )
        d = nx.group_degree_centrality(G, [1, 2])
        d_answer = 1
        assert d == d_answer

    def test_group_in_degree_centrality(self):
        """
        Group in-degree centrality in a DiGraph
        """
        G = nx.DiGraph()
        G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
        G.add_edges_from(
            [(1, 2), (1, 3), (1, 6), (1, 7), (1, 8), (2, 3), (2, 4), (2, 5)]
        )
        d = nx.group_in_degree_centrality(G, [1, 2])
        d_answer = 0
        assert d == d_answer

    def test_group_out_degree_centrality(self):
        """
        Group out-degree centrality in a DiGraph
        """
        G = nx.DiGraph()
        G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
        G.add_edges_from(
            [(1, 2), (1, 3), (1, 6), (1, 7), (1, 8), (2, 3), (2, 4), (2, 5)]
        )
        d = nx.group_out_degree_centrality(G, [1, 2])
        d_answer = 1
        assert d == d_answer

    def test_group_degree_centrality_node_not_in_graph(self):
        """
        Node(s) in S not in graph, raises NetworkXError
        """
        with pytest.raises(nx.NetworkXError):
            nx.group_degree_centrality(nx.path_graph(5), [6, 7, 8])
