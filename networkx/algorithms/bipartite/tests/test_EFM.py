from networkx.algorithms.bipartite.EFM_algorithms import *


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
            return nx.Graph([(i, i + size) for i in range(size)])

        A = nx.complete_bipartite_graph(3, 3)
        matching = max_size_envy_free_matching(A)
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
        matching = max_size_envy_free_matching(B)
        assert matching == {0: 3, 3: 0, 1: 4, 4: 1, 2: 5, 5: 2}

        # Check our algorithm with big inputs, array can be expanded to contain more values for which to generate graphs
        sizes = [10, 100, 10000]
        for size in sizes:
            G = generate_marriable_bipartite_graph(size)
            if nx.is_connected(G):
                matching = max_size_envy_free_matching(G)
                expected1 = {i: i + size for i in range(size)}
                expected2 = {i + size: i for i in range(size)}
                expected = {**expected1, **expected2}
                assert matching == expected

    def test_non_empty_envy_free_matching(self):
        A = nx.Graph([(0, 3), (3, 0), (0, 4), (4, 0), (1, 4), (4, 1), (2, 4), (4, 2)])
        matching = max_size_envy_free_matching(A)
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
        matching = max_size_envy_free_matching(B, top_nodes=[0, 1, 2, 3])
        assert matching == {0: 4, 4: 0, 1: 6, 6: 1}

    def test_empty_envy_free_matching(self):
        def generate_odd_path(size: int):
            """
            generate_odd_path

            input: positive odd(!!) number
            output: bipartite graph with one set of cardinality = size and one set of cardinality = size - 1
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

        A = generate_odd_path(3)  # check small input first

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

        C = generate_odd_path(11)  # check big inputs
        D = generate_odd_path(
            501
        )  # check even bigger inputs, may take too long, adjust the given value as needed

        graphs = {A, B, C, D}
        for graph in graphs:
            if nx.is_connected(graph):
                assert max_size_envy_free_matching(G=graph) == {}


class TestMinimumWeightEnvyFreeMatching:
    def test_envy_free_perfect_matching(self):
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
        matching = minimum_weight_envy_free_matching(G)
        assert matching == {
            0: 5,
            1: 4,
            2: 3,
            5: 0,
            4: 1,
            3: 2,
        }

    def test_non_empty_envy_free_matching(self):
        Graph = nx.Graph()
        Graph.add_weighted_edges_from(
            [(0, 4, 5), (1, 4, 1), (2, 5, 3), (2, 7, 9), (3, 6, 3), (3, 7, 7)]
        )
        matching = minimum_weight_envy_free_matching(Graph, top_nodes=[0, 1, 2, 3])
        assert matching == {
            2: 5,
            3: 6,
            5: 2,
            6: 3,
        }