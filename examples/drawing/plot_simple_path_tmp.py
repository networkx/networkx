"""
===============
Simple Path TMP
===============

Draw a graph with matplotlib.
"""
import matplotlib.pyplot as plt
import networkx as nx

G = nx.path_graph(9)
pos = nx.spring_layout(G, seed=47)  # Seed layout for reproducibility
nx.draw(G, pos=pos)
plt.show()
