"""Algorithm for compressing redundant edges in a directed graph."""

import networkx as nx
from collections import defaultdict

__author__ = "Peng Yu (pengyu.ut@gmail.com)"

__all__ = ['compress_path_digraph']

def is_upstream_deadend(G, n):
  return G.in_degree(n) == 0

def is_upstream_nonbranching(G, n):
  return G.in_degree(n) == 1

def is_upstream_branching(G, n):
  return G.in_degree(n) > 1

def is_dnstream_deadend(G, n):
  return G.out_degree(n) == 0

def is_dnstream_nonbranching(G, n):
  return G.out_degree(n) == 1

def is_dnstream_branching(G, n):
  return G.out_degree(n) > 1

def is_both_branching(G, n):
  return is_upstream_branching(G, n) and is_dnstream_branching(G, n)

class PathThroughFreeDAGCreator:
  def __init__(self):
    self.in_chains = {}
    #self.exclusive_upstream_node_to_chain_set = defaultdict(list)
    #self.exclusive_dnstream_node_to_chain_set = defaultdict(list)
    self.inclusive_node_to_chain_set = {}
    self.solo_chains = []
    self.dnstream_edges =  defaultdict(list)

  def create(self, G):
    for n in G:
      if not n in self.in_chains:
        #print '====', n 
        self.trace_chain(G, n)
        #print '  inclusive_node_to_chain_set:', self.inclusive_node_to_chain_set
        #print '  in_chains:', self.in_chains.keys()
        #print '  solo_chains:', self.solo_chains
        #print '  dnstream_edges:', self.dnstream_edges

  def trace_chain(self, G, n):

    if is_both_branching(G, n):
      for i in G.successors(n):
        self.dnstream_edges[n].append(i)
        self.inclusive_node_to_chain_set[n] = [n]
        self.in_chains[n] = 1
      return

    chain = [n]
    self.in_chains[n] = 1

    upstream_is_deadend = False
    dnstream_is_deadend = False

    if is_upstream_deadend(G, n):
      upstream_is_deadend = True
    elif is_upstream_nonbranching(G, n):
      v = G.predecessors(n)[0]
      while True:
        if is_dnstream_branching(G, v):
          self.inclusive_node_to_chain_set[chain[0]] = chain
          break
        else:
          if is_upstream_deadend(G, v):
            upstream_is_deadend = True
            chain.insert(0, v)
            self.in_chains[v] = 1
            break
          elif is_upstream_nonbranching(G, v):
            chain.insert(0, v)
            self.in_chains[v] = 1
            v = G.predecessors(v)[0]
          else: # is_upstream_branching(G, v):
            chain.insert(0, v)
            self.in_chains[v] = 1
            self.inclusive_node_to_chain_set[v] = chain
            break
    else: #is_upstream_branching(G, n)
      self.inclusive_node_to_chain_set[n] = chain


    if is_dnstream_deadend(G, n):
      dnstream_is_deadend = True
    elif is_dnstream_nonbranching(G, n):
      v = G.successors(n)[0]
      while True:
        if is_upstream_branching(G, v):
          self.dnstream_edges[chain[-1]].append(v)
          if not chain[-1] in self.inclusive_node_to_chain_set:
            self.inclusive_node_to_chain_set[chain[-1]] = chain
          break
        else:
          if is_dnstream_deadend(G, v):
            dnstream_is_deadend = True
            chain.append(v)
            self.in_chains[v] = 1
            break
          elif is_dnstream_nonbranching(G, v):
            chain.append(v)
            self.in_chains[v] = 1
            v = G.successors(v)[0]
          else: # is_dnstream_branching(G, v):
            chain.append(v)
            self.in_chains[v] = 1
            self.inclusive_node_to_chain_set[v] = chain

            for i in G.successors(v):
              self.dnstream_edges[v].append(i)
            break
    else: #is_dnstream_branching(G, n)
      self.inclusive_node_to_chain_set[n] = chain
      for v in G.successors(n):
        self.dnstream_edges[n].append(v)


    if upstream_is_deadend and dnstream_is_deadend:
      self.solo_chains.append(chain)

