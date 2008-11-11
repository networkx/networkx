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
nx.draw(G,pos,node_size=2000,alpha=0.8,with_labels=False)
nx.draw(G,pos,node_size=1000,nodelist=[0,1,2,3],node_color='b') # blue
plt.savefig("house_with_colors.png") # save as png
plt.show() # display
