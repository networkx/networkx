"""Unit tests for the :mod:`networkx.algorithms.bipartite.matching` module."""
import itertools

import pytest

import networkx as nx
from networkx.algorithms.bipartite.matching import (
    dulmage_mendelsohn_decomposition,
    eppstein_matching,
    hopcroft_karp_matching,
    maximum_matching,
    minimum_weight_full_matching,
    to_vertex_cover,
)


class TestMatching:
    """Tests for bipartite matching algorithms."""

    def setup_method(self):
        """Creates a bipartite graph for use in testing matching algorithms.

        The bipartite graph has a maximum cardinality matching that leaves
        vertex 1 and vertex 10 unmatched. The first six numbers are the left
        vertices and the next six numbers are the right vertices.

        """
        self.simple_graph = nx.complete_bipartite_graph(2, 3)
        self.simple_solution = {0: 2, 1: 3, 2: 0, 3: 1}

        edges = [(0, 7), (0, 8), (2, 6), (2, 9), (3, 8), (4, 8), (4, 9), (5, 11)]
        self.top_nodes = set(range(6))
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(12))
        self.graph.add_edges_from(edges)

        # Example bipartite graph from issue 2127
        G = nx.Graph()
        G.add_nodes_from(
            [
                (1, "C"),
                (1, "B"),
                (0, "G"),
                (1, "F"),
                (1, "E"),
                (0, "C"),
                (1, "D"),
                (1, "I"),
                (0, "A"),
                (0, "D"),
                (0, "F"),
                (0, "E"),
                (0, "H"),
                (1, "G"),
                (1, "A"),
                (0, "I"),
                (0, "B"),
                (1, "H"),
            ]
        )
        G.add_edge((1, "C"), (0, "A"))
        G.add_edge((1, "B"), (0, "A"))
        G.add_edge((0, "G"), (1, "I"))
        G.add_edge((0, "G"), (1, "H"))
        G.add_edge((1, "F"), (0, "A"))
        G.add_edge((1, "F"), (0, "C"))
        G.add_edge((1, "F"), (0, "E"))
        G.add_edge((1, "E"), (0, "A"))
        G.add_edge((1, "E"), (0, "C"))
        G.add_edge((0, "C"), (1, "D"))
        G.add_edge((0, "C"), (1, "I"))
        G.add_edge((0, "C"), (1, "G"))
        G.add_edge((0, "C"), (1, "H"))
        G.add_edge((1, "D"), (0, "A"))
        G.add_edge((1, "I"), (0, "A"))
        G.add_edge((1, "I"), (0, "E"))
        G.add_edge((0, "A"), (1, "G"))
        G.add_edge((0, "A"), (1, "H"))
        G.add_edge((0, "E"), (1, "G"))
        G.add_edge((0, "E"), (1, "H"))
        self.disconnected_graph = G

    def check_match(self, matching):
        """Asserts that the matching is what we expect from the bipartite graph
        constructed in the :meth:`setup` fixture.

        """
        # For the sake of brevity, rename `matching` to `M`.
        M = matching
        matched_vertices = frozenset(itertools.chain(*M.items()))
        # Assert that the maximum number of vertices (10) is matched.
        assert matched_vertices == frozenset(range(12)) - {1, 10}
        # Assert that no vertex appears in two edges, or in other words, that
        # the matching (u, v) and (v, u) both appear in the matching
        # dictionary.
        assert all(u == M[M[u]] for u in range(12) if u in M)

    def check_vertex_cover(self, vertices):
        """Asserts that the given set of vertices is the vertex cover we
        expected from the bipartite graph constructed in the :meth:`setup`
        fixture.

        """
        # By Konig's theorem, the number of edges in a maximum matching equals
        # the number of vertices in a minimum vertex cover.
        assert len(vertices) == 5
        # Assert that the set is truly a vertex cover.
        for u, v in self.graph.edges():
            assert u in vertices or v in vertices
        # TODO Assert that the vertices are the correct ones.

    def test_eppstein_matching(self):
        """Tests that David Eppstein's implementation of the Hopcroft--Karp
        algorithm produces a maximum cardinality matching.

        """
        self.check_match(eppstein_matching(self.graph, self.top_nodes))

    def test_hopcroft_karp_matching(self):
        """Tests that the Hopcroft--Karp algorithm produces a maximum
        cardinality matching in a bipartite graph.

        """
        self.check_match(hopcroft_karp_matching(self.graph, self.top_nodes))

    def test_to_vertex_cover(self):
        """Test for converting a maximum matching to a minimum vertex cover."""
        matching = maximum_matching(self.graph, self.top_nodes)
        vertex_cover = to_vertex_cover(self.graph, matching, self.top_nodes)
        self.check_vertex_cover(vertex_cover)

    def test_eppstein_matching_simple(self):
        match = eppstein_matching(self.simple_graph)
        assert match == self.simple_solution

    def test_hopcroft_karp_matching_simple(self):
        match = hopcroft_karp_matching(self.simple_graph)
        assert match == self.simple_solution

    def test_eppstein_matching_disconnected(self):
        with pytest.raises(nx.AmbiguousSolution):
            match = eppstein_matching(self.disconnected_graph)

    def test_hopcroft_karp_matching_disconnected(self):
        with pytest.raises(nx.AmbiguousSolution):
            match = hopcroft_karp_matching(self.disconnected_graph)

    def test_issue_2127(self):
        """Test from issue 2127"""
        # Build the example DAG
        G = nx.DiGraph()
        G.add_edge("A", "C")
        G.add_edge("A", "B")
        G.add_edge("C", "E")
        G.add_edge("C", "D")
        G.add_edge("E", "G")
        G.add_edge("E", "F")
        G.add_edge("G", "I")
        G.add_edge("G", "H")

        tc = nx.transitive_closure(G)
        btc = nx.Graph()

        # Create a bipartite graph based on the transitive closure of G
        for v in tc.nodes():
            btc.add_node((0, v))
            btc.add_node((1, v))

        for u, v in tc.edges():
            btc.add_edge((0, u), (1, v))

        top_nodes = {n for n in btc if n[0] == 0}
        matching = hopcroft_karp_matching(btc, top_nodes)
        vertex_cover = to_vertex_cover(btc, matching, top_nodes)
        independent_set = set(G) - {v for _, v in vertex_cover}
        assert {"B", "D", "F", "I", "H"} == independent_set

    def test_vertex_cover_issue_2384(self):
        G = nx.Graph([(0, 3), (1, 3), (1, 4), (2, 3)])
        matching = maximum_matching(G)
        vertex_cover = to_vertex_cover(G, matching)
        for u, v in G.edges():
            assert u in vertex_cover or v in vertex_cover

    def test_vertex_cover_issue_3306(self):
        G = nx.Graph()
        edges = [(0, 2), (1, 0), (1, 1), (1, 2), (2, 2)]
        G.add_edges_from([((i, "L"), (j, "R")) for i, j in edges])

        matching = maximum_matching(G)
        vertex_cover = to_vertex_cover(G, matching)
        for u, v in G.edges():
            assert u in vertex_cover or v in vertex_cover

    def test_unorderable_nodes(self):
        a = object()
        b = object()
        c = object()
        d = object()
        e = object()
        G = nx.Graph([(a, d), (b, d), (b, e), (c, d)])
        matching = maximum_matching(G)
        vertex_cover = to_vertex_cover(G, matching)
        for u, v in G.edges():
            assert u in vertex_cover or v in vertex_cover


