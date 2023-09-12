"""
================
Visibility Graph
================

Visibility Graph constructed from a time series
"""
from matplotlib import pyplot as plt

import networkx as nx

time_series = [0, 2, 1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 3, 4, 0]
# or
# import random
# time_series = [random.randint(1,10) for i in range(10)]

G = nx.visibility_graph(time_series)

labels = nx.get_node_attributes(G, "value")

fig, all_axes = plt.subplots(2, 1, num="Visibility Graph", figsize=(8, 12))
ax = all_axes.flat

ax[0].title.set_text("Line-of-Sight Connectivity")
ax[0].title.set_size(11)

ax[0].set_xlabel("Time", size=10)

ax[1].title.set_text(
    "Time Series values with Connectivity",
)
ax[1].title.set_size(11)
ax[1].set_xlabel("Time", size=10)
ax[1].set_ylabel("Value", size=10)

# a plot layout emphasizing the line-of-sight connectivity
pos = {x: (x, 0) for x in range(len(time_series))}
nx.draw_networkx_nodes(G, pos, ax=ax[0], alpha=0.5)
nx.draw_networkx_labels(G, pos, ax=ax[0], labels=labels)
nx.draw_networkx_edges(
    G,
    pos,
    ax=ax[0],
    arrows=True,
    arrowstyle="<->",
    arrowsize=10,
    connectionstyle="arc3,rad=-1.57079632679",
)

# a plot layout showcasing the time series values
pos = {i: (i, v) for i, v in enumerate(time_series)}
nx.draw_networkx_nodes(G, pos, ax=ax[1], alpha=0.5)
nx.draw_networkx_labels(G, pos, ax=ax[1], labels=labels)
nx.draw_networkx_edges(G, pos, ax=ax[1], arrows=True, arrowstyle="<->", arrowsize=10)

for a in ax:
    a.margins(0.10)
fig.suptitle("Visibility Graph")
fig.tight_layout()
plt.show()
