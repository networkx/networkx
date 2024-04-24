"""Greedy coloring test suite.

"""
import pytest

import networkx as nx

is_coloring = nx.algorithms.coloring.equitable_coloring.is_coloring
is_equitable = nx.algorithms.coloring.equitable_coloring.is_equitable

ALL_STRATEGIES = [
    "largest_first",
    "random_sequential",
    "smallest_last",
    "independent_set",
    "connected_sequential_bfs",
    "connected_sequential_dfs",
    "connected_sequential",
    "saturation_largest_first",
    "DSATUR",
    "rlf",
]


class TestColoring:
    def test_many_cases(self):
        for graph_func in TEST_CASES:
            for strategy in ALL_STRATEGIES:
                graph = graph_func()
                for tabuits in [0, 10, 1000]:
                    for interchange in [True, False]:
                        coloring = nx.coloring.greedy_color(
                            graph,
                            strategy=strategy,
                            tabu=tabuits,
                            interchange=interchange,
                        )
                        assert verify_coloring(graph, coloring)

    def test_bad_strategy(self):
        graph = singleton()
        pytest.raises(
            nx.NetworkXError,
            nx.coloring.greedy_color,
            graph,
            strategy="this is an invalid strategy",
        )

    def test_bad_tabu_parameter_1(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            nx.coloring.greedy_color,
            graph,
            tabu="this is not an integer argument",
        )

    def test_bad_tabu_parameter_2(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            nx.coloring.greedy_color,
            graph,
            tabu=-1,
        )

    def test_bad_interchange_parameter(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            nx.coloring.greedy_color,
            graph,
            interchange="this is not a bool",
        )

    def test_directed(self):
        graph = nx.DiGraph()
        graph.add_nodes_from([1, 2, 3, 4, 5, 6])
        graph.add_edges_from([(6, 1), (1, 4), (4, 3), (3, 2), (2, 5)])
        pytest.raises(
            nx.NetworkXNotImplemented,
            nx.coloring.greedy_color,
            graph,
        )

    def test_multidirected(self):
        graph = nx.MultiDiGraph()
        graph.add_nodes_from([1, 2, 3, 4, 5, 6])
        graph.add_edges_from([(6, 1), (6, 1), (1, 4), (4, 3), (3, 2), (2, 5)])
        pytest.raises(
            nx.NetworkXNotImplemented,
            nx.coloring.greedy_color,
            graph,
        )

    def test_strategy_as_function(self):
        graph = G1()
        colors_1 = nx.coloring.greedy_color(graph, "largest_first")
        colors_2 = nx.coloring.greedy_color(graph, nx.coloring.strategy_largest_first)
        assert colors_1 == colors_2

    def test_seed_argument(self):
        graph = G1()
        rs = nx.coloring.strategy_random_sequential
        c1 = nx.coloring.greedy_color(graph, lambda g, c: rs(g, c, seed=1))
        for u, v in graph.edges:
            assert c1[u] != c1[v]

    def test_is_coloring(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        coloring = {0: 0, 1: 1, 2: 0}
        assert is_coloring(G, coloring)
        coloring[0] = 1
        assert not is_coloring(G, coloring)
        assert not is_equitable(G, coloring)

    def test_is_equitable(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        coloring = {0: 0, 1: 1, 2: 0}
        assert is_equitable(G, coloring)
        G.add_edges_from([(2, 3), (2, 4), (2, 5)])
        coloring[3] = 1
        coloring[4] = 1
        coloring[5] = 1
        assert is_coloring(G, coloring)
        assert not is_equitable(G, coloring)

    def test_num_colors(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (0, 3)])
        coloring = nx.coloring.equitable_color(G, max_degree(G))
        assert is_equitable(G, coloring)
        coloring = nx.coloring.equitable_color(G, max_degree(G) + 1)
        assert is_equitable(G, coloring)

    def test_equitable_directed(self):
        graph = nx.DiGraph()
        graph.add_nodes_from([1, 2, 3, 4, 5, 6])
        graph.add_edges_from([(6, 1), (1, 4), (4, 3), (3, 2), (2, 5)])
        pytest.raises(
            nx.NetworkXNotImplemented,
            nx.coloring.equitable_color,
            graph,
            num_colors=max_degree(graph),
        )

    def test_equitable_multidirected(self):
        graph = nx.MultiDiGraph()
        graph.add_nodes_from([1, 2, 3, 4, 5, 6])
        graph.add_edges_from([(6, 1), (6, 1), (1, 4), (4, 3), (3, 2), (2, 5)])
        pytest.raises(
            nx.NetworkXNotImplemented,
            nx.coloring.equitable_color,
            graph,
            num_colors=max_degree(graph),
        )

    def test_equitable_bad_num_colors1(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            nx.coloring.equitable_color,
            graph,
            num_colors="this is not an int",
        )

    def test_equitable_bad_num_colors2(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            nx.coloring.equitable_color,
            graph,
            num_colors=-1,
        )

    def test_equitable_color(self):
        G = nx.fast_gnp_random_graph(n=10, p=0.2, seed=42)
        coloring = nx.coloring.equitable_color(G, max_degree(G))
        assert is_equitable(G, coloring)
        coloring = nx.coloring.equitable_color(G, max_degree(G) + 1)
        assert is_equitable(G, coloring)

    def test_equitable_color_empty(self):
        G = nx.empty_graph()
        coloring = nx.coloring.equitable_color(G, max_degree(G))
        assert is_equitable(G, coloring)
        coloring = nx.coloring.equitable_color(G, max_degree(G) + 1)
        assert is_equitable(G, coloring)

    def test_equitable_color_large(self):
        G = nx.fast_gnp_random_graph(100, 0.1, seed=42)
        coloring = nx.coloring.equitable_color(G, max_degree(G))
        assert is_equitable(G, coloring, num_colors=max_degree(G))
        coloring = nx.coloring.equitable_color(G, max_degree(G) + 1)
        assert is_equitable(G, coloring, num_colors=max_degree(G) + 1)

    def test_equitable_color_large_differing_num_colors(self):
        G = nx.fast_gnp_random_graph(100, 0.5, seed=42)
        for k in range(20):
            pytest.raises(nx.NetworkXAlgorithmError, nx.coloring.equitable_color, G, k)
        for k in range(20, 110):
            coloring = nx.coloring.equitable_color(G, k)
            assert is_equitable(G, coloring, k)

    def test_case_V_plus_not_in_A_cal(self):
        # Hand crafted case to avoid the easy case.
        L = {
            0: [2, 5],
            1: [3, 4],
            2: [0, 8],
            3: [1, 7],
            4: [1, 6],
            5: [0, 6],
            6: [4, 5],
            7: [3],
            8: [2],
        }
        F = {
            # Color 0
            0: 0,
            1: 0,
            # Color 1
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            # Color 2
            6: 2,
            7: 2,
            8: 2,
        }
        C = nx.algorithms.coloring.equitable_coloring.make_C_from_F(F)
        N = nx.algorithms.coloring.equitable_coloring.make_N_from_L_C(L, C)
        H = nx.algorithms.coloring.equitable_coloring.make_H_from_C_N(C, N)
        nx.algorithms.coloring.equitable_coloring.procedure_P(
            V_minus=0, V_plus=1, N=N, H=H, F=F, C=C, L=L
        )
        check_state(L=L, N=N, H=H, F=F, C=C)

    def test_cast_no_solo(self):
        L = {
            0: [8, 9],
            1: [10, 11],
            2: [8],
            3: [9],
            4: [10, 11],
            5: [8],
            6: [9],
            7: [10, 11],
            8: [0, 2, 5],
            9: [0, 3, 6],
            10: [1, 4, 7],
            11: [1, 4, 7],
        }
        F = {0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 1, 9: 1, 10: 1, 11: 1}
        C = nx.algorithms.coloring.equitable_coloring.make_C_from_F(F)
        N = nx.algorithms.coloring.equitable_coloring.make_N_from_L_C(L, C)
        H = nx.algorithms.coloring.equitable_coloring.make_H_from_C_N(C, N)
        nx.algorithms.coloring.equitable_coloring.procedure_P(
            V_minus=0, V_plus=1, N=N, H=H, F=F, C=C, L=L
        )
        check_state(L=L, N=N, H=H, F=F, C=C)

    def test_hard_prob(self):
        # Tests for two levels of recursion.
        num_colors, s = 5, 5
        G = nx.Graph()
        G.add_edges_from(
            [
                (0, 10),
                (0, 11),
                (0, 12),
                (0, 23),
                (10, 4),
                (10, 9),
                (10, 20),
                (11, 4),
                (11, 8),
                (11, 16),
                (12, 9),
                (12, 22),
                (12, 23),
                (23, 7),
                (1, 17),
                (1, 18),
                (1, 19),
                (1, 24),
                (17, 5),
                (17, 13),
                (17, 22),
                (18, 5),
                (19, 5),
                (19, 6),
                (19, 8),
                (24, 7),
                (24, 16),
                (2, 4),
                (2, 13),
                (2, 14),
                (2, 15),
                (4, 6),
                (13, 5),
                (13, 21),
                (14, 6),
                (14, 15),
                (15, 6),
                (15, 21),
                (3, 16),
                (3, 20),
                (3, 21),
                (3, 22),
                (16, 8),
                (20, 8),
                (21, 9),
                (22, 7),
            ]
        )
        F = {node: node // s for node in range(num_colors * s)}
        F[s - 1] = num_colors - 1
        params = make_params_from_graph(G=G, F=F)
        nx.algorithms.coloring.equitable_coloring.procedure_P(
            V_minus=0, V_plus=num_colors - 1, **params
        )
        check_state(**params)

    def test_hardest_prob(self):
        # Tests for two levels of recursion.
        num_colors, s = 10, 4
        G = nx.Graph()
        G.add_edges_from(
            [
                (0, 19),
                (0, 24),
                (0, 29),
                (0, 30),
                (0, 35),
                (19, 3),
                (19, 7),
                (19, 9),
                (19, 15),
                (19, 21),
                (19, 24),
                (19, 30),
                (19, 38),
                (24, 5),
                (24, 11),
                (24, 13),
                (24, 20),
                (24, 30),
                (24, 37),
                (24, 38),
                (29, 6),
                (29, 10),
                (29, 13),
                (29, 15),
                (29, 16),
                (29, 17),
                (29, 20),
                (29, 26),
                (30, 6),
                (30, 10),
                (30, 15),
                (30, 22),
                (30, 23),
                (30, 39),
                (35, 6),
                (35, 9),
                (35, 14),
                (35, 18),
                (35, 22),
                (35, 23),
                (35, 25),
                (35, 27),
                (1, 20),
                (1, 26),
                (1, 31),
                (1, 34),
                (1, 38),
                (20, 4),
                (20, 8),
                (20, 14),
                (20, 18),
                (20, 28),
                (20, 33),
                (26, 7),
                (26, 10),
                (26, 14),
                (26, 18),
                (26, 21),
                (26, 32),
                (26, 39),
                (31, 5),
                (31, 8),
                (31, 13),
                (31, 16),
                (31, 17),
                (31, 21),
                (31, 25),
                (31, 27),
                (34, 7),
                (34, 8),
                (34, 13),
                (34, 18),
                (34, 22),
                (34, 23),
                (34, 25),
                (34, 27),
                (38, 4),
                (38, 9),
                (38, 12),
                (38, 14),
                (38, 21),
                (38, 27),
                (2, 3),
                (2, 18),
                (2, 21),
                (2, 28),
                (2, 32),
                (2, 33),
                (2, 36),
                (2, 37),
                (2, 39),
                (3, 5),
                (3, 9),
                (3, 13),
                (3, 22),
                (3, 23),
                (3, 25),
                (3, 27),
                (18, 6),
                (18, 11),
                (18, 15),
                (18, 39),
                (21, 4),
                (21, 10),
                (21, 14),
                (21, 36),
                (28, 6),
                (28, 10),
                (28, 14),
                (28, 16),
                (28, 17),
                (28, 25),
                (28, 27),
                (32, 5),
                (32, 10),
                (32, 12),
                (32, 16),
                (32, 17),
                (32, 22),
                (32, 23),
                (33, 7),
                (33, 10),
                (33, 12),
                (33, 16),
                (33, 17),
                (33, 25),
                (33, 27),
                (36, 5),
                (36, 8),
                (36, 15),
                (36, 16),
                (36, 17),
                (36, 25),
                (36, 27),
                (37, 5),
                (37, 11),
                (37, 15),
                (37, 16),
                (37, 17),
                (37, 22),
                (37, 23),
                (39, 7),
                (39, 8),
                (39, 15),
                (39, 22),
                (39, 23),
            ]
        )
        F = {node: node // s for node in range(num_colors * s)}
        F[s - 1] = num_colors - 1  # V- = 0, V+ = num_colors - 1
        params = make_params_from_graph(G=G, F=F)
        nx.algorithms.coloring.equitable_coloring.procedure_P(
            V_minus=0, V_plus=num_colors - 1, **params
        )
        check_state(**params)


#  ############################  Utility functions ############################
def verify_coloring(graph, coloring):
    # Check all nodes in the graph are colored, that the coloring is feasible,
    # and that all colors are used at least once and are labeled 0,1,...,k-1
    if len(graph) == 0 and len(coloring) == 0:
        return True
    if len(coloring) != len(graph):
        return False
    for node in graph.nodes():
        if node not in coloring:
            return False
    for node in graph.nodes():
        color = coloring[node]
        for neighbor in graph.neighbors(node):
            if coloring[neighbor] == color:
                return False
    colset = set(coloring.values())
    if len(colset) != max(colset) + 1:
        return False
    return True


#  ############################  Graph Generation ############################
def null_graph():
    return nx.Graph()


def singleton():
    graph = nx.Graph()
    graph.add_nodes_from([1])
    return graph


def dyad():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2])
    graph.add_edges_from([(1, 2)])
    return graph


def three_node_clique():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3])
    graph.add_edges_from([(1, 2), (1, 3), (2, 3)])
    return graph


