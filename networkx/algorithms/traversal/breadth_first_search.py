"""
====================
Breadth-first search 
====================

Basic algorithms for breadth-first searching.
"""
__author__ = """\n""".join(['Aric Hagberg <hagberg@lanl.gov>', 'Peng Yu <pengyu.ut@gmail.com>'])

__all__ = [
  'bfs_edges'
  , 'bfs_tree'
  , 'bfs_predecessors'
  , 'bfs_successors'
  , 'dfs_wgb_undirected'
  , 'dfs_wgb_directed'
]

import networkx as nx
from collections import defaultdict
import sys

def bfs_edges(G,source):
    """Produce edges in a breadth-first-search starting at source."""
    # Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    # by D. Eppstein, July 2004.
    visited=set([source])
    stack = [(source,iter(G[source]))]
    while stack:
        parent,children = stack[0]
        try:
            child = next(children)
            if child not in visited:
                yield parent,child
                visited.add(child)
                stack.append((child,iter(G[child])))
        except StopIteration:
            stack.pop(0)


def bfs_tree(G, source):
    """Return directed tree of breadth-first-search from source."""
    return nx.DiGraph(bfs_edges(G,source))


def bfs_predecessors(G, source):
    """Return dictionary of predecessors in breadth-first-search from source."""
    return dict((t,s) for s,t in bfs_edges(G,source))


def bfs_successors(G, source):
    """Return dictionary of successors in breadth-first-search from source."""
    d=defaultdict(list)
    for s,t in bfs_edges(G,source):
        d[s].append(t)
    return dict(d)



def dfs_wgb_undirected(G
                       , process_gray = lambda x: sys.stdout.write('gray: ' + str(x) + '\n')
                       , process_tree_edge = lambda x, y: sys.stdout.write('tree edge: ' + str(x) + ', ' + str(y) + '\n')
                       , process_black = lambda x: sys.stdout.write('black: ' + str(x) + '\n')
                       , process_back_edge = lambda x, y: sys.stdout.write('back edge: ' + str(x) + ', ' + str(y) + '\n')
                      ):
  """
  White-Gray-Black Depth First Search (WGB-DFS) is the cornerstone of many graph algorithms.

  This function implements a template of WGB-DFS undirected graphs (``nx.Graph``), so that users can plug the function for pressing the node and edges in the order thay are visited in th WGB-DFS. The default is just to print them.

  Also, users can copy this function as a skeleton and modify the necessary part of the code to fit a particular need. ``bridges()`` was created in this way.
  """

  if G.is_directed():
    raise nx.NetworkXError('This function is for undirected graphs.\n'
                           'Use directed_wgb_dfs() for directed graphs.')

  class WhiteGrayBlackDFS:
    def __init__(self, G):
      # white: empty
      # gray: 1
      # black: 2

      self.color = {}
      self.dfs_num = {}
      self.num = 0
      self.G = G
      self.back_edges = defaultdict(set)

    def recursion(self, parent, current):
      self.color[current] = 1
      #print 'gray: ', current
      process_gray(current)
      self.dfs_num[current] = self.num
      self.num += 1

      for child in G.neighbors(current):
        if child != parent:
          #print 'current, child:', current, child
          if not current in self.back_edges or (current in self.back_edges and not child in self.back_edges[current]):
            if not child in self.color:
              process_tree_edge(current, child)
              self.recursion(current, child)
            elif self.color[child] == 1:
              process_back_edge(current, child)
              self.back_edges[child].add(current)
              #print self.back_edges
            else:
              raise nx.NetworkXError('Edge type other than regular and back should never happen')

      self.color[current] = 2
      process_black(current)

    def doit(self):
      for x in self.G:
        if not x in self.color: 
          self.recursion(x, x)

  dfs = WhiteGrayBlackDFS(G)
  dfs.doit()

def dfs_wgb_directed(G
                       , process_gray = lambda x: sys.stdout.write('gray: ' + str(x) + '\n')
                       , process_black = lambda x: sys.stdout.write('black: ' + str(x) + '\n')
                       , process_tree_edge = lambda x, y: sys.stdout.write('tree edge: ' + str(x) + ', ' + str(y) + '\n')
                       , process_back_edge = lambda x, y: sys.stdout.write('back edge: ' + str(x) + ', ' + str(y) + '\n')
                       , process_forward_edge = lambda x, y: sys.stdout.write('forward edge: ' + str(x) + ', ' + str(y) + '\n')
                       , process_cross_edge = lambda x, y: sys.stdout.write('cross edge: ' + str(x) + ', ' + str(y) + '\n')
                      ):
  """
  White-Gray-Black Depth First Search (WGB-DFS) is the cornerstone for many graph algorithms.

  This function implements a template of WGB-DFS for directed graphs (``nx.DiGraph``), so that users can plug the function for pressing the node and edges in the order thay are visited in th WGB-DFS. The default is just to print them.

  """

  if not G.is_directed():
    raise nx.NetworkXError('This function is for directed graphs.\n'
                           'Use undirected_wgb_dfs() for undirected graphs.')

  class WhiteGrayBlackDFS:
    def __init__(self, G):
      # white: empty
      # gray: 1
      # black: 2

      self.color = {}
      #self.dfs_num = {}
      self.discovery_time = {}
      #self.finishing_time = {} #not used
      self.current_time = 0
      self.G = G

    def recursion(self, parent, current):
      self.color[current] = 1
      #print 'gray: ', current
      process_gray(current)
      #self.dfs_num[current] = self.num
      #self.num += 1
      self.discovery_time[current] = self.current_time
      self.current_time += 1

      for child in G.neighbors(current):
        if child != parent:
          #print 'current, child:', current, child
          if not child in self.color:
            process_tree_edge(current, child)
            self.recursion(current, child)
          elif self.color[child] == 1:
            process_back_edge(current, child)
          elif self.color[child] == 2:
            if self.discovery_time[current] > self.discovery_time[child]:
              process_cross_edge(current, child)
            else:
              process_forward_edge(current, child)
          else:
            raise RuntimeError('Edge type other than tree, back, forward and cross should never happen')

      self.color[current] = 2
      process_black(current)

    def doit(self):
      for x in self.G:
        if not x in self.color: 
          self.recursion(x, x)

  dfs = WhiteGrayBlackDFS(G)
  dfs.doit()

