"""
Vitality measures.
"""
#    Copyright (C) 2012 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Renato Fabbri'])
__all__ = ['closeness_vitality']

def weiner_index(G, weight=None):
    # compute sum of distances between all node pairs
    # (with optional weights)
    weiner=0.0
    if weight is None:
        for n in G:
            path_length=nx.single_source_shortest_path_length(G,n)
            weiner+=sum(path_length.values())
    else:
        for n in G:
            path_length=nx.single_source_dijkstra_path_length(G,
                    n,weight=weight)
            weiner+=sum(path_length.values())
    return weiner


def closeness_vitality(G, v=None, weight=None):
    """Compute closeness vitality for nodes.

    Closeness vitality at a node is the change in the sum of distances
    between all node pairs when excluding that node.

    Parameters
    ----------
    G : graph

    weight : None or string, optional
      If None edge weights are ignored.
      Otherwise holds the name of the edge attribute used as weight.

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

    References
    ----------
    .. [1] Brandes, Ulrik.
       Network Analysis: Methodological Foundations. Springer, 2005.
    """
    multigraph = G.is_multigraph()
    wig = weiner_index(G,weight)
    closeness_vitality = {}
    for n in G:
        # remove edges connected to node n and keep list of edges with data
        # could remove node n but it doesn't count anyway
        if multigraph:
            edges = G.edges(n,data=True,keys=True)
            if G.is_directed():
                edges += G.in_edges(n,data=True,keys=True)
            for u,v,k,d in edges:
                G.remove_edge(u,v,key=k)
        else:
            edges = G.edges(n,data=True)
            if G.is_directed():
                edges += G.in_edges(n,data=True)
            G.remove_edges_from(edges)
        closeness_vitality[n] = wig - weiner_index(G,weight)
        # add edges and data back to graph
        G.add_edges_from(edges)
    return closeness_vitality
