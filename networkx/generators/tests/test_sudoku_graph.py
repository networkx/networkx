"""Unit tests for the :mod:`networkx.generators.sudoku_graph` module."""

import networkx as nx
import pytest


class TestSudokuGraph(object):

    def test_sudoku_negative(self):
        pytest.raises(nx.NetworkXError, nx.sudoku_graph, n=-1)


    def test_sudoku_empty(self):
        G = nx.sudoku_graph(0)
        assert G.is_directed() is False
        assert G.is_multigraph() is False
        assert nx.is_empty(G) is True


    def test_sudoku_1x1(self):
        G = nx.sudoku_graph(1)
        assert G.is_directed() is False
        assert G.is_multigraph() is False
        assert G.number_of_nodes() == 1
        assert G.number_of_edges() == 0


    def test_sudoku_4x4(self):
        G = nx.sudoku_graph(2)
        assert G.is_directed() is False
        assert G.is_multigraph() is False
        assert G.number_of_nodes() == 16
        assert G.number_of_edges() == 56
        assert all(d[1] == 7 for d in G.degree)
        assert sorted(G.neighbors(6)) == [2, 3, 4, 5, 7, 10, 14]


    def test_sudoku_9x9(self):
        G = nx.sudoku_graph()
        assert G.is_directed() is False
        assert G.is_multigraph() is False
        assert G.number_of_nodes() == 81
        assert G.number_of_edges() == 810
        assert all(d[1] == 20 for d in G.degree)
        assert sorted(G.neighbors(42)) == [
            6, 15, 24, 33, 34, 35, 36, 37, 38, 39,
            40, 41, 43, 44, 51, 52, 53, 60, 69, 78]

    def test_sudoku_16x16(self):
        G = nx.sudoku_graph(4)
        assert G.number_of_nodes() == 256
        assert G.number_of_edges() == 4992