def disconnected():
    graph = nx.Graph()
    graph.add_edges_from([(1, 2), (2, 3), (4, 5), (5, 6)])
    return graph


def G1():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4])
    graph.add_edges_from([(1, 2), (2, 3), (3, 4)])
    return graph


def G2():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    graph.add_edges_from(
        [(1, 2), (1, 5), (1, 6), (2, 3), (2, 7), (3, 4), (3, 7), (4, 5), (4, 6), (5, 6)]
    )
    return graph


def G3():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
    graph.add_edges_from(
        [
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (2, 3),
            (2, 4),
            (2, 6),
            (5, 7),
            (5, 8),
            (6, 7),
            (6, 8),
            (7, 8),
        ]
    )
    return graph


def G4():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6])
    graph.add_edges_from([(6, 1), (1, 4), (4, 3), (3, 2), (2, 5)])
    return graph


def G5():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    graph.add_edges_from(
        [
            (1, 7),
            (1, 6),
            (1, 3),
            (1, 4),
            (7, 2),
            (2, 6),
            (2, 3),
            (2, 5),
            (5, 3),
            (5, 4),
            (4, 3),
        ]
    )
    return graph


def G6():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6])
    graph.add_edges_from(
        [(1, 2), (1, 3), (2, 3), (1, 4), (2, 5), (3, 6), (4, 5), (4, 6), (5, 6)]
    )
    return graph


