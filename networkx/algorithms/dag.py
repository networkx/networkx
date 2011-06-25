# -*- coding: utf-8 -*-
from fractions import gcd
import networkx as nx
"""Algorithms for directed acyclic graphs (DAGs)."""
#    Copyright (C) 2006-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                            'Dan Schult (dschult@colgate.edu)',
                            'Ben Edwards (bedwards@cs.unm.edu)'])
__all__ = ['topological_sort', 
           'topological_sort_recursive',
           'is_directed_acyclic_graph',
           'is_aperiodic']

def is_directed_acyclic_graph(G):
    """Return True if the graph G is a directed acyclic graph (DAG) or 
    False if not.
    
    Parameters
    ----------
    G : NetworkX graph
      A graph

    Returns
    -------
    is_dag : bool
       True if G is a DAG, false otherwise
    """
    try:
        topological_sort(G)
        return True
    except nx.NetworkXUnfeasible:
        return False

def topological_sort(G,nbunch=None):
    """Return a list of nodes in topological sort order.

    A topological sort is a nonunique permutation of the nodes
    such that an edge from u to v implies that u appears before v in the
    topological sort order.

    Parameters
    ----------
    G : NetworkX digraph
       A directed graph

    nbunch : container of nodes (optional)
       Explore graph in specified order given in nbunch

    Raises
    ------
    NetworkXError
       Topological sort is defined for directed graphs only. If the
       graph G is undirected, a NetworkXError is raised.

    NetworkXUnfeasible
       If G is not a directed acyclic graph (DAG) no topological sort
       exists and a NetworkXUnfeasible exception is raised.

    Notes
    -----
    This algorithm is based on a description and proof in
    The Algorithm Design Manual [1]_ .

    See also
    --------
    is_directed_acyclic_graph

    References
    ----------
    .. [1] Skiena, S. S. The Algorithm Design Manual  (Springer-Verlag, 1998). 
        http://www.amazon.com/exec/obidos/ASIN/0387948600/ref=ase_thealgorithmrepo/
    """
    if not G.is_directed():
        raise nx.NetworkXError(
                "Topological sort not defined on undirected graphs.")

    # nonrecursive version
    seen={}
    order_explored=[] # provide order and 
    explored={}       # fast search without more general priorityDictionary
                     
    if nbunch is None:
        nbunch = G.nodes_iter() 
    for v in nbunch:     # process all vertices in G
        if v in explored: 
            continue
        fringe=[v]   # nodes yet to look at
        while fringe:
            w=fringe[-1]  # depth first search
            if w in explored: # already looked down this branch
                fringe.pop()
                continue
            seen[w]=1     # mark as seen
            # Check successors for cycles and for new nodes
            new_nodes=[]
            for n in G[w]:
                if n not in explored:
                    if n in seen: #CYCLE !!
                        raise nx.NetworkXUnfeasible("Graph contains a cycle.")
                    new_nodes.append(n)
            if new_nodes:   # Add new_nodes to fringe
                fringe.extend(new_nodes)
            else:           # No new nodes so w is fully explored
                explored[w]=1
                order_explored.insert(0,w) # reverse order explored
                fringe.pop()    # done considering this node
    return order_explored

def topological_sort_recursive(G,nbunch=None):
    """Return a list of nodes in topological sort order.

    A topological sort is a nonunique permutation of the nodes such
    that an edge from u to v implies that u appears before v in the
    topological sort order.

    Parameters
    ----------
    G : NetworkX digraph

    nbunch : container of nodes (optional)
       Explore graph in specified order given in nbunch

    Raises
    ------
    NetworkXError
       Topological sort is defined for directed graphs only. If the
       graph G is undirected, a NetworkXError is raised.

    NetworkXUnfeasible
        If G is not a directed acyclic graph (DAG) no topological sort
        exists and a NetworkXUnfeasible exception is raised.

    Notes
    -----
    This is a recursive version of topological sort.

    See also
    --------
    topological_sort
    is_directed_acyclic_graph

    """
    if not G.is_directed():
        raise nx.NetworkXError(
                "Topological sort not defined on undirected graphs.")

    # function for recursive dfs
    def _dfs(G,seen,explored,v):
        seen.add(v)
        for w in G[v]:
            if w not in seen: 
                if not _dfs(G,seen,explored,w):
                    return False
            elif w in seen and w not in explored:
                # cycle Found--- no topological sort
                raise nx.NetworkXUnfeasible("Graph contains a cycle.")
        explored.insert(0,v) # inverse order of when explored 
        return True

    seen=set()
    explored=[]

    if nbunch is None:
        nbunch = G.nodes_iter() 
    for v in nbunch:  # process all nodes
        if v not in explored:
            if not _dfs(G,seen,explored,v): 
                raise nx.NetworkXUnfeasible("Graph contains a cycle.")
    return explored

def is_aperiodic(G):
    """Return True if G is aperiodic.

    A directed graph is aperiodic if there is no integer k > 1 that 
    divides the length of every cycle in the graph.

    Parameters
    ----------
    G : NetworkX DiGraph
      Graph

    Returns
    -------
    aperiodic : boolean
      True if the graph is aperiodic False otherwise

    Raises
    ------
    NetworkXError
      If G is not directed

    Notes
    -----
    This uses the method outlined in [1]_, which runs in O(m) time
    given m edges in G. Note that a graph is not aperiodic if it is
    acyclic as every integer trivial divides length 0 cycles.

    References
    ----------
    .. [1] Jarvis, J. P.; Shier, D. R. (1996),
       Graph-theoretic analysis of finite Markov chains,
       in Shier, D. R.; Wallenius, K. T., Applied Mathematical Modeling:
       A Multidisciplinary Approach, CRC Press.
    """
    if not G.is_directed():
        raise nx.NetworkXError("is_aperiodic not defined for undirected graphs")

    s = next(G.nodes_iter())
    levels = {s:0}
    this_level = [s]
    g = 0
    l = 1
    while this_level:
        next_level = []
        for u in this_level:
            for v in G[u]:
                if v in levels: # Non-Tree Edge
                    g = gcd(g, levels[u]-levels[v] + 1)
                else: # Tree Edge
                    next_level.append(v)
                    levels[v] = l
        this_level = next_level
        l += 1
    if len(levels)==len(G): #All nodes in tree
        return g==1
    else:
        return g==1 and nx.is_aperiodic(G.subgraph(set(G)-set(levels)))
