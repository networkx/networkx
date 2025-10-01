"""
==============
Metric Closure
==============

The *metric closure* of a graph is the complete graph in which
each edge weight corresponds to the shortest-path distance
between two nodes in the original graph.

This example implements the *metric closure* of a given graph using
:func:`networkx.all_pairs_dijkstra_path_length`.
"""

import networkx as nx
import matplotlib.pyplot as plt

# Creating five nodes from index 0 to 4
G = nx.Graph()
G.add_nodes_from(range(5))
G.add_edge(0, 1, weight=6)
G.add_edge(0, 4, weight=3)
G.add_edge(1, 3, weight=12)
G.add_edge(1, 5, weight=5)
G.add_edge(2, 3, weight=8)
G.add_edge(2, 4, weight=10)
G.add_edge(2, 5, weight=9)
G.add_edge(3, 4, weight=2)
G.add_edge(3, 5, weight=3)
G.add_edge(4, 5, weight=7)

# Find the all-pairs shortest distance(weight)
# all_pairs_dijkstra_path_length returns a one-time generator,
# so wrap with dict() to materialize results for reuse.
paths = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))
for u, dist_dict in paths.items():
    print(f"Weighted shortest path distances from node {u}: {dist_dict}")

# Metric closure of G
M = nx.Graph()
for u, dist_dict in paths.items():
    for v, d in dist_dict.items():
        if u != v:  # avoid self-loops
            M.add_edge(u, v, weight=d)
# Visualize the G and metric closure of G
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

pos = nx.spring_layout(G, seed=2210)
nx.draw(G, pos, with_labels=True, ax=axes[0])
nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels={(u, v): d["weight"] for u, v, d in G.edges(data=True)},
    ax=axes[0],
)
axes[0].set_title("Original Graph")

pos_mc = nx.spring_layout(M, seed=2210)
nx.draw(M, pos_mc, with_labels=True, ax=axes[1])
nx.draw_networkx_edge_labels(
    M,
    pos,
    edge_labels={(u, v): d["weight"] for u, v, d in M.edges(data=True)},
    ax=axes[1],
)
axes[1].set_title("Metric Closure of Origin Graph")

plt.show()
