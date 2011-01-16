"""
Degree centrality measures.

"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Sasha Gutfraind (ag362@cornell.edu)'])

__all__ = ['degree_centrality',
           'in_degree_centrality',
           'out_degree_centrality']

import networkx as nx

def degree_centrality(G):
    """Compute the degree centrality for nodes.

    The degree centrality for a node v is the fraction of nodes it
    is connected to.

    Parameters
    ----------
    G : graph
      A networkx graph 

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with degree centrality as the value.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality

    Notes
    -----
    The degree centrality values are normalized by dividing by the maximum 
    possible degree in a simple graph n-1 where n is the number of nodes in G.

    For multigraphs or graphs with self loops the maximum degree might
    be higher than n-1 and values of degree centrality greater than 1
    are possible.
    """
    centrality={}
    s=1.0/(len(G)-1.0)
    centrality=dict((n,d*s) for n,d in G.degree_iter())
    return centrality

def in_degree_centrality(G):
    """Compute the in-degree centrality for nodes.

    The in-degree centrality for a node v is the fraction of nodes its 
    incoming edges are connected to.

    Parameters
    ----------
    G : graph
        A NetworkX graph

    Returns
    -------
    nodes : dictionary
        Dictionary of nodes with in-degree centrality as values.

    See Also
    --------
    degree_centrality, out_degree_centrality

    Notes
    -----
    The degree centrality values are normalized by dividing by the maximum 
    possible degree in a simple graph n-1 where n is the number of nodes in G.

    For multigraphs or graphs with self loops the maximum degree might
    be higher than n-1 and values of degree centrality greater than 1
    are possible.
    """
    if not G.is_directed():
        raise nx.NetworkXError(\
            "in_degree_centrality() not defined for undirected graphs.")
    centrality={}
    s=1.0/(len(G)-1.0)
    centrality=dict((n,d*s) for n,d in G.in_degree_iter())
    return centrality


def out_degree_centrality(G):
    """Compute the out-degree centrality for nodes.

    The out-degree centrality for a node v is the fraction of nodes its 
    outgoing edges are connected to.

    Parameters
    ----------
    G : graph
        A NetworkX graph

    Returns
    -------
    nodes : dictionary
        Dictionary of nodes with out-degree centrality as values.

    See Also
    --------
    degree_centrality, in_degree_centrality

    Notes
    -----
    The degree centrality values are normalized by dividing by the maximum 
    possible degree in a simple graph n-1 where n is the number of nodes in G.

    For multigraphs or graphs with self loops the maximum degree might
    be higher than n-1 and values of degree centrality greater than 1
    are possible.
    """
    if not G.is_directed():
        raise nx.NetworkXError(\
            "out_degree_centrality() not defined for undirected graphs.")
    centrality={}
    s=1.0/(len(G)-1.0)
    centrality=dict((n,d*s) for n,d in G.out_degree_iter())
    return centrality



