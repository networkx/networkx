# -*- coding: utf-8 -*-
"""
Strongly connected components.
"""
#    Copyright (C) 2004-2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__authors__ = "\n".join(['Eben Kenah',
                         'Aric Hagberg (hagberg@lanl.gov)'
                         'Christopher Ellison',
                         'Ben Edwards (bedwards@cs.unm.edu)'])

__all__ = ['number_strongly_connected_components',
           'strongly_connected_components',
           'strongly_connected_component_subgraphs',
           'is_strongly_connected',
           'strongly_connected_components_recursive',
           'kosaraju_strongly_connected_components',
           'condensation']

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
    G=G.reverse(copy=False)
    post=list(nx.dfs_postorder_nodes(G,source=source))
    G=G.reverse(copy=False)
    seen={}
    while post:
        r=post.pop()
        if r in seen:
            continue
        c=nx.dfs_preorder_nodes(G,r)
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
    The list is ordered from largest strongly connected component to smallest.

    Graph, node, and edge attributes are copied to the subgraphs.
    """
    cc=strongly_connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c).copy())
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
        raise nx.NetworkXError("""Not allowed for undirected graph G.
              See is_connected() for connectivity test.""")

    if len(G)==0:
        raise nx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(strongly_connected_components(G)[0])==len(G)

def condensation(G, scc=None):
    """Returns the condensation of G.

    The condensation of G is the graph with each of the strongly connected
    components contracted into a single node.

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph.

    scc:  list (optional, default=None)
       A list of strongly connected components.  If provided, the elements in
       `scc` must partition the nodes in `G`. If not provided, it will be
       calculated as scc=nx.strongly_connected_components(G).

    Returns
    -------
    C : NetworkX DiGraph
       The condensation of G. The node labels are integers corresponding
       to the index of the component in the list of strongly connected
       components.

    Notes
    -----
    After contracting all strongly connected components to a single node,
    the resulting graph is a directed acyclic graph.
    """
    if scc is None:
        scc = nx.strongly_connected_components(G)
    mapping = {}
    C = nx.DiGraph()
    for i,component in enumerate(scc):
        for n in component:
            mapping[n] = i
    C.add_nodes_from(range(len(scc)))
    for u,v in G.edges():
        if mapping[u] != mapping[v]:
            C.add_edge(mapping[u],mapping[v])
    return C
