# -*- coding: utf-8 -*-
#
# lattice.py - functions for generating graphs of point lattices
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for generating graphs representing `point lattices`_, such as
rectangular or triangular grid graphs.

The :func:`grid_2d_graph`, :func:`triangular_lattice_graph`, and
:func:`hexagonal_lattice_graph` functions correspond to the three
`regular tilings of the plane`_, the square, triangular, and hexagonal
tilings, respectively.

.. _point lattices: http://mathworld.wolfram.com/PointLattice.html
.. _regular tilings of the plane: https://en.wikipedia.org/wiki/List_of_regular_polytopes_and_compounds#Euclidean_tilings

"""
from __future__ import division

from itertools import chain

from networkx.classes import Graph
from networkx.algorithms.operators.product import cartesian_product
from networkx.exception import NetworkXError
from networkx.relabel import relabel_nodes
from networkx.utils import flatten
from networkx.utils import is_list_of_ints
from networkx.generators.classic import cycle_graph
from networkx.generators.classic import empty_graph
from networkx.generators.classic import path_graph

__all__ = ['grid_2d_graph', 'grid_graph', 'hypercube_graph',
           'triangular_lattice_graph']


def grid_2d_graph(m, n, periodic=False, create_using=None):
    """Returns the two-dimensional grid graph.

    Parameters
    ----------
    m, n : int
        The dimensions of the graph. The number of nodes will be ``m *
        n``.

    periodic : bool
        If this is ``True`` the nodes on the grid boundaries are joined
        to the corresponding nodes on the opposite grid boundaries.

    create_using : NetworkX graph
        If specified, a graph whose type matches that of this object
        will be returned.

    Returns
    -------
    NetworkX graph
        The (possibly periodic) grid graph of the specified dimensions.

    """
    G = empty_graph(0, create_using)
    G.name = "grid_2d_graph"
    rows = range(m)
    columns = range(n)
    G.add_nodes_from((i, j) for i in rows for j in columns)
    G.add_edges_from(((i, j), (i - 1, j)) for i in rows for j in columns
                     if i > 0)
    G.add_edges_from(((i, j), (i, j - 1)) for i in rows for j in columns
                     if j > 0)
    if G.is_directed():
        G.add_edges_from(((i, j), (i + 1, j)) for i in rows for j in columns
                         if i < m - 1)
        G.add_edges_from(((i, j), (i, j + 1)) for i in rows for j in columns
                         if j < n - 1)
    if periodic:
        if n > 2:
            G.add_edges_from(((i, 0), (i, n - 1)) for i in rows)
            if G.is_directed():
                G.add_edges_from(((i, n - 1), (i, 0)) for i in rows)
        if m > 2:
            G.add_edges_from(((0, j), (m - 1, j)) for j in columns)
            if G.is_directed():
                G.add_edges_from(((m - 1, j), (0, j)) for j in columns)
        G.name = "periodic_grid_2d_graph(%d,%d)" % (m, n)
    return G


def grid_graph(dim, periodic=False):
    """Returns the *n*-dimensional grid graph.

    The dimension *n* is the length of the list ``dim`` and the size in
    each dimension is the value of the corresponding list element.

    Parameters
    ----------
    dim : list
        A list of integers representing the size of each dimension. The
        number of dimensions is the length of this list.

    periodic : bool
        If this is ``True`` the nodes on the grid boundaries are joined
        to the corresponding nodes on the opposite grid boundaries.

    Returns
    -------
    NetworkX graph
        The (possibly periodic) grid graph of the specified dimensions.

    Examples
    --------
    To produce a 2 × 3 × 4 grid graph, a graph on 24 nodes::

        >>> G = grid_graph(dim=[2, 3, 4])
        >>> len(G)
        24

    """
    dlabel = "%s" % dim
    if dim == []:
        G = empty_graph(0)
        G.name = "grid_graph(%s)" % dim
        return G
    if not is_list_of_ints(dim):
        raise NetworkXError("dim is not a list of integers")
    if min(dim) <= 0:
        raise NetworkXError("dim is not a list of strictly positive integers")
    if periodic:
        func = cycle_graph
    else:
        func = path_graph

    dim = list(dim)
    current_dim = dim.pop()
    G = func(current_dim)
    while len(dim) > 0:
        current_dim = dim.pop()
        # order matters: copy before it is cleared during the creation of Gnew
        Gold = G.copy()
        Gnew = func(current_dim)
        # explicit: create_using = None
        # This is so that we get a new graph of Gnew's class.
        G = cartesian_product(Gnew, Gold)
    # graph G is done but has labels of the form (1,(2,(3,1)))
    # so relabel
    H = relabel_nodes(G, flatten)
    H.name = "grid_graph(%s)" % dlabel
    return H


def hypercube_graph(n):
    """Returns the *n*-dimensional hypercube graph.

    The nodes are the integers between 0 and ``2 ** n - 1``, inclusive.

    For more information on the hypercube graph, see the Wikipedia
    article *`Hypercube graph`_*.

    .. _Hypercube graph: https://en.wikipedia.org/wiki/Hypercube_graph

    Parameters
    ----------
    n : int
        The dimension of the hypercube. The number of nodes in the graph
        will be ``2 ** n - 1``.

    Returns
    -------
    NetworkX graph
        The hypercube graph of dimension *n*. This graph has ``2 ** n``
        nodes.

    """
    dim = n * [2]
    G = grid_graph(dim)
    G.name = "hypercube_graph_(%d)" % n
    return G


def triangular_lattice_graph(m, n, periodic=False, create_using=None):
    """Returns the *m* × *n* triangular lattice graph.

    The *`triangular lattice graph`_* is a two-dimensional grid graph in
    which each grid unit has a chord (in other words, each square has a
    diagonal edge).

    The returned graph will have ``m`` rows and ``n`` columns of
    primitive units.

    .. _triangular lattice graph: http://mathworld.wolfram.com/TriangularGrid.html

    Parameters
    ----------
    m : int
        The number of rows in the lattice.

    n : int
        The number of columns in the lattice.

    periodic : bool
        Whether to join the boundary vertices of the grid using periodic
        boundary conditions.

    create_using : NetworkX graph
        If specified, this must be an instance of a NetworkX graph
        class; the type of this graph dictates the type of the output
        graph. If not specified, the returned graph will have the same
        type as the input graph.

    Returns
    -------
    NetworkX graph
        The *m* × *n* triangular lattice graph.

    """
    G = grid_2d_graph(m, n, periodic=periodic, create_using=create_using)
    # If the graph is periodic, add edges as if the lattice were on a torus.
    rows = m if periodic else m - 1
    cols = n if periodic else n - 1
    # Add the triangle edges: a chord within each square.
    diag = lambda i, j: ((i + 1) % m, (j + 1) % n)
    chords = (((i, j), diag(i, j)) for i in range(rows) for j in range(cols))
    G.add_edges_from(chords)
    # If the graph is directed, add the reverse edges as well.
    if G.is_directed():
        G.add_edges_from((v, u) for (u, v) in G.edges())
    G.name = 'triangular_lattice_graph({}, {})'.format(m, n)
    return G


def hexagonal_lattice_graph(m, n, periodic=False, create_using=None):
    """Returns the *m* × *n* hexagonal lattice graph.

    The *hexagonal lattice graph* is a graph whose nodes and edges are
    the vertices and edges of the `hexagonal tiling`_ of the plane.

    The returned graph will have ``m`` rows of hexagons and ``n / 2``
    columns of hexagons.

    .. _hexagonal tiling: https://en.wikipedia.org/wiki/Hexagonal_tiling

    Parameters
    ----------
    m : int
        The number of rows of hexagons in the lattice.

    n : int
        Twice the number of columns of hexagons in the lattice.

    periodic : bool
        Whether to join the boundary vertices of the grid using periodic
        boundary conditions.

    create_using : NetworkX graph
        If specified, this must be an instance of a NetworkX graph
        class; the type of this graph dictates the type of the output
        graph. If not specified, the returned graph will have the same
        type as the input graph.

    Returns
    -------
    NetworkX graph
        The *m* × *n* hexagonal lattice graph.

    """
    G = create_using if create_using is not None else Graph()
    G.clear()
    G.add_nodes_from((i, j) for i in range(m) for j in range(n))
    # Add "row" edges and "column" edges.
    row_edges = (((i, j), (i, j + 1)) for i in range(m) for j in range(n - 1))
    col_edges = (((i, 2 * j + (i % 2)), (i + 1, 2 * j + (i % 2)))
                 for i in range(m - 1) for j in range((n // 2) - 1))
    G.add_edges_from(chain(row_edges, col_edges))
    if G.is_directed():
        G.add_edges_from((v, u) for (u, v) in G.edges())
    G.name = 'hexagonal_lattice_graph({}, {})'.format(m, n)
    return G
