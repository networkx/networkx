"""
=================
Layered layout
=================

This example presents `networkx.drawing.layered_layout` node positioning algorithm, and how its output can be used with `networkx.drawing.draw` to produce good looking graphs.
"""
import networkx as nx
import matplotlib.pyplot as plt

fig, axarr = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))

G1 = nx.gn_graph(20)

pos, edges_path = nx.layered_layout(G1, align="vertical")
nx.draw(G1, pos, edges_path=edges_path, ax=axarr[0][0])
axarr[0][0].set_title("Growing Network graph, vertical")

pos, edges_path = nx.layered_layout(G1, align="horizontal")
nx.draw(G1, pos, edges_path=edges_path, ax=axarr[0][1])
axarr[0][1].set_title("Growing Network graph, horizontal")

G2 = nx.binomial_tree(4, create_using=nx.DiGraph)

pos, edges_path = nx.layered_layout(G2, align="vertical")
nx.draw(G2, pos, edges_path=edges_path, ax=axarr[1][0])
axarr[1][0].set_title("Binomial tree graph, vertical")

pos, edges_path = nx.layered_layout(G2, align="horizontal")
nx.draw(G2, pos, edges_path=edges_path, ax=axarr[1][1])
axarr[1][1].set_title("Binomial tree graph, horizontal")

plt.tight_layout()
plt.show()
