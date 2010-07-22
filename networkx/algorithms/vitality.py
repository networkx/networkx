"""
Vitality measures.

"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Renato Fabbri'])

__all__ = ['closeness_vitality']

import networkx as nx

def weiner_index(G,weighted_edges=True):
    # compute sum of distances between all node pairs
    # (with optional weights) 
    if weighted_edges:
        path_length=nx.single_source_dijkstra_path_length
    else:
        path_length=nx.single_source_shortest_path_length
    weiner=0.0
    for n in G:
        l=path_length(G,n).values()
        weiner+=sum(l)
    return weiner


def closeness_vitality(G,v=None,weighted_edges=False):
    """Compute closeness vitality for nodes.

    Closeness vitality at a node is the change in the sum of distances 
    between all node pairs when excluding a that node.

    Parameters
    ----------
    G : graph
      A networkx graph 

    v : node, optional
      Return only the value for node v.

    weighted_edges : bool, optional
      Consider the edge weights in determining the shortest paths.
      If False, all edge weights are considered equal.
      
    Returns
    -------
    nodes : dictionary
       Dictionary with nodes as keys and closeness vitality as the value.

    Examples
    --------
    >>> G=nx.cycle_graph(3)
    >>> nx.closeness_vitality(G)
    {0: 4.0, 1: 4.0, 2: 4.0}

    See Also
    --------
    closeness_centrality()

    Notes
    -----
    """
    if v is None:
        nodes=G.nodes()
    else:
        nodes=[v]

    wig=weiner_index(G,weighted_edges=weighted_edges)
    closeness_vitality={}
    for n in G:
        # remove edges connected to node n and keep list of edges with data
        # could remove node n but it doesn't count anyway
        edges=G.edges(n,data=True)
        if G.is_directed():
            edges+=G.in_edges(n,data=True)
        G.remove_edges_from(edges) 
        closeness_vitality[n]=wig-weiner_index(G,weighted_edges=weighted_edges)
        # add edges and data back to graph
        G.add_edges_from(edges)
    if v is not None:
        return closeness_vitality[v]
    else:
        return closeness_vitality


        
