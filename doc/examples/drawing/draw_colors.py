#!/usr/bin/env python
"""
Draw a graph with matplotlib.
You must have matplotlib for this to work.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
try:
    import matplotlib.pyplot as plt
except:
    raise
    
import networkx as nx

G=nx.house_graph()
pos=nx.spring_layout(G)
nx.draw(G,pos,alpha=0.5,with_labels=False)
nx.draw(G,pos,nodelist=[0,1,2,3],node_color='b') # blue
plt.savefig("grid.png") # save as png
plt.show() # display
