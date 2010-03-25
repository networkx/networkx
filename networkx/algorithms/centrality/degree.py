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

import networkx

def _degree_centrality(degree,degree_iter,G,v=None):
    """Internal function to consolidate *-degree centrality functions."""
    if v is not None:
        d = G.__getattribute__(degree)
        return d(v)/(G.order()-1.0)
    centrality={}
    s=1.0/(G.order()-1.0)
    d_iter = G.__getattribute__(degree_iter)
    for n,deg in d_iter():
        centrality[n]=deg*s
    return centrality
 

def degree_centrality(G,v=None):
    """Compute the degree centrality for nodes.

    The degree centrality for a node v is the fraction of nodes it
    is connected to.

    Parameters
    ----------
    G : graph
      A networkx graph 

    v : node, optional
      Return only the value for node v.
      
    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with degree centrality as the value.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality

    Notes
    -----
    The degree centrality is normalized to the maximum possible degree
    in the graph G.  That is, G.degree(v)/(G.order()-1).

    """
    return _degree_centrality('degree', 'degree_iter', G, v)


def in_degree_centrality(G,v=None):
    """Compute the in-degree centrality for nodes.

    The in-degree centrality for a node v is the fraction of nodes its 
    incoming edges are connected to.

    Parameters
    ----------
    G : graph
        A NetworkX graph

    v : node, optional
        Return only the value for node.

    Returns
    -------
    nodes : dictionary
        Dictionary of nodes with in-degree centrality as values.

    See Also
    --------
    degree_centrality, out_degree_centrality

    """
    return _degree_centrality('in_degree', 'in_degree_iter', G, v)


def out_degree_centrality(G,v=None):
    """Compute the out-degree centrality for nodes.

    The out-degree centrality for a node v is the fraction of nodes its 
    outgoing edges are connected to.

    Parameters
    ----------
    G : graph
        A NetworkX graph

    v : node, optional
        Return only the value for node.

    Returns
    -------
    nodes : dictionary
        Dictionary of nodes with out-degree centrality as values.

    See Also
    --------
    degree_centrality, in_degree_centrality

    """
    return _degree_centrality('out_degree', 'out_degree_iter', G, v)


