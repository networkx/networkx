#!/usr/bin/env python

import networkx as nx

G = nx.DiGraph()

#G.add_edge('b', 'c')
#G.add_edge('c', 'e')
G.add_edge('b', 'e')
G.add_edge('e', 'f')

G.add_edge('b', 'x')
G.add_edge('x', 'y')
G.add_edge('y', 'f')

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

