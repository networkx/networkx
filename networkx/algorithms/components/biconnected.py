# -*- coding: utf-8 -*-
"""
Biconnected components and articulation points.
"""
#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from itertools import chain
import networkx as nx
__author__ = '\n'.join(['Jordi Torrents <jtorrents@milnou.net>',
                        'Dan Schult <dschult@colgate.edu>',
                        'Aric Hagberg <aric.hagberg@gmail.com>'])
__all__ = ['biconnected_components',
           'biconnected_component_edges',
           'biconnected_component_subgraphs',
           'is_biconnected',
           'articulation_points',
           ]

def is_biconnected(G):
    """Return True if the graph is biconnected, False otherwise.

    A graph is biconnected if, and only if, it cannot be disconnected by
    removing only one node (and all edges incident on that node). If
    removing a node increases the number of disconnected components
    in the graph, that node is called an articulation point, or cut
    vertex.  A biconnected graph has no articulation points.

    Parameters
    ----------
    G : NetworkX Graph
        An undirected graph.

    Returns
    -------
    biconnected : bool
        True if the graph is biconnected, False otherwise.

    Raises
    ------
    NetworkXError :
        If the input graph is not undirected.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> print(nx.is_biconnected(G))
    False
    >>> G.add_edge(0,3)
    >>> print(nx.is_biconnected(G))
    True

    See Also
    --------
    biconnected_components,
    articulation_points,
    biconnected_component_edges,
    biconnected_component_subgraphs

    Notes
    -----
    The algorithm to find articulation points and biconnected
    components is implemented using a non-recursive depth-first-search
    (DFS) that keeps track of the highest level that back edges reach
    in the DFS tree. A node `n` is an articulation point if, and only
    if, there exists a subtree rooted at `n` such that there is no
    back edge from any successor of `n` that links to a predecessor of
    `n` in the DFS tree. By keeping track of all the edges traversed
    by the DFS we can obtain the biconnected components because all
    edges of a bicomponent will be traversed consecutively between
    articulation points.

    References
    ----------
    .. [1] Hopcroft, J.; Tarjan, R. (1973). 
       "Efficient algorithms for graph manipulation". 
       Communications of the ACM 16: 372–378. doi:10.1145/362248.362272
    """
    bcc = list(biconnected_components(G))
    if not bcc: # No bicomponents (it could be an empty graph)
        return False
    return len(bcc[0]) == len(G)

def biconnected_component_edges(G):
    """Return a generator of lists of edges, one list for each biconnected
    component of the input graph.

    Biconnected components are maximal subgraphs such that the removal of a
    node (and all edges incident on that node) will not disconnect the
    subgraph. Note that nodes may be part of more than one biconnected
    component. Those nodes are articulation points, or cut vertices. However, 
    each edge belongs to one, and only one, biconnected component.

    Notice that by convention a dyad is considered a biconnected component.

    Parameters
    ----------
    G : NetworkX Graph
        An undirected graph.

    Returns
    -------
    edges : generator
        Generator of lists of edges, one list for each bicomponent.

    Raises
    ------
    NetworkXError :
        If the input graph is not undirected.

    Examples
    --------
    >>> G = nx.barbell_graph(4,2)
    >>> print(nx.is_biconnected(G))
    False
    >>> components = nx.biconnected_component_edges(G)
    >>> G.add_edge(2,8)
    >>> print(nx.is_biconnected(G))
    True
    >>> components = nx.biconnected_component_edges(G)

    See Also
    --------
    is_biconnected,
    biconnected_components,
    articulation_points,
    biconnected_component_subgraphs

    Notes
    -----
    The algorithm to find articulation points and biconnected
    components is implemented using a non-recursive depth-first-search
    (DFS) that keeps track of the highest level that back edges reach
    in the DFS tree. A node `n` is an articulation point if, and only
    if, there exists a subtree rooted at `n` such that there is no
    back edge from any successor of `n` that links to a predecessor of
    `n` in the DFS tree. By keeping track of all the edges traversed
    by the DFS we can obtain the biconnected components because all
    edges of a bicomponent will be traversed consecutively between
    articulation points.
 
    References
    ----------
    .. [1] Hopcroft, J.; Tarjan, R. (1973). 
       "Efficient algorithms for graph manipulation". 
       Communications of the ACM 16: 372–378. doi:10.1145/362248.362272
    """
    return sorted(_biconnected_dfs(G,components=True), key=len, reverse=True)

