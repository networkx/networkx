import math
from itertools import permutations

from pytest import raises

import networkx as nx
from networkx.algorithms.matching import matching_dict_to_set
from networkx.utils import edges_equal


class TestMaxWeightMatching:
    """Unit tests for the
    :func:`~networkx.algorithms.matching.max_weight_matching` function.

    """

    def test_trivial1(self):
        """Empty graph"""
        G = nx.Graph()
        assert nx.max_weight_matching(G) == set()
        assert nx.min_weight_matching(G) == set()

    def test_selfloop(self):
        G = nx.Graph()
        G.add_edge(0, 0, weight=100)
        assert nx.max_weight_matching(G) == set()
        assert nx.min_weight_matching(G) == set()

    def test_single_edge(self):
        G = nx.Graph()
        G.add_edge(0, 1)
        assert edges_equal(
            nx.max_weight_matching(G), matching_dict_to_set({0: 1, 1: 0})
        )
        assert edges_equal(
            nx.min_weight_matching(G), matching_dict_to_set({0: 1, 1: 0})
        )

    def test_two_path(self):
        G = nx.Graph()
        G.add_edge("one", "two", weight=10)
        G.add_edge("two", "three", weight=11)
        assert edges_equal(
            nx.max_weight_matching(G),
            matching_dict_to_set({"three": "two", "two": "three"}),
        )
        assert edges_equal(
            nx.min_weight_matching(G),
            matching_dict_to_set({"one": "two", "two": "one"}),
        )

    def test_path(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=5)
        G.add_edge(2, 3, weight=11)
        G.add_edge(3, 4, weight=5)
        assert edges_equal(
            nx.max_weight_matching(G), matching_dict_to_set({2: 3, 3: 2})
        )
        assert edges_equal(
            nx.max_weight_matching(G, 1), matching_dict_to_set({1: 2, 2: 1, 3: 4, 4: 3})
        )
        assert edges_equal(
            nx.min_weight_matching(G), matching_dict_to_set({1: 2, 3: 4})
        )
        assert edges_equal(
            nx.min_weight_matching(G, 1), matching_dict_to_set({1: 2, 3: 4})
        )

    def test_square(self):
        G = nx.Graph()
        G.add_edge(1, 4, weight=2)
        G.add_edge(2, 3, weight=2)
        G.add_edge(1, 2, weight=1)
        G.add_edge(3, 4, weight=4)
        assert edges_equal(
            nx.max_weight_matching(G), matching_dict_to_set({1: 2, 3: 4})
        )
        assert edges_equal(
            nx.min_weight_matching(G), matching_dict_to_set({1: 4, 2: 3})
        )

    def test_edge_attribute_name(self):
        G = nx.Graph()
        G.add_edge("one", "two", weight=10, abcd=11)
        G.add_edge("two", "three", weight=11, abcd=10)
        assert edges_equal(
            nx.max_weight_matching(G, weight="abcd"),
            matching_dict_to_set({"one": "two", "two": "one"}),
        )
        assert edges_equal(
            nx.min_weight_matching(G, weight="abcd"),
            matching_dict_to_set({"three": "two"}),
        )

    def test_floating_point_weights(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=math.pi)
        G.add_edge(2, 3, weight=math.exp(1))
        G.add_edge(1, 3, weight=3.0)
        G.add_edge(1, 4, weight=math.sqrt(2.0))
        assert edges_equal(
            nx.max_weight_matching(G), matching_dict_to_set({1: 4, 2: 3, 3: 2, 4: 1})
        )
        assert edges_equal(
            nx.min_weight_matching(G), matching_dict_to_set({1: 4, 2: 3, 3: 2, 4: 1})
        )

    def test_negative_weights(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=2)
        G.add_edge(1, 3, weight=-2)
        G.add_edge(2, 3, weight=1)
        G.add_edge(2, 4, weight=-1)
        G.add_edge(3, 4, weight=-6)
        assert edges_equal(
            nx.max_weight_matching(G), matching_dict_to_set({1: 2, 2: 1})
        )
        assert edges_equal(
            nx.max_weight_matching(G, maxcardinality=True),
            matching_dict_to_set({1: 3, 2: 4, 3: 1, 4: 2}),
        )
        assert edges_equal(
            nx.min_weight_matching(G), matching_dict_to_set({1: 2, 3: 4})
        )

    def test_s_blossom(self):
        """Create S-blossom and use it for augmentation:"""
        G = nx.Graph()
        G.add_weighted_edges_from([(1, 2, 8), (1, 3, 9), (2, 3, 10), (3, 4, 7)])
        answer = matching_dict_to_set({1: 2, 2: 1, 3: 4, 4: 3})
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

        G.add_weighted_edges_from([(1, 6, 5), (4, 5, 6)])
        answer = matching_dict_to_set({1: 6, 2: 3, 3: 2, 4: 5, 5: 4, 6: 1})
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_s_t_blossom(self):
        """Create S-blossom, relabel as T-blossom, use for augmentation:"""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [(1, 2, 9), (1, 3, 8), (2, 3, 10), (1, 4, 5), (4, 5, 4), (1, 6, 3)]
        )
        answer = matching_dict_to_set({1: 6, 2: 3, 3: 2, 4: 5, 5: 4, 6: 1})
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

        G.add_edge(4, 5, weight=3)
        G.add_edge(1, 6, weight=4)
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

        G.remove_edge(1, 6)
        G.add_edge(3, 6, weight=4)
        answer = matching_dict_to_set({1: 2, 2: 1, 3: 6, 4: 5, 5: 4, 6: 3})
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_nested_s_blossom(self):
        """Create nested S-blossom, use for augmentation:"""

        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 9),
                (1, 3, 9),
                (2, 3, 10),
                (2, 4, 8),
                (3, 5, 8),
                (4, 5, 10),
                (5, 6, 6),
            ]
        )
        dict_format = {1: 3, 2: 4, 3: 1, 4: 2, 5: 6, 6: 5}
        expected = {frozenset(e) for e in matching_dict_to_set(dict_format)}
        answer = {frozenset(e) for e in nx.max_weight_matching(G)}
        assert answer == expected
        answer = {frozenset(e) for e in nx.min_weight_matching(G)}
        assert answer == expected

    def test_nested_s_blossom_relabel(self):
        """Create S-blossom, relabel as S, include in nested S-blossom:"""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 10),
                (1, 7, 10),
                (2, 3, 12),
                (3, 4, 20),
                (3, 5, 20),
                (4, 5, 25),
                (5, 6, 10),
                (6, 7, 10),
                (7, 8, 8),
            ]
        )
        answer = matching_dict_to_set({1: 2, 2: 1, 3: 4, 4: 3, 5: 6, 6: 5, 7: 8, 8: 7})
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_nested_s_blossom_expand(self):
        """Create nested S-blossom, augment, expand recursively:"""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 8),
                (1, 3, 8),
                (2, 3, 10),
                (2, 4, 12),
                (3, 5, 12),
                (4, 5, 14),
                (4, 6, 12),
                (5, 7, 12),
                (6, 7, 14),
                (7, 8, 12),
            ]
        )
        answer = matching_dict_to_set({1: 2, 2: 1, 3: 5, 4: 6, 5: 3, 6: 4, 7: 8, 8: 7})
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_s_blossom_relabel_expand(self):
        """Create S-blossom, relabel as T, expand:"""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 23),
                (1, 5, 22),
                (1, 6, 15),
                (2, 3, 25),
                (3, 4, 22),
                (4, 5, 25),
                (4, 8, 14),
                (5, 7, 13),
            ]
        )
        answer = matching_dict_to_set({1: 6, 2: 3, 3: 2, 4: 8, 5: 7, 6: 1, 7: 5, 8: 4})
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_nested_s_blossom_relabel_expand(self):
        """Create nested S-blossom, relabel as T, expand:"""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 19),
                (1, 3, 20),
                (1, 8, 8),
                (2, 3, 25),
                (2, 4, 18),
                (3, 5, 18),
                (4, 5, 13),
                (4, 7, 7),
                (5, 6, 7),
            ]
        )
        answer = matching_dict_to_set({1: 8, 2: 3, 3: 2, 4: 7, 5: 6, 6: 5, 7: 4, 8: 1})
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_nasty_blossom1(self):
        """Create blossom, relabel as T in more than one way, expand,
        augment:
        """
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 45),
                (1, 5, 45),
                (2, 3, 50),
                (3, 4, 45),
                (4, 5, 50),
                (1, 6, 30),
                (3, 9, 35),
                (4, 8, 35),
                (5, 7, 26),
                (9, 10, 5),
            ]
        )
        ansdict = {1: 6, 2: 3, 3: 2, 4: 8, 5: 7, 6: 1, 7: 5, 8: 4, 9: 10, 10: 9}
        answer = matching_dict_to_set(ansdict)
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_nasty_blossom2(self):
        """Again but slightly different:"""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 45),
                (1, 5, 45),
                (2, 3, 50),
                (3, 4, 45),
                (4, 5, 50),
                (1, 6, 30),
                (3, 9, 35),
                (4, 8, 26),
                (5, 7, 40),
                (9, 10, 5),
            ]
        )
        ans = {1: 6, 2: 3, 3: 2, 4: 8, 5: 7, 6: 1, 7: 5, 8: 4, 9: 10, 10: 9}
        answer = matching_dict_to_set(ans)
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_nasty_blossom_least_slack(self):
        """Create blossom, relabel as T, expand such that a new
        least-slack S-to-free dge is produced, augment:
        """
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 45),
                (1, 5, 45),
                (2, 3, 50),
                (3, 4, 45),
                (4, 5, 50),
                (1, 6, 30),
                (3, 9, 35),
                (4, 8, 28),
                (5, 7, 26),
                (9, 10, 5),
            ]
        )
        ans = {1: 6, 2: 3, 3: 2, 4: 8, 5: 7, 6: 1, 7: 5, 8: 4, 9: 10, 10: 9}
        answer = matching_dict_to_set(ans)
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_nasty_blossom_augmenting(self):
        """Create nested blossom, relabel as T in more than one way"""
        # expand outer blossom such that inner blossom ends up on an
        # augmenting path:
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 45),
                (1, 7, 45),
                (2, 3, 50),
                (3, 4, 45),
                (4, 5, 95),
                (4, 6, 94),
                (5, 6, 94),
                (6, 7, 50),
                (1, 8, 30),
                (3, 11, 35),
                (5, 9, 36),
                (7, 10, 26),
                (11, 12, 5),
            ]
        )
        ans = {
            1: 8,
            2: 3,
            3: 2,
            4: 6,
            5: 9,
            6: 4,
            7: 10,
            8: 1,
            9: 5,
            10: 7,
            11: 12,
            12: 11,
        }
        answer = matching_dict_to_set(ans)
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_nasty_blossom_expand_recursively(self):
        """Create nested S-blossom, relabel as S, expand recursively:"""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (1, 2, 40),
                (1, 3, 40),
                (2, 3, 60),
                (2, 4, 55),
                (3, 5, 55),
                (4, 5, 50),
                (1, 8, 15),
                (5, 7, 30),
                (7, 6, 10),
                (8, 10, 10),
                (4, 9, 30),
            ]
        )
        ans = {1: 2, 2: 1, 3: 5, 4: 9, 5: 3, 6: 7, 7: 6, 8: 10, 9: 4, 10: 8}
        answer = matching_dict_to_set(ans)
        assert edges_equal(nx.max_weight_matching(G), answer)
        assert edges_equal(nx.min_weight_matching(G), answer)

    def test_wrong_graph_type(self):
        error = nx.NetworkXNotImplemented
        raises(error, nx.max_weight_matching, nx.MultiGraph())
        raises(error, nx.max_weight_matching, nx.MultiDiGraph())
        raises(error, nx.max_weight_matching, nx.DiGraph())
        raises(error, nx.min_weight_matching, nx.DiGraph())


