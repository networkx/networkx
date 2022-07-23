import collections

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import (
    consistent_PT,
    cut_PT,
)


def compute_Ti(G1, G2, mapping, reverse_mapping):
    T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
    T2 = {
        nbr
        for node in reverse_mapping
        for nbr in G2[node]
        if nbr not in reverse_mapping
    }

    T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in T1}
    T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in T2}
    return T1, T2, T1_out, T2_out


class TestGraphISOFeasibility:
    GraphParameters = collections.namedtuple(
        "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
    )
    StateParameters = collections.namedtuple(
        "StateParameters",
        ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
    )

    def test_different_number_of_selfloops(self):
        G1 = nx.Graph([(0, 0)])
        G2 = nx.Graph([(1, 2), (2, 3)])
        gparams = self.GraphParameters(G1, G2, None, None)
        u, v = 0, 1
        assert not feasibility(u, v, gparams, None)

    def test_const_covered_neighbors(self):
        G1 = nx.Graph([(0, 1), (1, 2), (3, 0), (3, 2)])
        G2 = nx.Graph([("a", "b"), ("b", "c"), ("k", "a"), ("k", "c")])
        gparams = self.GraphParameters(G1, G2, None, None)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, None, None, None, None
        )
        u, v = 3, "k"
        assert consistent_PT(u, v, gparams, sparams)

    def test_const_no_covered_neighbors(self):
        G1 = nx.Graph([(0, 1), (1, 2), (3, 4), (3, 5)])
        G2 = nx.Graph([("a", "b"), ("b", "c"), ("k", "w"), ("k", "z")])
        gparams = self.GraphParameters(G1, G2, None, None)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, None, None, None, None
        )
        u, v = 3, "k"
        assert consistent_PT(u, v, gparams, sparams)

    def test_const_mixed_covered_uncovered_neighbors(self):
        G1 = nx.Graph([(0, 1), (1, 2), (3, 0), (3, 2), (3, 4), (3, 5)])
        G2 = nx.Graph(
            [("a", "b"), ("b", "c"), ("k", "a"), ("k", "c"), ("k", "w"), ("k", "z")]
        )
        gparams = self.GraphParameters(G1, G2, None, None)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, None, None, None, None
        )
        u, v = 3, "k"
        assert consistent_PT(u, v, gparams, sparams)

    def test_const_fail_cases(self):
        G1 = nx.Graph(
            [
                (0, 1),
                (1, 2),
                (10, 0),
                (10, 3),
                (10, 4),
                (10, 5),
                (10, 6),
                (4, 1),
                (5, 3),
            ]
        )
        G2 = nx.Graph(
            [
                ("a", "b"),
                ("b", "c"),
                ("k", "a"),
                ("k", "d"),
                ("k", "e"),
                ("k", "f"),
                ("k", "g"),
                ("e", "b"),
                ("f", "d"),
            ]
        )
        gparams = self.GraphParameters(G1, G2, None, None)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            None,
            None,
            None,
            None,
        )
        u, v = 10, "k"
        assert consistent_PT(u, v, gparams, sparams)

        """
        Delete one uncovered neighbor of u. Notice how it still passes the test. Two reasons for this:
        1. If u, v had different degrees from the beginning, they wouldn't be selected as candidates in the first place.
        2. Even if they are selected, consistency is basically 1-look-ahead, meaning that we take into consideration 
           the relation of the candidates with their mapped neighbors. The node we deleted is not a covered neighbor.
           Such nodes will be checked by the cut_PT function, which is basically the 2-look-ahead, checking the relation
           of the candidates with T1, T2 (in which belongs the node we just deleted). 
        """
        G1.remove_node(6)
        assert consistent_PT(u, v, gparams, sparams)

        # Add one more covered neighbor of u in G1
        G1.add_edge(u, 2)
        assert not consistent_PT(u, v, gparams, sparams)

        # Compensate in G2
        G2.add_edge(v, "c")
        assert consistent_PT(u, v, gparams, sparams)

        # Add one more covered neighbor of v in G2
        G2.add_edge(v, "x")
        G1.add_node(7)
        sparams.mapping.update({7: "x"})
        sparams.reverse_mapping.update({"x": 7})
        assert not consistent_PT(u, v, gparams, sparams)

        # Compendate in G1
        G1.add_edge(u, 7)
        assert consistent_PT(u, v, gparams, sparams)

    def test_cut_inconsistent_labels(self):
        G1 = nx.Graph(
            [
                (0, 1),
                (1, 2),
                (10, 0),
                (10, 3),
                (10, 4),
                (10, 5),
                (10, 6),
                (4, 1),
                (5, 3),
            ]
        )
        G2 = nx.Graph(
            [
                ("a", "b"),
                ("b", "c"),
                ("k", "a"),
                ("k", "d"),
                ("k", "e"),
                ("k", "f"),
                ("k", "g"),
                ("e", "b"),
                ("f", "d"),
            ]
        )

        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {n: "blue" for n in G2.nodes()}
        l1.update({6: "green"})  # Change the label of one neighbor of u

        gparams = self.GraphParameters(G1, G2, l1, l2)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            None,
            None,
            None,
            None,
        )

        u, v = 10, "k"
        assert cut_PT(u, v, gparams, sparams)

    def test_cut_consistent_labels(self):
        G1 = nx.Graph(
            [
                (0, 1),
                (1, 2),
                (10, 0),
                (10, 3),
                (10, 4),
                (10, 5),
                (10, 6),
                (4, 1),
                (5, 3),
            ]
        )
        G2 = nx.Graph(
            [
                ("a", "b"),
                ("b", "c"),
                ("k", "a"),
                ("k", "d"),
                ("k", "e"),
                ("k", "f"),
                ("k", "g"),
                ("e", "b"),
                ("f", "d"),
            ]
        )

        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {n: "blue" for n in G2.nodes()}

        gparams = self.GraphParameters(G1, G2, l1, l2)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5},
            {6},
            {"e", "f"},
            {"g"},
        )

        u, v = 10, "k"
        assert not cut_PT(u, v, gparams, sparams)

    def test_cut_same_labels(self):
        G1 = nx.Graph(
            [
                (0, 1),
                (1, 2),
                (10, 0),
                (10, 3),
                (10, 4),
                (10, 5),
                (10, 6),
                (4, 1),
                (5, 3),
            ]
        )
        mapped = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 10: "k"}
        G2 = nx.relabel_nodes(G1, mapped)
        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {n: "blue" for n in G2.nodes()}

        gparams = self.GraphParameters(G1, G2, l1, l2)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5},
            {6},
            {"e", "f"},
            {"g"},
        )

        u, v = 10, "k"
        assert not cut_PT(u, v, gparams, sparams)

        # Change intersection between G1[u] and T1, so it's not the same as the one between G2[v] and T2
        G1.remove_edge(u, 4)
        assert cut_PT(u, v, gparams, sparams)

        # Compensate in G2
        G2.remove_edge(v, mapped[4])
        assert not cut_PT(u, v, gparams, sparams)

        # Change intersection between G2[v] and T2_out, so it's not the same as the one between G1[u] and T1_out
        G2.remove_edge(v, mapped[6])
        assert cut_PT(u, v, gparams, sparams)

        # Compensate in G1
        G1.remove_edge(u, 6)
        assert not cut_PT(u, v, gparams, sparams)

        # Add disconnected nodes, which will form the new Ti_out
        G1.add_nodes_from([6, 7, 8])
        G2.add_nodes_from(["g", "y", "z"])
        sparams.T1_out.update({6, 7, 8})
        sparams.T2_out.update({"g", "y", "z"})

        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {n: "blue" for n in G2.nodes()}
        gparams = self.GraphParameters(G1, G2, l1, l2)

        assert not cut_PT(u, v, gparams, sparams)

        # Add some new nodes to the mapping
        sparams.mapping.update({6: "g", 7: "y"})
        sparams.reverse_mapping.update({"g": 6, "y": 7})

        # Add more nodes to T1, T2.
        G1.add_edges_from([(6, 20), (7, 20), (6, 21)])
        G2.add_edges_from([("g", "i"), ("g", "j"), ("y", "j")])

        sparams.mapping.update({20: "j", 21: "i"})
        sparams.reverse_mapping.update({"j": 20, "i": 21})
        sparams.T1.update({20, 21})
        sparams.T2.update({"i", "j"})
        sparams.T1_out.difference_update({6, 7})
        sparams.T2_out.difference_update({"g", "y"})

        assert not cut_PT(u, v, gparams, sparams)

        # Add nodes from the new T1 and T2, as neighbors of u and v respectively
        G1.add_edges_from([(u, 20), (u, 21)])
        G2.add_edges_from([(v, "i"), (v, "j")])
        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {n: "blue" for n in G2.nodes()}
        gparams = self.GraphParameters(G1, G2, l1, l2)

        assert not cut_PT(u, v, gparams, sparams)

        # Change the edges, maintaining the G1[u]-T1 intersection
        G1.remove_edge(u, 20)
        G1.add_edge(u, 4)
        assert not cut_PT(u, v, gparams, sparams)

        # Connect u to 8 which is still in T1_out
        G1.add_edge(u, 8)
        assert cut_PT(u, v, gparams, sparams)

        # Same for v and z, so that inters(G1[u], T1out) == inters(G2[v], T2out)
        G2.add_edge(v, "z")
        assert not cut_PT(u, v, gparams, sparams)

    def test_cut_different_labels(self):
        G1 = nx.Graph(
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
                (20, 3),
                (20, 5),
                (20, 0),
            ]
        )
        mapped = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h",
            8: "i",
            9: "j",
            10: "k",
            11: "l",
            12: "m",
            13: "n",
            14: "o",
            15: "p",
            20: "x",
        }
        G2 = nx.relabel_nodes(G1, mapped)

        l1 = {n: "none" for n in G1.nodes()}
        l2 = dict()

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
        l2.update({mapped[n]: l for n, l in l1.items()})

        gparams = self.GraphParameters(G1, G2, l1, l2)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5, 6, 7, 14},
            {9, 10, 15, 12, 11, 13, 8},
            {"e", "f", "g", "h", "o"},
            {"j", "k", "l", "m", "n", "i", "p"},
        )

        u, v = 20, "x"
        assert not cut_PT(u, v, gparams, sparams)

        # Change the orientation of the labels on neighbors of u compared to neighbors of v. Leave the structure intact
        l1.update({9: "red"})
        assert cut_PT(u, v, gparams, sparams)

        # compensate in G2
        l2.update({mapped[9]: "red"})
        assert not cut_PT(u, v, gparams, sparams)

        # Change the intersection of G1[u] and T1
        G1.add_edge(u, 4)
        assert cut_PT(u, v, gparams, sparams)

        # Same for G2[v] and T2
        G2.add_edge(v, mapped[4])
        assert not cut_PT(u, v, gparams, sparams)

        # Change the intersection of G2[v] and T2_out
        G2.remove_edge(v, mapped[8])
        assert cut_PT(u, v, gparams, sparams)

        # Same for G1[u] and T1_out
        G1.remove_edge(u, 8)
        assert not cut_PT(u, v, gparams, sparams)

        # Place 8 and mapped[8] in T1 and T2 respectively, by connecting it to covered nodes
        G1.add_edge(8, 3)
        G2.add_edge(mapped[8], mapped[3])
        sparams.T1.add(8)
        sparams.T2.add(mapped[8])
        sparams.T1_out.remove(8)
        sparams.T2_out.remove(mapped[8])

        assert not cut_PT(u, v, gparams, sparams)

        # Remove neighbor of u from T1
        G1.remove_node(5)
        l1.pop(5)
        sparams.T1.remove(5)
        assert cut_PT(u, v, gparams, sparams)

        # Same in G2
        G2.remove_node(mapped[5])
        l2.pop(mapped[5])
        sparams.T2.remove(mapped[5])
        assert not cut_PT(u, v, gparams, sparams)

    def test_feasibility_same_labels(self):
        G1 = nx.Graph(
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
        mapped = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h",
            8: "i",
            9: "j",
            10: "k",
            11: "l",
            12: "m",
            13: "n",
            14: "o",
            15: "p",
            20: "x",
        }
        G2 = nx.relabel_nodes(G1, mapped)

        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {mapped[n]: "blue" for n in G1.nodes()}

        gparams = self.GraphParameters(G1, G2, l1, l2)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5, 6, 7, 14},
            {9, 10, 15, 12, 11, 13, 8},
            {"e", "f", "g", "h", "o"},
            {"j", "k", "l", "m", "n", "i", "p"},
        )

        u, v = 20, "x"
        assert not cut_PT(u, v, gparams, sparams)

        # Change structure in G2 such that, ONLY consistency is harmed
        G2.remove_edge(mapped[20], mapped[2])
        G2.add_edge(mapped[20], mapped[3])

        # Consistency check fails, while the cutting rules are satisfied!
        assert not cut_PT(u, v, gparams, sparams)
        assert not consistent_PT(u, v, gparams, sparams)

        # Compensate in G1 and make it consistent
        G1.remove_edge(20, 2)
        G1.add_edge(20, 3)
        assert not cut_PT(u, v, gparams, sparams)
        assert consistent_PT(u, v, gparams, sparams)

        # ONLY fail the cutting check
        G2.add_edge(v, mapped[10])
        assert cut_PT(u, v, gparams, sparams)
        assert consistent_PT(u, v, gparams, sparams)

    def test_feasibility_different_labels(self):
        G1 = nx.Graph(
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
        mapped = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h",
            8: "i",
            9: "j",
            10: "k",
            11: "l",
            12: "m",
            13: "n",
            14: "o",
            15: "p",
            20: "x",
        }
        G2 = nx.relabel_nodes(G1, mapped)

        l1 = {n: "none" for n in G1.nodes()}
        l2 = dict()

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
        l2.update({mapped[n]: l for n, l in l1.items()})

        gparams = self.GraphParameters(G1, G2, l1, l2)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5, 6, 7, 14},
            {9, 10, 15, 12, 11, 13, 8},
            {"e", "f", "g", "h", "o"},
            {"j", "k", "l", "m", "n", "i", "p"},
        )

        u, v = 20, "x"
        assert not cut_PT(u, v, gparams, sparams)

        # Change structure in G2 such that, ONLY consistency is harmed
        G2.remove_edge(mapped[20], mapped[2])
        G2.add_edge(mapped[20], mapped[3])
        l2.update({mapped[3]: "green"})

        # Consistency check fails, while the cutting rules are satisfied!
        assert not cut_PT(u, v, gparams, sparams)
        assert not consistent_PT(u, v, gparams, sparams)

        # Compensate in G1 and make it consistent
        G1.remove_edge(20, 2)
        G1.add_edge(20, 3)
        l1.update({3: "green"})
        assert not cut_PT(u, v, gparams, sparams)
        assert consistent_PT(u, v, gparams, sparams)

        # ONLY fail the cutting check
        l1.update({5: "red"})
        assert cut_PT(u, v, gparams, sparams)
        assert consistent_PT(u, v, gparams, sparams)


