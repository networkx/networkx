"""Unary operations on graphs"""
#    Copyright (C) 2004-2012 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils import is_string_like
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
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
        name="complement(%s)"%(G.name)
    R=G.__class__()
    R.name=name
    R.add_nodes_from(G)
    R.add_edges_from( ((n,n2)
                       for n,nbrs in G.adjacency_iter()
                       for n2 in G if n2 not in nbrs
                       if n != n2) )
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
    from copy import deepcopy

    if not G.is_directed():
        raise nx.NetworkXError("Cannot reverse an undirected graph.")

    if copy:
        H = G.__class__(name="Reverse of ({0})".format(G.name))
        H.add_nodes_from(G)
        if G.is_multigraph():
            rev_edges = [ (v,u,k,deepcopy(d))
                          for u,v,k,d in G.edges(keys=True, data=True) ]
        else:
            rev_edges = [ (v,u,deepcopy(d)) for u,v,d in G.edges(data=True) ]
        H.add_edges_from(rev_edges)
        H.graph = deepcopy(G.graph)
        H.node = deepcopy(G.node)
    else:
        G.pred, G.succ = G.succ, G.pred
        G.adj = G.succ
        H = G

    return H

