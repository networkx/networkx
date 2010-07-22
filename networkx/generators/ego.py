"""
Ego graph.

"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Drew Conway <drew.conway@nyu.edu>',
                            'Aric Hagberg <hagberg@lanl.gov>'])
__all__ = ['ego_graph']

import networkx as nx

def ego_graph(G,n,radius=1,center=True):
    """Returns induced subgraph of neighbors centered at node n. 
    
    Parameters
    ----------
    G : graph
      A NetworkX Graph or DiGraph

    n : node 
      A single node 

    radius : integer
      Include all neighbors of distance<=radius from n
      
    center : bool, optional
      If False, do not include center node in graph 

    Notes
    -----
    For directed graphs D this produces the "out" neighborhood
    or successors.  If you want the neighborhood of predecessors
    first reverse the graph with D.reverse().  If you want both
    first convert the graph to an undirected graph using G=nx.Graph(D).

    """
    sp=nx.single_source_shortest_path_length(G,n,cutoff=radius)
    H=G.subgraph(sp.keys())
    if not center:
        H.remove_node(n)
    return  H