class TestMultiGraphISOFeasibility:
    GraphParameters = collections.namedtuple(
        "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
    )
    StateParameters = collections.namedtuple(
        "StateParameters",
        ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
    )

    def test_different_number_of_selfloops(self):
        G1 = nx.MultiGraph([(0, 0), (0, 0), (0, 0)])
        G2 = nx.MultiGraph([(1, 2), (1, 1), (1, 1), (2, 3)])
        gparams = self.GraphParameters(G1, G2, None, None)
        u, v = 0, 1
        assert not feasibility(u, v, gparams, None)

    def test_const_covered_neighbors(self):
        G1 = nx.MultiGraph(
            [(0, 1), (0, 1), (1, 2), (3, 0), (3, 0), (3, 0), (3, 2), (3, 2)]
        )
        G2 = nx.MultiGraph(
            [
                ("a", "b"),
                ("a", "b"),
                ("b", "c"),
                ("k", "a"),
                ("k", "a"),
                ("k", "a"),
                ("k", "c"),
                ("k", "c"),
            ]
        )
        gparams = self.GraphParameters(G1, G2, None, None)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, None, None, None, None
        )
        u, v = 3, "k"
        assert consistent_PT(u, v, gparams, sparams)

    def test_const_no_covered_neighbors(self):
        G1 = nx.MultiGraph([(0, 1), (0, 1), (1, 2), (3, 4), (3, 4), (3, 5)])
        G2 = nx.MultiGraph([("a", "b"), ("b", "c"), ("k", "w"), ("k", "w"), ("k", "z")])
        gparams = self.GraphParameters(G1, G2, None, None)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, None, None, None, None
        )
        u, v = 3, "k"
        assert consistent_PT(u, v, gparams, sparams)

    def test_const_mixed_covered_uncovered_neighbors(self):
        G1 = nx.MultiGraph(
            [(0, 1), (1, 2), (3, 0), (3, 0), (3, 0), (3, 2), (3, 2), (3, 4), (3, 5)]
        )
        G2 = nx.MultiGraph(
            [
                ("a", "b"),
                ("b", "c"),
                ("k", "a"),
                ("k", "a"),
                ("k", "a"),
                ("k", "c"),
                ("k", "c"),
                ("k", "w"),
                ("k", "z"),
            ]
        )
        gparams = self.GraphParameters(G1, G2, None, None)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c"}, {"a": 0, "b": 1, "c": 2}, None, None, None, None
        )
        u, v = 3, "k"
        assert consistent_PT(u, v, gparams, sparams)

    def test_const_fail_cases(self):
        G1 = nx.MultiGraph(
            [
                (0, 1),
                (1, 2),
                (10, 0),
                (10, 0),
                (10, 0),
                (10, 3),
                (10, 3),
                (10, 4),
                (10, 5),
                (10, 6),
                (10, 6),
                (4, 1),
                (5, 3),
            ]
        )
        mapped = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 10: "k"}
        G2 = nx.relabel_nodes(G1, mapped)

        gparams = self.GraphParameters(G1, G2, None, None)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            None,
            None,
            None,
            None,
        )
        u, v = 10, "k"
        assert consistent_PT(u, v, gparams, sparams)

        """
        Delete one uncovered neighbor of u. Notice how it still passes the test. Two reasons for this:
        1. If u, v had different degrees from the beginning, they wouldn't be selected as candidates in the first place.
        2. Even if they are selected, consistency is basically 1-look-ahead, meaning that we take into consideration 
           the relation of the candidates with their mapped neighbors. The node we deleted is not a covered neighbor.
           Such nodes will be checked by the cut_PT function, which is basically the 2-look-ahead, checking the relation
           of the candidates with T1, T2 (in which belongs the node we just deleted). 
        """
        G1.remove_node(6)
        assert consistent_PT(u, v, gparams, sparams)

        # Add one more covered neighbor of u in G1
        G1.add_edge(u, 2)
        assert not consistent_PT(u, v, gparams, sparams)

        # Compensate in G2
        G2.add_edge(v, "c")
        assert consistent_PT(u, v, gparams, sparams)

        # Add one more covered neighbor of v in G2
        G2.add_edge(v, "x")
        G1.add_node(7)
        sparams.mapping.update({7: "x"})
        sparams.reverse_mapping.update({"x": 7})
        assert not consistent_PT(u, v, gparams, sparams)

        # Compendate in G1
        G1.add_edge(u, 7)
        assert consistent_PT(u, v, gparams, sparams)

        # Delete an edge between u and a covered neighbor
        G1.remove_edges_from([(u, 0), (u, 0)])
        assert not consistent_PT(u, v, gparams, sparams)

        # Compensate in G2
        G2.remove_edges_from([(v, mapped[0]), (v, mapped[0])])
        assert consistent_PT(u, v, gparams, sparams)

        # Remove an edge between v and a covered neighbor
        G2.remove_edge(v, mapped[3])
        assert not consistent_PT(u, v, gparams, sparams)

        # Compensate in G1
        G1.remove_edge(u, 3)
        assert consistent_PT(u, v, gparams, sparams)

    def test_cut_same_labels(self):
        G1 = nx.MultiGraph(
            [
                (0, 1),
                (1, 2),
                (10, 0),
                (10, 0),
                (10, 0),
                (10, 3),
                (10, 3),
                (10, 4),
                (10, 4),
                (10, 5),
                (10, 5),
                (10, 5),
                (10, 5),
                (10, 6),
                (10, 6),
                (4, 1),
                (5, 3),
            ]
        )
        mapped = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 10: "k"}
        G2 = nx.relabel_nodes(G1, mapped)
        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {n: "blue" for n in G2.nodes()}

        gparams = self.GraphParameters(G1, G2, l1, l2)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5},
            {6},
            {"e", "f"},
            {"g"},
        )

        u, v = 10, "k"
        assert not cut_PT(u, v, gparams, sparams)

        # Remove one of the multiple edges between u and a neighbor
        G1.remove_edge(u, 4)
        assert cut_PT(u, v, gparams, sparams)

        # Compensate in G2
        G1.remove_edge(u, 4)
        G2.remove_edges_from([(v, mapped[4]), (v, mapped[4])])
        assert not cut_PT(u, v, gparams, sparams)

        # Change intersection between G2[v] and T2_out, so it's not the same as the one between G1[u] and T1_out
        G2.remove_edge(v, mapped[6])
        assert cut_PT(u, v, gparams, sparams)

        # Compensate in G1
        G1.remove_edge(u, 6)
        assert not cut_PT(u, v, gparams, sparams)

        # Add more edges between u and neighbor which belongs in T1_out
        G1.add_edges_from([(u, 5), (u, 5), (u, 5)])
        assert cut_PT(u, v, gparams, sparams)

        # Compensate in G2
        G2.add_edges_from([(v, mapped[5]), (v, mapped[5]), (v, mapped[5])])
        assert not cut_PT(u, v, gparams, sparams)

        # Add disconnected nodes, which will form the new Ti_out
        G1.add_nodes_from([6, 7, 8])
        G2.add_nodes_from(["g", "y", "z"])
        G1.add_edges_from([(u, 6), (u, 6), (u, 6), (u, 8)])
        G2.add_edges_from([(v, "g"), (v, "g"), (v, "g"), (v, "z")])

        sparams.T1_out.update({6, 7, 8})
        sparams.T2_out.update({"g", "y", "z"})

        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {n: "blue" for n in G2.nodes()}
        gparams = self.GraphParameters(G1, G2, l1, l2)

        assert not cut_PT(u, v, gparams, sparams)

        # Add some new nodes to the mapping
        sparams.mapping.update({6: "g", 7: "y"})
        sparams.reverse_mapping.update({"g": 6, "y": 7})

        # Add more nodes to T1, T2.
        G1.add_edges_from([(6, 20), (7, 20), (6, 21)])
        G2.add_edges_from([("g", "i"), ("g", "j"), ("y", "j")])

        sparams.T1.update({20, 21})
        sparams.T2.update({"i", "j"})
        sparams.T1_out.difference_update({6, 7})
        sparams.T2_out.difference_update({"g", "y"})

        assert not cut_PT(u, v, gparams, sparams)

        # Remove some edges
        G2.remove_edge(v, "g")
        assert cut_PT(u, v, gparams, sparams)

        G1.remove_edge(u, 6)
        G1.add_edge(u, 8)
        G2.add_edge(v, "z")
        assert not cut_PT(u, v, gparams, sparams)

        # Add nodes from the new T1 and T2, as neighbors of u and v respectively
        G1.add_edges_from([(u, 20), (u, 20), (u, 20), (u, 21)])
        G2.add_edges_from([(v, "i"), (v, "i"), (v, "i"), (v, "j")])
        l1 = {n: "blue" for n in G1.nodes()}
        l2 = {n: "blue" for n in G2.nodes()}
        gparams = self.GraphParameters(G1, G2, l1, l2)

        assert not cut_PT(u, v, gparams, sparams)

        # Change the edges
        G1.remove_edge(u, 20)
        G1.add_edge(u, 4)
        assert cut_PT(u, v, gparams, sparams)

        G2.remove_edge(v, "i")
        G2.add_edge(v, mapped[4])
        assert not cut_PT(u, v, gparams, sparams)

    def test_cut_different_labels(self):
        G1 = nx.MultiGraph(
            [
                (0, 1),
                (0, 1),
                (1, 2),
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
                (20, 9),
                (20, 9),
                (20, 15),
                (20, 15),
                (20, 12),
                (20, 11),
                (20, 11),
                (20, 11),
                (12, 13),
                (11, 13),
                (20, 8),
                (20, 8),
                (20, 3),
                (20, 3),
                (20, 5),
                (20, 5),
                (20, 5),
                (20, 0),
                (20, 0),
                (20, 0),
            ]
        )
        mapped = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h",
            8: "i",
            9: "j",
            10: "k",
            11: "l",
            12: "m",
            13: "n",
            14: "o",
            15: "p",
            20: "x",
        }
        G2 = nx.relabel_nodes(G1, mapped)

        l1 = {n: "none" for n in G1.nodes()}
        l2 = dict()

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
        l2.update({mapped[n]: l for n, l in l1.items()})

        gparams = self.GraphParameters(G1, G2, l1, l2)
        sparams = self.StateParameters(
            {0: "a", 1: "b", 2: "c", 3: "d"},
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {4, 5, 6, 7, 14},
            {9, 10, 15, 12, 11, 13, 8},
            {"e", "f", "g", "h", "o"},
            {"j", "k", "l", "m", "n", "i", "p"},
        )

        u, v = 20, "x"
        assert not cut_PT(u, v, gparams, sparams)

        # Change the orientation of the labels on neighbors of u compared to neighbors of v. Leave the structure intact
        l1.update({9: "red"})
        assert cut_PT(u, v, gparams, sparams)

        # compensate in G2
        l2.update({mapped[9]: "red"})
        assert not cut_PT(u, v, gparams, sparams)

        # Change the intersection of G1[u] and T1
        G1.add_edge(u, 4)
        assert cut_PT(u, v, gparams, sparams)

        # Same for G2[v] and T2
        G2.add_edge(v, mapped[4])
        assert not cut_PT(u, v, gparams, sparams)

        # Delete one from the multiple edges
        G2.remove_edge(v, mapped[8])
        assert cut_PT(u, v, gparams, sparams)

        # Same for G1[u] and T1_out
        G1.remove_edge(u, 8)
        assert not cut_PT(u, v, gparams, sparams)

        # Place 8 and mapped[8] in T1 and T2 respectively, by connecting it to covered nodes
        G1.add_edges_from([(8, 3), (8, 3), (8, u)])
        G2.add_edges_from([(mapped[8], mapped[3]), (mapped[8], mapped[3])])
        sparams.T1.add(8)
        sparams.T2.add(mapped[8])
        sparams.T1_out.remove(8)
        sparams.T2_out.remove(mapped[8])

        assert cut_PT(u, v, gparams, sparams)

        # Fix uneven edges
        G1.remove_edge(8, u)
        assert not cut_PT(u, v, gparams, sparams)

        # Remove neighbor of u from T1
        G1.remove_node(5)
        l1.pop(5)
        sparams.T1.remove(5)
        assert cut_PT(u, v, gparams, sparams)

        # Same in G2
        G2.remove_node(mapped[5])
        l2.pop(mapped[5])
        sparams.T2.remove(mapped[5])
        assert not cut_PT(u, v, gparams, sparams)


