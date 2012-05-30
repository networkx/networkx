#!/usr/bin/env python

import networkx as nx

G = nx.Graph()
G.add_edge('a', 'b')
G.add_edge('b', 'c')
G.add_edge('a', 'c')
G.add_edge('c', 'd')
G.add_edge('d', 'e')
G.add_edge('d', 'f')
G.add_edge('e', 'f')

print list(nx.bridges(G))

