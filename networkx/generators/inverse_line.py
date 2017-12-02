#    Copyright (C) 2016 by
#    James Clough <james.clough91@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Author:      James Clough (james.clough91@gmail.com)
"""Functions for generating inverse line graphs."""
from itertools import combinations
from collections import defaultdict

import networkx as nx
from networkx.utils import arbitrary_element
from networkx.utils.decorators import *


__all__ = ['inverse_line_graph']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def inverse_line_graph(G):
    """ Returns the inverse line graph of graph G.

    If H is a graph, and G is the line graph of H, such that H = L(G).
    Then H is the inverse line graph of G.

    Not all graphs are line graphs and these do not have an inverse line graph.
    In these cases this generator returns a NetworkXError.

    Parameters
    ----------
    G : graph
        A NetworkX Graph

    Returns
    -------
    H : graph
        The inverse line graph of G.

    Raises
    ------
    NetworkXNotImplemented
        If G is directed or a multigraph

    NetworkXError
        If G is not a line graph

    Notes
    -----
    This is an implementation of the Roussopoulos algorithm.

    References
    ----------
    * Roussopolous, N, "A max {m, n} algorithm for determining the graph H from
      its line graph G", Information Processing Letters 2, (1973), 108--112.

    """
    if G.number_of_edges() == 0 or G.number_of_nodes() == 0:
        msg = "G is not a line graph (has zero vertices or edges)"
        raise nx.NetworkXError(msg)

    starting_cell = _select_starting_cell(G)
    P = _find_partition(G, starting_cell)
    # count how many times each vertex appears in the partition set
    P_count = {u: 0 for u in G.nodes()}
    for p in P:
        for u in p:
            P_count[u] += 1

    if max(P_count.values()) > 2:
        msg = "G is not a line graph (vertex found in more " \
              "than two partition cells)"
        raise nx.NetworkXError(msg)
    W = tuple([(u,) for u in P_count if P_count[u] == 1])
    H = nx.Graph()
    H.add_nodes_from(P)
    H.add_nodes_from(W)
    for a, b in combinations(H.nodes(), 2):
        if len(set(a).intersection(set(b))) > 0:
            H.add_edge(a, b)
    return H


def _triangles(G, e):
    """ Return list of all triangles containing edge e"""
    u, v = e
    if u not in G:
        raise nx.NetworkXError("Vertex %s not in graph" % u)
    if v not in G.neighbors(u):
        raise nx.NetworkXError("Edge (%s, %s) not in graph" % (u, v))
    triangle_list = []
    for x in G.neighbors(u):
        if x in G.neighbors(v):
            triangle_list.append((u, v, x))
    return triangle_list


def _odd_triangle(G, T):
    """ Test whether T is an odd triangle in G

    Parameters
    ----------
    G : NetworkX Graph
    T : 3-tuple of vertices forming triangle in G

    Returns
    -------
    True is T is an odd triangle
    False otherwise

    Raises
    ------
    NetworkXError
        T is not a triangle in G

    Notes
    -----
    An odd triangle is one in which there exists another vertex in G which is
    adjacent to either exactly one or exactly all three of the vertices in the
    triangle.

    """
    for u in T:
        if u not in G.nodes():
            raise nx.NetworkXError("Vertex %s not in graph" % u)
    for e in list(combinations(T, 2)):
        if e[0] not in G.neighbors(e[1]):
            raise nx.NetworkXError("Edge (%s, %s) not in graph" % (e[0], e[1]))

    T_neighbors = defaultdict(int)
    for t in T:
        for v in G.neighbors(t):
            if v not in T:
                T_neighbors[v] += 1
    for v in T_neighbors:
        if T_neighbors[v] in [1, 3]:
            return True
    return False