def G7():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
    graph.add_edges_from(
        [
            (1, 2),
            (1, 3),
            (1, 5),
            (1, 7),
            (2, 3),
            (2, 4),
            (2, 8),
            (8, 4),
            (8, 6),
            (8, 7),
            (7, 5),
            (7, 6),
            (3, 4),
            (4, 6),
            (6, 5),
            (5, 3),
        ]
    )
    return graph


def G8():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4])
    graph.add_edges_from([(1, 2), (2, 3), (3, 4)])
    return graph


def G9():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6])
    graph.add_edges_from([(1, 5), (2, 5), (3, 6), (4, 6), (5, 6)])
    return graph


def G10():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5])
    graph.add_edges_from([(1, 2), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (4, 5)])
    return graph


def G11():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6])
    graph.add_edges_from(
        [(1, 2), (1, 5), (1, 6), (2, 3), (3, 4), (4, 5), (4, 6), (5, 6)]
    )
    return graph


def G12():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    graph.add_edges_from(
        [(1, 2), (1, 5), (1, 6), (2, 3), (2, 7), (3, 4), (3, 7), (4, 5), (4, 6), (5, 6)]
    )
    return graph


def G13():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
    graph.add_edges_from(
        [
            (1, 2),
            (1, 5),
            (1, 6),
            (1, 7),
            (2, 3),
            (2, 8),
            (2, 9),
            (3, 4),
            (3, 8),
            (3, 9),
            (4, 5),
            (4, 6),
            (4, 7),
            (5, 6),
        ]
    )
    return graph


