# test_lattice.py - unit tests for the lattice module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.generators.lattice` module."""
import itertools

from nose.tools import assert_equal
from nose.tools import assert_true

import networkx as nx


class TestGrid2DGraph:
    """Unit tests for the :func:`networkx.generators.lattice.grid_2d_graph`
    function.

    """
    def test_number_of_vertices(self):
        m, n = 5, 6
        G = nx.grid_2d_graph(m, n)
        assert_equal(len(G), m * n)

    def test_degree_distribution(self):
        m, n = 5, 6
        G = nx.grid_2d_graph(m, n)
        expected_histogram = [0, 0, 4, 2 * (m + n) - 8, (m - 2) * (n - 2)]
        assert_equal(nx.degree_histogram(G), expected_histogram)

    def test_directed(self):
        m, n = 5, 6
        G = nx.grid_2d_graph(m, n)
        H = nx.grid_2d_graph(m, n, create_using=nx.DiGraph())
        assert_equal(H.succ, G.adj)
        assert_equal(H.pred, G.adj)

    def test_multigraph(self):
        m, n = 5, 6
        G = nx.grid_2d_graph(m, n)
        H = nx.grid_2d_graph(m, n, create_using=nx.MultiGraph())
        assert_equal(list(H.edges()), list(G.edges()))

    def test_periodic(self):
        G = nx.grid_2d_graph(0, 0, periodic=True)
        assert_equal(dict(G.degree()), {})

        for m, n, H in [(2, 2, nx.cycle_graph(4)), (1, 7, nx.cycle_graph(7)),
                        (7, 1, nx.cycle_graph(7)),
                        (2, 5, nx.circular_ladder_graph(5)),
                        (5, 2, nx.circular_ladder_graph(5)),
                        (2, 4, nx.cubical_graph()),
                        (4, 2, nx.cubical_graph())]:
            G = nx.grid_2d_graph(m, n, periodic=True)
            assert_true(nx.could_be_isomorphic(G, H))

    def test_periodic_directed(self):
        G = nx.grid_2d_graph(4, 2, periodic=True)
        H = nx.grid_2d_graph(4, 2, periodic=True, create_using=nx.DiGraph())
        assert_equal(H.succ, G.adj)
        assert_equal(H.pred, G.adj)

    def test_periodic_multigraph(self):
        G = nx.grid_2d_graph(4, 2, periodic=True)
        H = nx.grid_2d_graph(4, 2, periodic=True, create_using=nx.MultiGraph())
        assert_equal(list(G.edges()), list(H.edges()))


class TestGridGraph:
    """Unit tests for the :func:`networkx.generators.lattice.grid_graph`
    function.

    """

    def test_grid_graph(self):
        """grid_graph([n,m]) is a connected simple graph with the
        following properties:
        number_of_nodes = n*m
        degree_histogram = [0,0,4,2*(n+m)-8,(n-2)*(m-2)]
        """
        for n, m in [(3, 5), (5, 3), (4, 5), (5, 4)]:
            dim = [n, m]
            g = nx.grid_graph(dim)
            assert_equal(len(g), n*m)
            assert_equal(nx.degree_histogram(g), [0, 0, 4, 2 * (n + m) - 8,
                                                  (n - 2) * (m - 2)])
            assert_equal(dim, [n, m])

        for n, m in [(1, 5), (5, 1)]:
            dim = [n, m]
            g = nx.grid_graph(dim)
            assert_equal(len(g), n*m)
            assert_true(nx.is_isomorphic(g, nx.path_graph(5)))
            assert_equal(dim, [n, m])

#        mg = grid_graph([n,m], create_using=MultiGraph())
#        assert_equal(mg.edges(), g.edges())


class TestHypercubeGraph:
    """Unit tests for the :func:`networkx.generators.lattice.hypercube_graph`
    function.

    """

    def test_special_cases(self):
        for n, H in [(0, nx.null_graph()), (1, nx.path_graph(2)),
                     (2, nx.cycle_graph(4)), (3, nx.cubical_graph())]:
            G = nx.hypercube_graph(n)
            assert_true(nx.could_be_isomorphic(G, H))

    def test_degree_distribution(self):
        for n in range(1, 10):
            G = nx.hypercube_graph(n)
            expected_histogram = [0] * n + [2 ** n]
            assert_equal(nx.degree_histogram(G), expected_histogram)


class TestTriangularLatticeGraph:
    """Unit tests for the
    :func:`networkx.generators.lattice.triangular_lattice_graph`
    function.

    """

    def test_lattice_points(self):
        """Tests that the graph is really a triangular lattice."""
        m = 3
        n = 4
        G = nx.triangular_lattice_graph(m, n)
        assert_equal(len(G), m * n)
        for (i, j) in itertools.product(range(m - 1), range(n - 1)):
            assert_true((i, j + 1) in G[(i, j)])
            assert_true((i + 1, j) in G[(i, j)])
            assert_true((i + 1, j + 1) in G[(i, j)])

    def test_directed(self):
        """Tests for creating a directed triangular lattice."""
        G = nx.triangular_lattice_graph(3, 4, create_using=nx.Graph())
        H = nx.triangular_lattice_graph(3, 4, create_using=nx.DiGraph())
        assert_true(H.is_directed())
        assert_equal(H.succ, G.adj)
        assert_equal(H.pred, G.adj)

    def test_multigraph(self):
        """Tests for creating a triangular lattice multigraph."""
        G = nx.triangular_lattice_graph(3, 4, create_using=nx.Graph())
        H = nx.triangular_lattice_graph(3, 4, create_using=nx.MultiGraph())
        assert_equal(list(H.edges()), list(G.edges()))


class TestHexagonalLatticeGraph:
    """Unit tests for the
    :func:`networkx.generators.lattice.hexagonal_lattice_graph`
    function.

    """

    def test_lattice_points(self):
        """Tests that the graph is really a hexagonal lattice."""
        m = 3
        n = 5
        G = nx.hexagonal_lattice_graph(m, n)
        assert_equal(len(G), m * n)
        C_6 = nx.cycle_graph(6)
        hexagons = [
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)],
            [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)],
            [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)],
            [(2, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 2)],
            [(2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4)],
            ]
        for hexagon in hexagons:
            assert_true(nx.is_isomorphic(G.subgraph(hexagon), C_6))

    def test_directed(self):
        """Tests for creating a directed hexagonal lattice."""
        G = nx.hexagonal_lattice_graph(3, 5, create_using=nx.Graph())
        H = nx.hexagonal_lattice_graph(3, 5, create_using=nx.DiGraph())
        assert_true(H.is_directed())
        assert_equal(H.succ, G.adj)
        assert_equal(H.pred, G.adj)

    def test_multigraph(self):
        """Tests for creating a hexagonal lattice multigraph."""
        G = nx.hexagonal_lattice_graph(3, 5, create_using=nx.Graph())
        H = nx.hexagonal_lattice_graph(3, 5, create_using=nx.MultiGraph())
        assert_equal(list(H.edges()), list(G.edges()))
