import itertools as it
import operator

import pytest

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import (
    _feasibility,
    _feasible_look_ahead,
    _feasible_node_pair,
    _find_candidates,
    _find_candidates_Di,
    _GraphInfo,
    _init_info,
    _matching_order,
    _restore_Tinout,
    _restore_Tinout_Di,
    _StateInfo,
    _update_Tinout,
)

graph_classes = [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]

five_dicts = ({},) * 5
six_sets = (set(),) * 6
two_eq = (operator.eq, operator.eq)

labels_same = ["blue"]

labels_many = ["white", "red", "blue", "green", "orange", "black", "purple"]


class TestNodeOrdering:
    def test_empty_graph(self):
        SG = nx.Graph()
        FG = nx.Graph()
        g_info = _GraphInfo(*two_eq, False, FG, SG, *five_dicts)
        assert len(set(_matching_order(g_info))) == 0

    def test_single_node(self):
        SG = nx.empty_graph(["node_A"])
        FG = SG.copy()

        l1 = dict(zip(SG, it.cycle(labels_many)))
        l2 = dict(zip(FG, it.cycle(labels_many)))
        l2groups = nx.utils.groups(l2)
        SG_deg = dict(SG.degree)
        FG_deg = dict(FG.degree)
        g_info = _GraphInfo(*two_eq, False, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        assert _matching_order(g_info) == ["node_A"]

    def test_matching_order(self):
        labels = [
            "blue",
            "blue",
            "red",
            "red",
            "red",
            "red",
            "green",
            "green",
            "green",
            "yellow",
            "purple",
            "purple",
            "blue",
            "blue",
        ]
        SG = nx.Graph(
            [
                (0, 1),
                (0, 2),
                (1, 2),
                (2, 5),
                (2, 4),
                (1, 3),
                (1, 4),
                (3, 6),
                (4, 6),
                (6, 7),
                (7, 8),
                (9, 10),
                (9, 11),
                (11, 12),
                (11, 13),
                (12, 13),
                (10, 13),
            ]
        )
        FG = SG.copy()
        l1 = dict(zip(SG, it.cycle(labels)))
        l2 = dict(zip(FG, it.cycle(labels)))
        l2groups = nx.utils.groups(l2)
        SG_deg = dict(SG.degree)
        FG_deg = dict(FG.degree)
        g_info = _GraphInfo(*two_eq, False, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        expected = [9, 11, 10, 13, 12, 1, 2, 4, 0, 3, 6, 5, 7, 8]
        assert _matching_order(g_info) == expected

    def test_matching_order_all_branches(self):
        SG = nx.Graph(
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)]
        )
        SG.add_node(5)
        FG = SG.copy()

        l1 = l2 = {0: "black", 1: "blue", 2: "blue", 3: "red", 4: "red", 5: "blue"}
        l2groups = nx.utils.groups(l2)
        SG_deg = dict(SG.degree)
        FG_deg = dict(FG.degree)
        g_info = _GraphInfo(*two_eq, False, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        expected = [0, 4, 1, 3, 2, 5]
        assert _matching_order(g_info) == expected


@pytest.mark.parametrize("Gclass", graph_classes)
class TestCandidateSelection:
    edges = [
        (1, 2),
        (1, 4),
        (5, 1),
        (2, 3),
        (4, 2),
        (3, 4),
        (4, 5),
        (1, 6),
        (6, 7),
        (6, 8),
        (8, 9),
        (7, 9),
    ]

    def test_no_covered_neighbors_no_labels(self, Gclass):
        mapped = dict(enumerate("xabcdefghi"))
        SG = Gclass(self.edges)
        SG.add_node(0)
        FG = nx.relabel_nodes(SG, mapped)

        # setup g_info
        directed = SG.is_directed()
        find_cands = _find_candidates_Di if directed else _find_candidates
        if directed:
            SG_deg = {n: (i, o) for (n, i), (_, o) in zip(SG.in_degree, SG.out_degree)}
            FG_deg = {n: (i, o) for (n, i), (_, o) in zip(FG.in_degree, FG.out_degree)}
        else:
            SG_deg = dict(SG.degree)
            FG_deg = dict(FG.degree)
        l1 = dict(SG.nodes(data="label", default=-1))
        l2 = dict(FG.nodes(data="label", default=-1))
        l2groups = nx.utils.groups(l2)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        m = {9: mapped[9], 1: mapped[1]}
        m_rev = {mapped[9]: 9, mapped[1]: 1}

        if directed:
            T1 = {2, 4, 6}
            T1_in = {5, 7, 8}
            T1_tilde = {0, 3}
            T2 = {"b", "d", "f"}
            T2_in = {"e", "g", "h"}
            T2_tilde = {"x", "c"}
        else:
            T1 = {7, 8, 2, 4, 5}
            T1_tilde = {0, 3, 6}
            T2 = {"g", "h", "b", "d", "e"}
            T2_tilde = {"x", "c", "f"}
            T1_in = T2_in = set()

        s_info = _StateInfo(m, m_rev, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # u = 3, expected={mapped[v] for v in [u]}, g_info_Di_no_lbls, s_info246_578
        u = 3
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]}

        # u = 0, expected={mapped[v] for v in [u]}, g_info_Di_no_lbls, s_info246
        u = 0
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]}

        m.pop(9)
        m_rev.pop(mapped[9])

        if directed:
            T1 = {2, 4, 6}
            T1_in = {5}
            T1_tilde = {0, 3, 7, 8, 9}
            T2 = {"b", "d", "f"}
            T2_in = {"e"}
            T2_tilde = {"x", "c", "g", "h", "i"}
            cands = {mapped[7], mapped[8], mapped[3]}
        else:
            T1 = {2, 4, 5, 6}
            T1_tilde = {0, 3, 7, 8, 9}
            T2 = {"g", "h", "b", "d", "e", "f"}
            T2_tilde = {"x", "c", "g", "h", "i"}
            cands = {mapped[7], mapped[8], mapped[3], mapped[9]}

        s_info = _StateInfo(m, m_rev, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # u = 7, expected={mapped[v] for v in [u, 8, 3]}, g_info_Di_no_lbls, s_info246_5
        u = 7
        candidates = find_cands(u, g_info, s_info)
        assert candidates == cands

    def test_no_covered_neighbors_with_labels(self, Gclass):
        mapped = dict(enumerate("xabcdefghi"))
        SG = Gclass()
        SG.add_edges_from(self.edges)
        SG.add_node(0)
        FG = nx.relabel_nodes(SG, mapped)

        # setup g_info
        directed = SG.is_directed()
        find_cands = _find_candidates_Di if directed else _find_candidates
        if directed:
            SG_deg = {n: (i, o) for (n, i), (_, o) in zip(SG.in_degree, SG.out_degree)}
            FG_deg = {n: (i, o) for (n, i), (_, o) in zip(FG.in_degree, FG.out_degree)}
        else:
            SG_deg = dict(SG.degree)
            FG_deg = dict(FG.degree)
        l1 = dict(zip(SG, it.cycle(labels_many)))
        l2 = dict(zip(FG, it.cycle(labels_many)))
        l2groups = nx.utils.groups(l2)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        # setup s_info
        m = {9: mapped[9], 1: mapped[1]}
        m_rev = {mapped[9]: 9, mapped[1]: 1}

        T1 = {2, 4, 6}
        T1_in = {5, 7, 8}
        T1_tilde = {0, 3}
        T2 = {"b", "d", "f"}
        T2_in = {"e", "g", "h"}
        T2_tilde = {"x", "c"}

        s_info = _StateInfo(m, m_rev, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # u = 3, expected={mapped[v] for v in [u]}, g_info_Di_manylbls, s_info246_578
        u = 3
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]}

        # u = 0, expected={mapped[v] for v in [u]}, g_info_Di_manylbls, s_info246_578
        u = 0  # disconnected node
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]}

        # Change label of disconnected node => No candidate
        l1[u] = "purple"
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        # u = 0, expected={mapped[v] for v in [u]}, g_info_Di_manylbls_0newcolor, s_info246_578
        candidates = find_cands(u, g_info, s_info)
        assert candidates == set()

        # update state for next tests
        m.pop(9)
        m_rev.pop(mapped[9])

        T1 = {2, 4, 6}
        T1_in = {5}
        T1_tilde = {0, 3, 7, 8, 9}
        T2 = {"b", "d", "f"}
        T2_in = {"e"}
        T2_tilde = {"x", "c", "g", "h", "i"}

        s_info = _StateInfo(m, m_rev, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # u = 7, expected={mapped[v] for v in [u]}, g_info_Di_manylbls, s_info246_5
        u = 7
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]}

        l1[8] = l1[7]
        l2[mapped[8]] = l1[7]
        l2groups = nx.utils.groups(l2)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        # u = 7, expected={mapped[v] for v in [u]}, g_info_Di_manylbls_78same, s_info246_5
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u], mapped[8]}

    def test_covered_neighbors_no_labels(self, Gclass):
        mapped = dict(enumerate("xabcdefghi"))
        SG = Gclass()
        SG.add_edges_from(self.edges)
        SG.add_node(0)
        FG = nx.relabel_nodes(SG, mapped)

        # setup g_info
        directed = SG.is_directed()
        find_cands = _find_candidates_Di if directed else _find_candidates
        if directed:
            SG_deg = {n: (i, o) for (n, i), (_, o) in zip(SG.in_degree, SG.out_degree)}
            FG_deg = {n: (i, o) for (n, i), (_, o) in zip(FG.in_degree, FG.out_degree)}
        else:
            SG_deg = dict(SG.degree)
            FG_deg = dict(FG.degree)
        l1 = dict(SG.nodes(data="label", default=-1))
        l2 = dict(FG.nodes(data="label", default=-1))
        l2groups = nx.utils.groups(l2)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        m = {9: mapped[9], 1: mapped[1]}
        m_rev = {mapped[9]: 9, mapped[1]: 1}

        T1 = {2, 4, 6}
        T1_in = {5, 7, 8}
        T1_tilde = {0, 3}
        T2 = {"b", "d", "f"}
        T2_in = {"e", "g", "h"}
        T2_tilde = {"x", "c"}

        s_info = _StateInfo(m, m_rev, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # u = 5, expected={mapped[v] for v in [u]}, g_info_Di_no_lbls, s_info246_578
        u = 5
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]}

        # u = 6, expected={mapped[v] for v in [u]}, g_info_Di_no_lbls, s_info246_578
        u = 6
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]} if directed else {mapped[2], mapped[u]}

        # Change edge orientation to make degree match 1st candidate of u
        SG.remove_edge(4, 2)
        SG.add_edge(2, 4)
        FG.remove_edge("d", "b")
        FG.add_edge("b", "d")
        if directed:
            SG_deg = {n: (i, o) for (n, i), (_, o) in zip(SG.in_degree, SG.out_degree)}
            FG_deg = {n: (i, o) for (n, i), (_, o) in zip(FG.in_degree, FG.out_degree)}
        else:
            SG_deg = dict(SG.degree)
            FG_deg = dict(FG.degree)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        # u = 6, expected={mapped[v] for v in [u]}, g_info_Di_no_lbls, s_info246_578
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u], mapped[2]} if directed else {mapped[u]}

    def test_covered_neighbors_with_labels(self, Gclass):
        mapped = dict(enumerate("xabcdefghi"))
        SG = Gclass()
        SG.add_edges_from(self.edges)
        SG.add_node(0)
        FG = nx.relabel_nodes(SG, mapped)

        SG.remove_edge(4, 2)
        SG.add_edge(2, 4)
        FG.remove_edge("d", "b")
        FG.add_edge("b", "d")

        # setup g_info
        directed = SG.is_directed()
        find_cands = _find_candidates_Di if directed else _find_candidates
        if directed:
            SG_deg = {n: (i, o) for (n, i), (_, o) in zip(SG.in_degree, SG.out_degree)}
            FG_deg = {n: (i, o) for (n, i), (_, o) in zip(FG.in_degree, FG.out_degree)}
        else:
            SG_deg = dict(SG.degree)
            FG_deg = dict(FG.degree)
        l1 = dict(zip(SG, it.cycle(labels_many)))
        l2 = dict(zip([mapped[n] for n in SG], it.cycle(labels_many)))
        l2groups = nx.utils.groups(l2)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        m = {9: mapped[9], 1: mapped[1]}
        m_rev = {mapped[9]: 9, mapped[1]: 1}

        T1 = {2, 4, 6}
        T1_in = {5, 7, 8}
        T1_tilde = {0, 3}
        T2 = {"b", "d", "f"}
        T2_in = {"e", "g", "h"}
        T2_tilde = {"x", "c"}

        s_info = _StateInfo(m, m_rev, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # u = 5, expected={mapped[v] for v in [u]}, g_info_Di_manylbls_24switch, s_info246_578
        u = 5
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]}

        # u = 6, expected={mapped[v] for v in [u]}, g_info_Di_manylbls_24switch, s_info246_578
        u = 6
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]}

        # Assign to 2, the same label as 6
        l1[2] = l1[u]
        l2[mapped[2]] = l1[u]
        l2groups = nx.utils.groups(l2)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        # u = 6, expected={mapped[v] for v in [u, 2]}, g_info_Di_manylbls_24switch_26same, s_info246_578
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u], mapped[2]}

        # Change edge orientation to make degree match 1st candidate of u
        SG.remove_edge(2, 4)
        SG.add_edge(4, 2)
        FG.remove_edge("b", "d")
        FG.add_edge("d", "b")
        if directed:
            SG_deg = {n: (i, o) for (n, i), (_, o) in zip(SG.in_degree, SG.out_degree)}
            FG_deg = {n: (i, o) for (n, i), (_, o) in zip(FG.in_degree, FG.out_degree)}
        else:
            SG_deg = dict(SG.degree)
            FG_deg = dict(FG.degree)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        # u = 6, expected={mapped[v] for v in [u, 2]}, g_info_Di_manylbls_26same, s_info246_578
        candidates = find_cands(u, g_info, s_info)
        assert candidates == {mapped[u]} if directed else {mapped[u], mapped[2]}

    def test_same_in_out_degrees_no_candidate(self, Gclass):
        mapped = dict(enumerate("xabcdefghi"))
        SG = Gclass([(4, 1), (4, 2), (3, 4), (5, 4), (6, 4)])
        FG = Gclass([(1, 4), (2, 4), (3, 4), (4, 5), (4, 6)])

        # setup g_info
        directed = SG.is_directed()
        find_cands = _find_candidates_Di if directed else _find_candidates
        if directed:
            SG_deg = {n: (i, o) for (n, i), (_, o) in zip(SG.in_degree, SG.out_degree)}
            FG_deg = {n: (i, o) for (n, i), (_, o) in zip(FG.in_degree, FG.out_degree)}
        else:
            SG_deg = dict(SG.degree)
            FG_deg = dict(FG.degree)
        l1 = dict(SG.nodes(data="label", default=-1))
        l2 = dict(FG.nodes(data="label", default=-1))
        l2groups = nx.utils.groups(l2)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, SG_deg, FG_deg, l2groups)

        m = {1: 1, 2: 2, 3: 3}
        m_rev = m.copy()

        T1 = {4}
        T1_in = {4}
        T1_tilde = {5, 6}
        T2 = {4}
        T2_in = {4}
        T2_tilde = {5, 6}

        s_info = _StateInfo(m, m_rev, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        u = 4
        # despite the same in and out degree, there's no candidate for u=4
        candidates = find_cands(u, g_info, s_info)
        assert candidates == set() if directed else {4}


@pytest.mark.parametrize("Gclass", graph_classes)
class TestISOFeasibility:
    def test_feasible_node_pair_covered_neighbors(self, Gclass):
        directed = Gclass.is_directed(None)
        SG = Gclass([(0, 1), (1, 2), (0, 3), (2, 3)])
        FG = Gclass([("a", "b"), ("b", "c"), ("a", "k"), ("c", "k")])
        g_info = _GraphInfo(*two_eq, directed, FG, SG, *five_dicts)
        s_info = _StateInfo(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, *six_sets
        )
        u, v = 3, "k"
        assert _feasible_node_pair(u, v, g_info, s_info)

    def test_feasible_node_pair_no_covered_neighbors(self, Gclass):
        directed = Gclass.is_directed(None)
        SG = Gclass([(0, 1), (1, 2), (3, 4), (3, 5)])
        FG = Gclass([("a", "b"), ("b", "c"), ("k", "w"), ("k", "z")])
        g_info = _GraphInfo(*two_eq, directed, FG, SG, *five_dicts)
        s_info = _StateInfo(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, *six_sets
        )
        u, v = 3, "k"
        assert _feasible_node_pair(u, v, g_info, s_info)

    def test_feasible_node_pair_mixed_covered_uncovered_neighbors(self, Gclass):
        directed = Gclass.is_directed(None)
        SG = Gclass([(0, 1), (1, 2), (3, 0), (3, 2), (3, 4), (3, 5)])
        FG = Gclass(
            [("a", "b"), ("b", "c"), ("k", "a"), ("k", "c"), ("k", "w"), ("k", "z")]
        )
        g_info = _GraphInfo(*two_eq, directed, FG, SG, *five_dicts)
        s_info = _StateInfo(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, *six_sets
        )
        u, v = 3, "k"
        assert _feasible_node_pair(u, v, g_info, s_info)

    def test_feasible_node_pair_fail_cases(self, Gclass):
        directed = Gclass.is_directed(None)
        SG = Gclass(
            [
                (0, 1),
                (2, 1),
                (10, 0),
                (10, 3),
                (10, 4),
                (5, 10),
                (10, 6),
                (1, 4),
                (5, 3),
            ]
        )
        FG = Gclass(
            [
                ("a", "b"),
                ("c", "b"),
                ("k", "a"),
                ("k", "d"),
                ("k", "e"),
                ("f", "k"),
                ("k", "g"),
                ("b", "e"),
                ("f", "d"),
            ]
        )
        g_info = _GraphInfo(*two_eq, directed, FG, SG, *five_dicts)
        s_info = _StateInfo(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            *six_sets,
        )
        u, v = 10, "k"
        assert _feasible_node_pair(u, v, g_info, s_info)

        # Delete one uncovered neighbor of u. Notice how it still passes the
        # test. Two reasons for this:
        #   1. If u, v had different degrees from the beginning, they wouldn't
        #      be selected as candidates in the first place.
        #   2. Even if they are selected, consistency is basically
        #      1-look-ahead, meaning that we take into consideration the
        #      relation of the candidates with their mapped neighbors.
        #      The node we deleted is not a covered neighbor.
        #      Such nodes will be checked by the cut function, which is
        #      basically the 2-look-ahead, checking the relation of the
        #      candidates with T1, T2 (in which belongs the node we just deleted).
        SG.remove_node(6)
        assert _feasible_node_pair(u, v, g_info, s_info)

        # Add one more covered neighbor of u in SG
        SG.add_edge(u, 2)
        assert not _feasible_node_pair(u, v, g_info, s_info)

        # Compensate in FG
        FG.add_edge(v, "c")
        assert _feasible_node_pair(u, v, g_info, s_info)

        # Add one more covered neighbor of v in FG
        FG.add_edge(v, "x")
        SG.add_node(7)
        s_info.mapping.update({7: "x"})
        s_info.rev_map.update({"x": 7})
        assert not _feasible_node_pair(u, v, g_info, s_info)

        # Compensate in SG
        SG.add_edge(u, 7)
        assert _feasible_node_pair(u, v, g_info, s_info)

    def test_feasible_look_ahead_mismatched_labels(self, Gclass):
        directed = Gclass.is_directed(None)
        SG = Gclass(
            [
                (0, 1),
                (2, 1),
                (10, 0),
                (10, 3),
                (10, 4),
                (5, 10),
                (10, 6),
                (1, 4),
                (5, 3),
            ]
        )
        FG = Gclass(
            [
                ("a", "b"),
                ("c", "b"),
                ("k", "a"),
                ("k", "d"),
                ("k", "e"),
                ("f", "k"),
                ("k", "g"),
                ("b", "e"),
                ("f", "d"),
            ]
        )

        l1 = {n: "blue" for n in SG.nodes()}
        l2 = {n: "blue" for n in FG.nodes()}
        l1.update({5: "green"})  # Change the label of one neighbor of u
        l2groups = nx.utils.groups(l2)

        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)
        mapping = {0: "a", 1: "b", 2: "c", 3: "d"}
        rev_map = {"a": 0, "b": 1, "c": 2, "d": 3}
        s_info = _StateInfo(mapping, rev_map, *six_sets)

        u, v = 10, "k"
        assert not _feasible_look_ahead(u, v, g_info, s_info)

    def test_feasible_look_ahead_matched_labels(self, Gclass):
        directed = Gclass.is_directed(None)
        SG = Gclass(
            [
                (0, 1),
                (2, 1),
                (10, 0),
                (10, 3),
                (10, 4),
                (5, 10),
                (10, 6),
                (1, 4),
                (5, 3),
            ]
        )
        FG = Gclass(
            [
                ("a", "b"),
                ("c", "b"),
                ("k", "a"),
                ("k", "d"),
                ("k", "e"),
                ("f", "k"),
                ("k", "g"),
                ("b", "e"),
                ("f", "d"),
            ]
        )

        l1 = {n: "blue" for n in SG.nodes()}
        l2 = {n: "blue" for n in FG.nodes()}
        l2groups = nx.utils.groups(l2)

        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)
        s_info = _StateInfo(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4},
            {5, 10},
            {6},
            {"e"},
            {"f", "k"},
            {"g"},
        )

        u, v = 10, "k"
        assert _feasible_look_ahead(u, v, g_info, s_info)

    def test_feasible_look_ahead_same_labels(self, Gclass):
        directed = Gclass.is_directed(None)
        SG = Gclass(
            [
                (0, 1),
                (2, 1),
                (10, 0),
                (10, 0),
                (10, 0),
                (10, 3),
                (10, 3),
                (10, 4),
                (10, 4),
                (5, 10),
                (5, 10),
                (5, 10),
                (5, 10),
                (10, 6),
                (10, 6),
                (1, 4),
                (5, 3),
            ]
        )
        mapped = dict(enumerate("abcdefg"))
        mapped[10] = "k"
        FG = nx.relabel_nodes(SG, mapped)
        l1 = {n: "blue" for n in SG.nodes()}
        l2 = {n: "blue" for n in FG.nodes()}
        l2groups = nx.utils.groups(l2)

        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)
        mapping = {0: "a", 1: "b", 2: "c", 3: "d"}
        rev_map = {"a": 0, "b": 1, "c": 2, "d": 3}
        if directed:
            # (T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)
            T_info = ({4, 10}, {5, 10}, {6}, {"e"}, {"f", "k"}, {"g"})
        else:
            T_info = ({4, 5, 10}, None, {6}, {"e", "f", "k"}, None, {"g"})
        s_info = _StateInfo(mapping, rev_map, *T_info)

        u, v = 10, "k"
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Remove one of the multiple edges between u and a neighbor
        SG.remove_edge(u, 4)
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Change intersection between SG[u] and T1_out, so it's not the same as
        # the one between FG[v] and T2_out
        if SG.is_multigraph():  # such edge is left only when multigraph
            SG.remove_edge(u, 4)
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Compensate in FG
        FG.remove_edges_from([(v, mapped[4])] * 2)
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change intersection between SG[u] and T1_in, so it's not the same as
        # the one between FG[v] and T2_in
        SG.remove_edges_from([(5, u)] * 4)
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Compensate in FG
        FG.remove_edges_from([(mapped[5], v)] * 4)
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change intersection between FG[v] and T2_tilde, so it's not the same
        # as the one between SG[u] and T1_tilde
        FG.remove_edge(v, mapped[6])
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Compensate in SG
        SG.remove_edge(u, 6)
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Add more edges between u and neighbor which belongs in T1_in
        SG.add_edges_from([(u, 5), (u, 5), (u, 5)])
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Compensate in FG
        FG.add_edges_from([(v, mapped[5]), (v, mapped[5]), (v, mapped[5])])
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Add disconnected nodes, which will form the new Ti_tilde
        SG.add_nodes_from([7, 8, 9])
        FG.add_nodes_from(["y", "z", "w"])
        SG.add_edges_from([(u, 6), (u, 6), (u, 6)])
        FG.add_edges_from([(v, "g"), (v, "g"), (v, "g")])
        s_info.T1_tilde.update({7, 8, 9})
        s_info.T2_tilde.update({"y", "z", "w"})

        l1 = {n: "blue" for n in SG.nodes()}
        l2 = {n: "blue" for n in FG.nodes()}
        l2groups = nx.utils.groups(l2)
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)

        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Add some new nodes to the mapping
        s_info.mapping.update({6: "g", 7: "y"})
        s_info.rev_map.update({"g": 6, "y": 7})

        # Add more nodes to T1, T2.
        SG.add_edges_from([(6, 20), (7, 20), (6, 21)])
        FG.add_edges_from([("g", "i"), ("y", "i"), ("g", "j")])

        s_info.T1.update({20, 21})
        s_info.T2.update({"i", "j"})
        s_info.T1_tilde.difference_update({6, 7})
        s_info.T2_tilde.difference_update({"g", "y"})

        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Remove some edges
        FG.remove_edge(v, "g")
        if FG.is_multigraph():
            assert not _feasible_look_ahead(u, v, g_info, s_info)
        else:
            assert _feasible_look_ahead(u, v, g_info, s_info)

        SG.remove_edge(u, 6)
        SG.add_edge(u, 8)
        FG.add_edge(v, "z")
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Add nodes from the new T1 and T2, as neighbors of u and v respectively
        SG.add_edges_from([(u, 20), (u, 20), (u, 20), (u, 21)])
        FG.add_edges_from([(v, "i"), (v, "i"), (v, "i"), (v, "j")])
        l1 = {n: "blue" for n in SG.nodes()}
        l2 = {n: "blue" for n in FG.nodes()}
        l2groups = nx.utils.groups(l2)
        directed = SG.is_directed()
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)

        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change the edges, maintaining the SG[u]-T1 intersection
        SG.remove_edge(u, 21)
        SG.add_edge(u, 4)
        assert _feasible_look_ahead(u, v, g_info, s_info)

        FG.remove_edge(v, "j")
        FG.add_edge(v, mapped[4])
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Connect u to 9 which is still in T1_tilde
        SG.add_edge(u, 9)
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Same for v and z, so that inters(SG[u], T1out) == inters(FG[v], T2out)
        FG.add_edge(v, "w")
        assert _feasible_look_ahead(u, v, g_info, s_info)

    def test_feasible_look_ahead_different_labels(self, Gclass):
        directed = Gclass.is_directed(None)
        SG = Gclass(
            [
                (0, 1),
                (1, 2),
                (14, 1),
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7),
                (3, 6),
                (10, 4),
                (4, 9),
                (6, 10),
                (20, 9),
                (20, 15),
                (20, 12),
                (20, 11),
                (12, 13),
                (11, 13),
                (20, 8),
                (20, 3),
                (20, 5),
                (0, 20),
            ]
        )
        mapped = dict(enumerate("abcdefghijklmnop"))
        mapped[20] = "x"
        FG = nx.relabel_nodes(SG, mapped)

        l1 = {n: "none" for n in SG}
        l1.update(
            {
                9: "blue",
                15: "blue",
                12: "blue",
                11: "green",
                3: "green",
                8: "red",
                0: "red",
                5: "yellow",
            }
        )
        l2 = {mapped[n]: l for n, l in l1.items()}
        l2groups = nx.utils.groups(l2)

        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)
        mapping = {0: "a", 1: "b", 2: "c", 3: "d"}
        rev_map = {"a": 0, "b": 1, "c": 2, "d": 3}
        if directed:
            # (T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)
            T_info = (
                {4, 5, 6, 7, 20},
                {14, 20},
                {9, 10, 15, 12, 11, 13, 8},
                {"e", "f", "g", "x"},
                {"o", "x"},
                {"j", "k", "l", "m", "n", "i", "p"},
            )
        else:
            T_info = (
                {4, 5, 6, 7, 14},
                None,
                {9, 10, 15, 12, 11, 13, 8},
                {"e", "f", "g", "h", "o"},
                None,
                {"j", "k", "l", "m", "n", "i", "p"},
            )
        s_info = _StateInfo(mapping, rev_map, *T_info)

        u, v = 20, "x"
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change the orientation of the labels on neighbors of u compared to
        # neighbors of v. Leave the structure intact
        l1.update({9: "red"})
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # compensate in FG
        l2.update({mapped[9]: "red"})
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change the intersection of SG[u] and T1_out
        SG.add_edge(u, 4)
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Same for FG[v] and T2_out
        FG.add_edge(v, mapped[4])
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change the intersection of SG[u] and T1_in
        SG.add_edge(u, 14)
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Same for FG[v] and T2_in
        FG.add_edge(v, mapped[14])
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change the intersection of FG[v] and T2_tilde
        FG.remove_edge(v, mapped[8])
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Same for SG[u] and T1_tilde
        SG.remove_edge(u, 8)
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Put 8 and mapped[8] in T1 and T2, resp, by connecting to covered nodes
        SG.add_edges_from([(8, 3), (8, 3), (8, u)])
        FG.add_edges_from([(mapped[8], mapped[3]), (mapped[8], mapped[3])])
        s_info.T1.add(8)
        s_info.T2.add(mapped[8])
        s_info.T1_tilde.remove(8)
        s_info.T2_tilde.remove(mapped[8])

        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Fix uneven edges
        SG.remove_edge(8, u)
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Remove neighbor of u from T1
        SG.remove_node(5)
        l1.pop(5)
        s_info.T1.remove(5)
        assert not _feasible_look_ahead(u, v, g_info, s_info)

        # Same in FG
        FG.remove_node(mapped[5])
        l2.pop(mapped[5])
        s_info.T2.remove(mapped[5])
        assert _feasible_look_ahead(u, v, g_info, s_info)

    def test_predecessor_T1_in_fail(self, Gclass):
        directed = Gclass.is_directed(Gclass)
        SG = Gclass([(0, 1), (0, 3), (4, 0), (1, 5), (5, 2), (3, 6), (4, 6), (6, 5)])
        mapped = dict(enumerate("abcdefg"))
        FG = nx.relabel_nodes(SG, mapped)
        l1 = {n: "blue" for n in SG.nodes()}
        l2 = {n: "blue" for n in FG.nodes()}
        l2groups = nx.utils.groups(l2)

        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)
        m = {0: "a", 1: "b", 2: "c"}
        rev_m = {"a": 0, "b": 1, "c": 2}
        s_info = _StateInfo(m, rev_m, {3, 5}, {4, 5}, {6}, {"d", "f"}, {"f"}, {"g"})

        u, v = 6, "g"
        assert _feasible_look_ahead(u, v, g_info, s_info) != directed

        s_info.T2_in.add("e")
        assert _feasible_look_ahead(u, v, g_info, s_info)

    def test_all_feasibility_same_labels(self, Gclass):
        SG = Gclass(
            [
                (0, 1),
                (1, 2),
                (14, 1),
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7),
                (3, 6),
                (4, 10),
                (4, 9),
                (6, 10),
                (20, 9),
                (20, 15),
                (20, 12),
                (20, 11),
                (12, 13),
                (11, 13),
                (20, 8),
                (20, 2),
                (20, 5),
                (20, 0),
            ]
        )
        mapped = dict(enumerate("abcdefghijklmnop"))
        mapped[20] = "x"
        FG = nx.relabel_nodes(SG, mapped)

        l1 = {n: "blue" for n in SG.nodes()}
        l2 = {mapped[n]: "blue" for n in SG.nodes()}
        l2groups = nx.utils.groups(l2)

        directed = SG.is_directed()
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)
        s_info = _StateInfo(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5, 6, 7},
            {14},
            {9, 10, 15, 12, 11, 13, 8},
            {"e", "f", "g", "h"},
            {"o"},
            {"j", "k", "l", "m", "n", "i", "p"},
        )

        u, v = 20, "x"
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change structure in FG such that, ONLY consistency is harmed
        FG.remove_edge(mapped[20], mapped[2])
        FG.add_edge(mapped[20], mapped[3])

        # Consistency check fails, while the cutting rules are satisfied!
        assert _feasible_look_ahead(u, v, g_info, s_info)
        assert not _feasible_node_pair(u, v, g_info, s_info)

        # Compensate in SG and make it consistent
        SG.remove_edge(20, 2)
        SG.add_edge(20, 3)
        assert _feasible_look_ahead(u, v, g_info, s_info)
        assert _feasible_node_pair(u, v, g_info, s_info)

        # ONLY fail the cutting check
        FG.add_edge(v, mapped[10])
        assert not _feasible_look_ahead(u, v, g_info, s_info)
        assert _feasible_node_pair(u, v, g_info, s_info)

    def test_all_feasibility_different_labels(self, Gclass):
        SG = Gclass(
            [
                (0, 1),
                (1, 2),
                (1, 14),
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7),
                (3, 6),
                (4, 10),
                (4, 9),
                (6, 10),
                (20, 9),
                (20, 15),
                (20, 12),
                (20, 11),
                (12, 13),
                (11, 13),
                (20, 8),
                (20, 2),
                (20, 5),
                (20, 0),
            ]
        )
        mapped = dict(enumerate("abcdefghijklmnop"))
        mapped[20] = "x"
        FG = nx.relabel_nodes(SG, mapped)

        l1 = {n: "none" for n in SG.nodes()}
        l1.update(
            {
                9: "blue",
                15: "blue",
                12: "blue",
                11: "green",
                2: "green",
                8: "red",
                0: "red",
                5: "yellow",
            }
        )
        l2 = {mapped[n]: l for n, l in l1.items()}
        l2groups = nx.utils.groups(l2)

        directed = SG.is_directed()
        g_info = _GraphInfo(*two_eq, directed, FG, SG, l1, l2, {}, {}, l2groups)
        s_info = _StateInfo(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5, 6, 7},
            {14},
            {9, 10, 15, 12, 11, 13, 8},
            {"e", "f", "g", "h"},
            {"o"},
            {"j", "k", "l", "m", "n", "i", "p"},
        )

        u, v = 20, "x"
        assert _feasible_look_ahead(u, v, g_info, s_info)

        # Change structure in FG such that, ONLY consistency is harmed
        FG.remove_edge(mapped[20], mapped[2])
        FG.add_edge(mapped[20], mapped[3])
        l2.update({mapped[3]: "green"})

        # Consistency check fails, while the cutting rules are satisfied!
        assert _feasible_look_ahead(u, v, g_info, s_info)
        assert not _feasible_node_pair(u, v, g_info, s_info)

        # Compensate in SG and make it consistent
        SG.remove_edge(20, 2)
        SG.add_edge(20, 3)
        l1.update({3: "green"})
        assert _feasible_look_ahead(u, v, g_info, s_info)
        assert _feasible_node_pair(u, v, g_info, s_info)

        # ONLY fail the cutting check
        l1.update({5: "red"})
        assert not _feasible_look_ahead(u, v, g_info, s_info)
        assert _feasible_node_pair(u, v, g_info, s_info)


