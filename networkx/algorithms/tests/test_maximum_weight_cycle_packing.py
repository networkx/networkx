import networkx as nx
from networkx.algorithms.approximation.Maximum_weight_cycle_packing_approximation_algorithm import (
    Maximum_weight_cycle_packing_approximation_algorithm,
)
from networkx.algorithms.maximum_weight_cycle_packing import (
    maximum_weight_cycle_packing,
)


def test_1():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from([1, 2, 3, 4, 5, 6])
    graphEX3.add_weighted_edges_from(
        [
            (1, 2, 4),
            (2, 1, 3),
            (1, 3, 5),
            (3, 1, 6),
            (3, 2, 1),
            (2, 3, 2),
            (1, 5, 9),
            (1, 6, 8),
            (6, 1, 7),
            (4, 1, 11),
            (6, 4, 10),
            (5, 6, 12),
        ]
    )
    assert Maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3) == [
        (1, 6, 4),
        (2, 3),
    ]
    assert maximum_weight_cycle_packing(graphEX3, 3) == [[1, 6, 4], [2, 3]]
    assert Maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 2) == [
        (1, 6),
        (2, 3),
    ]
    assert maximum_weight_cycle_packing(graphEX3, 2) == [[1, 6, 4]]


def test_2():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from([1, 2, 3])
    graphEX3.add_weighted_edges_from([(1, 2, 1), (2, 1, 5), (2, 3, 2), (3, 1, 2)])
    assert Maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3) == [[1, 2, 3]]
    assert maximum_weight_cycle_packing(graphEX3, 3) == [
        [1, 2, 3]
    ]
    assert Maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 2) == [(1, 2)]
    assert maximum_weight_cycle_packing(graphEX3, 2) == [[1, 2]]


def test_3():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
    graphEX3.add_weighted_edges_from(
        [
            (1, 6, 11),
            (6, 1, 10),
            (1, 5, 3),
            (5, 1, 2),
            (8, 9, 11),
            (9, 8, 20),
            (3, 2, 6),
            (2, 6, 5),
            (6, 3, 8),
            (5, 7, 6),
            (7, 4, 11),
            (4, 5, 5),
        ]
    )
    assert Maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3) == [
        (1, 6),
        (4, 5, 7),
        (8, 9),
    ]
    assert maximum_weight_cycle_packing(graphEX3, 3) == [[2, 6, 3], [8, 9], [4, 5, 7]]


def test_4():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    )
    graphEX3.add_weighted_edges_from(
        [
            (1, 6, 11),
            (6, 1, 10),
            (1, 5, 3),
            (5, 1, 2),
            (8, 9, 11),
            (9, 8, 20),
            (3, 2, 6),
            (2, 6, 5),
            (6, 3, 8),
            (5, 7, 6),
            (7, 4, 11),
            (4, 5, 5),
            (10, 16, 1),
            (16, 11, 10),
            (11, 15, 3),
            (15, 11, 2),
            (18, 19, 11),
            (19, 18, 20),
            (13, 12, 6),
            (12, 16, 5),
            (16, 13, 8),
        ]
    )
    assert Maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3) == [
        (1, 6),
        (4, 5, 7),
        (8, 9),
        (11, 15),
        (16, 13, 12),
        (18, 19),
    ]
    assert maximum_weight_cycle_packing(graphEX3, 3) == [
        [16, 13, 12],
        [4, 5, 7],
        [2, 6, 3],
        [11, 15],
        [8, 9],
        [18, 19],
    ]
    assert Maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 2) == [
        (1, 6),
        (11, 15),
        (18, 19),
        (8, 9),
    ]
    assert maximum_weight_cycle_packing(graphEX3, 3) == [
        [1, 6],
        [11, 15],
        [18, 19],
        [8, 9],
    ]
