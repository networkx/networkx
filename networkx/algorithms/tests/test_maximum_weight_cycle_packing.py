# import logger

import random

import networkx as nx
from networkx.algorithms.maximum_weight_cycle_packing import (
    maximum_weight_cycle_packing,
)


def test_normal_1():
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
    assert len(maximum_weight_cycle_packing(graphEX3, 3)) == 2
    assert len(maximum_weight_cycle_packing(graphEX3, 2)) == 2


def test_normal_2():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from([1, 2, 3])
    graphEX3.add_weighted_edges_from([(1, 2, 1), (2, 1, 5), (2, 3, 2), (3, 1, 2)])
    assert len(maximum_weight_cycle_packing(graphEX3, 3)) == 1
    assert len(maximum_weight_cycle_packing(graphEX3, 2)) == 1


def test_normal_3():
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
    assert len(maximum_weight_cycle_packing(graphEX3, 3)) == 3


def test_normal_4():
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
    assert len(maximum_weight_cycle_packing(graphEX3, 3)) == 6


def test_random_check_disjoint():
    """This test is used to check that all the cycles in the result of the algorithm
    are disjointed"""
    graphEX3 = nx.fast_gnp_random_graph(20, 0.15, directed=True)
    for (u, v, w) in graphEX3.edges(data=True):
        w["weight"] = random.randint(0, 10)
    res = maximum_weight_cycle_packing(graphEX3, 3)
    nodes_seen = []
    for cyc in res:
        for node in cyc:
            if node in nodes_seen:
                #                logger.logger.error("Graph: ", graphEX3)
                assert False
            nodes_seen.append(node)
    assert True


def test_random_check_cycle_len():
    """This test is used to check that the length of the received cycles
    are normal"""
    graphEX3 = nx.fast_gnp_random_graph(20, 0.15, directed=True)
    for (u, v, w) in graphEX3.edges(data=True):
        w["weight"] = random.randint(0, 10)
    res = maximum_weight_cycle_packing(graphEX3, 3)
    for cyc in res:
        # if len(cyc)<2:
        #     logger.logger.error("Graph: ",graphEX3)
        assert len(cyc) >= 2


def test_random_check_1cycle():
    """This test is used to check the case of if there are cycles in the graph
    then the result of the algorithm should also contain at least 1 cycle
    """

    while 1:
        graphEX3 = nx.fast_gnp_random_graph(20, 0.15, directed=True)
        sc = nx.simple_cycles(graphEX3, k)
        if next(sc) is not None:
            break
    for (u, v, w) in graphEX3.edges(data=True):
        w["weight"] = random.randint(0, 10)
    res = maximum_weight_cycle_packing(graphEX3, 3)
    assert len(res) >= 1
