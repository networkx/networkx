import itertools

import pytest

import networkx as nx
import networkx.algorithms.bipartite.envy_free_matching as algo
# from networkx.algorithms.bipartite.matching import (
#     eppstein_matching,
#     hopcroft_karp_matching,
#     maximum_matching,
#     minimum_weight_full_matching,
#     to_vertex_cover,
#     envy_free_matching,
#     minimum_weight_envy_free_matching,
# )

class TestEnvyFreeMatching:

    def test_envy_free_perfect_matching(self):
        def generate_marriable_bipartite_graph(size: int):
            """
            generate_marriable_bipartite_graph

            input: positive number
            output: bipartite graph with both sets of cardinality = size each node has one edge to exactly one node.

            >>> generate_marriable_bipartite_graph(3).edges
            [(0, 3), (1, 4), (2, 5)]
            """
            return nx.Graph([(i, i+size) for i in range(size)])

        A = nx.complete_bipartite_graph(3, 3)
        matching = algo.envy_free_matching(A)
        assert matching == {0: 3, 3: 0, 1: 4, 4: 1, 2: 5, 5: 2}

        # B = nx.Graph([(0, 3), (3, 0), (0, 4), (4, 0), (1, 4), (4, 1), (1, 5), (5, 1), (2, 5), (5, 2)])
        # matching = algo.envy_free_matching(B)
        # assert matching == {0: 3, 3: 0, 1: 4, 4: 1, 2: 5, 5: 2}
        #
        # C = generate_marriable_bipartite_graph(10)
        # matching = algo.envy_free_matching(C)
        # assert matching == {(i, i+10) for i in range(10)}
        #
        # D = generate_marriable_bipartite_graph(10000)
        # matching = algo.envy_free_matching(D)
        # assert matching == {(i, i + 10000) for i in range(10000)}

    def test_non_empty_envy_free_matching(self):
        A = nx.Graph([(0, 3), (3, 0), (0, 4), (4, 0), (1, 4), (4, 1), (2, 4), (4, 2)])
        matching = algo.envy_free_matching(A)
        assert matching == {0: 3, 3: 0}

        # B = nx.Graph([(0, 4), (4, 0), (0, 5), (5, 0), (0, 8), (8, 0), (1, 6), (6, 1), (2, 7), (7, 2), (3, 7), (7, 3)])
        # matching = algo.envy_free_matching(B)
        # assert matching == {0: 4, 4: 0, 1: 6, 6: 1}

    def test_empty_envy_free_matching(self):
        # def generate_odd_path(size: int):
        #     """
        #     generate_odd_path
        #
        #     input: positive number
        #     output: bipartite graph with one set of cardinality = size and one set of cardinality = size - 1
        #     with the shape of an odd path.
        #
        #     >>> generate_odd_path(3).edges
        #     [(0, 3), (1, 3), (1, 4), (2, 4), (3, 0), (3, 1), (4, 1), (4, 2)]
        #
        #     """
        #     edges = [(0, size)]
        #
        #     actions = {
        #         0: lambda: edges.append((edges[-1][0], edges[-1][1] + 1)),
        #
        #         1: lambda: edges.append((edges[-1][0] + 1, edges[-1][1]))
        #     }
        #
        #     for i in range(1, size + 1):
        #         actions[i % 2]()
        #     return nx.Graph(edges)
        #
        # A = generate_odd_path(3)  # check small input first

        B = nx.Graph(
            [(0, 6), (6, 0), (1, 6), (6, 1), (1, 7), (7, 1), (2, 6), (6, 2), (2, 8), (8, 2), (3, 9), (9, 3), (3, 6),
             (6, 3), (4, 8), (8, 4), (4, 7), (7, 4), (5, 9), (9, 5)])  # more intricate graph

        # C = generate_odd_path(100)  # check big inputs
        # D = generate_odd_path(10000)  # check even bigger inputs
        #
        # graphs = {A, B, C, D}
        # for graph in graphs:
        #     assert algo.envy_free_matching(G=graph) == {}


class TestMinimumWeightEnvyFreeMatching:
    def test_envy_free_perfect_matching(self):
        A = nx.Graph()
        A.add_nodes_from([0, 1, 2], bipartite=0)
        A.add_nodes_from([3, 4, 5], bipartite=1)
        A.add_edge(0, 3, weight=250)
        A.add_edge(3, 0, weight=250)
        A.add_edge(0, 4, weight=148)
        A.add_edge(4, 0, weight=148)
        A.add_edge(0, 5, weight=122)
        A.add_edge(5, 0, weight=122)
        A.add_edge(1, 3, weight=175)
        A.add_edge(3, 1, weight=175)
        A.add_edge(1, 4, weight=135)
        A.add_edge(4, 1, weight=135)
        A.add_edge(1, 5, weight=150)
        A.add_edge(5, 1, weight=150)
        A.add_edge(2, 3, weight=150)
        A.add_edge(3, 2, weight=150)
        A.add_edge(2, 4, weight=125)
        A.add_edge(4, 2, weight=125)
        matching = algo.minimum_weight_full_matching(A)
        assert matching == {0: 5, 1: 4, 2: 3, 5: 0, 4: 1, 3: 2}
        B = nx.Graph()
        B.add_nodes_from([0, 1, 2], bipartite=0)
        B.add_nodes_from([3, 4, 5], bipartite=1)
        B.add_edge(0, 3, weight=0)
        B.add_edge(3, 0, weight=0)
        B.add_edge(0, 4, weight=0)
        B.add_edge(4, 0, weight=0)
        B.add_edge(0, 5, weight=0)
        B.add_edge(5, 0, weight=0)
        B.add_edge(1, 3, weight=0)
        B.add_edge(3, 0, weight=0)
        B.add_edge(1, 4, weight=0)
        B.add_edge(4, 1, weight=0)
        B.add_edge(1, 5, weight=0)
        B.add_edge(5, 1, weight=0)
        B.add_edge(2, 3, weight=0)
        B.add_edge(3, 2, weight=0)
        B.add_edge(2, 4, weight=0)
        B.add_edge(4, 2, weight=0)
        matching = algo.minimum_weight_envy_free_matching(B)
        assert matching == {0: 3, 1: 5, 2: 4, 3: 0, 5: 1, 4: 2}

    def test_non_empty_envy_free_matching(self):
        A = nx.Graph()
        A.add_nodes_from([0, 1, 2, 3], bipartite=0)
        A.add_nodes_from([4, 5, 6, 7], bipartite=1)
        A.add_edge(0, 4, weight=5)
        A.add_edge(4, 0, weight=5)
        A.add_edge(1, 4, weight=1)
        A.add_edge(4, 1, weight=1)
        A.add_edge(1, 5, weight=500)
        A.add_edge(5, 1, weight=500)
        A.add_edge(2, 5, weight=3)
        A.add_edge(5, 2, weight=3)
        A.add_edge(2, 7, weight=9)
        A.add_edge(7, 2, weight=9)
        A.add_edge(3, 6, weight=3)
        A.add_edge(6, 3, weight=3)
        A.add_edge(3, 7, weight=7)
        A.add_edge(7, 3, weight=7)
        matching = algo.minimum_weight_envy_free_matching(A)
        assert matching == {2: 5, 3: 6, 5: 2, 6: 3}