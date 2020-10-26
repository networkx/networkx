"""
============
Simple graph
============

Draw simple graph with manual layout.
"""

import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edge(1, 2)
G.add_edge(1, 3)
G.add_edge(1, 5)
G.add_edge(2, 3)
G.add_edge(3, 4)
G.add_edge(4, 5)

# explicitly set positions
pos = {1: (0, 0), 2: (-0.1, 0.03), 3: (0.2, 0.017), 4: (0.4, 0.0255), 5: (0.5, 0.003)}

nx.draw_networkx(
    G,
    pos,
    font_size=36,
    node_size=3000,
    node_color="white",
    edgecolors="black",
    linewidths=5,
    width=5,
)

# Set margins for the axes so that nodes aren't clipped
ax = plt.gca()
ax.margins(0.20)
plt.axis("off")
plt.show()
