#!/usr/bin/env python
"""
Draw a graph with matplotlib, color by degree.
You must have matplotlib for this to work.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

try:
    import matplotlib.pyplot as plt
except:
    raise 
import networkx as nx


G=nx.cycle_graph(12)
pos=nx.spring_layout(G)
nx.draw(G,pos,node_color=range(12),node_size=800)
plt.savefig("grid.png") # save as png
plt.show() # display