class TestIsMatching:
    """Unit tests for the
    :func:`~networkx.algorithms.matching.is_matching` function.

    """

    def test_dict(self):
        G = nx.path_graph(4)
        assert nx.is_matching(G, {0: 1, 1: 0, 2: 3, 3: 2})

    def test_empty_matching(self):
        G = nx.path_graph(4)
        assert nx.is_matching(G, set())

    def test_single_edge(self):
        G = nx.path_graph(4)
        assert nx.is_matching(G, {(1, 2)})

    def test_edge_order(self):
        G = nx.path_graph(4)
        assert nx.is_matching(G, {(0, 1), (2, 3)})
        assert nx.is_matching(G, {(1, 0), (2, 3)})
        assert nx.is_matching(G, {(0, 1), (3, 2)})
        assert nx.is_matching(G, {(1, 0), (3, 2)})

    def test_valid_matching(self):
        G = nx.path_graph(4)
        assert nx.is_matching(G, {(0, 1), (2, 3)})

    def test_invalid_input(self):
        error = nx.NetworkXError
        G = nx.path_graph(4)
        # edge to node not in G
        raises(error, nx.is_matching, G, {(0, 5), (2, 3)})
        # edge not a 2-tuple
        raises(error, nx.is_matching, G, {(0, 1, 2), (2, 3)})
        raises(error, nx.is_matching, G, {(0,), (2, 3)})

    def test_selfloops(self):
        error = nx.NetworkXError
        G = nx.path_graph(4)
        # selfloop for node not in G
        raises(error, nx.is_matching, G, {(5, 5), (2, 3)})
        # selfloop edge not in G
        assert not nx.is_matching(G, {(0, 0), (1, 2), (2, 3)})
        # selfloop edge in G
        G.add_edge(0, 0)
        assert not nx.is_matching(G, {(0, 0), (1, 2)})

    def test_invalid_matching(self):
        G = nx.path_graph(4)
        assert not nx.is_matching(G, {(0, 1), (1, 2), (2, 3)})

    def test_invalid_edge(self):
        G = nx.path_graph(4)
        assert not nx.is_matching(G, {(0, 3), (1, 2)})
        raises(nx.NetworkXError, nx.is_matching, G, {(0, 55)})

        G = nx.DiGraph(G.edges)
        assert nx.is_matching(G, {(0, 1)})
        assert not nx.is_matching(G, {(1, 0)})


