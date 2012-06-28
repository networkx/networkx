#!/usr/bin/env python

import networkx as nx

G = nx.Graph()
G.add_edge('a', 'b')

print list(nx.bridges(G))
