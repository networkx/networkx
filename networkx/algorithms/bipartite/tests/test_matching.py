"""Unit tests for the :mod:`networkx.algorithms.bipartite.matching` module."""
import itertools

import pytest

import networkx as nx
from networkx.algorithms.bipartite.matching import (
    eppstein_matching,
    hopcroft_karp_matching,
    maximum_envy_free_matching,
    maximum_matching,
    minimum_weight_envy_free_matching,
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


def test_envy_free_matching_partition():
    # Perfect matching
    G = nx.complete_bipartite_graph(3, 3)
    M = nx.bipartite.hopcroft_karp_matching(G)
    tup = nx.bipartite.envy_free_matching_partition(G, M=M)

    assert tup == ({0, 1, 2}, set(), {3, 4, 5}, set())

    # Non-empty EFM partition
    G = nx.Graph([(0, 3), (0, 4), (1, 4), (2, 4)])
    M = {0: 3, 3: 0, 1: 4, 4: 1}
    tup = nx.bipartite.envy_free_matching_partition(G, M=M)

    assert tup == ({0}, {1, 2}, {3}, {4})

    # Odd path - X_L and Y_L should be empty
    G = nx.Graph([(0, 3), (1, 3), (1, 4), (2, 4)])
    M = {0: 3, 3: 0, 4: 1, 1: 4}
    tup = nx.bipartite.envy_free_matching_partition(G, M=M)
    assert tup == (set(), {0, 1, 2}, set(), {3, 4})

    # Y-path-saturated graph
    G = nx.Graph(
        [(0, 6), (1, 6), (1, 7), (2, 6), (2, 8), (3, 9), (3, 6), (4, 8), (4, 7), (5, 9)]
    )
    M = {0: 6, 6: 0, 1: 7, 7: 1, 2: 8, 8: 2, 3: 9, 9: 3}
    tup = nx.bipartite.envy_free_matching_partition(G, M=M)
    assert tup == (set(), {0, 1, 2, 3, 4, 5}, set(), {8, 9, 6, 7})


def test_envy_free_perfect_matching():
    def _generate_marriable_bipartite_graph(size: int):
        """
        generate_marriable_bipartite_graph

        input: positive number
        output: bipartite graph with both sets of cardinality = size each node has one edge to exactly one node.

        >>> generate_marriable_bipartite_graph(3).edges
        [(0, 3), (1, 4), (2, 5)]
        """
        return nx.Graph([(i, i + size) for i in range(size)])

    A = nx.complete_bipartite_graph(3, 3)
    matching = maximum_envy_free_matching(A)
    assert matching == {0: 3, 3: 0, 1: 4, 4: 1, 2: 5, 5: 2}

    B = nx.Graph(
        [
            (0, 3),
            (3, 0),
            (0, 4),
            (4, 0),
            (1, 4),
            (4, 1),
            (1, 5),
            (5, 1),
            (2, 5),
            (5, 2),
        ]
    )
    matching = maximum_envy_free_matching(B)
    assert matching == {0: 3, 3: 0, 1: 4, 4: 1, 2: 5, 5: 2}

    # Check our algorithm with big inputs, array can be expanded to contain more values for which to generate graphs
    sizes = [10, 100, 10000]
    for size in sizes:
        G = _generate_marriable_bipartite_graph(size)
        if nx.is_connected(G):
            matching = maximum_envy_free_matching(G)
            expected1 = {i: i + size for i in range(size)}
            expected2 = {i + size: i for i in range(size)}
            expected = {**expected1, **expected2}
            assert matching == expected


def test_non_empty_envy_free_matching():
    A = nx.Graph([(0, 3), (3, 0), (0, 4), (4, 0), (1, 4), (4, 1), (2, 4), (4, 2)])
    matching = maximum_envy_free_matching(A)
    assert matching == {0: 3, 3: 0}

    B = nx.Graph(
        [
            (0, 4),
            (4, 0),
            (0, 5),
            (5, 0),
            (0, 8),
            (8, 0),
            (1, 6),
            (6, 1),
            (2, 7),
            (7, 2),
            (3, 7),
            (7, 3),
        ]
    )
    matching = maximum_envy_free_matching(B, top_nodes=[0, 1, 2, 3])
    assert matching == {0: 4, 4: 0, 1: 6, 6: 1}


def test_empty_envy_free_matching():
    def _generate_odd_path(size):
        """
        generate_odd_path

        input: positive odd(!!) number
        output: bipartite graph with one set of cardinality = size
                and one set of cardinality = size - 1
                with the shape of an odd path.

        >>> generate_odd_path(3).edges
        [(0, 3), (1, 3), (1, 4), (2, 4), (3, 0), (3, 1), (4, 1), (4, 2)]

        """
        if size % 2 == 0:
            raise Exception

        edges = [(0, size)]

        actions = {
            0: lambda: edges.append((edges[-1][0], edges[-1][1] + 1)),
            1: lambda: edges.append((edges[-1][0] + 1, edges[-1][1])),
        }

        for i in range(1, size + 1):
            actions[i % 2]()
        return nx.Graph(edges)

    A = _generate_odd_path(3)  # check small input first

    B = nx.Graph(
        [
            (0, 6),
            (6, 0),
            (1, 6),
            (6, 1),
            (1, 7),
            (7, 1),
            (2, 6),
            (6, 2),
            (2, 8),
            (8, 2),
            (3, 9),
            (9, 3),
            (3, 6),
            (6, 3),
            (4, 8),
            (8, 4),
            (4, 7),
            (7, 4),
            (5, 9),
            (9, 5),
        ]
    )  # more intricate graph

    C = _generate_odd_path(11)  # check big inputs
    D = _generate_odd_path(
        501
    )  # check even bigger inputs, may take too long, adjust the given value as needed

    graphs = {A, B, C, D}
    for graph in graphs:
        if nx.is_connected(graph):
            assert maximum_envy_free_matching(G=graph) == {}


def test_envy_free_perfect_matching_min_weight():
    G = nx.Graph()
    weights = [
        (0, 3, 250),
        (0, 4, 148),
        (0, 5, 122),
        (1, 3, 175),
        (1, 4, 135),
        (1, 5, 150),
        (2, 3, 150),
        (2, 4, 125),
    ]
    G.add_weighted_edges_from(weights)
    assert minimum_weight_envy_free_matching(G) == {
        0: 5,
        1: 4,
        2: 3,
        5: 0,
        4: 1,
        3: 2,
    }


def test_non_empty_envy_free_matching_min_weight():
    G = nx.Graph()
    G.add_weighted_edges_from(
        [(0, 4, 5), (1, 4, 1), (2, 5, 3), (2, 7, 9), (3, 6, 3), (3, 7, 7)]
    )
    matching = minimum_weight_envy_free_matching(G, top_nodes=[0, 1, 2, 3])
    assert matching == {
        2: 5,
        3: 6,
        5: 2,
        6: 3,
    }
