#!/usr/bin/env python

import networkx
import time

# ubigraph server should already be running

G=networkx.UbiGraph()
G.add_node('a')
G.add_node('b')
G.add_edge('a','b','edge a-b')
G.add_edge('b','c')
G.add_edge('c','a')



