"""
Search algorithms.
"""
__authors__ = """Eben Kenah\nAric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.


__all__ = ['dfs_preorder', 'dfs_postorder',
           'dfs_predecessor', 'dfs_successor', 'dfs_tree']

import networkx

def dfs_preorder(G,source=None,reverse_graph=False):
    """Return list of nodes connected to source in depth-first-search preorder.

    Traverse the graph G with depth-first-search from source.
    Non-recursive algorithm.
    """
    if source is None:
        nlist=G.nodes() # process entire graph
    else:
        nlist=[source]  # only process component with source

    if reverse_graph:
        try:
            neighbors=G.predecessors_iter
        except:
            neighbors=G.neighbors_iter
    else:
        neighbors=G.neighbors_iter

    seen={} # nodes seen      
    pre=[]  # list of nodes in a DFS preorder
    for source in nlist:
        if source in seen: continue
        queue=[source]     # use as LIFO queue
        while queue:
            v=queue[-1]
            if v not in seen:
                pre.append(v)
                seen[v]=True
            done=1
            for w in neighbors(v):
                if w not in seen:
                    queue.append(w)
                    done=0
                    break
            if done==1:
                queue.pop()
    return pre


def dfs_postorder(G,source=None,reverse_graph=False):
    """ 
    Return list of nodes connected to source in depth-first-search postorder.

    Traverse the graph G with depth-first-search from source.
    Non-recursive algorithm.
    """
    if source is None:
        nlist=G.nodes() # process entire graph
    else:
        nlist=[source]  # only process component with source
    
    if reverse_graph==True:
        try:
            neighbors=G.predecessors_iter
        except:
            neighbors=G.neighbors_iter
    else:
        neighbors=G.neighbors_iter
    
    seen={} # nodes seen      
    post=[] # list of nodes in a DFS postorder
    for source in nlist:
        if source in seen: continue
        queue=[source]     # use as LIFO queue
        while queue:
            v=queue[-1]
            if v not in seen:
                seen[v]=True
            done=1
            for w in neighbors(v):
                if w not in seen:
                    queue.append(w)
                    done=0
                    break
            if done==1:
                post.append(v)
                queue.pop()
    return post


def dfs_tree(G,source=None,reverse_graph=False):
    """Return directed graph (tree) of depth-first-search with root at source.

    If the graph is disconnected, return a disconnected graph (forest).
    """
    succ=dfs_successor(G,source=source,reverse_graph=reverse_graph)
    return networkx.DiGraph(succ)

def dfs_predecessor(G,source=None,reverse_graph=False):
    """
    Return predecessors of depth-first-search with root at source.
    """
    if source is None:
        nlist=G.nodes() # process entire graph
    else:
        nlist=[source]  # only process component with source

    if reverse_graph==True:
        try:
            neighbors=G.predecessors_iter
        except:
            neighbors=G.neighbors_iter
    else:
        neighbors=G.neighbors_iter

    seen={}   # nodes seen      
    pred={}
    for source in nlist:
        if source in seen: continue
        queue=[source]     # use as LIFO queue
        pred[source]=[]
        while queue:
            v=queue[-1]
            if v not in seen:
                seen[v]=True
            done=1
            for w in neighbors(v):
                if w not in seen:
                    queue.append(w)
                    pred[w]=[v]     # Each node has at most one predecessor
                    done=0
                    break
            if done==1:
                queue.pop()
    return pred


def dfs_successor(G,source=None,reverse_graph=False):
    """
    Return succesors of depth-first-search with root at source.
    """

    if source is None:
        nlist=G.nodes() # process entire graph
    else:
        nlist=[source]  # only process component with source

    if reverse_graph==True:
        try:
            neighbors=G.predecessors_iter
        except:
            neighbors=G.neighbors_iter
    else:
        neighbors=G.neighbors_iter

    seen={}   # nodes seen      
    succ={}
    for source in nlist:
        if source in seen: continue
        queue=[source]     # use as LIFO queue
        while queue:
            v=queue[-1]
            if v not in seen:
                seen[v]=True
                succ[v]=[]
            done=1
            for w in neighbors(v):
                if w not in seen:
                    queue.append(w)
                    succ[v].append(w)
                    done=0
                    break
            if done==1:
                queue.pop()
    return succ

