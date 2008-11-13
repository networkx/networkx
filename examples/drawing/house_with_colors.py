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
# explicitly set positions
pos={0:(0,0),
     1:(1,0),
     2:(0,1),
     3:(1,1),
     4:(0.5,2.0)}

nx.draw_networkx_nodes(G,pos,node_size=2000,nodelist=[4])
nx.draw_networkx_nodes(G,pos,node_size=3000,nodelist=[0,1,2,3],node_color='b')
nx.draw_networkx_edges(G,pos,alpha=0.5,width=6)
plt.axis('off')
plt.savefig("house_with_colors.png") # save as png
plt.show() # display
