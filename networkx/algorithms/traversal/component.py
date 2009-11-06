# -*- coding: utf-8 -*-
"""
Connected components and strongly connected components.
"""
__authors__ = """Eben Kenah\nAric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['number_connected_components', 'connected_components',
           'is_connected', 'connected_component_subgraphs',
           'node_connected_component',
           'number_strongly_connected_components', 
           'strongly_connected_components',
           'is_strongly_connected', 'strongly_connected_component_subgraphs',
           'strongly_connected_components_recursive',
           'kosaraju_strongly_connected_components']


import networkx
from networkx.algorithms.traversal.path import \
     single_source_shortest_path,\
     single_source_shortest_path_length
from networkx.algorithms.traversal.search import \
     dfs_postorder,dfs_preorder


def connected_components(G):
    """
    Return a list of lists of nodes in each connected component of G.

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
            c=single_source_shortest_path_length(G,v)
            components.append(c.keys())
            seen.update(c)
    components.sort(key=len,reverse=True)            
    return components            


def number_connected_components(G):
    """Return the number of connected components in G.
    For undirected graphs only. 
    """
    return len(connected_components(G))


def is_connected(G):
    """Return True if G is connected.
    For undirected graphs only. 
    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""

    if len(G)==0:
        raise networkx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(single_source_shortest_path(G, G.nodes_iter().next()))==len(G)


def connected_component_subgraphs(G):
    """
    Return a list of graphs of each connected component of G.

    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 

    Examples
    --------
    Get largest connected component

    >>> G=nx.path_graph(4)
    >>> G.add_edge(5,6)
    >>> H=nx.connected_component_subgraphs(G)[0]

    """
    cc=connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c))
    return graph_list


def node_connected_component(G,n):
    """
    Return a list of nodes of the connected component containing node n.

    For undirected graphs only. 

    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    return single_source_shortest_path_length(G,n).keys()



def strongly_connected_components(G):
    """Returns a list of strongly connected components in G.

     Uses Tarjan's algorithm with Nuutila's modifications.
     Nonrecursive version of algorithm.

     References:

      R. Tarjan (1972). Depth-first search and linear graph algorithms.
      SIAM Journal of Computing 1(2):146-160.

      E. Nuutila and E. Soisalon-Soinen (1994).
      On finding the strongly connected components in a directed graph.
      Information Processing Letters 49(1): 9-14.

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
    """Returns list of strongly connected components in G.

     Uses Kosaraju's algorithm.
     """
    components=[]
    post=dfs_postorder(G,source=source,reverse_graph=True)
    seen={}
    while post:
        r=post.pop()
        if r in seen:
            continue
        c=dfs_preorder(G,r)
        new=[v for v in c if v not in seen]
        seen.update([(u,True) for u in new])
        components.append(new)
    components.sort(key=len,reverse=True)            
    return components            


def strongly_connected_components_recursive(G):
    """Returns list of strongly connected components in G.

     Uses Tarjan's algorithm with Nuutila's modifications.
     this recursive version of the algorithm will hit the
     Python stack limit for large graphs.
     
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
    """
    Return a list of graphs of each strongly connected component of G.

    The list is ordered from largest connected component to smallest.

    For example, to get the largest strongly connected component:
    >>> G=nx.path_graph(4)
    >>> H=nx.strongly_connected_component_subgraphs(G)[0]

    """
    cc=strongly_connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c))
    return graph_list


def number_strongly_connected_components(G):
    """Return the number of strongly connected components in G.

    For directed graphs only. 
    """
    return len(strongly_connected_components(G))

def is_strongly_connected(G):
    """Return True if G is strongly connected.
    """
    if not G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for undirected graph G.
              See is_connected() for connectivity test."""

    if len(G)==0:
        raise networkx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(strongly_connected_components(G)[0])==len(G)