class TestIsMaximalMatching:
    """Unit tests for the
    :func:`~networkx.algorithms.matching.is_maximal_matching` function.

    """

    def test_dict(self):
        G = nx.path_graph(4)
        assert nx.is_maximal_matching(G, {0: 1, 1: 0, 2: 3, 3: 2})

    def test_invalid_input(self):
        error = nx.NetworkXError
        G = nx.path_graph(4)
        # edge to node not in G
        raises(error, nx.is_maximal_matching, G, {(0, 5)})
        raises(error, nx.is_maximal_matching, G, {(5, 0)})
        # edge not a 2-tuple
        raises(error, nx.is_maximal_matching, G, {(0, 1, 2), (2, 3)})
        raises(error, nx.is_maximal_matching, G, {(0,), (2, 3)})

    def test_valid(self):
        G = nx.path_graph(4)
        assert nx.is_maximal_matching(G, {(0, 1), (2, 3)})

    def test_not_matching(self):
        G = nx.path_graph(4)
        assert not nx.is_maximal_matching(G, {(0, 1), (1, 2), (2, 3)})
        assert not nx.is_maximal_matching(G, {(0, 3)})
        G.add_edge(0, 0)
        assert not nx.is_maximal_matching(G, {(0, 0)})

    def test_not_maximal(self):
        G = nx.path_graph(4)
        assert not nx.is_maximal_matching(G, {(0, 1)})


