import networkx as nx
import pytest
from Exchange_Algorithm import APXalgorithm, ExactAlgorithm


def test_1():
    graphEX3 = nx.DiGraph()
    graphEX3.add_node(1)
    graphEX3.add_node(2)
    graphEX3.add_node(3)
    graphEX3.add_node(4)
    graphEX3.add_node(5)
    graphEX3.add_node(6)
    graphEX3.add_edge(1, 2, weight=4)
    graphEX3.add_edge(2, 1, weight=3)
    graphEX3.add_edge(1, 3, weight=5)
    graphEX3.add_edge(3, 1, weight=6)
    graphEX3.add_edge(3, 2, weight=1)
    graphEX3.add_edge(2, 3, weight=2)
    graphEX3.add_edge(1, 5, weight=9)
    graphEX3.add_edge(1, 6, weight=8)
    graphEX3.add_edge(6, 1, weight=7)
    graphEX3.add_edge(4, 1, weight=11)
    graphEX3.add_edge(6, 4, weight=10)
    graphEX3.add_edge(5, 6, weight=12)
    assert APXalgorithm(graphEX3, 3) == [[1, 6, 4]]
    assert ExactAlgorithm(graphEX3, 3) == [[1, 6, 4]]
    assert APXalgorithm(graphEX3, 2) == [[1, 6]]
    assert ExactAlgorithm(graphEX3, 2) == [[1, 6]]


def test_2():
    graphEX3 = nx.DiGraph()
    graphEX3.add_node(1)
    graphEX3.add_node(2)
    graphEX3.add_node(3)
    graphEX3.add_edge(1, 2, weight=1)
    graphEX3.add_edge(2, 1, weight=5)
    graphEX3.add_edge(2, 3, weight=2)
    graphEX3.add_edge(3, 1, weight=2)
    assert APXalgorithm(graphEX3, 3) == [[1, 2]]
    assert ExactAlgorithm(graphEX3, 3) == [[1, 2]]
    assert APXalgorithm(graphEX3, 2) == [[1, 2]]
    assert ExactAlgorithm(graphEX3, 2) == [[1, 2]]


def test_3():
    graphEX3 = nx.DiGraph()
    graphEX3.add_node(1)
    graphEX3.add_node(2)
    graphEX3.add_node(3)
    graphEX3.add_node(4)
    graphEX3.add_node(5)
    graphEX3.add_node(6)
    graphEX3.add_node(7)
    graphEX3.add_node(8)
    graphEX3.add_node(9)
    graphEX3.add_edge(1, 6, weight=11)
    graphEX3.add_edge(6, 1, weight=10)
    graphEX3.add_edge(1, 5, weight=3)
    graphEX3.add_edge(5, 1, weight=2)
    graphEX3.add_edge(8, 9, weight=11)
    graphEX3.add_edge(9, 8, weight=20)
    graphEX3.add_edge(3, 2, weight=6)
    graphEX3.add_edge(2, 6, weight=5)
    graphEX3.add_edge(6, 3, weight=8)
    graphEX3.add_edge(5, 7, weight=6)
    graphEX3.add_edge(7, 4, weight=11)
    graphEX3.add_edge(4, 5, weight=5)
    assert APXalgorithm(graphEX3, 3) == [[1, 5], [8, 9], [1, 3, 2]]
    assert ExactAlgorithm(graphEX3, 3) == [[8, 9], [1, 6], [4, 5, 7]]