def test_eppstein_matching():
    """Test in accordance to issue #1927"""
    G = nx.Graph()
    G.add_nodes_from(["a", 2, 3, 4], bipartite=0)
    G.add_nodes_from([1, "b", "c"], bipartite=1)
    G.add_edges_from([("a", 1), ("a", "b"), (2, "b"), (2, "c"), (3, "c"), (4, 1)])
    matching = eppstein_matching(G)
    assert len(matching) == len(maximum_matching(G))
    assert all(x in set(matching.keys()) for x in set(matching.values()))


class TestMinimumWeightFullMatching:
    @classmethod
    def setup_class(cls):
        pytest.importorskip("scipy")

    def test_minimum_weight_full_matching_incomplete_graph(self):
        B = nx.Graph()
        B.add_nodes_from([1, 2], bipartite=0)
        B.add_nodes_from([3, 4], bipartite=1)
        B.add_edge(1, 4, weight=100)
        B.add_edge(2, 3, weight=100)
        B.add_edge(2, 4, weight=50)
        matching = minimum_weight_full_matching(B)
        assert matching == {1: 4, 2: 3, 4: 1, 3: 2}

    def test_minimum_weight_full_matching_with_no_full_matching(self):
        B = nx.Graph()
        B.add_nodes_from([1, 2, 3], bipartite=0)
        B.add_nodes_from([4, 5, 6], bipartite=1)
        B.add_edge(1, 4, weight=100)
        B.add_edge(2, 4, weight=100)
        B.add_edge(3, 4, weight=50)
        B.add_edge(3, 5, weight=50)
        B.add_edge(3, 6, weight=50)
        with pytest.raises(ValueError):
            minimum_weight_full_matching(B)

    def test_minimum_weight_full_matching_square(self):
        G = nx.complete_bipartite_graph(3, 3)
        G.add_edge(0, 3, weight=400)
        G.add_edge(0, 4, weight=150)
        G.add_edge(0, 5, weight=400)
        G.add_edge(1, 3, weight=400)
        G.add_edge(1, 4, weight=450)
        G.add_edge(1, 5, weight=600)
        G.add_edge(2, 3, weight=300)
        G.add_edge(2, 4, weight=225)
        G.add_edge(2, 5, weight=300)
        matching = minimum_weight_full_matching(G)
        assert matching == {0: 4, 1: 3, 2: 5, 4: 0, 3: 1, 5: 2}

    def test_minimum_weight_full_matching_smaller_left(self):
        G = nx.complete_bipartite_graph(3, 4)
        G.add_edge(0, 3, weight=400)
        G.add_edge(0, 4, weight=150)
        G.add_edge(0, 5, weight=400)
        G.add_edge(0, 6, weight=1)
        G.add_edge(1, 3, weight=400)
        G.add_edge(1, 4, weight=450)
        G.add_edge(1, 5, weight=600)
        G.add_edge(1, 6, weight=2)
        G.add_edge(2, 3, weight=300)
        G.add_edge(2, 4, weight=225)
        G.add_edge(2, 5, weight=290)
        G.add_edge(2, 6, weight=3)
        matching = minimum_weight_full_matching(G)
        assert matching == {0: 4, 1: 6, 2: 5, 4: 0, 5: 2, 6: 1}

    def test_minimum_weight_full_matching_smaller_top_nodes_right(self):
        G = nx.complete_bipartite_graph(3, 4)
        G.add_edge(0, 3, weight=400)
        G.add_edge(0, 4, weight=150)
        G.add_edge(0, 5, weight=400)
        G.add_edge(0, 6, weight=1)
        G.add_edge(1, 3, weight=400)
        G.add_edge(1, 4, weight=450)
        G.add_edge(1, 5, weight=600)
        G.add_edge(1, 6, weight=2)
        G.add_edge(2, 3, weight=300)
        G.add_edge(2, 4, weight=225)
        G.add_edge(2, 5, weight=290)
        G.add_edge(2, 6, weight=3)
        matching = minimum_weight_full_matching(G, top_nodes=[3, 4, 5, 6])
        assert matching == {0: 4, 1: 6, 2: 5, 4: 0, 5: 2, 6: 1}

    def test_minimum_weight_full_matching_smaller_right(self):
        G = nx.complete_bipartite_graph(4, 3)
        G.add_edge(0, 4, weight=400)
        G.add_edge(0, 5, weight=400)
        G.add_edge(0, 6, weight=300)
        G.add_edge(1, 4, weight=150)
        G.add_edge(1, 5, weight=450)
        G.add_edge(1, 6, weight=225)
        G.add_edge(2, 4, weight=400)
        G.add_edge(2, 5, weight=600)
        G.add_edge(2, 6, weight=290)
        G.add_edge(3, 4, weight=1)
        G.add_edge(3, 5, weight=2)
        G.add_edge(3, 6, weight=3)
        matching = minimum_weight_full_matching(G)
        assert matching == {1: 4, 2: 6, 3: 5, 4: 1, 5: 3, 6: 2}

    def test_minimum_weight_full_matching_negative_weights(self):
        G = nx.complete_bipartite_graph(2, 2)
        G.add_edge(0, 2, weight=-2)
        G.add_edge(0, 3, weight=0.2)
        G.add_edge(1, 2, weight=-2)
        G.add_edge(1, 3, weight=0.3)
        matching = minimum_weight_full_matching(G)
        assert matching == {0: 3, 1: 2, 2: 1, 3: 0}

    def test_minimum_weight_full_matching_different_weight_key(self):
        G = nx.complete_bipartite_graph(2, 2)
        G.add_edge(0, 2, mass=2)
        G.add_edge(0, 3, mass=0.2)
        G.add_edge(1, 2, mass=1)
        G.add_edge(1, 3, mass=2)
        matching = minimum_weight_full_matching(G, weight="mass")
        assert matching == {0: 3, 1: 2, 2: 1, 3: 0}


