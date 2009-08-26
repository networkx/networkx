"""
======================
Minimum Spanning Trees
======================
"""
#    Copyright (C) 2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['mst', 'kruskal_mst']

import networkx

def kruskal_mst(G):
    """Generate a minimum spanning tree of an undirected graph.

    Uses Kruskal's algorithm.

    Parameters
    ----------
    G : NetworkX Graph
    
    Returns
    -------
    A generator that produces edges in the minimum spanning tree.
    The edges are three-tuples (u,v,w) where w is the weight.
    
    Examples
    --------
    >>> G=nx.cycle_graph(4)
    >>> G.add_edge(0,3,weight=2) # assign weight 2 to edge 0-3
    >>> mst=nx.kruskal_mst(G) # a generator of MST edges
    >>> edgelist=list(mst) # make a list of the edges
    >>> print sorted(edgelist)
    [(0, 1, {'weight': 1}), (1, 2, {'weight': 1}), (2, 3, {'weight': 1})]
    >>> T=nx.Graph(edgelist)  # build a graph of the MST.
    >>> print sorted(T.edges(data=True))
    [(0, 1, {'weight': 1}), (1, 2, {'weight': 1}), (2, 3, {'weight': 1})]

    Notes
    -----
    Modified code from David Eppstein, April 2006
    http://www.ics.uci.edu/~eppstein/PADS/

    """
    # Modified code from David Eppstein, April 2006
    # http://www.ics.uci.edu/~eppstein/PADS/
    # Kruskal's algorithm: sort edges by weight, and add them one at a time.
    # We use Kruskal's algorithm, first because it is very simple to
    # implement once UnionFind exists, and second, because the only slow
    # part (the sort) is sped up by being built in to Python.
    from networkx.utils import UnionFind
    subtrees = UnionFind()
    edges = sorted((G[u][v].get('weight',1),u,v) for u in G for v in G[u])
    for W,u,v in edges:
        if subtrees[u] != subtrees[v]:
            yield (u,v,{'weight':W})
            subtrees.union(u,v)

mst=kruskal_mst

