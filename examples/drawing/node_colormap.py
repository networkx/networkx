#!/usr/bin/env python
"""
Draw a graph with matplotlib, color by degree.
You must have matplotlib for this to work.
"""
# Author: Aric Hagberg (hagberg@lanl.gov)

try:
    import matplotlib.pyplot as plt
except:
    raise
import networkx as nx


G=nx.cycle_graph(24)
pos=nx.spring_layout(G,iterations=200)
nx.draw(G,pos,node_color=range(24),node_size=800,cmap=plt.cm.Blues)
plt.savefig("node_colormap.png") # save as png
plt.show() # display