# class TestFeasibilityISO:
#     V = 2000
# G = nx.gnp_random_graph(V, 0.67, seed=42)
# colors = [
#     "blue",
#     "red",
#     "green",
#     "orange",
#     "grey",
#     "yellow",
#     "purple",
#     "black",
#     "white",
# ]
# for i in range(V):
#     G.nodes[i]["label"] = colors[random.randrange(len(colors))]
#
# def test_prune_iso(self):
#     G1_labels = {n: self.G.nodes[n]["label"] for n in self.G.nodes()}
#     G2_labels = G1_labels
#
#     m = {
#         node: node
#         for node in self.G.nodes()
#         if node < self.G.number_of_nodes() // 4
#     }
#     T1, T2, T1_out, T2_out = compute_Ti(self.G, self.G, m, m)
#
#     GraphParameters = collections.namedtuple(
#         "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
#     )
#     StateParameters = collections.namedtuple(
#         "StateParameters",
#         ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
#     )
#
#     graph_params = GraphParameters(self.G, self.G, G1_labels, G2_labels)
#     state_params = StateParameters(m, m, T1, T1_out, T2, T2_out)
#
#     cnt = 0
#     feasible = -1
#     for n in self.G.nodes():
#         if not cut_PT(1756, n, graph_params, state_params):
#             feasible = n
#             cnt += 1
#     assert cnt == 1
#     assert feasible == 1756
#
# def test_iso_feasibility1(self):
#     """Uses the same graph as G1 and G2, and checks if there is only one feasible candidate for every node of G1."""
#     G1_labels = {n: self.G.nodes[n]["label"] for n in self.G.nodes()}
#     G2_labels = G1_labels
#     m = {
#         node: node
#         for node in self.G.nodes()
#         if node < self.G.number_of_nodes() // 4
#     }
#     T1, T2, T1_out, T2_out = compute_Ti(self.G, self.G, m, m)
#
#     GraphParameters = collections.namedtuple(
#         "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
#     )
#     StateParameters = collections.namedtuple(
#         "StateParameters",
#         ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
#     )
#
#     graph_params = GraphParameters(self.G, self.G, G1_labels, G2_labels)
#     state_params = StateParameters(m, m, T1, T1_out, T2, T2_out)
#
#     cnt = 0
#     feasible = -1
#     for n in self.G.nodes():
#         if feasibility(1999, n, graph_params, state_params):
#             feasible = n
#             cnt += 1
#     assert cnt == 1
#     assert feasible == 1999
#
# def test_iso_feasibility2(self):
#     """Uses two isomorphic graphs with different nodes but same labels. For every node of G1, its mapped node from
#     G2 must be feasible. Apart from its mapped counterpart, there could be more than one feasible candidates,
#     because all the nodes have the same label, so the checking is based on degree mainly.
#     """
#     G1 = nx.Graph()
#     G2 = nx.Graph()
#
#     G1_edges = [
#         (1, 2),
#         (1, 4),
#         (1, 5),
#         (2, 3),
#         (2, 4),
#         (3, 4),
#         (4, 5),
#         (1, 6),
#         (6, 7),
#         (6, 8),
#         (8, 9),
#         (7, 9),
#     ]
#     G2_edges = [
#         (1, 2),
#         (2, 3),
#         (3, 4),
#         (1, 4),
#         (4, 9),
#         (9, 8),
#         (8, 7),
#         (7, 6),
#         (8, 6),
#         (9, 6),
#         (5, 6),
#         (5, 9),
#     ]
#
#     G1.add_edges_from(G1_edges)
#     G2.add_edges_from(G2_edges)
#     G1.add_node(0)
#     G2.add_node(0)
#
#     mapped_nodes = {0: 0, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 1, 8: 3, 9: 2}
#
#     # same labels
#     for n in G1.nodes():
#         G1.nodes[n]["label"] = "blue"
#         G2.nodes[n]["label"] = "blue"
#
#     G1_labels = {node: G1.nodes[node]["label"] for node in G1.nodes()}
#     G2_labels = {node: G2.nodes[node]["label"] for node in G2.nodes()}
#
#     mapping = dict()
#     reverse_mapping = dict()
#     T1, T2, T1_out, T2_out = compute_Ti(G1, G2, mapping, reverse_mapping)
#
#     GraphParameters = collections.namedtuple(
#         "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
#     )
#     StateParameters = collections.namedtuple(
#         "StateParameters",
#         ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
#     )
#
#     graph_params = GraphParameters(G1, G2, G1_labels, G2_labels)
#     state_params = StateParameters(mapping, reverse_mapping, T1, T1_out, T2, T2_out)
#
#     for node1 in G1.nodes():
#         for node2 in G2.nodes():
#             if node2 == mapped_nodes[node1]:
#                 assert feasibility(node1, node2, graph_params, state_params)
#
# def test_iso_feasibility3(self):
#     """Uses two isomorphic graphs with different nodes and labels. For every node of G1, ONLY its mapped node from
#     G2 must be feasible. We cannot have more than one feasible candidates, because every mapped pair has a unique
#     label tha represents it.
#     """
#     G1 = nx.Graph()
#     G2 = nx.Graph()
#
#     G1_edges = [
#         (1, 2),
#         (1, 4),
#         (1, 5),
#         (2, 3),
#         (2, 4),
#         (3, 4),
#         (4, 5),
#         (1, 6),
#         (6, 7),
#         (6, 8),
#         (8, 9),
#         (7, 9),
#     ]
#     G2_edges = [
#         (1, 2),
#         (2, 3),
#         (3, 4),
#         (1, 4),
#         (4, 9),
#         (9, 8),
#         (8, 7),
#         (7, 6),
#         (8, 6),
#         (9, 6),
#         (5, 6),
#         (5, 9),
#     ]
#
#     G1.add_edges_from(G1_edges)
#     G2.add_edges_from(G2_edges)
#     G1.add_node(0)
#     G2.add_node(0)
#
#     mapped_nodes = {0: 0, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 1, 8: 3, 9: 2}
#
#     # different labels
#     colors = [
#         "white",
#         "black",
#         "green",
#         "purple",
#         "orange",
#         "red",
#         "blue",
#         "pink",
#         "yellow",
#         "none",
#     ]
#     for node, color in zip(G1.nodes, colors):
#         G1.nodes[node]["label"] = color
#         G2.nodes[mapped_nodes[node]]["label"] = color
#
#     G1_labels = {node: G1.nodes[node]["label"] for node in G1.nodes()}
#     G2_labels = {node: G2.nodes[node]["label"] for node in G2.nodes()}
#
#     mapping = dict()
#     reverse_mapping = dict()
#     T1, T2, T1_out, T2_out = compute_Ti(G1, G2, mapping, reverse_mapping)
#
#     GraphParameters = collections.namedtuple(
#         "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
#     )
#     StateParameters = collections.namedtuple(
#         "StateParameters",
#         ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
#     )
#
#     graph_params = GraphParameters(G1, G2, G1_labels, G2_labels)
#     state_params = StateParameters(mapping, reverse_mapping, T1, T1_out, T2, T2_out)
#
#     for node1 in G1.nodes():
#         for node2 in G2.nodes():
#             if node2 == mapped_nodes[node1]:
#                 assert feasibility(node1, node2, graph_params, state_params)
# else:
#     assert not check_feasibility(node1, node2, G1, G2, G1_labels, G2_labels, mapping, reverse_mapping,
#                                  T1, T1_out, T2, T2_out)
# This fails because the two candidate nodes labels are checked in the candidate selection, not feasibility.
