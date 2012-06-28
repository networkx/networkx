#!/usr/bin/env python

import networkx as nx

G = nx.DiGraph()
G.add_edge(1, 2)
G.add_edge(2, 3)
G.add_edge(1, 3)

for v1, v2 in G.edges_iter():
  G[v1][v2]['attr'] = '->'.join([str(v1), str(v2)])

for n in G:
  G.node[n]['attr'] = n

PTF_G = nx.algorithms.compress_path_digraph(G)

for n in PTF_G.nodes(data=True):
  print n

print '---------------'

for e in PTF_G.edges(data=True):
  print e

nx.to_pydot(G).write_png('main.png')
nx.to_pydot(PTF_G).write_png('main_ptf.png')

