"""Algorithm for spliting nodes in a directed graph."""

import networkx as nx
from collections import defaultdict

__author__ = "Peng Yu (pengyu.ut@gmail.com)"

__all__ = ['split_pass_through_node_digraph']

def split_pass_through_node_digraph(G):
  """
  The operation splits pass-through nodes (i.e. nodes with both incoming edges and outgoing edges), into pairs of nodes connected by a directed edges indicating the flow direction.
  For each new edge, the tail node has all the incoming old edges and the head node has all the outgoing old edges.
  
  For example, since B has both incoming and outgoing edge in the following digraph, B is split.::
  
      A->B->C
  
  The result is::
  
      A->B:i->B:o->C
  
  For a digraph like the following, since B has both incoming and outgoing edge, split it at B::
  
      D--+
         |
         v
      A->B->C
         |
         +->E
  
  we have::
  
      D--+
         |
         v
      A->Bi->Bo->C
             |
             +-->E

  >>> G=nx.DiGraph()
  >>> G.add_edge(1,2)
  >>> G.add_edge(2,3)
  >>> split_pass_through_node_digraph(G)
  >>> print G.nodes()
  ['2:o', 1, 3, '2:i']
  >>> print G.edges()
  [('2:o', 3), (1, '2:i'), ('2:i', '2:o')]
  >>> G=nx.DiGraph()
  >>> G.add_edge(1, 3)
  >>> G.add_edge(2, 3)
  >>> G.add_edge(3, 4)
  >>> G.add_edge(3, 5)
  >>> split_pass_through_node_digraph(G)
  >>> print G.nodes()
  [1, 2, '3:i', 4, 5, '3:o']
  >>> print G.edges()
  [(1, '3:i'), (2, '3:i'), ('3:i', '3:o'), ('3:o', 4), ('3:o', 5)]
  """

  if not G.is_directed():
    raise nx.NetworkXError('This function only works for directed graphs.')

  for n in list(G):
    if G.in_degree(n) > 0 and G.out_degree(n) > 0:
      n_i = ':'.join((str(n), 'i'))
      n_o = ':'.join((str(n), 'o'))
      for p in G.predecessors_iter(n):
        G.add_edge(p, n_i)
      for s in G.successors_iter(n):
        G.add_edge(n_o, s)
      G.remove_node(n)
      G.add_edge(n_i, n_o)


