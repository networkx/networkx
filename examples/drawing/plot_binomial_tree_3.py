"""
================================
Labeled Binomial Tree of order 3
================================

Draw a binomial_tree(3) with matplotlib, and labeled nodes.
"""

import matplotlib.pyplot as plt
import networkx as nx

G = nx.binomial_tree(3)
nx.draw(
    G,
    pos=nx.hierarchy_layout(G, root=0),
    with_labels=True,
    node_color="white",
    edgecolors="black",
)
plt.show()
