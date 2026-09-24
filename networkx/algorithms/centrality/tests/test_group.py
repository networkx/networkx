"""
Tests for Group Centrality Measures
"""

import itertools
from functools import partial

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

    @pytest.mark.parametrize("create_using", [nx.Graph, nx.DiGraph])
    def test_group_betweenness_with_endpoints(self, create_using):
        """
        Impact of endpoints on group betweenness centrality
        """
        G = nx.path_graph(5, create_using=create_using)
        nx.add_path(G, [3, 2, 1])  # only affects DiGraph
        C = [1]
        gbc = nx.group_betweenness_centrality(G, C, normalized=False, endpoints=False)
        assert gbc == 3
        egbc = nx.group_betweenness_centrality(G, C, normalized=False, endpoints=True)
        assert egbc == (9 if G.is_directed() else 7)

        C = [2]
        gbc = nx.group_betweenness_centrality(G, C, normalized=False, endpoints=False)
        assert gbc == (5 if G.is_directed() else 4)
        egbc = nx.group_betweenness_centrality(G, C, normalized=False, endpoints=True)
        assert egbc == (11 if G.is_directed() else 8)

    @pytest.mark.parametrize("create_using", [nx.Graph, nx.DiGraph])
    def test_group_betweenness_endpoints_normalized(self, create_using):
        G = nx.path_graph(7, create_using=create_using)
        C = [1, 3, 5]  # check group of length >2
        ans = 0.5 if G.is_directed() else 1  # for DiGraph, only one way (half) cross C
        gbc = nx.group_betweenness_centrality(G, C, normalized=True, endpoints=False)
        assert gbc == ans
        ngbc = nx.group_betweenness_centrality(G, C, normalized=True, endpoints=True)
        assert ngbc == ans

    def test_group_betweenness_normalized(self):
        """
        Group betweenness centrality for group with more than
        1 node and normalized
        """
        G = nx.path_graph(5)
        C = [1, 3]
        assert nx.group_betweenness_centrality(G, C, normalized=True) == 1

    @pytest.mark.parametrize(
        "create_using, gbc, ngbc",
        [(nx.Graph, 6, 1), (nx.DiGraph, 7, 7 / 12)],
    )
    def test_group_betweenness_normalized_connected(self, create_using, gbc, ngbc):
        """
        Normalization for group with 3 nodes
        """
        G = nx.path_graph(7, create_using=create_using)
        nx.add_path(G, [6, 5, 4])  # only affects DiGraph
        C = [1, 3, 5]
        assert nx.group_betweenness_centrality(G, C, normalized=False) == gbc
        ngbc = pytest.approx(ngbc)
        assert nx.group_betweenness_centrality(G, C, normalized=True) == ngbc
        # undirected: 4*3/2=6 nongroup node-pairs, 6 reachable through C. 6/6=1
        # directed: 4*2=12 nongroup node-pairs, 7 of them through C. 7/12=0.58333

    @pytest.mark.parametrize(
        "create_using, gbc, ngbc",
        [(nx.Graph, 6, 6 / 15), (nx.DiGraph, 6, 6 / 30)],
    )
    def test_group_betweenness_normalized_disconnected(self, create_using, gbc, ngbc):
        # disconnected
        G = nx.path_graph(5, create_using=create_using)
        nx.add_path(G, range(6, 11))
        nx.add_path(G, [3, 2, 1])  # only affects DiGraph
        C = [1, 3, 7, 9]
        assert nx.group_betweenness_centrality(G, C, normalized=False) == gbc
        assert nx.group_betweenness_centrality(G, C, normalized=True) == ngbc
        # undirected: 6*5/2=15 nongroup node-pairs, 6 reachable through C. 6/15=0.4
        # directed: 6*5=30 nongroup node-pairs. 6 reachable through C. 6/30=0.2

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

    def test_group_betweenness_order_dependent(self):
        # see gh-8931
        G = nx.path_graph(5, create_using=nx.DiGraph)
        nx.add_path(G, range(6, 11))
        nx.add_path(G, [3, 2, 1])  # only affects DiGraph
        C = [1, 3, 7, 9]
        b_order1 = nx.group_betweenness_centrality(G, C, normalized=False)
        C = [9, 7, 3, 1]
        b_order2 = nx.group_betweenness_centrality(G, C, normalized=False)
        assert b_order1 == b_order2

    def test_group_betweenness_all_group_orders_agree(self):
        G = nx.path_graph(5, create_using=nx.DiGraph)
        nx.add_path(G, range(6, 11))
        nx.add_path(G, [3, 2, 1])  # only affects DiGraph
        C = [1, 3, 7, 9]
        b_order1 = nx.group_betweenness_centrality(G, C, normalized=False)
        assert all(
            nx.group_betweenness_centrality(G, group, normalized=False) == b_order1
            for group in itertools.permutations(C, 4)
        )

    def test_group_betweenness_order_dependent_smaller(self):
        G = nx.DiGraph([(1, 0), (1, 5), (2, 0), (2, 3), (3, 2), (5, 3)])
        C = [2, 3]
        b_order1 = nx.group_betweenness_centrality(G, C, normalized=False)
        C = [3, 2]
        b_order2 = nx.group_betweenness_centrality(G, C, normalized=False)
        assert b_order1 == b_order2

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