def biconnected_components(G):
    """Return a generator of sets of nodes, one set for each biconnected
    component of the graph

    Biconnected components are maximal subgraphs such that the removal of a
    node (and all edges incident on that node) will not disconnect the
    subgraph. Note that nodes may be part of more than one biconnected
    component. Those nodes are articulation points, or cut vertices. The 
    removal of articulation points will increase the number of connected 
    components of the graph.

    Notice that by convention a dyad is considered a biconnected component.

    Parameters
    ----------
    G : NetworkX Graph
        An undirected graph.

    Returns
    -------
    nodes : generator
        Generator of sets of nodes, one set for each biconnected component.

    Raises
    ------
    NetworkXError :
        If the input graph is not undirected.

    Examples
    --------
    >>> G = nx.barbell_graph(4,2)
    >>> print(nx.is_biconnected(G))
    False
    >>> components = nx.biconnected_components(G)
    >>> G.add_edge(2,8)
    >>> print(nx.is_biconnected(G))
    True
    >>> components = nx.biconnected_components(G)

    See Also
    --------
    is_biconnected,
    articulation_points,
    biconnected_component_edges,
    biconnected_component_subgraphs

    Notes
    -----
    The algorithm to find articulation points and biconnected
    components is implemented using a non-recursive depth-first-search
    (DFS) that keeps track of the highest level that back edges reach
    in the DFS tree. A node `n` is an articulation point if, and only
    if, there exists a subtree rooted at `n` such that there is no
    back edge from any successor of `n` that links to a predecessor of
    `n` in the DFS tree. By keeping track of all the edges traversed
    by the DFS we can obtain the biconnected components because all
    edges of a bicomponent will be traversed consecutively between
    articulation points.

    References
    ----------
    .. [1] Hopcroft, J.; Tarjan, R. (1973). 
       "Efficient algorithms for graph manipulation". 
       Communications of the ACM 16: 372–378. doi:10.1145/362248.362272
    """
    bicomponents = (set(chain.from_iterable(comp))
                        for comp in _biconnected_dfs(G,components=True))
    return sorted(bicomponents, key=len, reverse=True)

def biconnected_component_subgraphs(G):
    """Return a generator of graphs, one graph for each biconnected component
    of the input graph.

    Biconnected components are maximal subgraphs such that the removal of a
    node (and all edges incident on that node) will not disconnect the
    subgraph. Note that nodes may be part of more than one biconnected
    component. Those nodes are articulation points, or cut vertices. The 
    removal of articulation points will increase the number of connected 
    components of the graph.

    Notice that by convention a dyad is considered a biconnected component.

    Parameters
    ----------
    G : NetworkX Graph
        An undirected graph.

    Returns
    -------
    graphs : generator
        Generator of graphs, one graph for each biconnected component.

    Raises
    ------
    NetworkXError :
        If the input graph is not undirected.

    Examples
    --------
    >>> G = nx.barbell_graph(4,2)
    >>> print(nx.is_biconnected(G))
    False
    >>> subgraphs = nx.biconnected_component_subgraphs(G)

    See Also
    --------
    is_biconnected,
    articulation_points,
    biconnected_component_edges,
    biconnected_components

    Notes
    -----
    The algorithm to find articulation points and biconnected
    components is implemented using a non-recursive depth-first-search
    (DFS) that keeps track of the highest level that back edges reach
    in the DFS tree. A node `n` is an articulation point if, and only
    if, there exists a subtree rooted at `n` such that there is no
    back edge from any successor of `n` that links to a predecessor of
    `n` in the DFS tree. By keeping track of all the edges traversed
    by the DFS we can obtain the biconnected components because all
    edges of a bicomponent will be traversed consecutively between
    articulation points.

    Graph, node, and edge attributes are copied to the subgraphs.

    References
    ----------
    .. [1] Hopcroft, J.; Tarjan, R. (1973). 
       "Efficient algorithms for graph manipulation". 
       Communications of the ACM 16: 372–378. doi:10.1145/362248.362272
    """
    def edge_subgraph(G,edges):
        # create new graph and copy subgraph into it
        H = G.__class__()
        for u,v in edges:
            H.add_edge(u,v,attr_dict=G[u][v])
        for n in H:
            H.node[n]=G.node[n].copy()
        H.graph=G.graph.copy()
        return H
    return (edge_subgraph(G,edges) for edges in 
            sorted(_biconnected_dfs(G,components=True), key=len, reverse=True))

