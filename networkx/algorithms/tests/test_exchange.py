import networkx as nx
import pytest
from Exchange_Algorithm import APXalgorithm, ExactAlgorithm


def test_1():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from([1, 2, 3, 4, 5, 6])
    graphEX3.add_weighted_edges_from(
        [(1, 2, 4), (2, 1, 3), (1, 3, 5), (3, 1, 6), (3, 2, 1), (2, 3, 2), (1, 5, 9), (1, 6, 8), (6, 1, 7), (4, 1, 11),
         (6, 4, 10), (5, 6, 12)])
    assert APXalgorithm(graphEX3, 3) == [[1, 6, 4]]
    assert ExactAlgorithm(graphEX3, 3) == [[1, 6, 4]]
    assert APXalgorithm(graphEX3, 2) == [[1, 6]]
    assert ExactAlgorithm(graphEX3, 2) == [[1, 6]]


def test_2():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from([1, 2, 3])
    graphEX3.add_weighted_edges_from([(1, 2, 1), (2, 1, 5), (2, 3, 2), (3, 1, 2)])
    assert APXalgorithm(graphEX3, 3) == [[1, 2]]
    assert ExactAlgorithm(graphEX3, 3) == [[1, 2]]
    assert APXalgorithm(graphEX3, 2) == [[1, 2]]
    assert ExactAlgorithm(graphEX3, 2) == [[1, 2]]


def test_3():
    graphEX3 = nx.DiGraph()
    graphEX3.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
    graphEX3.add_weighted_edges_from(
        [(1, 6, 11), (6, 1, 10), (1, 5, 3), (5, 1, 2), (8, 9, 11), (9, 8, 20), (3, 2, 6), (2, 6, 5), (6, 3, 8),
         (5, 7, 6), (7, 4, 11), (4, 5, 5)])
    assert APXalgorithm(graphEX3, 3) == [[1, 5], [8, 9], [1, 3, 2]]
    assert ExactAlgorithm(graphEX3, 3) == [[8, 9], [1, 6], [4, 5, 7]]
