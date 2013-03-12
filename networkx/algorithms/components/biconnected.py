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
from collections import defaultdict

__author__ = '\n'.join(['Jordi Torrents <jtorrents@milnou.net>',
                        'Dan Schult <dschult@colgate.edu>',
                        'Aric Hagberg <aric.hagberg@gmail.com>',
                        'Peng Yu <pengyu.ut@gmail.com>'])
__all__ = ['biconnected_components',
           'biconnected_component_edges',
           'biconnected_component_subgraphs',
           'is_biconnected',
           'articulation_points',
           'bridges',
           'weakly_biconnected_component_subdigraphs'
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

def bridges(G):
  """
  Bridge detection algorithm based on WGB-DFS.

  """

  if G.is_directed():
    raise nx.NetworkXError('This function is for undirected graphs.\n'
                           'Use directed_wgb_dfs() for directed graphs.')

  class WhiteGrayBlackDFS:
    def __init__(self, G):
      # white: empty
      # gray: 1
      # black: 2

      self.visited = set()
      self.dfs_num = {}
      self.num = 0
      self.G = G
      self.back_edges = defaultdict(set)

    def bridges(self, parent, current):
      #print '{'
      #print 'parent, current:', parent, current
      #print 'dfs_num:', self.dfs_num
      self.visited.add(current)
      current_lowpoint = self.dfs_num[current] = self.num

      self.num += 1
      #print 'dfs_num:', self.dfs_num

      for child in G.neighbors(current):
        if child != parent:
          #print 'current, child:', current, child
          if not current in self.back_edges or (current in self.back_edges and not child in self.back_edges[current]):
            if child in self.visited:
              current_lowpoint = min(current_lowpoint, self.dfs_num[child])
            else:
              for x in self.bridges(current, child):
                yield x
              if self.child_lowpoint > self.dfs_num[current]:
                #print '>>> bridge:', current, child
                yield (current, child)
              current_lowpoint = min(current_lowpoint, self.child_lowpoint)

      #print 'parent, current, current_lowpoint:', parent, current, current_lowpoint
      #print 'dfs_num:', self.dfs_num
      #print '}'
      self.child_lowpoint = current_lowpoint


  dfs = WhiteGrayBlackDFS(G)

  for x in G:
    if not x in dfs.visited: 
      #print x
      for e in dfs.bridges(x, x):
        yield e

import re

def weakly_biconnected_component_subdigraphs(G):
  """
  >>> G = nx.DiGraph()
  >>> G.add_edge('a', 'c')
  >>> G.add_edge('b', 'c')
  >>> G.add_edge('c', 'd')
  >>> G.add_edge('c', 'e')
  >>> G.add_edge('x', 'y')
  >>> G.add_node('z')
  >>> for n in G.nodes_iter():
  ...   G.node[n]['attr'] = n
  >>> for e in G.edges_iter():
  ...  G[e[0]][e[1]]['attr'] = '->'.join([str(i) for i in e])
  >>> for g in weakly_biconnected_component_subdigraphs(G):
  ...   print '------------------'
  ...   print g.nodes(data=True)
  ...   print g.edges(data=True)
  ------------------
  [('a', {'attr': 'a'}), ('c', {'attr': 'c'}), ('b', {'attr': 'b'})]
  [('a', 'c', {'attr': 'a->c'}), ('b', 'c', {'attr': 'b->c'})]
  ------------------
  [('c', {'attr': 'c'}), ('e', {'attr': 'e'}), ('d', {'attr': 'd'})]
  [('c', 'e', {'attr': 'c->e'}), ('c', 'd', {'attr': 'c->d'})]
  ------------------
  [('y', {'attr': 'y'}), ('x', {'attr': 'x'})]
  [('x', 'y', {'attr': 'x->y'})]
  ------------------
  [('z', {'attr': 'z'})]
  []
  """

  if not G.is_directed():
    raise nx.NetworkXError('Input graph must be a digraph')

  if not all(isinstance(n, basestring) for n in G):
    raise nx.NetworkXError('Node names must all be strings.')

  split_G=nx.DiGraph(G)
  nx.algorithms.split_pass_through_node_digraph(split_G)

  #print '=================='
  #print split_G.nodes()
  #print split_G.edges()

  for e in nx.bridges(nx.Graph(split_G)):
    m0 = re.match('^(.*):(o|i)$', e[0])
    m1 = re.match('^(.*):(o|i)$', e[1])

    if m0 is not None and m1 is not None:
      if m0.group(1) == m1.group(1) and m0.group(2) != m1.group(2):
        split_G.remove_edge(':'.join((m0.group(1), 'i')), ':'.join((m0.group(1), 'o')))

  for wcc in nx.weakly_connected_component_subgraphs(split_G):
    def extract_original_node(n):
      m = re.match('^(.*):(o|i)$', n)
      if m is not None:
        return m.group(1)
      else:
        return n

    subgraph_nodes = set([extract_original_node(n) for n in wcc])
    yield G.subgraph(subgraph_nodes)

