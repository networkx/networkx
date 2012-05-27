#!/usr/bin/env python

import networkx as nx

n = 7
G = nx.path_graph(n, create_using=nx.DiGraph())
mapping = {}
for i in xrange(n):
  mapping[i] = chr(ord('a')+i)

G=nx.relabel_nodes(G,mapping)

G.add_edge(1, 'b')
G.add_edge('f', 8)

G.add_edge(1, 2)
G.add_edge(2, 'b')

G.add_edge(8, 9)
G.add_edge('f', 9)
G.add_edge('b', 'x')
G.add_edge('x', 'y')
G.add_edge('y', 'z')
G.add_edge('z', 'f')

##G = nx.DiGraph()
G.add_node('A')

G.add_edge('W', 'X')
G.add_edge('X', 'Y')
G.add_edge('Y', 'Z')

G.add_edge('P', 'Q')
G.add_edge('Q', 'R')
G.add_edge('R', 'S')

for v1, v2 in G.edges_iter():
  G[v1][v2]['attr'] = '->'.join([str(v1), str(v2)])

for n in G:
  G.node[n]['attr'] = n

nx.to_pydot(G).write_png('main.png')

PTF_G = nx.algorithms.compress_path_digraph(G)

for n in PTF_G.nodes(data=True):
  print n

print '---------------'

for e in PTF_G.edges(data=True):
  print e

nx.to_pydot(PTF_G).write_png('main_ptf.png')

