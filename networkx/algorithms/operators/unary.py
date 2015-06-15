"""Unary operations on graphs"""
#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult(dschult@colgate.edu)'])
__all__ = ['complement', 'reverse']


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
                      for n, nbrs in G.adjacency_iter()
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
