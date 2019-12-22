"""Unit tests for the :mod:`networkx.generators.sudoku_graph` module."""

import pytest
import networkx as nx


def test_sudoku_negative():
    """Verify that an error is raised when generating a Sudoku graph of order -1."""
    pytest.raises(nx.NetworkXError, nx.sudoku_graph, n=-1)


def test_sudoku_empty():
    """Generate an empty Sudoku graph."""
    G = nx.sudoku_graph(0)
    assert G.is_directed() is False
    assert G.is_multigraph() is False
    assert nx.is_empty(G) is True


def test_sudoku_1x1():
    """Generate a 1-Sudoku graph (1x1) and verify its properties."""
    G = nx.sudoku_graph(1)
    assert G.is_directed() is False
    assert G.is_multigraph() is False
    assert G.number_of_nodes() == 1
    assert G.number_of_edges() == 0


def test_sudoku_4x4():
    """Generate a 2-Sudoku graph (4x4) and verify its properties."""
    G = nx.sudoku_graph(2)
    assert G.is_directed() is False
    assert G.is_multigraph() is False
    assert G.number_of_nodes() == 16
    assert G.number_of_edges() == 56
    assert all(d[1] == 7 for d in G.degree)
    assert sorted(G.neighbors(6)) == [2, 3, 4, 5, 7, 10, 14]


def test_sudoku_9x9():
    """Generate a 3-Sudoku graph (9x9) and verify its properties."""
    G = nx.sudoku_graph()
    assert G.is_directed() is False
    assert G.is_multigraph() is False
    assert G.number_of_nodes() == 81
    assert G.number_of_edges() == 810
    assert all(d[1] == 20 for d in G.degree)
    assert sorted(G.neighbors(42)) == [
        6, 15, 24, 33, 34, 35, 36, 37, 38, 39,
        40, 41, 43, 44, 51, 52, 53, 60, 69, 78]


def test_sudoku_16x16():
    """Generate a 4-Sudoku graph (16x16) and verify its properties."""
    G = nx.sudoku_graph(4)
    assert G.number_of_nodes() == 256
    assert G.number_of_edges() == 4992