class TestIsPerfectMatching:
    """Unit tests for the
    :func:`~networkx.algorithms.matching.is_perfect_matching` function.

    """

    def test_dict(self):
        G = nx.path_graph(4)
        assert nx.is_perfect_matching(G, {0: 1, 1: 0, 2: 3, 3: 2})

    def test_valid(self):
        G = nx.path_graph(4)
        assert nx.is_perfect_matching(G, {(0, 1), (2, 3)})

    def test_valid_not_path(self):
        G = nx.cycle_graph(4)
        G.add_edge(0, 4)
        G.add_edge(1, 4)
        G.add_edge(5, 2)

        assert nx.is_perfect_matching(G, {(1, 4), (0, 3), (5, 2)})

    def test_invalid_input(self):
        error = nx.NetworkXError
        G = nx.path_graph(4)
        # edge to node not in G
        raises(error, nx.is_perfect_matching, G, {(0, 5)})
        raises(error, nx.is_perfect_matching, G, {(5, 0)})
        # edge not a 2-tuple
        raises(error, nx.is_perfect_matching, G, {(0, 1, 2), (2, 3)})
        raises(error, nx.is_perfect_matching, G, {(0,), (2, 3)})

    def test_selfloops(self):
        error = nx.NetworkXError
        G = nx.path_graph(4)
        # selfloop for node not in G
        raises(error, nx.is_perfect_matching, G, {(5, 5), (2, 3)})
        # selfloop edge not in G
        assert not nx.is_perfect_matching(G, {(0, 0), (1, 2), (2, 3)})
        # selfloop edge in G
        G.add_edge(0, 0)
        assert not nx.is_perfect_matching(G, {(0, 0), (1, 2)})

    def test_not_matching(self):
        G = nx.path_graph(4)
        assert not nx.is_perfect_matching(G, {(0, 3)})
        assert not nx.is_perfect_matching(G, {(0, 1), (1, 2), (2, 3)})

    def test_maximal_but_not_perfect(self):
        G = nx.cycle_graph(4)
        G.add_edge(0, 4)
        G.add_edge(1, 4)

        assert not nx.is_perfect_matching(G, {(1, 4), (0, 3)})


