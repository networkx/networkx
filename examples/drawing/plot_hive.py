"""===============
Hive plot
===============

This  example shows  how to  visualize a  network with  hive
layout. A  hive layout  can be  used to  visualize clustered
data.  The layout  visualizes a  graph along  different axes
representing the different groups.

"""
import matplotlib.pyplot as plt, numpy as np, networkx as nx

fig, ax = plt.subplots(ncols=2, nrows=2)
for axi, n in zip(ax.flatten(), range(4, 8)):
    G = nx.complete_multipartite_graph(*[5 for _ in range(n)])
    pos = nx.arc_layout(G, subset_key="subset", radius=10, offset=3)

    color_vals = np.linspace(0, 1, n, 0)
    colors = plt.cm.tab20c(color_vals)
    nc = [colors[G.nodes[node]["subset"]] for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, ax=axi, node_size=32, node_color=nc)
    nx.draw_networkx_edges(
        G, pos, ax=axi, alpha=0.05, connectionstyle="arc3,rad=0.3", arrows=True
    )
    axi.grid(False)
    axi.set_title(f"{n}-group multipartite")
plt.show(block=1)