@pytest.mark.parametrize("Gclass", graph_classes)
class TestTinoutUpdating:
    edges = [
        (1, 3),
        (3, 2),
        (3, 4),
        (4, 9),
        (4, 5),
        (3, 9),
        (5, 8),
        (5, 7),
        (8, 7),
        (7, 6),
    ]

    @staticmethod
    def check_Ts(directed, s_info, eT1, eT1_in, eT1_tilde, eT2, eT2_in, eT2_tilde):
        # eT1 for expected T1 value. s_info holds actual values.
        T1, T1_in, T1_tilde, T2, T2_in, T2_tilde = s_info[2:]
        if directed:
            assert T1 == eT1
            assert T1_in == eT1_in
            assert T2 == eT2
            assert T2_in == eT2_in
        else:
            assert T1 == (eT1 | eT1_in)
            assert T2 == (eT2 | eT2_in)

        assert T1_tilde == eT1_tilde
        assert T2_tilde == eT2_tilde

    def test_updating(self, Gclass):
        mapped = dict(enumerate("xabcdefghi"))
        SG = Gclass(self.edges)
        SG.add_node(0)
        FG = nx.relabel_nodes(SG, mapping=mapped)
        directed = SG.is_directed()

        g_info, s_info = _init_info(FG, SG, None, None, "ISO")
        m, m_rev = s_info.mapping, s_info.rev_map

        # Add node to the mapping
        m[4] = mapped[4]
        m_rev[mapped[4]] = 4
        _update_Tinout(4, mapped[4], g_info, s_info)

        T1 = {5, 9}
        T1_in = {3}
        T2 = {"i", "e"}
        T2_in = {"c"}
        T1_tilde = {0, 1, 2, 6, 7, 8}
        T2_tilde = {"x", "a", "b", "f", "g", "h"}
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # Add node to the mapping
        m[5] = mapped[5]
        m_rev[mapped[5]] = 5
        _update_Tinout(5, mapped[5], g_info, s_info)

        T1 = {9, 8, 7}
        T1_in = {3}
        T2 = {"i", "g", "h"}
        T2_in = {"c"}
        T1_tilde = {0, 1, 2, 6}
        T2_tilde = {"x", "a", "b", "f"}
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # Add node to the mapping
        m[6] = mapped[6]
        m_rev[mapped[6]] = 6
        _update_Tinout(6, mapped[6], g_info, s_info)

        T1 = {9, 8, 7}
        T1_in = {3, 7}
        T2 = {"i", "g", "h"}
        T2_in = {"c", "g"}
        T1_tilde = {0, 1, 2}
        T2_tilde = {"x", "a", "b"}
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # Add node to the mapping
        m[3] = mapped[3]
        m_rev[mapped[3]] = 3
        _update_Tinout(3, mapped[3], g_info, s_info)

        T1 = {9, 8, 7, 2}
        T1_in = {7, 1}
        T2 = {"i", "g", "h", "b"}
        T2_in = {"g", "a"}
        T1_tilde = {0}
        T2_tilde = {"x"}
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # Add node to the mapping
        m[0] = mapped[0]
        m_rev[mapped[0]] = 0
        _update_Tinout(0, mapped[0], g_info, s_info)

        # T1 = {9, 8, 7, 2}
        # T1_in = {7, 1}
        # T2 = {"i", "g", "h", "b"}
        # T2_in = {"g", "a"}
        T1_tilde = set()
        T2_tilde = set()
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

    def test_restoring(self, Gclass):
        mapped = dict(enumerate("xabcdefghi"))
        SG = Gclass(self.edges)
        SG.add_node(0)
        FG = nx.relabel_nodes(SG, mapping=mapped)
        directed = SG.is_directed()
        _restore_Ts = _restore_Tinout_Di if directed else _restore_Tinout

        g_info = _GraphInfo(*two_eq, directed, FG, SG, *five_dicts)

        m = {0: "x", 3: "c", 4: "d", 5: "e", 6: "f"}
        m_rev = {"x": 0, "c": 3, "d": 4, "e": 5, "f": 6}

        # initial T sets
        T1 = {2, 7, 9, 8}
        T1_in = {1, 7}
        T2 = {"b", "g", "i", "h"}
        T2_in = {"a", "g"}
        T1_tilde = set()
        T2_tilde = set()

        if directed:
            s_info = _StateInfo(m, m_rev, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)
        else:
            T1 = T1 | T1_in
            T2 = T2 | T2_in
            s_info = _StateInfo(m, m_rev, T1, set(), T1_tilde, T2, set(), T2_tilde)

        # Remove a node from the mapping
        m.pop(0)
        m_rev.pop("x")
        _restore_Ts(0, mapped[0], g_info, s_info)

        T1 = {2, 7, 9, 8}
        T1_in = {1, 7}
        T2 = {"b", "g", "i", "h"}
        T2_in = {"a", "g"}
        T1_tilde = {0}
        T2_tilde = {"x"}
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # Remove a node from the mapping
        m.pop(6)
        m_rev.pop("f")
        _restore_Ts(6, mapped[6], g_info, s_info)

        T1 = {2, 9, 8, 7}
        T1_in = {1}
        T2 = {"b", "i", "h", "g"}
        T2_in = {"a"}
        T1_tilde = {0, 6}
        T2_tilde = {"x", "f"}
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # Remove a node from the mapping
        m.pop(3)
        m_rev.pop("c")
        _restore_Ts(3, mapped[3], g_info, s_info)

        T1 = {9, 8, 7}
        T1_in = {3}
        T2 = {"i", "h", "g"}
        T2_in = {"c"}
        T1_tilde = {0, 6, 1, 2}
        T2_tilde = {"x", "f", "a", "b"}
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # Remove a node from the mapping
        m.pop(5)
        m_rev.pop("e")
        _restore_Ts(5, mapped[5], g_info, s_info)

        T1 = {9, 5}
        T1_in = {3}
        T2 = {"i", "e"}
        T2_in = {"c"}
        T1_tilde = {0, 6, 1, 2, 8, 7}
        T2_tilde = {"x", "f", "a", "b", "h", "g"}
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)

        # Remove a node from the mapping
        m.pop(4)
        m_rev.pop("d")
        _restore_Ts(4, mapped[4], g_info, s_info)

        T1 = set()
        T1_in = set()
        T2 = set()
        T2_in = set()
        T1_tilde = set(SG)
        T2_tilde = set(FG)
        self.check_Ts(directed, s_info, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde)