class TestMaximalMatching:
    """Unit tests for the
    :func:`~networkx.algorithms.matching.maximal_matching`.

    """

    def test_valid_matching(self):
        edges = [(1, 2), (1, 5), (2, 3), (2, 5), (3, 4), (3, 6), (5, 6)]
        G = nx.Graph(edges)
        matching = nx.maximal_matching(G)
        assert nx.is_maximal_matching(G, matching)

    def test_single_edge_matching(self):
        # In the star graph, any maximal matching has just one edge.
        G = nx.star_graph(5)
        matching = nx.maximal_matching(G)
        assert 1 == len(matching)
        assert nx.is_maximal_matching(G, matching)

    def test_self_loops(self):
        # Create the path graph with two self-loops.
        G = nx.path_graph(3)
        G.add_edges_from([(0, 0), (1, 1)])
        matching = nx.maximal_matching(G)
        assert len(matching) == 1
        # The matching should never include self-loops.
        assert not any(u == v for u, v in matching)
        assert nx.is_maximal_matching(G, matching)

    def test_ordering(self):
        """Tests that a maximal matching is computed correctly
        regardless of the order in which nodes are added to the graph.

        """
        for nodes in permutations(range(3)):
            G = nx.Graph()
            G.add_nodes_from(nodes)
            G.add_edges_from([(0, 1), (0, 2)])
            matching = nx.maximal_matching(G)
            assert len(matching) == 1
            assert nx.is_maximal_matching(G, matching)

    def test_wrong_graph_type(self):
        error = nx.NetworkXNotImplemented
        raises(error, nx.maximal_matching, nx.MultiGraph())
        raises(error, nx.maximal_matching, nx.MultiDiGraph())
        raises(error, nx.maximal_matching, nx.DiGraph())


