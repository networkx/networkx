"""Unit tests for the :mod:`networkx.algorithms.bipartite.matching` module."""
import itertools

import pytest

import networkx as nx
from networkx.algorithms.bipartite.matching import (
    eppstein_matching,
    hopcroft_karp_matching,
    maximum_matching,
    minimum_weight_full_matching,
    to_vertex_cover,
)


class TestMatching:
    """Tests for bipartite matching algorithms."""

    def setup(self):
        self.simple_graph = nx.complete_bipartite_graph(2, 3)
        self.simple_solution = {0: 2, 1: 3, 2: 0, 3: 1}

        edges = [(0, 7), (0, 8), (2, 6), (2, 9), (3, 8), (4, 8), (4, 9), (5, 11)]
        self.top_nodes = set(range(6))
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(12))
        self.graph.add_edges_from(edges)

        self.eppstein_edge_case = nx.Graph()
        self.eppstein_edge_case.add_edges_from(
            [
                (0, 5),
                (0, 8),
                (1, 6),
                (1, 7),
                (1, 8),
                (1, 9),
                (2, 6),
                (2, 9),
                (3, 5),
                (3, 6),
                (3, 9),
                (4, 5),
                (4, 8),
                (4, 9),
            ]
        )

        G = nx.complete_bipartite_graph(2, 2)
        self.disconnected_graph = nx.disjoint_union(G, G)

    def test_eppstein_matching(self):
        M = eppstein_matching(self.graph, self.top_nodes)
        assert frozenset(itertools.chain(*M.items())) == frozenset(range(12)) - {1, 10}
        assert all(u == M[M[u]] for u in M)

    def test_big_matching(self):
        G = nx.bipartite.random_graph(1000, 1000, 0.01, seed=1)
        M1 = eppstein_matching(G)
        M2 = hopcroft_karp_matching(G)
        assert len(M1) == len(M2)

    def test_eppstein_matching2(self):
        assert eppstein_matching(self.eppstein_edge_case) == {
            5: 0,
            6: 3,
            9: 2,
            8: 4,
            7: 1,
            0: 5,
            3: 6,
            2: 9,
            4: 8,
            1: 7,
        }

    def test_hopcroft_karp_matching(self):
        M = hopcroft_karp_matching(self.graph, self.top_nodes)
        assert frozenset(itertools.chain(*M.items())) == frozenset(range(12)) - {1, 10}
        assert all(u == M[M[u]] for u in M)

    def test_to_vertex_cover(self):
        matching = maximum_matching(self.graph, self.top_nodes)
        vertices = to_vertex_cover(self.graph, matching, self.top_nodes)
        for (u, v) in self.graph.edges():
            assert u in vertices or v in vertices
        assert vertices == {0, 2, 3, 4, 5} or vertices == {6, 7, 8, 9, 11}

    def test_eppstein_matching_simple(self):
        assert self.simple_solution == eppstein_matching(self.simple_graph)

    def test_hopcroft_karp_matching_simple(self):
        assert hopcroft_karp_matching(self.simple_graph) == self.simple_solution

    def test_eppstein_matching_disconnected(self):
        with pytest.raises(nx.AmbiguousSolution):
            eppstein_matching(self.disconnected_graph)

    def test_hopcroft_karp_matching_disconnected(self):
        with pytest.raises(nx.AmbiguousSolution):
            hopcroft_karp_matching(self.disconnected_graph)

    def test_unorderable_nodes(self):
        a, b, c, d, e, = (
            object(),
            object(),
            object(),
            object(),
            object(),
        )
        G = nx.Graph([(a, d), (b, d), (b, e), (c, d)])
        matching = maximum_matching(G)
        vertex_cover = to_vertex_cover(G, matching)
        for u, v in G.edges():
            assert u in vertex_cover or v in vertex_cover


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
