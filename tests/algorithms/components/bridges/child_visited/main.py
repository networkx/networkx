#!/usr/bin/env python

import networkx as nx

G = nx.Graph()
G.add_edge(1, 2)
G.add_edge(2, 3)
G.add_edge(3, 1)

print list(nx.bridges(G))

