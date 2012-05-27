#!/usr/bin/env python

import networkx as nx
from collections import defaultdict

__author__ = "Peng Yu (pengyu.ut@gmail.com)"

__all__ = ['compress_path_digraph']

def is_solo_node(G, n):
  """
  >>> G = nx.DiGraph()
  >>> G.add_node(1)
  >>> is_solo_node(G, 1)
  True
  """

  return G.in_degree(n) == 0 and G.out_degree(n) == 0

def is_simple_start_node(G, n):
  """
  >>> G = nx.DiGraph()
  >>> G.add_edge(1,2)
  >>> is_simple_start_node(G, 1)
  True
  """

  return G.in_degree(n) == 0 and G.out_degree(n) == 1

def is_complex_start_node(G, n):
  """
  >>> G = nx.DiGraph()
  >>> G.add_edge(1,2)
  >>> G.add_edge(1,3)
  >>> is_complex_start_node(G, 1)
  True
  """

  return G.in_degree(n) == 0 and G.out_degree(n) > 1

def is_simple_end_node(G, n):
  """
  >>> G = nx.DiGraph()
  >>> G.add_edge(1,2)
  >>> is_simple_end_node(G, 2)
  True
  """

  return G.out_degree(n) == 0 and G.in_degree(n) == 1

def is_complex_end_node(G, n):
  """
  >>> G = nx.DiGraph()
  >>> G.add_edge(1,3)
  >>> G.add_edge(2,3)
  >>> is_complex_end_node(G, 3)
  True
  """

  return G.out_degree(n) == 0 and G.in_degree(n) > 1

def is_pass_through_node(G, n):
  """
  >>> G = nx.path_graph(3, create_using=nx.DiGraph())
  >>> is_pass_through_node(G, 1)
  True
  """

  return G.in_degree(n) == 1 and G.out_degree(n) == 1

def is_branching_node(G, n):
  """
  >>> G = nx.path_graph(3, create_using=nx.DiGraph())
  >>> G.add_edge(1,3)
  >>> is_branching_node(G, 1)
  True
  """
  return ((G.in_degree(n) >= 1 and G.out_degree(n) > 1)
          or (G.in_degree(n) > 1 and G.out_degree(n) >= 1))

class PathThroughFreeDAGCreator:
  def __init__(self):
    self.chains = []
    self.in_chains = {}
    self.stored_chains_from_start = defaultdict(list)
    self.stored_chains_from_end = defaultdict(list)
    self.complex_start_nodes = defaultdict(list)
    self.complex_end_nodes = []
    self.branching_nodes = defaultdict(list)
    #UNNECESSARY: self.solo_nodes = []
    #UNNECESSARY: self.solo_chains = []

  def create(self, G):
    for n in G:
      if not n in self.in_chains:
        self.in_chains[n] = 1
        if is_pass_through_node(G, n):
          self.init_chain(n)
          self.trace_parent(G, n)
          self.trace_child(G, n)
        elif is_simple_start_node(G, n):
          self.init_chain(n, True)
          self.trace_child(G, n)
        elif is_simple_end_node(G, n):
          self.init_chain(n)
          self.trace_parent(G, n)
        elif is_complex_start_node(G, n):
          self.complex_start_nodes[n]
          for s in G.successors(n):
            if not is_pass_through_node(G, s):
              self.complex_start_nodes[n].append(s)
        elif is_complex_end_node(G, n):
          self.complex_end_nodes.append(n)
        elif is_branching_node(G, n):
          self.branching_nodes[n]
          for s in G.successors(n):
            if not is_pass_through_node(G, s):
              self.branching_nodes[n].append(s)
        elif is_solo_node(G, n):
          #UNNECESSARY: self.solo_nodes.append(n)
          pass
        else:
          raise RuntimeError("The node type is not found")

  def init_chain(self, n, is_simple_start=False):
    self.chains.append([n])
    self.is_chain_start_simple=is_simple_start

  def trace_parent(self, G, n):
    """
    n must be a path-through node, which will not be checked. 
    """
    while True:
      n=G.predecessors(n)[0]
      if is_pass_through_node(G, n):
        self.in_chains[n] = 1
        self.chains[-1].insert(0, n)
      else:
        if is_complex_start_node(G, n) or is_branching_node(G, n):
          self.stored_chains_from_start[n].append(len(self.chains)-1)
        elif is_simple_start_node(G, n):
          self.in_chains[n] = 1
          self.chains[-1].insert(0, n)
          self.is_chain_start_simple = True
        else:
          raise RuntimeError("The node type is not found 1")

        return

  def trace_child(self, G, n):
    """
    n must be a path-through node, which will not be checked. 
    """
    while True:
      n=G.successors(n)[0]
      if is_pass_through_node(G, n):
        self.in_chains[n] = 1
        self.chains[-1].append(n)
      else:
        if is_complex_end_node(G, n) or is_branching_node(G, n):
          self.stored_chains_from_end[n].append(len(self.chains)-1)
        elif is_simple_end_node(G, n):
          self.in_chains[n] = 1
          self.chains[-1].append(n)
          if self.is_chain_start_simple:
            #UNNECESSARY: self.solo_chains.append(len(self.chains)-1)
            pass
        else:
          raise RuntimeError("The node type is not found 2")

        return

#print G.nodes(data=True)
#print G.edges(data=True)

