"""
==========================
Bipartite Graph Algorithms
==========================
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__=['project','is_bipartite','bipartite_color','bipartite_sets']

import networkx as nx

def project(B,nodes,create_using=None):
    """Return the projection of the graph onto a subset of nodes.

    The nodes retain their names and are connected in the resulting
    graph if have an edge to a common node in the original graph.

    Parameters
    ----------
    B : NetworkX graph 
      The input graph should be bipartite. 

    nodes : list or iterable
      Nodes to project onto.

    Returns
    -------
    Graph : NetworkX graph 
       A graph that is the projection onto the given nodes.

    Examples
    --------
    >>> B=nx.path_graph(4)
    >>> G=nx.project(B,[1,3]) 
    >>> print G.nodes()
    [1, 3]
    >>> print G.edges()
    [(1, 3)]
    
    Notes
    ------
    Returns a graph that is the projection of the bipartite graph B
    onto the set of nodes given in list nodes.
    No attempt is made to verify that the input graph B is bipartite.

    See Also
    --------
    is_bipartite(), bipartite_sets()

    """

    if create_using==None:
        create_using=nx.Graph()

    G=nx.empty_graph(0,create_using)

    for v in nodes:
        G.add_node(v)
        for nbr in B[v]:
            G.add_edges_from([(v,u) for u in B[nbr] if u!=v])
    return G


def bipartite_color(G):
    """Returns a two-coloring of the graph.

    Raises an exception if the graph is not bipartite.

    Parameters
    ----------
    G : NetworkX graph 

    Returns
    -------
    color : dictionary
       A dictionary keyed by node with a 1 or 0 as data for each node color.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> c=nx.bipartite_color(G)
    >>> print c
    {0: 1, 1: 0, 2: 1, 3: 0}

    """
    color={}
    for n in G: # handle disconnected graphs
        if n in color: continue
        queue=[n]  
        color[n]=1 # nodes seen with color (1 or 0)
        while queue:
            v=queue.pop()
            c=1-color[v] # opposite color of node v
            for w in G[v]: 
                if w in color: 
                    if color[w]==color[v]:
                        raise nx.NetworkXError("Graph is not bipartite.")
                else:
                    color[w]=c
                    queue.append(w)
    return color

def is_bipartite(G):
    """ Returns True if graph G is bipartite, False if not.

    Parameters
    ----------
    G : NetworkX graph 

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> print nx.is_bipartite(G)
    True

    See Also
    --------
    bipartite_color()

    """
    try:
        bipartite_color(G)
        return True
    except:
        return False
    
def bipartite_sets(G):
    """Returns bipartite node sets of graph G.

    Raises an exception if the graph is not bipartite.

    Parameters
    ----------
    G : NetworkX graph 

    Returns
    -------
    (X,Y) : two-tuple of sets
       One set of nodes for each part of the bipartite graph.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> X,Y=nx.bipartite_sets(G)
    >>> print X
    set([0, 2])
    >>> print Y
    set([1, 3])

    See Also
    --------
    bipartite_color()

    """
    color=bipartite_color(G)
    X=set(n for n in color if color[n]==1)
    Y=set(n for n in color if color[n]==0)
    return (X,Y)

