# -*- coding: utf-8 -*-
"""
Connected components and strongly connected components.
"""
__authors__ = "\n".join(['Eben Kenah',
                         'Aric Hagberg (hagberg@lanl.gov)'
                         'Christopher Ellison'])
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['number_connected_components', 
           'connected_components',
           'connected_component_subgraphs',
           'is_connected',
           'node_connected_component',
           'number_strongly_connected_components', 
           'strongly_connected_components',
           'strongly_connected_component_subgraphs',
           'is_strongly_connected', 
           'strongly_connected_components_recursive',
           'kosaraju_strongly_connected_components',
           'condensation',
           'number_attracting_components', 
           'attracting_components',
           'is_attracting_component', 
           'attracting_component_subgraphs',
           'number_weakly_connected_components', 
           'weakly_connected_components',
           'weakly_connected_component_subgraphs',
           'is_weakly_connected' 
           ]

import networkx

def connected_components(G):
    """Return nodes in connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    comp : list of lists
       A list of nodes for each component of G.

    See Also       
    --------
    strongly_connected_components

    Notes
    -----
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 
    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    seen={}
    components=[]
    for v in G:      
        if v not in seen:
            c=networkx.single_source_shortest_path_length(G,v)
            components.append(c.keys())
            seen.update(c)
    components.sort(key=len,reverse=True)            
    return components            


def number_connected_components(G):
    """Return number of connected components in graph.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    n : integer
       Number of connected components

    See Also       
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    return len(connected_components(G))


def is_connected(G):
    """Test graph connectivity

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    connected : bool
      True if the graph is connected, false otherwise.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> print nx.is_connected(G)
    True

    See Also
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    if G.is_directed():
        raise networkx.NetworkXError(\
            """Not allowed for directed graph G.
Use UG=G.to_undirected() to create an undirected graph.""")

    if len(G)==0:
        raise networkx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(networkx.single_source_shortest_path_length(G,
                                              G.nodes_iter().next()))==len(G)


def connected_component_subgraphs(G):
    """Return connected components as subgraphs.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    glist : list
      A list of graphs, one for each connected component of G.

    Examples
    --------
    Get largest connected component as subgraph

    >>> G=nx.path_graph(4)
    >>> G.add_edge(5,6)
    >>> H=nx.connected_component_subgraphs(G)[0]

    See Also
    --------
    connected_components

    Notes
    -----
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 
    """
    cc=connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c))
    return graph_list


def node_connected_component(G,n):
    """Return nodes in connected components of graph containing node n.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    n : node label       
       A node in G

    Returns
    -------
    comp : lists
       A list of nodes in component of G containing node n.

    See Also       
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    return networkx.single_source_shortest_path_length(G,n).keys()



def strongly_connected_components(G):
    """Return nodes in strongly connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
       An directed graph.

    Returns
    -------
    comp : list of lists
       A list of nodes for each component of G.
       The list is ordered from largest connected component to smallest.

    See Also       
    --------
    connected_components

    Notes
    -----
    Uses Tarjan's algorithm with Nuutila's modifications.
    Nonrecursive version of algorithm.

    References
    ----------
    .. [1] Depth-first search and linear graph algorithms, R. Tarjan
       SIAM Journal of Computing 1(2):146-160, (1972).

    .. [2] On finding the strongly connected components in a directed graph.
       E. Nuutila and E. Soisalon-Soinen 
       Information Processing Letters 49(1): 9-14, (1994)..
    """
    preorder={}
    lowlink={}    
    scc_found={}
    scc_queue = []
    scc_list=[]
    i=0     # Preorder counter
    for source in G:
        if source not in scc_found:
            queue=[source]
            while queue:
                v=queue[-1]
                if v not in preorder:
                    i=i+1
                    preorder[v]=i
                done=1
                v_nbrs=G[v]
                for w in v_nbrs:
                    if w not in preorder:
                        queue.append(w)
                        done=0
                        break
                if done==1:
                    lowlink[v]=preorder[v]
                    for w in v_nbrs:
                        if w not in scc_found:
                            if preorder[w]>preorder[v]:
                                lowlink[v]=min([lowlink[v],lowlink[w]])
                            else:
                                lowlink[v]=min([lowlink[v],preorder[w]])
                    queue.pop()
                    if lowlink[v]==preorder[v]:
                        scc_found[v]=True
                        scc=[v]
                        while scc_queue and preorder[scc_queue[-1]]>preorder[v]:
                            k=scc_queue.pop()
                            scc_found[k]=True
                            scc.append(k)
                        scc_list.append(scc)
                    else:
                        scc_queue.append(v)
    scc_list.sort(key=len,reverse=True)            
    return scc_list


