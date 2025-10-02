"""
==============
Metric Closure
==============

The *metric closure* of a graph is the complete graph in which
each edge weight corresponds to the shortest-path distance
between two nodes in the original graph.

This example demonstrates the *unweighted* version of the metric closure,
constructed using :func:`networkx.all_pairs_shortest_path_length`.
Here, each edge is assumed to have weight 1, so distances correspond to
the minimum number of hops between nodes.

For weighted graphs, the metric closure can be obtained instead with
:func:`networkx.all_pairs_dijkstra_path_length`, which computes distances
using the minimum total edge weights along paths.
"""

import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint

# Creating five nodes from index 0 to 4
G = nx.house_graph()

# Find the all-pairs shortest distance
# all_pairs_shortest_path_length returns a one-time generator,
# so wrap with dict() to materialize results for reuse.
paths = dict(nx.all_pairs_shortest_path_length(G))

# Dictionary format: u: {v: d}, meaning "distance d from node u to node v"
pprint(paths)

# Metric closure of G
M = nx.Graph()
for u, dist_dict in paths.items():
    for v, d in dist_dict.items():
        if u != v:  # avoid self-loops
            M.add_edge(u, v, distance=d)
# Visualize the G and metric closure of G
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

pos = nx.circular_layout(G)
nx.draw(G, pos, with_labels=True, ax=axes[0])
nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels={(u, v): 1 for u, v, d in G.edges(data=True)},
    ax=axes[0],
)
axes[0].set_title("Original Graph")

pos_mc = nx.circular_layout(M)
nx.draw(M, pos_mc, with_labels=True, ax=axes[1])
nx.draw_networkx_edge_labels(
    M,
    pos,
    edge_labels={(u, v): d for u, v, d in M.edges(data="distance")},
    ax=axes[1],
)
axes[1].set_title("Metric Closure of Original Graph")

plt.show()
