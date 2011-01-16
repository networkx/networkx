"""
Closeness centrality measures.

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

__all__ = ['closeness_centrality']

import networkx as nx

def closeness_centrality(G,v=None,weighted_edges=False,normalized=True):
    """Compute closeness centrality for nodes.

    Closeness centrality at a node is 1/average distance to all other nodes.

    Parameters
    ----------
    G : graph
      A networkx graph 
    v : node, optional
      Return only the value for node v
    weighted_edges : bool, optional
      If True use edge weights in computing degree and size.
    normalized : bool, optional      
      If True (default) normalize by the graph size.

    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with closeness centrality as the value.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality,
    degree_centrality

    Notes
    -----
    The closeness centrality is normalized to to n-1 / size(G)-1 where
    n is the number of nodes in the connected part of graph containing
    the node.  If the graph is not completely connected, this
    algorithm computes the closeness centrality for each connected
    part separately.
    """
    if weighted_edges:
        path_length=nx.single_source_dijkstra_path_length
    else:
        path_length=nx.single_source_shortest_path_length

    if v is None:
        nodes=G.nodes()
    else:
        nodes=[v]
    closeness_centrality={}

    for n in nodes:
        sp=path_length(G,n)
        totsp=sum(sp.values())
        if totsp > 0.0 and len(G) > 1:
            closeness_centrality[n]= (len(sp)-1.0) / totsp
            # normalize to number of nodes-1 in connected part
            if normalized:
                s=(len(sp)-1.0) / ( len(G) - 1 )
                closeness_centrality[n] *= s
        else:                                                                
            closeness_centrality[n]=0.0           
    if v is not None:
        return closeness_centrality[v]
    else:
        return closeness_centrality