def articulation_points(G):
    """Return a generator of articulation points, or cut vertices, of a graph.

    An articulation point or cut vertex is any node whose removal (along with
    all its incident edges) increases the number of connected components of 
    a graph. An undirected connected graph without articulation points is
    biconnected. Articulation points belong to more than one biconnected
    component of a graph.

    Notice that by convention a dyad is considered a biconnected component.

    Parameters
    ----------
    G : NetworkX Graph
        An undirected graph.

    Returns
    -------
    articulation points : generator
        generator of nodes

    Raises
    ------
    NetworkXError :
        If the input graph is not undirected.

    Examples
    --------
    >>> G = nx.barbell_graph(4,2)
    >>> print(nx.is_biconnected(G))
    False
    >>> list(nx.articulation_points(G))
    [6, 5, 4, 3]
    >>> G.add_edge(2,8)
    >>> print(nx.is_biconnected(G))
    True
    >>> list(nx.articulation_points(G))
    []

    See Also
    --------
    is_biconnected,
    biconnected_components,
    biconnected_component_edges,
    biconnected_component_subgraphs

    Notes
    -----
    The algorithm to find articulation points and biconnected
    components is implemented using a non-recursive depth-first-search
    (DFS) that keeps track of the highest level that back edges reach
    in the DFS tree. A node `n` is an articulation point if, and only
    if, there exists a subtree rooted at `n` such that there is no
    back edge from any successor of `n` that links to a predecessor of
    `n` in the DFS tree. By keeping track of all the edges traversed
    by the DFS we can obtain the biconnected components because all
    edges of a bicomponent will be traversed consecutively between
    articulation points.

    References
    ----------
    .. [1] Hopcroft, J.; Tarjan, R. (1973). 
       "Efficient algorithms for graph manipulation". 
       Communications of the ACM 16: 372–378. doi:10.1145/362248.362272
    """
    return _biconnected_dfs(G,components=False)

def _biconnected_dfs(G, components=True):
    # depth-first search algorithm to generate articulation points 
    # and biconnected components
    if G.is_directed():
        raise nx.NetworkXError('Not allowed for directed graph G. '
                               'Use UG=G.to_undirected() to create an '
                               'undirected graph.')
    visited = set()
    for start in G:
        if start in visited:
            continue
        discovery = {start:0} # "time" of first discovery of node during search
        low = {start:0}
        root_children = 0
        visited.add(start)
        edge_stack = []
        stack = [(start, start, iter(G[start]))]
        while stack:
            grandparent, parent, children = stack[-1]
            try:
                child = next(children)
                if grandparent == child:
                    continue
                if child in visited:
                    if discovery[child] <= discovery[parent]: # back edge
                        low[parent] = min(low[parent],discovery[child])
                        if components:
                            edge_stack.append((parent,child))
                else:
                    low[child] = discovery[child] = len(discovery)
                    visited.add(child)
                    stack.append((parent, child, iter(G[child])))
                    if components:
                        edge_stack.append((parent,child))
            except StopIteration:
                stack.pop()
                if len(stack) > 1:
                    if low[parent] >= discovery[grandparent]:
                        if components:
                            ind = edge_stack.index((grandparent,parent))
                            yield edge_stack[ind:]
                            edge_stack=edge_stack[:ind]
                        else:
                            yield grandparent
                    low[grandparent] = min(low[parent], low[grandparent])
                elif stack: # length 1 so grandparent is root
                    root_children += 1
                    if components:
                        ind = edge_stack.index((grandparent,parent))
                        yield edge_stack[ind:]
        if not components:
            # root node is articulation point if it has more than 1 child
            if root_children > 1:
                yield start