def check_prominent(
    gbc_exp, grp_exp, gbc, grp, G, k, weight=None, normalized=True, endpoints=False
):
    gbc_exp_calc = nx.group_betweenness_centrality(
        G, grp_exp, normalized=normalized, weight=weight, endpoints=endpoints
    )
    assert gbc_exp_calc == pytest.approx(gbc_exp), (
        f"input {gbc_exp=} != GBC({grp_exp=})={gbc_exp_calc}"
    )
    gbc_calc = nx.group_betweenness_centrality(
        G, grp, normalized=normalized, weight=weight, endpoints=endpoints
    )
    assert len(grp) == k and gbc == pytest.approx(gbc_exp)
    if grp == grp_exp:
        return

    # if multple groups tie for best betweenness grp != grp_exp might occur
    gbc_group = nx.group_betweenness_centrality(
        G, grp, normalized=normalized, weight=weight, endpoints=endpoints
    )
    assert len(grp) == k and gbc_group == gbc_exp_calc


def check_prominent_brute_force(G, k, wt=None, norm=True, ep=False):
    GBC = partial(
        nx.group_betweenness_centrality, G, weight=wt, normalized=norm, endpoints=ep
    )
    return max((GBC(nodes), nodes) for nodes in itertools.combinations(G, k))


class TestProminentGroup:
    np = pytest.importorskip("numpy")
    pd = pytest.importorskip("pandas")

    @pytest.mark.parametrize(
        "create_using",
        [nx.Graph, pytest.param(nx.DiGraph, marks=pytest.mark.xfail(rasies=KeyError))],
    )
    def test_prominent_group_single_node(self, create_using):
        G = nx.path_graph(5, create_using=create_using)
        k = 1
        b, g = nx.prominent_group(G, k, normalized=False, endpoints=False)
        assert b == 4
        assert nx.group_betweenness_centrality(G, g, normalized=False) == b
        GBC = partial(nx.group_betweenness_centrality, G, normalized=False)
        assert GBC(g) == b
        max_gbc, max_group = max((GBC([n]), [n]) for n in G)
        assert g == max_group
        assert b == max_gbc
        check_prominent(4, [2], b, g, G, k, normalized=False, endpoints=False)

    @pytest.mark.xfail(reason="known KeyError in GBC calculation", raises=KeyError)
    def test_group_betweenness_guard_against_keyerror(self):
        """
        Check for KeyErrors in D[u][v] inside prominent_group
        """
        G = nx.path_graph(6, create_using=nx.DiGraph)
        k = 3
        # y_in_Dx is enforced by the loop bounds. (KeyError if not enforced)
        # This checks v_in_Dy, y_in_Dv, x_in_Dv and v_in_Dx. Note: do not need x_in_Dy
        b, g = nx.prominent_group(G, k, normalized=False)
        check_prominent(2, [3, 1, 0], b, g, G, k, normalized=False)

    def test_prominent_group_with_excluded_nodes(self):
        G = nx.path_graph(5)
        k = 1
        b, g = nx.prominent_group(G, k, normalized=False, C=[2])
        check_prominent(3, [1], b, g, G, k, normalized=False, endpoints=False)

        b, g = nx.prominent_group(G, k, normalized=False, C=[1])
        check_prominent(4, [2], b, g, G, k, normalized=False)

    @pytest.mark.parametrize(
        "cls, k, norm, ep, gbc_exp, grp_exp",
        [
            # (nx.Graph, 3, True, True, 0.952381, [1, 3, 6]),
            (nx.Graph, 3, True, False, 0.833333, [1, 3, 6]),
            (nx.Graph, 3, False, True, 20, [1, 3, 6]),
            (nx.Graph, 3, False, False, 5, [1, 3, 6]),
            # (nx.Graph, 2, True, True, 0.8095238, [2, 5]),
            (nx.Graph, 2, True, False, 0.6, [2, 5]),
            (nx.Graph, 2, False, True, 17, [2, 5]),
            (nx.Graph, 2, False, False, 6, [2, 5]),
            # (nx.DiGraph, 3, True, True, 4.0833333, [2, 4, 6]),
            # (nx.DiGraph, 3, True, False, 1.5833333, [2, 4, 6]),
            # (nx.DiGraph, 3, False, True, 49, [2, 4, 6]),
            # (nx.DiGraph, 3, False, False, 11, [2, 4, 6]),
            # (nx.DiGraph, 2, True, True, 0.904762, [2, 5]),
            (nx.DiGraph, 2, True, False, 0.8, [2, 5]),
            (nx.DiGraph, 2, False, True, 38, [2, 5]),
            (nx.DiGraph, 2, False, False, 16, [2, 5]),
        ],
    )
    def test_prom_group_normalized_endpoints(self, cls, k, norm, ep, gbc_exp, grp_exp):
        G = nx.cycle_graph(7, create_using=cls)

        true_gbc, true_grp = check_prominent_brute_force(
            G, k, wt=None, norm=norm, ep=ep
        )
        gbc_exp_calc = nx.group_betweenness_centrality(
            G, grp_exp, normalized=norm, endpoints=ep
        )
        if true_gbc != pytest.approx(gbc_exp):
            gbc_exp_calc = nx.group_betweenness_centrality(
                G, grp_exp, normalized=norm, endpoints=ep
            )
        assert true_gbc == pytest.approx(gbc_exp)

        b, g = nx.prominent_group(G, k, normalized=norm, endpoints=ep)
        gbc_g = nx.group_betweenness_centrality(G, g, normalized=norm, endpoints=ep)
        # gbc_360 = nx.group_betweenness_centrality(G, [3, 6, 0], normalized=norm, endpoints=ep)
        # gbc_246 = nx.group_betweenness_centrality(G, [2, 4, 6], normalized=norm, endpoints=ep)
        # print(f"{b=} {g=} {gbc_g=} {gbc_360=} {gbc_246=}")
        assert gbc_g == pytest.approx(b)
        assert b == pytest.approx(true_gbc)
        check_prominent(gbc_exp, grp_exp, b, g, G, k, normalized=norm, endpoints=ep)

    @pytest.mark.parametrize(
        "create_using, gbc, ngbc",
        [(nx.Graph, 5, 0.833333), (nx.DiGraph, 5, 0.833333)],
    )
    def test_prominent_group_connected_graph(self, create_using, gbc, ngbc):
        G = nx.cycle_graph(7)
        nx.add_path(G, [6, 5, 4])  # only affects DiGraph
        k = 3
        b, g = nx.prominent_group(G, k, normalized=False)
        check_prominent(gbc, [1, 3, 5], b, g, G, k, normalized=False)

        b, g = nx.prominent_group(G, k, normalized=True)
        check_prominent(ngbc, [1, 3, 5], b, g, G, k, normalized=True)

    @pytest.mark.parametrize(
        "create_using, gbc, ngbc",
        [(nx.Graph, 6, 1), (nx.DiGraph, 7, 7 / 12)],
    )
    def test_prominent_group_disconnected_graph(self, create_using, gbc, ngbc):
        G = nx.path_graph(6)
        G.remove_edge(0, 1)
        k = 1
        b, g = nx.prominent_group(G, k, normalized=False)
        check_prominent(4, [3], b, g, G, k, normalized=False)

        b, g = nx.prominent_group(G, k, normalized=True)
        check_prominent(0.4, [3], b, g, G, k, normalized=True)

    def test_prominent_group_excluded_node_not_in_graph(self):
        with pytest.raises(nx.NodeNotFound):
            nx.prominent_group(nx.path_graph(5), 1, C=[10])

    def test_prominent_group_weighted(self):
        G = nx.Graph()
        G.add_edge(1, 0, weight=1)  # 0-2-4
        G.add_edge(0, 2, weight=2)  # | |/
        G.add_edge(1, 2, weight=3)  # 1-3
        G.add_edge(3, 1, weight=4)
        G.add_edge(2, 3, weight=1)
        G.add_edge(4, 3, weight=6)
        G.add_edge(2, 4, weight=7)
        k = 2
        b, g = nx.prominent_group(G, k, weight="weight", normalized=False)
        check_prominent(2, [1, 2], b, g, G, k, weight="weight", normalized=False)

        b, g = nx.prominent_group(G, k, weight="weight", normalized=True)
        check_prominent(0.6666666, [1, 2], b, g, G, k, weight="weight", normalized=True)

    def test_prominent_group_undirected_weighted(self):
        G = nx.DiGraph()
        G.add_edge(1, 0, weight=1)  # 0->2->4
        G.add_edge(0, 2, weight=2)  # ^  |  |
        G.add_edge(1, 2, weight=3)  # |  v  v
        G.add_edge(3, 1, weight=4)  # 1<-3-/
        G.add_edge(2, 3, weight=1)
        G.add_edge(4, 3, weight=6)
        G.add_edge(2, 4, weight=7)
        k = 2
        b, g = nx.prominent_group(G, k, weight="weight", normalized=False)
        check_prominent(5, [1, 2], b, g, G, k, weight="weight", normalized=False)

        b, g = nx.prominent_group(G, k, weight="weight", normalized=True)
        check_prominent(
            0.83333333, [1, 2], b, g, G, k, weight="weight", normalized=True
        )

    def test_prominent_group_greedy_algorithm(self):
        G = nx.cycle_graph(7)
        k = 2
        b, g = nx.prominent_group(G, k, normalized=False, endpoints=False, greedy=True)
        check_prominent(6, [6, 3], b, g, G, k, normalized=False)

        b, g = nx.prominent_group(G, k, normalized=False, endpoints=True, greedy=True)
        check_prominent(17, [6, 3], b, g, G, k, normalized=False, endpoints=True)

        b, g = nx.prominent_group(G, k, normalized=True, endpoints=False, greedy=True)
        check_prominent(0.6, [6, 3], b, g, G, k, normalized=True)

        # Currently fails due to normalization error with endpoints=True
        # b, g = nx.prominent_group(G, k, normalized=True, endpoints=True, greedy=True)
        # check_prominent(6, [6, 3], b, g, G, k, normalized=True, endpoints=True)

    def test_prominent_group_directed_greedy_algorithm(self):
        G = nx.cycle_graph(7, create_using=nx.DiGraph)
        k = 2
        b, g = nx.prominent_group(G, k, normalized=False, endpoints=False, greedy=True)
        check_prominent(16, [6, 3], b, g, G, k, normalized=False)

        b, g = nx.prominent_group(G, k, normalized=False, endpoints=True, greedy=True)
        check_prominent(38, [6, 3], b, g, G, k, normalized=False, endpoints=True)

        b, g = nx.prominent_group(G, k, normalized=True, endpoints=False, greedy=True)
        check_prominent(0.8, [6, 3], b, g, G, k, normalized=True)

        # Currently fails due to normalization error with endpoints=True
        # b, g = nx.prominent_group(G, k, normalized=True, endpoints=True, greedy=True)
        # check_prominent(1.9, [6, 3], b, g, G, k, normalized=True, endpoints=True)


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
