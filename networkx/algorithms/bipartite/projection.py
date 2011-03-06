# -*- coding: utf-8 -*-
"""Create one-mode ("unipartite") projections from bipartite graphs.
"""
import networkx as nx
#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__all__ = ['project',
           'projected_graph',
           'weighted_projected_graph']


def projected_graph(B, nodes, multigraph=False):
    """Return the graph that is the projection of B onto the nodes.

    The nodes retain their names and are connected in the resulting
    graph if have an edge to a common node in the original graph.

    Parameters
    ----------
    B : NetworkX graph 
      The input graph should be bipartite. 

    nodes : list or iterable
      Nodes to project onto (the "bottom" nodes).

    multigraph: bool (default=False)
       If True return a multigraph where the multiple edges represent multiple
       shared neighbors.

    Returns
    -------
    Graph : NetworkX graph or multigraph
       A graph that is the projection onto the given nodes.

    Examples
    --------
    >>> B = nx.path_graph(4)
    >>> G = nx.projected_graph(B, [1,3]) 
    >>> print(G.nodes())
    [1, 3]
    >>> print(G.edges())
    [(1, 3)]
    
    Notes
    ------
    No attempt is made to verify that the input graph B is bipartite.
    Returns a simple graph that is the projection of the bipartite graph B
    onto the set of nodes given in list nodes.  If multigraph=True then
    a multigraph is returned with an edge for every shared neighbor.

    Directed graphs are allowed as input.  The output will also then
    be a directed graph with edges if there is a directed path between
    the nodes.

    See Also
    --------
    is_bipartite, is_bipartite_node_set, bipartite_sets, 
    weighted_projected_graph 
    """
    if B.is_multigraph():
        raise nx.NetworkXError("not defined for multigraphs")
    if B.is_directed():
        directed=True
        if multigraph:
            G=nx.MultiDiGraph()
        else:
            G=nx.DiGraph()
    else:
        directed=False
        if multigraph:
            G=nx.MultiGraph()
        else:
            G=nx.Graph()
    G.add_nodes_from(nodes)
    for u in nodes:
        nbrs2=set((v for nbr in B[u] for v in B[nbr])) -set([u])
        if multigraph:
            for n in nbrs2:
                if directed:
                    nparallel=len(set(B[u]) & set(B.pred[n]))
                else:
                    nparallel=len(set(B[u]) & set(B[n]))/2
                G.add_edges_from([(u,n)]*int(nparallel))
        else:
            G.add_edges_from((u,n) for n in nbrs2)
    return G


def weighted_projected_graph(B, nodes, collaboration=False):
    """Return the graph that is the projection of B onto the nodes with
    weights representing shared neighbor information.

    The nodes retain their names and are connected in the resulting
    graph if have an edge to a common node in the original graph.

    Parameters
    ----------
    B : NetworkX graph 
      The input graph should be bipartite. 

    nodes : list or iterable
      Nodes to project onto (the "bottom" nodes).

    collaboration: bool (default=False)
       If False the weight is number of shared neighbors. 
       If True use the "collaboration" model [1]_ for the weights.  

    Returns
    -------
    Graph : NetworkX graph 
       A graph that is the projection onto the given nodes.

    Examples
    --------
    >>> B = nx.path_graph(4)
    >>> G = nx.projected_graph(B, [1,3]) 
    >>> print(G.nodes())
    [1, 3]
    >>> print(G.edges())
    [(1, 3)]
    
    Notes
    ------
    No attempt is made to verify that the input graph B is bipartite.

    See Also
    --------
    is_bipartite, is_bipartite_node_set, bipartite_sets, projected_graph 

    References
    ----------
    ..[1] Scientific collaboration networks: II. 
       Shortest paths, weighted networks, and centrality, 
       M. E. J. Newman, Phys. Rev. E 64, 016132 (2001). 
    """
    if B.is_multigraph():
        raise nx.NetworkXError("not defined for multigraphs")
    if B.is_directed():
        pred=B.pred
        G=nx.DiGraph()
    else:
        pred=B.adj
        G=nx.Graph()
    G.add_nodes_from(nodes)
    for u in nodes:
        nbrs2=set((v for nbr in B[u] for v in B[nbr])) -set([u])
        for n in nbrs2:
            common=set(B[u]) & set(pred[n])
            if collaboration:
                weight=sum([1.0/(len(B[c]) - 1) for c in common])
            else:
                weight=len(common)
            G.add_edge(u,n,weight=weight)
    return G


def project(B, nodes, create_using=None):
    """Return the graph of the the given bipartite graph projected onto 
    a subset of nodes.

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
    >>> B = nx.path_graph(4)
    >>> G = nx.project(B, [1,3]) 
    >>> print(G.nodes())
    [1, 3]
    >>> print(G.edges())
    [(1, 3)]
    
    Notes
    ------
    Returns a graph that is the projection of the bipartite graph B
    onto the set of nodes given in list nodes.
    No attempt is made to verify that the input graph B is bipartite.

    See Also
    --------
    is_bipartite, is_bipartite_node_set, bipartite_sets, 
    """
    if create_using is None:
        create_using = nx.Graph()

    G = nx.empty_graph(0, create_using)

    for v in nodes:
        G.add_node(v)
        for nbr in B[v]:
            G.add_edges_from([(v, u) for u in B[nbr] if u != v])
    return G