def kosaraju_strongly_connected_components(G,source=None):
    """Return nodes in strongly connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
       An directed graph.

    Returns
    -------
    comp : list of lists
       A list of nodes for each component of G.
       The list is ordered from largest connected component to smallest.

    See Also       
    --------
    connected_components

    Notes
    -----
    Uses Kosaraju's algorithm.
    """
    components=[]
    post=networkx.dfs_postorder(G,source=source,reverse_graph=True)
    seen={}
    while post:
        r=post.pop()
        if r in seen:
            continue
        c=networkx.dfs_preorder(G,r)
        new=[v for v in c if v not in seen]
        seen.update([(u,True) for u in new])
        components.append(new)
    components.sort(key=len,reverse=True)            
    return components            


def strongly_connected_components_recursive(G):
    """Return nodes in strongly connected components of graph.

    Recursive version of algorithm.

    Parameters
    ----------
    G : NetworkX Graph
       An directed graph.

    Returns
    -------
    comp : list of lists
       A list of nodes for each component of G.
       The list is ordered from largest connected component to smallest.

    See Also       
    --------
    connected_components

    Notes
    -----
    Uses Tarjan's algorithm with Nuutila's modifications.

    References
    ----------
    .. [1] Depth-first search and linear graph algorithms, R. Tarjan
       SIAM Journal of Computing 1(2):146-160, (1972).

    .. [2] On finding the strongly connected components in a directed graph.
       E. Nuutila and E. Soisalon-Soinen 
       Information Processing Letters 49(1): 9-14, (1994)..
    """
    def visit(v,cnt):
        root[v]=cnt
        visited[v]=cnt
        cnt+=1
        stack.append(v)
        for w in G[v]:
            if w not in visited: visit(w,cnt)
            if w not in component:
                root[v]=min(root[v],root[w])
        if root[v]==visited[v]:
            component[v]=root[v]
            tmpc=[v] # hold nodes in this component
            while stack[-1]!=v:
                w=stack.pop()                
                component[w]=root[v]
                tmpc.append(w)
            stack.remove(v) 
            scc.append(tmpc) # add to scc list
    scc=[]
    visited={}   
    component={}
    root={}
    cnt=0
    stack=[]
    for source in G:
        if source not in visited: 
            visit(source,cnt)

    scc.sort(key=len,reverse=True)            
    return scc


def strongly_connected_component_subgraphs(G):
    """Return strongly connected components as subgraphs.

    Parameters
    ----------
    G : NetworkX Graph
       A graph.

    Returns
    -------
    glist : list
      A list of graphs, one for each strongly connected component of G.

    See Also
    --------
    connected_component_subgraphs

    Notes
    -----
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 
    """
    cc=strongly_connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c))
    return graph_list


def number_strongly_connected_components(G):
    """Return number of strongly connected components in graph.

    Parameters
    ----------
    G : NetworkX graph
       A directed graph.

    Returns
    -------
    n : integer
       Number of strongly connected components

    See Also       
    --------
    connected_components

    Notes
    -----
    For directed graphs only. 
    """
    return len(strongly_connected_components(G))