def G14():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    graph.add_edges_from(
        [
            (1, 2),
            (1, 3),
            (1, 5),
            (1, 7),
            (2, 3),
            (2, 6),
            (3, 4),
            (4, 5),
            (4, 6),
            (5, 7),
            (6, 7),
        ]
    )
    return graph


def G15():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
    graph.add_edges_from(
        [
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (2, 3),
            (2, 7),
            (2, 8),
            (2, 9),
            (3, 6),
            (3, 7),
            (3, 9),
            (4, 5),
            (4, 6),
            (4, 8),
            (4, 9),
            (5, 6),
            (5, 7),
            (5, 8),
            (6, 7),
            (6, 9),
            (7, 8),
            (8, 9),
        ]
    )
    return graph


def big_empty():
    return nx.erdos_renyi_graph(50, 0.0, 1)


def big_sparse():
    return nx.erdos_renyi_graph(50, 0.1, 1)


def big_rand():
    return nx.erdos_renyi_graph(50, 0.5, 1)


def big_dense():
    return nx.erdos_renyi_graph(50, 0.9, 1)


def big_complete():
    return nx.erdos_renyi_graph(50, 1.0, 1)


# --------------------------------------------------------------------------
# Test graphs
TEST_CASES = [
    null_graph,
    singleton,
    dyad,
    disconnected,
    three_node_clique,
    G1,
    G2,
    G3,
    G4,
    G5,
    G6,
    G7,
    G8,
    G9,
    G10,
    G11,
    G12,
    G13,
    G14,
    G15,
    big_empty,
    big_sparse,
    big_rand,
    big_dense,
    big_complete,
]


