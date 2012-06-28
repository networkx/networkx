#!/usr/bin/env python

import networkx as nx

G = nx.DiGraph()
#G.add_edge(1, 2)
#G.add_edge(2, 3)
#G.add_edge(2, 4)
#
#G.add_edge('a', 'c')
#G.add_edge('b', 'c')
#G.add_edge('c', 'd')
#
#G.add_edge('a1', 'c1')
#G.add_edge('b1', 'c1')
#G.add_edge('c1', 'd1')
#G.add_edge('d1', 'e1')
#G.add_edge('d1', 'f1')

G.add_edge('A', 'C')
G.add_edge('B', 'C')
G.add_edge('C', 'D')
G.add_edge('C', 'E')

G.add_edge('X', 'Y')
G.add_edge('Y', 'Z')

G.add_edge('U', 'V')
G.add_edge('U', 'W')

G.add_edge('O', 'Q')
G.add_edge('P', 'Q')


for v1, v2 in G.edges_iter():
  G[v1][v2]['attr'] = '->'.join([str(v1), str(v2)])

for n in G:
  G.node[n]['attr'] = n

nx.to_pydot(G).write_png('main.png')


PTF_G = nx.algorithms.compress_path_digraph(G)

print '---------------'
for n in PTF_G.nodes(data=True):
  print n

for e in PTF_G.edges(data=True):
  print e

nx.to_pydot(PTF_G).write_png('main_ptf.png')