def compress_path_digraph(G):
  """
  >>> n = 7
  >>> G = nx.path_graph(n, create_using=nx.DiGraph())
  >>> mapping = {}
  >>> for i in xrange(n):
  ...   mapping[i] = chr(ord('a')+i)
  >>> 
  >>> G=nx.relabel_nodes(G,mapping)
  >>> 
  >>> G.add_edge(1,'b')
  >>> G.add_edge(1,2)
  >>> G.add_edge(2, 'b')
  >>> G.add_edge('f', 8)
  >>> G.add_edge(8, 9)
  >>> G.add_edge('f', 9)
  >>> G.add_edge('b', 'x')
  >>> G.add_edge('x', 'y')
  >>> G.add_edge('y', 'z')
  >>> G.add_edge('z', 'f')
  >>>
  >>> G.add_node('A')
  >>> 
  >>> G.add_edge('W', 'X')
  >>> G.add_edge('X', 'Y')
  >>> G.add_edge('Y', 'Z')
  >>> 
  >>> G.add_edge('P', 'Q')
  >>> G.add_edge('Q', 'R')
  >>> G.add_edge('R', 'S')
  >>>
  >>> for v1, v2 in G.edges_iter():
  ...   G[v1][v2]['attr'] = '->'.join([str(v1), str(v2)])
  >>> 
  >>> for n in G:
  ...   G.node[n]['attr'] = n
  >>> 
  >>> PTF_G = compress_path_digraph(G)
  >>> 
  >>> for n in PTF_G.nodes(data=True):
  ...   print n
  ('a', {'attr': 'a'})
  (1, {'attr': 1})
  (2, {'attr': 2})
  ('b', {'attr': 'b'})
  ('g', {'attr': 'g'})
  ('f', {'attr': 'f'})
  (8, {'attr': 8})
  (9, {'attr': 9})
  ('c;d;e', {})
  ('x;y;z', {})
  >>> 
  >>> for e in PTF_G.edges(data=True):
  ...   print e
  ('a', 'b', {'attr': 'a->b'})
  (1, 2, {'attr': '1->2'})
  (1, 'b', {'attr': '1->b'})
  (2, 'b', {'attr': '2->b'})
  ('b', 'x;y;z', {'attr': 'b->x'})
  ('b', 'c;d;e', {'attr': 'b->c'})
  ('f', 8, {'attr': 'f->8'})
  ('f', 9, {'attr': 'f->9'})
  ('f', 'g', {'attr': 'f->g'})
  (8, 9, {'attr': '8->9'})
  ('c;d;e', 'f', {'attr': 'e->f'})
  ('x;y;z', 'f', {'attr': 'z->f'})
  """

  ptf_dag_creator = PathThroughFreeDAGCreator()
  
  ptf_dag_creator.create(G)

  #print 'stored_chains_from_start:', ptf_dag_creator.stored_chains_from_start
  #print 'stored_chains_from_end:', ptf_dag_creator.stored_chains_from_end
  #print 'chains:', ptf_dag_creator.chains
  #print 'complex_start_nodes:', ptf_dag_creator.complex_start_nodes
  #print 'branching_nodes:', ptf_dag_creator.branching_nodes
  #print 'complex_end_nodes:', ptf_dag_creator.complex_end_nodes
  #print 'solo_nodes:', ptf_dag_creator.solo_nodes
  #print 'self.solo_chains:', ptf_dag_creator.solo_chains
  
  PTF_G = nx.DiGraph()

  nodes_to_add_attributes={}
  
  for k, v in ptf_dag_creator.stored_chains_from_start.iteritems():
    PTF_G.add_node(k, G.node[k])
    for i in v:
      c = ptf_dag_creator.chains[i]
      if len(c) == 1:
        c_concat = c[0]
        nodes_to_add_attributes[c_concat] = 1
      else:
        c_concat = ';'.join([str(x) for x in c])

      #PTF_G.add_edge(k, c_concat, **G[k][c[0]])
      PTF_G.add_edge(k, c_concat, G[k][c[0]])
  
  for k, v in ptf_dag_creator.stored_chains_from_end.iteritems():
    PTF_G.add_node(k, G.node[k])
    for i in v:
      c = ptf_dag_creator.chains[i]
      if len(c) == 1:
        c_concat = c[0]
        nodes_to_add_attributes[c_concat]=1
      else:
        c_concat = ';'.join([str(x) for x in c])

      #PTF_G.add_edge(c_concat, k, **G[c[-1]][k])
      PTF_G.add_edge(c_concat, k, G[c[-1]][k])
  
  for k, v in ptf_dag_creator.complex_start_nodes.iteritems():
    PTF_G.add_node(k, G.node[k])
    for i in v:
      #PTF_G.add_edge(k, i, **G[k][i])
      PTF_G.add_edge(k, i, G[k][i])
  
  for k, v in ptf_dag_creator.branching_nodes.iteritems():
    PTF_G.add_node(k, G.node[k])
    for i in v:
      #PTF_G.add_edge(k, i, **G[k][i])
      PTF_G.add_edge(k, i, G[k][i])
  
  for v in ptf_dag_creator.complex_end_nodes:
    PTF_G.add_node(v, G.node[v])
  
#UNNECESSARY:  for v in ptf_dag_creator.solo_nodes:
#UNNECESSARY:    PTF_G.add_node(v, G.node[v])
#UNNECESSARY:
#UNNECESSARY:  for v in ptf_dag_creator.solo_chains:
#UNNECESSARY:    c = ptf_dag_creator.chains[v]
#UNNECESSARY:    if len(c) == 1:
#UNNECESSARY:      c_concat = c[0]
#UNNECESSARY:      nodes_to_add_attributes[c_concat]=1
#UNNECESSARY:    else:
#UNNECESSARY:      c_concat = ';'.join([str(x) for x in c])
#UNNECESSARY:
#UNNECESSARY:    PTF_G.add_node(c_concat)

  for n in nodes_to_add_attributes.keys():
    PTF_G.add_node(n, G.node[n])

  return PTF_G