class TestDulmageMendelsohnDecomposition:
    def test_pothen_fan_example(self):
        """Test the graph shown in Figure 1 of "Computing the block triangular
        form of a sparse matrix", Pothen and Fan, ACM Trans. Math. Softw., 1990.
        """
        G = nx.Graph()
        NL = 12
        NR = 11
        left_nodes = list(range(NL))
        right_nodes = list(range(NL, NL + NR))

        G.add_nodes_from(left_nodes, bipartite=0)
        G.add_nodes_from(right_nodes, bipartite=1)

        edges = [
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (1, 3),
            (1, 4),
            (1, 6),
            (1, 7),
            (1, 9),
            (2, 0),
            (2, 2),
            (2, 4),
            (3, 5),
            (3, 6),
            (3, 10),
            (4, 5),
            (4, 6),
            (4, 8),
            (5, 7),
            (5, 8),
            (6, 7),
            (6, 8),
            (6, 9),
            (7, 9),
            (7, 10),
            (8, 10),
            (9, 9),
            (10, 9),
            (10, 10),
            (11, 10),
        ]
        # Edges above are labeled as in Pothen & Fan paper. Need to
        # convert into our space of nodes
        edges = [(i, j + NL) for i, j in edges]
        G.add_edges_from(edges)

        reachable_top, reachable_bot, unreachable = dulmage_mendelsohn_decomposition(
            G, left_nodes
        )
        # Here we switch from left/right to top/bot for consistency with
        # function terminology
        top_set = set(left_nodes)
        top_reachable_from_top = [n for n in reachable_top if n in top_set]
        bot_reachable_from_top = [n for n in reachable_top if n not in top_set]
        bot_reachable_from_bot = [n for n in reachable_bot if n not in top_set]
        top_reachable_from_bot = [n for n in reachable_bot if n in top_set]
        top_unreachable = [n for n in unreachable if n in top_set]
        bot_unreachable = [n for n in unreachable if n not in top_set]

        assert top_reachable_from_top == [7, 8, 9, 10, 11]
        assert top_unreachable == [3, 4, 5, 6]
        assert top_reachable_from_bot == [0, 1, 2]
        assert bot_reachable_from_top == [21, 22]
        assert bot_unreachable == [17, 18, 19, 20]
        assert bot_reachable_from_bot == [12, 13, 14, 15, 16]

    def test_bunus_fritzson_simple_example(self):
        """
        Test graph shown in Figure 11 of "Automatic static analysis of
        equation-based components", Bunus and Fritzson, Simulation (2004).
        """
        n_eq = 7
        n_var = 7
        top_nodes = [f"eq{i}" for i in range(1, n_eq + 1)]
        bot_nodes = [f"var{i}" for i in range(1, n_var + 1)]

        G = nx.Graph()
        G.add_nodes_from(top_nodes)
        G.add_nodes_from(bot_nodes)

        edges = [
            ("eq1", "var1"),
            ("eq2", "var1"),
            ("eq2", "var2"),
            ("eq3", "var1"),
            ("eq3", "var2"),
            ("eq4", "var2"),
            ("eq4", "var3"),
            ("eq4", "var4"),
            ("eq5", "var4"),
            ("eq5", "var5"),
            ("eq6", "var3"),
            ("eq6", "var4"),
            ("eq6", "var5"),
            ("eq7", "var5"),
            ("eq7", "var6"),
            ("eq7", "var7"),
        ]
        G.add_edges_from(edges)

        reachable_top, reachable_bot, unreachable = dulmage_mendelsohn_decomposition(
            G, top_nodes
        )

        pred_reachable_top = {"eq1", "eq2", "eq3", "var1", "var2"}
        pred_reachable_bot = {"eq7", "var6", "var7"}
        pred_unreachable = {"eq4", "eq5", "eq6", "var3", "var4", "var5"}

        assert set(reachable_top) == pred_reachable_top
        assert set(reachable_bot) == pred_reachable_bot
        assert set(unreachable) == pred_unreachable

    def test_bunus_fritzson_circuit_example(self):
        """Test graph shown in Figure 15 of "Automatic static analysis of
        equation-based components", Bunus and Fritzson, Simulation (2004).
        """
        n_eq = 15
        n_var = 14
        left_nodes = [f"eq{i}" for i in range(1, n_eq + 1)]
        right_nodes = [f"var{i}" for i in range(1, n_var + 1)]
        G = nx.Graph()
        G.add_nodes_from(left_nodes)
        G.add_nodes_from(right_nodes)

        edges = [
            ("eq1", "var1"),
            ("eq1", "var3"),
            ("eq1", "var5"),
            ("eq2", "var2"),
            ("eq2", "var4"),
            ("eq3", "var2"),
            ("eq3", "var6"),
            ("eq4", "var5"),
            ("eq4", "var6"),
            ("eq5", "var6"),
            ("eq6", "var7"),
            ("eq6", "var9"),
            ("eq6", "var11"),
            ("eq7", "var8"),
            ("eq7", "var10"),
            ("eq8", "var8"),
            ("eq8", "var12"),
            ("eq9", "var11"),
            ("eq10", "var13"),
            ("eq11", "var1"),
            ("eq11", "var7"),
            ("eq12", "var2"),
            ("eq12", "var8"),
            ("eq13", "var3"),
            ("eq13", "var9"),
            ("eq14", "var9"),
            ("eq14", "var13"),
            ("eq15", "var4"),
            ("eq15", "var10"),
            ("eq15", "var14"),
        ]
        G.add_edges_from(edges)

        reach_left, reach_right, unreachable = dulmage_mendelsohn_decomposition(
            G, left_nodes
        )

        pred_reachable_left = {
            "eq1",
            "eq4",
            "eq5",
            "eq6",
            "eq9",
            "eq10",
            "eq11",
            "eq13",
            "eq14",
            "var1",
            "var3",
            "var5",
            "var6",
            "var7",
            "var9",
            "var11",
            "var13",
        }
        pred_unreachable = {
            "eq2",
            "eq3",
            "eq7",
            "eq8",
            "eq12",
            "eq15",
            "var2",
            "var4",
            "var8",
            "var10",
            "var12",
            "var14",
        }

        assert set(reach_left) == pred_reachable_left
        assert set(reach_right) == set()
        assert set(unreachable) == pred_unreachable

    def test_pyomo_example(self):
        """Test the bipartite graph of variables and constraints from the Pyomo
        example of the Dulmage-Mendelsohn partition, accessed at
        https://pyomo.readthedocs.io/en/stable/contributed_packages/incidence/tutorial.dm.html
        on June 17, 2023.
        """
        varnames = [
            "x[1]",
            "x[2]",
            "x[3]",
            "flow[1]",
            "flow[2]",
            "flow[3]",
            "total_flow",
            "density",
        ]
        connames = [
            "sum_eqn",
            "holdup_eqn[1]",
            "holdup_eqn[2]",
            "holdup_eqn[3]",
            "density_eqn",
            "flow_eqn[1]",
            "flow_eqn[2]",
            "flow_eqn[3]",
        ]
        G = nx.Graph()
        G.add_nodes_from(varnames)
        G.add_nodes_from(connames)

        edges = [
            ("sum_eqn", "x[1]"),
            ("sum_eqn", "x[2]"),
            ("sum_eqn", "x[3]"),
            ("holdup_eqn[1]", "x[1]"),
            ("holdup_eqn[1]", "density"),
            ("holdup_eqn[2]", "x[2]"),
            ("holdup_eqn[2]", "density"),
            ("holdup_eqn[3]", "x[3]"),
            ("holdup_eqn[3]", "density"),
            ("density_eqn", "density"),
            ("density_eqn", "x[1]"),
            ("density_eqn", "x[2]"),
            ("density_eqn", "x[3]"),
            ("flow_eqn[1]", "x[1]"),
            ("flow_eqn[1]", "flow[1]"),
            ("flow_eqn[1]", "total_flow"),
            ("flow_eqn[2]", "x[2]"),
            ("flow_eqn[2]", "flow[2]"),
            ("flow_eqn[2]", "total_flow"),
            ("flow_eqn[3]", "x[3]"),
            ("flow_eqn[3]", "flow[3]"),
            ("flow_eqn[3]", "total_flow"),
        ]
        G.add_edges_from(edges)

        reach_from_con, reach_from_var, unreachable = dulmage_mendelsohn_decomposition(
            G, connames
        )

        pred_reachable_from_con = {
            "x[1]",
            "x[2]",
            "x[3]",
            "density",
            "sum_eqn",
            "holdup_eqn[1]",
            "holdup_eqn[2]",
            "holdup_eqn[3]",
            "density_eqn",
        }
        pred_reachable_from_var = {
            "flow[1]",
            "flow[2]",
            "flow[3]",
            "total_flow",
            "flow_eqn[1]",
            "flow_eqn[2]",
            "flow_eqn[3]",
        }

        assert set(reach_from_con) == pred_reachable_from_con
        assert set(reach_from_var) == pred_reachable_from_var
        assert set(unreachable) == set()

    def test_graph_not_bipartite(self):
        G = nx.Graph()
        G.add_nodes_from(range(3))
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])
        top_nodes = [0, 1]

        msg = "Provided graph is not bipartite"
        with pytest.raises(nx.NetworkXError, match=msg):
            dulmage_mendelsohn_decomposition(G, top_nodes)

    def test_invalid_bipartite_set(self):
        G = nx.Graph()
        G.add_nodes_from(range(3))
        G.add_edges_from([(0, 1), (0, 2)])
        top_nodes = [0, 2]
        msg = "Provided nodes are not a valid bipartite set"
        with pytest.raises(nx.NetworkXError, match=msg):
            dulmage_mendelsohn_decomposition(G, top_nodes)

    def test_matching_provided(self):
        G = nx.Graph()
        G.add_nodes_from(range(3))
        G.add_edges_from([(0, 1), (0, 2)])
        top_nodes = [0]
        matching = {0: 1, 1: 0}
        reach_from_top, reach_from_bot, unreach = dulmage_mendelsohn_decomposition(
            G, top_nodes, matching=matching
        )
        assert len(reach_from_top) == 0
        assert set(reach_from_bot) == {0, 1, 2}
        assert len(unreach) == 0