class TestCountPlanarPerfectMatchings:
    """Unit tests for the
    :func:`~networkx.algorithms.matching.kasteleyn_orientation`.

    """

    numerical_stability_threshold = 1e-5

    def test_unweighted_grids(self):
        """Tests that the FKT algorithm returns the correct result (to within
        numerical stability tolerance) for 2x2, 3x3, and 4x4 unweighted grid
        graphs. The 3x3 grid graph should have 0 perfect matchings because it
        has an odd number of nodes."""

        unweighted_grids = [
            self.grid_graph_unweighted(lattice_size) for lattice_size in [2, 3, 4]
        ]

        brute_force_results = [
            self.count_perfect_matchings_brute_force(grid) for grid in unweighted_grids
        ]

        fkt_results = [
            nx.algorithms.matching.count_planar_perfect_matchings(grid)
            for grid in unweighted_grids
        ]

        for i in range(len(brute_force_results)):
            assert (
                math.abs(brute_force_results[i] - math.abs(fkt_results[i]))
                < self.numerical_stability_threshold
            )

        assert brute_force_results[1] == 0.0

    def test_weighted_grids(self):
        """Tests that the FKT algorithm returns the correct result (to within
        numerical stability tolerance) for 2x2, 3x3, and 4x4 weighted grid
        graphs. The 3x3 grid graph should have 0 perfect matchings because it
        has an odd number of nodes."""

        weighted_grids = [
            self.grid_graph_weighted(lattice_size) for lattice_size in [2, 3, 4]
        ]

        brute_force_results = [
            self.count_perfect_matchings_brute_force(grid) for grid in weighted_grids
        ]

        fkt_results = [
            nx.algorithms.matching.count_planar_perfect_matchings(grid)
            for grid in weighted_grids
        ]

        for i in range(len(brute_force_results)):
            assert (
                math.abs(brute_force_results[i] - math.abs(fkt_results[i]))
                < self.numerical_stability_threshold
            )

        assert brute_force_results[1] == 0.0

    def test_multiple_components(self):
        pass  # TODO

    def test_small_graphs(self):
        pass  # TODO

    def test_nonplanar(self):
        """Tests that count_planar_perfect_matchings raises a NetworkXError
        when given a nonplanar graph."""
        k33 = nx.Graph()
        for i in range(3):
            for j in range(3, 6):
                k33.add_edge(i, j)

        with raises(nx.NetworkXError):
            nx.matching.count_planar_perfect_matchings(k33)

        k5 = nx.Graph()
        for i in range(5):
            for j in range(i + 1, 5):
                k5.add_edge(i, j)

        with raises(nx.NetworkXError):
            nx.matching.count_planar_perfect_matchings(k5)

    # Exaple graphs to test FKT algorithm.

    def grid_graph_unweighted(self, lattice_size: int):
        """Square grid graph on a grid of size `lattice_size` x `lattice_size`.

        Parameters
        ----------
        lattice_size : int
            Dimension of the grid. The graph will have `lattice_size` x
            `lattice_size` nodes.

        Returns
        ----------
        NetworkX Graph
            Unweighted grid graph.
        """

        graph = nx.Graph()
        for i in range(lattice_size):
            for j in range(lattice_size - 1):
                graph.add_edge((i, j), (i, j + 1))
        for i in range(lattice_size - 1):
            for j in range(lattice_size):
                graph.add_edge((i, j), (i + 1, j))

        return graph

    def grid_graph_weighted(self, lattice_size: int):
        """Square grid graph on a grid of size `lattice_size` x `lattice_size`.

        The graph edges will have various weights.

        The edge from (i, j) to (i, j+1) will have weight i+j+1.

        The edge from (i, j) to (i+1, j) will have weight -i-j-2.

        Parameters
        ----------
        lattice_size : int
            Dimension of the grid. The graph will have `lattice_size` x
            `lattice_size` nodes.

        Returns
        ----------
        NetworkX Graph
            Weighted grid graph.
        """

        graph = nx.Graph()
        for i in range(lattice_size):
            for j in range(lattice_size - 1):
                graph.add_edge((i, j), (i, j + 1), weight=i + j + 1)
        for i in range(lattice_size - 1):
            for j in range(lattice_size):
                graph.add_edge((i, j), (i + 1, j), weight=-i - j - 2)

        return graph

    # Below methods count perfect matchings via brute force.
    # For testing purposes.

    def matching_weight(self, G: nx.Graph, matching: set):
        """Returns the weight of this matching in the graph `G`, that is, the
        product of edge weights. Edges without weights are assumed to have
        weight 1.

        Parameters
        ----------
        G : NetworkX Graph

        matching : set
            A `set` of edges that makes up a matching.

        Returns
        ----------
        Float
            Product of edge weights.
        """

        weight = 1.0
        for edge in matching:
            weight *= G.get_edge_data(edge[0], edge[1]).get("weight", 1)
        return weight

    def generate_perfect_matchings(self, G: nx.Graph):
        """Generator giving all perfect matchings for this graph.

        Parameters
        ----------
        G : NetworkX Graph

        Yields
        ----------
        set
            Matchings as sets of edges.
        """

        # set telling us which vertices have been covered.
        covered_nodes = set()

        # edges we're including in the matching
        included_edges = set()

        yield from self.generate_perfect_matchings_recursive(
            G.number_of_nodes(), list(G.edges()), covered_nodes, included_edges, 0
        )

    def generate_perfect_matchings_recursive(
        self,
        num_nodes: int,
        all_edges: list,
        covered_nodes: set,
        included_edges: set,
        edge_index: int,
    ):
        """Generator that recursively generates all perfect matchings in a
        graph. This generator assumes that we have already determined which
        edges in the list `all_edges` we want to include, up to index edge
        index-1 (inclusive). `covered_nodes` is what nodes are covered so far
        by those edges. This generator recursively tries including or not
        including all edges in the list `all_edges` on or after index
        `edge_index`.

        Parameters
        ----------
        num_nodes : int
            Number of ndoes in the graph.

        all_edges: list
            List of all edges in this graph. These need not have edge data.

        covered_nodes : set
            Nodes covered so far by the edges in `included_edges`.

        included_edges : set
            Edges included so far in the matching. These should all be before
            index `edge_index` in the list `all_edges`.

        edge_index : int
            Index of list `all_edges` where this generator will start including
            or not including edges.

        Yields
        ----------
        set
            Matchings as sets of edges.
        """

        # Base case: if covered_nodes includes all nodes, yield this matching.
        # Else, if edge_index is the number of nodes, return and yield nothing.
        if len(covered_nodes) == num_nodes:
            yield included_edges
            return
        elif edge_index == len(all_edges):
            return

        # try NOT including the edge at edgeIndex
        yield from self.generate_perfect_matchings_recursive(
            num_nodes, all_edges, covered_nodes, included_edges, edge_index + 1
        )

        # try including the edge at edgeIndex
        current_edge = all_edges[edge_index]
        if (
            current_edge[0] not in covered_nodes
            and current_edge[1] not in covered_nodes
        ):
            covered_nodes.add(current_edge[0])
            covered_nodes.add(current_edge[1])
            included_edges.add(current_edge)
            yield from self.generate_perfect_matchings_recursive(
                num_nodes, all_edges, covered_nodes, included_edges, edge_index + 1
            )
            covered_nodes.remove(current_edge[0])
            covered_nodes.remove(current_edge[1])
            included_edges.remove(current_edge)

    def count_perfect_matchings_brute_force(self, G: nx.Graph):
        """Sums weights of perfect matchings, via brute force counting all
        perfect matchings.

        Parameters
        ----------
        G : NetworkX Graph

        Returns
        ----------
        Float
            Sum of weights of all perfect matghings. The weight of a perfect
            matching is the product of edge weights. Edges without weights are
            assumed to have weight 1.
        """

        sum = 0
        for matching in self.generate_perfect_matchings(G):
            sum += self.matching_weight(G, matching)
        return sum


class TestKasteleynOrientation:
    """Unit tests for the
    :func:`~networkx.algorithms.matching.kasteleyn_orientation`.

    """
