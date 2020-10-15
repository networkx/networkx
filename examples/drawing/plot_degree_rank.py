"""
===========
Degree Rank
===========

Random graph from given degree sequence.
Draw degree rank plot and graph with matplotlib.
"""
import networkx as nx
import matplotlib.pyplot as plt

G = nx.gnp_random_graph(100, 0.02)

degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
dmax = max(degree_sequence)

plt.plot(degree_sequence, "b-", marker="o")
plt.title("Degree rank plot", fontweight="bold")
plt.ylabel("degree", fontweight="bold")
plt.xlabel("rank", fontweight="bold")

# draw graph in inset
plt.axes([0.44, 0.44, 0.45, 0.45])
Gcc = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])
pos = nx.spring_layout(Gcc)
plt.axis("off")
nx.draw_networkx_nodes(Gcc, pos, node_size=20)
nx.draw_networkx_edges(Gcc, pos, alpha=0.4)
plt.show()
