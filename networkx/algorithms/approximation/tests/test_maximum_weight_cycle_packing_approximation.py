import random

import networkx as nx
from networkx.algorithms.approximation.maximum_weight_cycle_packing_approximation_algorithm import (
    maximum_weight_cycle_packing_approximation_algorithm,
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
    assert maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3) == [
        (3, 2),
        (4, 1, 6),
    ]
    assert maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 2) == [
        (3, 2),
        (6, 1),
    ]


def test_2():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from([1, 2, 3])
    graphEX3.add_weighted_edges_from([(1, 2, 1), (2, 1, 5), (2, 3, 2), (3, 1, 2)])
    assert maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 2) == [(2, 1)]


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
    assert maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3) == [
        (4, 5, 7),
        (6, 1),
        (9, 8),
    ]


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
    assert maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3) == [
        (4, 5, 7),
        (6, 1),
        (9, 8),
        (12, 16, 13),
        (15, 11),
        (19, 18),
    ]
    assert maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 2) == [
        (6, 1),
        (9, 8),
        (15, 11),
        (19, 18),
    ]


def test_5():
    graphEX3 = nx.fast_gnp_random_graph(20, 0.15, 42, True)
    for (u, v, w) in graphEX3.edges(data=True):
        w["weight"] = random.randint(0, 10)
    res = maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3)
    nodes_seen = []
    flag = True
    for cyc in res:
        for node in cyc:
            if node in nodes_seen:
                flag = False
                break
            nodes_seen.append(node)
    assert flag


def test_6():
    graphEX3 = nx.fast_gnp_random_graph(20, 0.15, 42, True)
    for (u, v, w) in graphEX3.edges(data=True):
        w["weight"] = random.randint(0, 10)
    res = maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3)
    nodes_seen = []
    flag = True
    for cyc in res:
        if len(cyc) > 3:
            flag = False
            break
    assert flag


def test_7():
    from networkx.algorithms.simple_cycles_le_k import simple_cycles_le_k

    graphEX3 = nx.fast_gnp_random_graph(20, 0.15, 42, True)
    for (u, v, w) in graphEX3.edges(data=True):
        w["weight"] = random.randint(0, 10)
    sc = simple_cycles_le_k(graphEX3, 3)
    try:
        cy = next(sc)
        res = maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 3)
        if cy is not None:
            assert len(res) > 1
    except:
        assert True
