import networkx as nx
import pytest
import networkx.generators.sudoku_graph as sudoku_graph
from networkx.testing.utils import assert_edges_equal


def test_sudoku_negative():
    pytest.raises(nx.NetworkXError, sudoku_graph, n=-1)


def test_sudoku_empty():
    G = sudoku_graph(0)
    assert G.is_directed() is False
    assert G.is_multigraph() is False
    assert nx.is_empty(G) is True


def test_sudoku_1x1():
    G = sudoku_graph(1)
    assert G.is_directed() is False
    assert G.is_multigraph() is False
    assert G.number_of_nodes() == 1
    assert G.number_of_edges() == 0


def test_sudoku_4x4():
    G = sudoku_graph(2)
    assert G.is_directed() is False
    assert G.is_multigraph() is False
    assert G.number_of_nodes() == 16
    assert G.number_of_edges() == 56
    assert all(d[1] == 7 for d in G.degree)
    assert sorted(G.neighbors(6)) == [2, 3, 4, 5, 7, 10, 14]


def test_sudoku_9x9():
    G = sudoku_graph()
    assert G.is_directed() is False
    assert G.is_multigraph() is False
    assert G.number_of_nodes() == 81
    assert G.number_of_edges() == 810
    assert all(d[1] == 20 for d in G.degree)
    assert sorted(G.neighbors(42)) == [
        6, 15, 24, 33, 34, 35, 36, 37, 38, 39,
        40, 41, 43, 44, 51, 52, 53, 60, 69, 78]