# --------------------------------------------------------------------------
# Helper functions to test
# (graph function, valid # of colors)
def check_state(L, N, H, F, C):
    s = len(C[0])
    num_colors = len(C.keys())
    assert all(u in L[v] for u in L for v in L[u])
    assert all(F[u] != F[v] for u in L for v in L[u])
    assert all(len(L[u]) < num_colors for u in L)
    assert all(len(C[x]) == s for x in C)
    assert all(H[(c1, c2)] >= 0 for c1 in C for c2 in C)
    assert all(N[(u, F[u])] == 0 for u in F)


def max_degree(G):
    """Get the maximum degree of any node in G."""
    return max(G.degree(node) for node in G.nodes) if len(G.nodes) > 0 else 0


def make_params_from_graph(G, F):
    """Returns {N, L, H, C} from the given graph."""
    num_nodes = len(G)
    L = {u: [] for u in range(num_nodes)}
    for u, v in G.edges:
        L[u].append(v)
        L[v].append(u)
    C = nx.algorithms.coloring.equitable_coloring.make_C_from_F(F)
    N = nx.algorithms.coloring.equitable_coloring.make_N_from_L_C(L, C)
    H = nx.algorithms.coloring.equitable_coloring.make_H_from_C_N(C, N)
    return {"N": N, "F": F, "C": C, "H": H, "L": L}
