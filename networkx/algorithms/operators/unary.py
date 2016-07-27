"""Unary operations on graphs"""
#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils import not_implemented_for
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult(dschult@colgate.edu)'])
__all__ = ['complement', 'reverse', 'mycielski']


def complement(G, name=None):
    """Return the graph complement of G.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    name : string
       Specify name for new graph

    Returns
    -------
    GC : A new graph.

    Notes
    ------
    Note that complement() does not create self-loops and also
    does not produce parallel edges for MultiGraphs.

    Graph, node, and edge data are not propagated to the new graph.
    """
    if name is None:
        name = "complement(%s)" % (G.name)
    R = G.__class__()
    R.name = name
    R.add_nodes_from(G)
    R.add_edges_from(((n, n2)
                      for n, nbrs in G.adjacency()
                      for n2 in G if n2 not in nbrs
                      if n != n2))
    return R


def reverse(G, copy=True):
    """Return the reverse directed graph of G.

    Parameters
    ----------
    G : directed graph
        A NetworkX directed graph
    copy : bool
        If True, then a new graph is returned. If False, then the graph is
        reversed in place.

    Returns
    -------
    H : directed graph
        The reversed G.

    """
    if not G.is_directed():
        raise nx.NetworkXError("Cannot reverse an undirected graph.")
    else:
        return G.reverse(copy=copy)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def mycielski(G, iterations):
    """Returns the Mycielskian of a simple, undirected graph G

    The Mycielskian of graph preserves a graph's triangle free
    property while increasing the chromatic number by 1.

    Parameters
    ----------
    G : graph
        A simple, undirected NetworkX graph
    iterations : int
        The number of iterations of the Mycielski operation to
        preform on G. Defaults to 1. Must be a non-negative integer.

    Returns
    -------
    M : graph
        The Mycielskian of G after the specified number of iterations.

    Notes
    ------
    Graph, node, and edge data are not necessarily propagated to the new graph.

    """

    n = G.number_of_nodes()
    M = nx.convert_node_labels_to_integers(G)

    for i in range(iterations):
        n = M.number_of_nodes()
        M.add_nodes_from(range(n, 2*n))
        old_edges = list(M.edges())
        M.add_edges_from((u,v+n) for u,v in old_edges)
        M.add_edges_from((u+n, v) for u,v in old_edges)
        M.add_node(2*n)
        M.add_edges_from((u+n, 2*n) for u in range(n))

    return M