def compress_path_digraph(G):
  """
  This algorithm determines the nonbranching edges in a directed graph and consolidate each set of the adjacent nonbranching and nonterminal nodes to a single node.
  
  For example, C and D are adjacent nonbranching nodes in the following digraph::
  
         1
         |
         V 
      A->B->C->D->E->F
                  ^
                  |
                  2
  
  Therefore, we can consolidate C and D into a single node C,D, and we get the following path-compressed digraph::
  
         1
         |
         V 
      A->B->C;D->E->F
                 ^
                 |
                 2
  
  For a given digraph (called G), constructed a path-compressed digraph.
  
  Pick an *unvisited* node in the DAG

  1. If it is a out-non-branching node,
    * trace all its child, grandchild, etc., until one of the following two conditions satisfies:

      * an in-branching node is reached

        * push all the nodes visited to the back of `chain` (excluding the last node)

      * an out-branching node is reached.

        * push all the nodes visited to the back of chain (including the last node)

  2. If it is a in-non-branching node,
    * trace all its parent, grandparent, etc., until one of the following two conditions satisfies:

      * an out-branching node is reached

        * push all the nodes visited to the front of `chain` (excluding the last node)

      * an in-branching node is reached

        * push all the nodes visited to the front of `chain` (including the last node)

  3. Collapse all the nodes in chain.

  Do the above procedure until all the nodes have been visited.
  
  Assumption: node names are not consist of ';'. Therefore, the new chain name is the concatenation of the original node names, separated by ';'.

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
  ('c;d;e', {})
  (8, {'attr': 8})
  (9, {'attr': 9})
  ('f', {'attr': 'f'})
  ('x;y;z', {})
  ('P;Q;R;S', {})
  ('A', {'attr': 'A'})
  ('W;X;Y;Z', {})
  >>> 
  >>> for e in PTF_G.edges(data=True):
  ...   print e
  ('a', 'b', {'attr': 'a->b'})
  (1, 2, {'attr': '1->2'})
  (1, 'b', {'attr': '1->b'})
  (2, 'b', {'attr': '2->b'})
  ('b', 'x;y;z', {'attr': 'b->x'})
  ('b', 'c;d;e', {'attr': 'b->c'})
  ('c;d;e', 'f', {'attr': 'e->f'})
  (8, 9, {'attr': '8->9'})
  ('f', 8, {'attr': 'f->8'})
  ('f', 9, {'attr': 'f->9'})
  ('f', 'g', {'attr': 'f->g'})
  ('x;y;z', 'f', {'attr': 'z->f'})
  """

  ptf_dag_creator = PathThroughFreeDAGCreator()
  
  ptf_dag_creator.create(G)

  #print 'inclusive_node_to_chain_set:', ptf_dag_creator.inclusive_node_to_chain_set
  #print 'in_chains:', ptf_dag_creator.in_chains.keys()
  #print 'solo_chains:', ptf_dag_creator.solo_chains
  #print 'dnstream_edges:', ptf_dag_creator.dnstream_edges

  PTF_G = nx.DiGraph()

  nodes_to_add_attributes={}
  
  for k, v in ptf_dag_creator.dnstream_edges.iteritems():
    node_chain = ptf_dag_creator.inclusive_node_to_chain_set[k]
    if len(node_chain) == 1:
      node_concat = node_chain[0]
      nodes_to_add_attributes[node_concat]=1
    else:
      node_concat = ';'.join([str(x) for x in node_chain])

    PTF_G.add_node(node_concat)

    for i in v:
      c = ptf_dag_creator.inclusive_node_to_chain_set[i]
      if len(c) == 1:
        c_concat = c[0]
        nodes_to_add_attributes[c_concat] = 1
      else:
        c_concat = ';'.join([str(x) for x in c])

      PTF_G.add_edge(node_concat, c_concat, G[k][c[0]])
  
  for c in ptf_dag_creator.solo_chains:
    if len(c) == 1:
      c_concat = c[0]
      nodes_to_add_attributes[c_concat]=1
    else:
      c_concat = ';'.join([str(x) for x in c])
  
    PTF_G.add_node(c_concat)

  for n in nodes_to_add_attributes.keys():
    PTF_G.add_node(n, G.node[n])

  return PTF_G

