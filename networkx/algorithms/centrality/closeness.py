"""
Closeness centrality measures.

"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import functools
import networkx as nx
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Sasha Gutfraind (ag362@cornell.edu)'])
__all__ = ['closeness_centrality']


def closeness_centrality(G, v=None, distance=None, normalized=True):
    r"""Compute closeness centrality for nodes.

    Closeness centrality [1]_ of a node `u` is a measure based on the 
    inverse of the sum of geodesic distances from `u` to all other nodes.
    The raw sum of distances is dependent on graph order, thus 
    closeness measure is normalized by the sum of minimum possible 
    distances: `n - 1`.

    .. math::

        C(u) = \left [\frac{\sum_{v=1}^{n} d(v, u)}{n - 1} \right]^{-1} 
             = \frac{n - 1}{\sum_{v=1}^{n} d(v, u)}

    Where `d(v, u)` is the shortest path distance between `v` and `u`.
    Notice that higher values of closeness indicate higher centrality.

    Parameters
    ----------
    G : graph
      A networkx graph 
    v : node, optional
      Return only the value for node v
    distance : string key, optional (default=None)
      Use specified edge key as edge distance. 
      If True, use 'weight' as the edge key.
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
    The closeness centrality is normalized to `\frac{n-1}{order(G)-1}`
    where `n` is the number of nodes in the connected part of graph 
    containing the node.  If the graph is not completely connected, this
    algorithm computes the closeness centrality for each connected
    part separately.

    References
    ----------
    .. [1] Freeman, L.C., 1979. Centrality in networks: I. Conceptual clarification. 
           Social Networks 1, 215--239.
           http://www.soc.ucsb.edu/faculty/friedkin/Syllabi/Soc146/Freeman78.PDF

    """
    if distance is not None:
        if distance is True: distance='weight'
        path_length=functools.partial(nx.single_source_dijkstra_path_length,
                                      weight=distance)
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