def _find_partition(G, starting_cell):
    """ Find a partition of the vertices of G into cells of complete graphs

    Parameters
    ----------
    G : NetworkX Graph
    starting_cell : tuple of vertices in G which form a cell

    Returns
    -------
    List of tuples of vertices of G

    Raises
    ------
    NetworkXError
        If a cell is not a complete subgraph then G is not a line graph
    """
    G_partition = G.copy()
    P = [starting_cell]  # partition set
    G_partition.remove_edges_from(list(combinations(starting_cell, 2)))
    # keep list of partitioned nodes which might have an edge in G_partition
    partitioned_vertices = list(starting_cell)
    while G_partition.number_of_edges() > 0:
        # there are still edges left and so more cells to be made
        u = partitioned_vertices[-1]
        deg_u = len(G_partition[u])
        if deg_u == 0:
            # if u has no edges left in G_partition then we have found
            # all of its cells so we do not need to keep looking
            partitioned_vertices.pop()
        else:
            # if u still has edges then we need to find its other cell
            # this other cell must be a complete subgraph or else G is
            # not a line graph
            new_cell = [u] + list(G_partition.neighbors(u))
            for u in new_cell:
                for v in new_cell:
                    if (u != v) and (v not in G.neighbors(u)):
                        msg = "G is not a line graph" \
                              "(partition cell not a complete subgraph)"
                        raise nx.NetworkXError(msg)
            P.append(tuple(new_cell))
            G_partition.remove_edges_from(list(combinations(new_cell, 2)))
            partitioned_vertices += new_cell
    return P


def _select_starting_cell(G, starting_edge=None):
    """ Select a cell to initiate _find_partition

    Parameters
    ----------
    G : NetworkX Graph
    starting_edge: an edge to build the starting cell from

    Returns
    -------
    Tuple of vertices in G

    Raises
    ------
    NetworkXError
        If it is determined that G is not a line graph

    Notes
    -----
    If starting edge not specified then pick an arbitrary edge - doesn't
    matter which. However, this function may call itself requiring a
    specific starting edge. Note that the r, s notation for counting
    triangles is the same as in the Roussopoulos paper cited above.
    """
    if starting_edge is None:
        e = arbitrary_element(list(G.edges()))
    else:
        e = starting_edge
        if e[0] not in G[e[1]]:
            msg = 'starting_edge (%s, %s) is not in the Graph'
            raise nx.NetworkXError(msg % e)
    e_triangles = _triangles(G, e)
    r = len(e_triangles)
    if r == 0:
        # there are no triangles containing e, so the starting cell is just e
        starting_cell = e
    elif r == 1:
        # there is exactly one triangle, T, containing e. If other 2 edges
        # of T belong only to this triangle then T is starting cell
        T = e_triangles[0]
        a, b, c = T
        # ab was original edge so check the other 2 edges
        ac_edges = [x for x in _triangles(G, (a, c))]
        bc_edges = [x for x in _triangles(G, (b, c))]
        if len(ac_edges) == 1:
            if len(bc_edges) == 1:
                starting_cell = T
            else:
                return _select_starting_cell(G, starting_edge=(b, c))
        else:
            return _select_starting_cell(G, starting_edge=(a, c))
    else:
        # r >= 2 so we need to count the number of odd triangles, s
        s = 0
        odd_triangles = []
        for T in e_triangles:
            if _odd_triangle(G, T):
                s += 1
                odd_triangles.append(T)
        if r == 2 and s == 0:
            # in this case either triangle works, so just use T
            starting_cell = T
        elif r-1 <= s <= r:
            # check if odd triangles containing e form complete subgraph
            # there must be exactly s+2 of them
            # and they must all be connected
            triangle_nodes = set([])
            for T in odd_triangles:
                for x in T:
                    triangle_nodes.add(x)
            if len(triangle_nodes) == s+2:
                for u in triangle_nodes:
                    for v in triangle_nodes:
                        if u != v and (v not in G.neighbors(u)):
                            msg = "G is not a line graph (odd triangles " \
                                  "do not form complete subgraph)"
                            raise nx.NetworkXError(msg)
                # otherwise then we can use this as the starting cell
                starting_cell = tuple(triangle_nodes)
            else:
                msg = "G is not a line graph (odd triangles " \
                      "do not form complete subgraph)"
                raise nx.NetworkXError(msg)
        else:
            msg = "G is not a line graph (incorrect number of " \
                  "odd triangles around starting edge)"
            raise nx.NetworkXError(msg)
    return starting_cell
