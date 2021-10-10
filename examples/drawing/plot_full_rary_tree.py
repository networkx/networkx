"""
==========================================
Full binary tree of depth 6 with 127 nodes
==========================================

Draw a full binary tree with 6 levels, having 127 nodes.

This example shows how to adjust node size using the minimum-separation
between nodes.
"""

import matplotlib.pyplot as plt
import networkx as nx

G = nx.full_rary_tree(2, 127)
pos, min_sep = nx.hierarchy_layout_with_min_sep(G, root=0)
nx.draw(G, pos=pos, node_size=min_sep * 1500)
plt.show()