def is_strongly_connected(G):
    """Test directed graph for strong connectivity.

    Parameters
    ----------
    G : NetworkX Graph
       A directed graph.

    Returns
    -------
    connected : bool
      True if the graph is strongly connected, False otherwise.

    See Also
    --------
    strongly_connected_components

    Notes
    -----
    For directed graphs only. 
    """
    if not G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for undirected graph G.
              See is_connected() for connectivity test."""

    if len(G)==0:
        raise networkx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(strongly_connected_components(G)[0])==len(G)


def condensation(G):
    """Returns the condensation of G.

    The condensation of G is the graph with each of the strongly connected 
    components contracted into a single node.

    Parameters
    ----------
    G : NetworkX Graph
       A directed graph.

    Returns
    -------
    cG : NetworkX DiGraph
       The condensation of G.

    Notes
    -----
    After contracting all strongly connected components to a single node,
    the resulting graph is a directed acyclic graph.

    """
    scc = strongly_connected_components(G)
    mapping = dict([(n,tuple(sorted(c))) for c in scc for n in c])
    cG = networkx.DiGraph()
    for u in mapping:
        cG.add_node(mapping[u])
        for _,v,d in G.edges_iter(u, data=True):
            if v not in mapping[u]:
                cG.add_edge(mapping[u], mapping[v])
    return cG


def attracting_components(G):
    """Returns a list of attracting components in `G`.

    An attracting component in a directed graph `G` is a strongly connected
    component with the property that a random walker on the graph will never
    leave the component, once it enters the component.

    The nodes in attracting components can also be thought of as recurrent
    nodes.  If a random walker enters the attractor containing the node, then
    the node will be visited infinitely often.

    Parameters
    ----------
    G : DiGraph, MultiDiGraph
        The graph to be analyzed.

    Returns
    -------
    attractors : list
        The list of attracting components, sorted from largest attracting
        component to smallest attracting component.

    See Also
    --------
    number_attracting_components
    is_attracting_component 
    attracting_component_subgraphs

    """
    cG = condensation(G)
    attractors = [scc for scc in cG if cG.out_degree(scc) == 0]
    attractors.sort(key=len,reverse=True)
    return attractors


def number_attracting_components(G):
    """Returns the number of attracting components in `G`.

    Parameters
    ----------
    G : DiGraph, MultiDiGraph
        The graph to be analyzed.

    Returns
    -------
    n : int
        The number of attracting components in G.

    See Also
    --------
    attracting_components
    is_attracting_component
    attracting_component_subgraphs

    """
    n = len(attracting_components(G))
    return n


def is_attracting_component(G):
    """Returns True if `G` consists of a single attracting component.

    Parameters
    ----------
    G : DiGraph, MultiDiGraph
        The graph to be analyzed.

    Returns
    -------
    attracting : bool
        True if `G` has a single attracting component. Otherwise, False.

    See Also
    --------
    attracting_components
    number_attracting_components
    attracting_component_subgraphs

    """
    ac = attracting_components(G)
    if len(ac[0]) == len(G):
        attracting = True
    else:
        attracting = False
    return attracting


def attracting_component_subgraphs(G):
    """Returns a list of attracting component subgraphs from `G`.

    Parameters
    ----------
    G : DiGraph, MultiDiGraph
        The graph to be analyzed.

    Returns
    -------
    subgraphs : list
        A list of node-induced subgraphs of the attracting components of `G`.
    
    See Also
    --------
    attracting_components
    number_attracting_components
    is_attracting_component

    """
    subgraphs = [G.subgraph(ac) for ac in attracting_components(G)]
    return subgraphs


def weakly_connected_components(G):
    """Return weakly connected components of G.
    """
    if not G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for undirected graph G. 
              Use connected_components() """
    seen={}
    components=[]
    for v in G:
        if v not in seen:
            c=_single_source_shortest_unipath_length(G,v)
            components.append(c.keys())
            seen.update(c)
    components.sort(key=len,reverse=True)
    return components


def number_weakly_connected_components(G):
    """Return the number of connected components in G.
    For directed graphs only. 
    """
    return len(weakly_connected_components(G))

def weakly_connected_component_subgraphs(G):
    """Return weakly connected components as subgraphs.
    """
    wcc=weakly_connected_components(G)
    graph_list=[]
    for c in wcc:
        graph_list.append(G.subgraph(c))
    return graph_list

def is_weakly_connected(G):
    """Test directed graph for weak connectivity.

    Parameters
    ----------
    G : NetworkX Graph
       A directed graph.

    Returns
    -------
    connected : bool
      True if the graph is weakly connected, False otherwise.

    See Also
    --------
    strongly_connected_components

    Notes
    -----
    For directed graphs only. 
    """
    if not G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for undirected graph G.
              See is_connected() for connectivity test."""

    if len(G)==0:
        raise networkx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(weakly_connected_components(G)[0])==len(G)

def _single_source_shortest_unipath_length(G,source,cutoff=None):
    """Compute the shortest path lengths from source to all reachable nodes.

    The direction of the edge between nodes is ignored.
    
    For directed graphs only.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    lengths : dictionary
        Dictionary of shortest path lengths keyed by target.
    """
    # namespace speedups
    Gsucc = G.succ
    Gpred = G.pred

    seen={}                  # level (number of hops) when seen in BFS
    level=0                  # the current level
    nextlevel={source:1}  # dict of nodes to check at next level
    while nextlevel:
        thislevel=nextlevel  # advance to next level
        nextlevel={}         # and start a new list (fringe)
        for v in thislevel:
            if v not in seen:
                seen[v]=level # set the level of vertex v
                nextlevel.update(Gsucc[v]) # add successors of v
                nextlevel.update(Gpred[v]) # add predecessors of v
        if (cutoff is not None and cutoff <= level):  break
        level=level+1
    return seen  # return all path lengths as dictionary
