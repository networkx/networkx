"""
Computes minimum spanning tree of a weighted graph.

"""
#    Copyright (C) 2009-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['mst', 'kruskal_mst',
           'minimum_spanning_edges',
           'minimum_spanning_tree']

import networkx as nx

def minimum_spanning_edges(G):
    """Generate edges in a minimum spanning forest of an undirected 
    weighted graph.

    A minimum spanning tree is a subgraph of the graph (a tree)
    with the minimum sum of edge weights.  A spanning forest is a
    union of the spanning trees for each connected component of the graph.

    Parameters
    ----------
    G : NetworkX Graph
    
    Returns
    -------
    edges : iterator
       A generator that produces edges in the minimum spanning tree.
       The edges are three-tuples (u,v,w) where w is the weight.
    
    Examples
    --------
    >>> G=nx.cycle_graph(4)
    >>> G.add_edge(0,3,weight=2) # assign weight 2 to edge 0-3
    >>> mst=nx.minimum_spanning_edges(G) # a generator of MST edges
    >>> edgelist=list(mst) # make a list of the edges
    >>> print(sorted(edgelist))
    [(0, 1, {'weight': 1}), (1, 2, {'weight': 1}), (2, 3, {'weight': 1})]
    >>> T=nx.Graph(edgelist)  # build a graph of the MST.
    >>> print(sorted(T.edges(data=True)))
    [(0, 1, {'weight': 1}), (1, 2, {'weight': 1}), (2, 3, {'weight': 1})]

    Notes
    -----
    Uses Kruskal's algorithm.

    If the graph edges do not have a weight attribute a default weight of 1
    will be assigned.

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

    if G.is_directed():
        raise NetworkXError(\
            "Mimimum spanning tree not defined for directed graphs.")

    subtrees = UnionFind()
    edges = sorted((G[u][v].get('weight',1),u,v) for u in G for v in G[u])
    for W,u,v in edges:
        if subtrees[u] != subtrees[v]:
            yield (u,v,{'weight':W})
            subtrees.union(u,v)


def minimum_spanning_tree(G):
    """Return a minimum spanning tree or forest of an undirected 
    weighted graph.

    A minimum spanning tree is a subgraph of the graph (a tree) with
    the minimum sum of edge weights.

    If the graph is not connected a spanning forest is constructed.  A
    spanning forest is a union of the spanning trees for each
    connected component of the graph.


    Parameters
    ----------
    G : NetworkX Graph
    
    Returns
    -------
    G : NetworkX Graph
       A minimum spanning tree or forest. 
    
    Examples
    --------
    >>> G=nx.cycle_graph(4)
    >>> G.add_edge(0,3,weight=2) # assign weight 2 to edge 0-3
    >>> T=nx.minimum_spanning_tree(G)
    >>> print(sorted(T.edges(data=True)))
    [(0, 1, {'weight': 1}), (1, 2, {'weight': 1}), (2, 3, {'weight': 1})]

    Notes
    -----
    Uses Kruskal's algorithm.

    If the graph edges do not have a weight attribute a default weight of 1
    will be assigned.
    """
    T=nx.Graph(nx.minimum_spanning_edges(G))
    # Add isolated nodes
    if len(T)!=len(G):
        T.add_nodes_from([n for n,d in G.degree().items() if d==0])
    return T

kruskal_mst=minimum_spanning_tree
mst=minimum_spanning_tree

