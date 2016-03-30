"""Disjoint paths computation using removal of found shortest paths.
"""

#    Copyright (C) 2015-2016 by
#    Niels L. M. van Adrichem <n.l.m.vanadrichem@tudelft.nl>
#    All rights reserved.
#    BSD license.

__author__ = """\n""".join(['Niels L. M. van Adrichem <n.l.m.vanadrichem@tudelft.nl>'])
__all__ = ['simple_disjoint']

import networkx as nx

def simple_disjoint(G, source, target, weight=None, k=2, node_disjoint=False):
    """ Simplest, even naive, disjoint path computation by removing previously
    found paths and computing the next shortest path. This method, although it 
    often works out, gives no guaranteed correct result since it is susceptibl
    e to trap topologies where the removal of the shortest path blocks finding
    2 non-shortest path disjoint paths. Furthermore, besides the first
    found path equalling the shortest path, it doesn't optimize for path
    lengths.

    """

    if k < 2:
        raise nx.NetworkXUnfeasible("You need at least k>=2 paths to be disjoint, k=%d"%(k))
        
    if source == target:
        raise nx.NetworkXUnfeasible("There is no such thing as a disjoint path to oneself, as oneself has to be excluded from the disjoint path to be able to exist")

    if weight is not None and nx.is_negatively_weighted(G, weight=weight):
        negatively_weighted = True
    else:
        negatively_weighted = False
    
    paths = []
    dists = []
    G_copy = G.copy(with_data=False)
    for i in range(0, k):
        try:
            if weight is None:
                path = nx.bidirectional_shortest_path(G_copy, source, target)
                dist = len(path)-1
            elif not negatively_weighted:
                dist,path = nx.single_source_dijkstra(G_copy, source, target=target, weight=weight)
                dist = dist[target]
                path = path[target]
            else:
                dist,path = nx.single_source_bellman_ford(G_copy, source, target=target, weight=weight)
                dist = dist[target]
                path = path[target]
                
        except (nx.NetworkXNoPath, KeyError):
            raise nx.NetworkXNoPath(
                "Cannot find more than %d disjoint path(s), possibly a trap topology has occurred."%(i))

        paths.append(path)
        dists.append(dist)
        
        if i == k:
            break
        
        if node_disjoint:        
            for n in path[1:-1]:
                G_copy.remove_node(n)
                
        else:
            u = path[0]
            for v in path[1:]:
                G_copy.remove_edge(u, v)
                u = v
                                
    return dists,paths
