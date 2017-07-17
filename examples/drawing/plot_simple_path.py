#!/usr/bin/env python
"""
===========
Simple Path
===========

Draw a graph with matplotlib.
You must have matplotlib for this to work.
"""
try:
    import matplotlib.pyplot as plt
except:
    raise

import networkx as nx

G = nx.path_graph(8)
nx.draw(G)
plt.show()
