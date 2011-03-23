# encoding: utf-8
"""
Functions for identifying isolate (degree zero) nodes.
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['Drew Conway <drew.conway@nyu.edu>',
                            'Aric Hagberg <hagberg@lanl.gov>'])
__all__=['is_isolate','isolates']

def is_isolate(G,n):
    """Determine of node n is an isolate (degree zero).  

    Parameters
    ----------
    G : graph
        A networkx graph
    n : node
        A node in G

    Returns
    -------
    isolate : bool
       True if n has no neighbors, False otherwise.
    
    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_edge(1,2)
    >>> G.add_node(3)
    >>> nx.is_isolate(G,2)
    False
    >>> nx.is_isolate(G,3)
    True
    """
    return G.degree(n)==0 

def isolates(G):
    """Return list of isolates in the graph.

    Isolates are nodes with no neighbors (degree zero).

    Parameters
    ----------
    G : graph
        A networkx graph

    Returns
    -------
    isolates : list
       List of isolate nodes.
    
    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_edge(1,2)
    >>> G.add_node(3)
    >>> nx.isolates(G)
    [3]

    To remove all isolates in the graph use
    >>> G.remove_nodes_from(nx.isolates(G))
    >>> G.nodes()
    [1, 2]

    For digraphs isolates have zero in-degree and zero out_degre
    >>> G = nx.DiGraph([(0,1),(1,2)])
    >>> G.add_node(3)
    >>> nx.isolates(G)
    [3]
    """
    return [n for (n,d) in G.degree_iter() if d==0]
