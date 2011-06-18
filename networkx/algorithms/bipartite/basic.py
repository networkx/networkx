# -*- coding: utf-8 -*-
"""
==========================
Bipartite Graph Algorithms
==========================
"""
import networkx as nx
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__all__ = ['is_bipartite', 'is_bipartite_node_set',
           'color', 'sets',
           'density', 'degrees']

def color(G):
    """Returns a two-coloring of the graph.

    Raises an exception if the graph is not bipartite.

    Parameters
    ----------
    G : NetworkX graph 

    Returns
    -------
    color : dictionary
       A dictionary keyed by node with a 1 or 0 as data for each node color.

    Raises
    ------
    NetworkXError if the graph is not two-colorable.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> c = bipartite.color(G)
    >>> print(c)
    {0: 1, 1: 0, 2: 1, 3: 0}

    You can use this to set a node attribute indicating the biparite set:
    
    >>> nx.set_node_attributes(G, 'bipartite', c)
    >>> print(G.node[0]['bipartite'])
    1
    >>> print(G.node[1]['bipartite'])
    0
    """
    color = {}
    for n in G: # handle disconnected graphs
        if n in color or len(G[n])==0: # skip isolates
            continue
        queue = [n]  
        color[n] = 1 # nodes seen with color (1 or 0)
        while queue:
            v = queue.pop()
            c = 1 - color[v] # opposite color of node v
            for w in G[v]: 
                if w in color: 
                    if color[w] == color[v]:
                        raise nx.NetworkXError("Graph is not bipartite.")
                else:
                    color[w] = c
                    queue.append(w)
    # color isolates with 0
    color.update(dict.fromkeys(nx.isolates(G),0))
    return color

def is_bipartite(G):
    """ Returns True if graph G is bipartite, False if not.

    Parameters
    ----------
    G : NetworkX graph 

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> print(bipartite.is_bipartite(G))
    True

    See Also
    --------
    color, is_bipartite_node_set
    """
    try:
        color(G)
        return True
    except nx.NetworkXError:
        return False
    
def is_bipartite_node_set(G,nodes):
    """Returns True if nodes and G/nodes are a bipartition of G.

    Parameters
    ----------
    G : NetworkX graph 

    nodes: list or container
      Check if nodes are a one of a bipartite set.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> X = set([1,3])
    >>> bipartite.is_bipartite_node_set(G,X)
    True

    Notes
    -----
    For connected graphs the bipartite sets are unique.  This function handles
    disconnected graphs.
    """
    S=set(nodes)
    for CC in nx.connected_component_subgraphs(G):
        X,Y=sets(CC)
        if not ( (X.issubset(S) and Y.isdisjoint(S)) or 
                 (Y.issubset(S) and X.isdisjoint(S)) ):
            return False
    return True
    

def sets(G):
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
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> X, Y = bipartite.sets(G)
    >>> list(X)
    [0, 2]
    >>> list(Y)
    [1, 3]

    See Also
    --------
    color
    """
    c = color(G)
    X = set(n for n in c if c[n]) # c[n] == 1
    Y = set(n for n in c if not c[n]) # c[n] == 0
    return (X, Y)

def density(B, nodes):
    """Return density of bipartite graph B.

    Parameters
    ----------
    G : NetworkX graph 

    nodes: list or container
      Nodes in one set of the bipartite graph.

    Returns
    -------
    d : float
       The bipartite density

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.complete_bipartite_graph(3,2)
    >>> X=set([0,1,2])
    >>> bipartite.density(G,X)
    1.0
    >>> Y=set([3,4])
    >>> bipartite.density(G,Y)
    1.0

    See Also
    --------
    color
    """
    n=len(B)
    m=nx.number_of_edges(B)
    nb=len(nodes)
    nt=n-nb
    if m==0: # includes cases n==0 and n==1
        d=0.0
    else:
        if B.is_directed():
            d=m/(2.0*float(nb*nt))
        else:
            d= m/float(nb*nt)
    return d

def degrees(B, nodes, weight=None):
    """Return the degrees of the two node sets in the bipartite graph B.

    Parameters
    ----------
    G : NetworkX graph 

    nodes: list or container
      Nodes in one set of the bipartite graph.

    weight : string or None, optional (default=None)
       The edge attribute that holds the numerical value used as a weight.
       If None, then each edge has weight 1.
       The degree is the sum of the edge weights adjacent to the node.

    Returns
    -------
    (degX,degY) : tuple of dictionaries
       The degrees of the two bipartite sets as dictionaries keyed by node.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.complete_bipartite_graph(3,2)
    >>> Y=set([3,4])
    >>> degX,degY=bipartite.degrees(G,Y)
    >>> degX
    {0: 2, 1: 2, 2: 2}

    See Also
    --------
    color, density
    """
    bottom=set(nodes)
    top=set(B)-bottom
    return (B.degree(top,weight),B.degree(bottom,weight))
