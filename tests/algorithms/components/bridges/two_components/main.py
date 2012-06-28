#!/usr/bin/env python

import networkx as nx

G = nx.Graph()
G.add_edge(1,2)
G.add_edge(3,4)

print list(nx.bridges(G))
