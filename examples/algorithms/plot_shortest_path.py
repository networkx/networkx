"""
==================
Find Shortest Path
==================

Finding the shortest path between 2 nodes of a given graph
using `shortest_path` function.

"""

import networkx as nx
import matplotlib.pyplot as plt

# Create a graph with nodes and edges
G = nx.Graph()
G.add_nodes_from(["A", "B", "C", "D", "E", "F", "G", "H"])
G.add_edge("A", "B", weight=4)
G.add_edge("A", "H", weight=8)
G.add_edge("B", "C", weight=8)
G.add_edge("B", "H", weight=11)
G.add_edge("C", "D", weight=7)
G.add_edge("C", "F", weight=4)
G.add_edge("C", "I", weight=2)
G.add_edge("D", "E", weight=9)
G.add_edge("D", "F", weight=14)
G.add_edge("E", "F", weight=10)
G.add_edge("F", "G", weight=2)
G.add_edge("G", "H", weight=1)
G.add_edge("G", "I", weight=6)
G.add_edge("H", "I", weight=7)

# Find the shortest path from node A to node E
path = nx.shortest_path(G, "A", "E", weight="weight")
print(path)

# Create a list of edges in the shortest path
path_edges = list(zip(path, path[1:]))

# Create a list of all edges, and assign colors based on whether they are in the shortest path or not
edge_colors = [
    "red" if edge in path_edges or tuple(reversed(edge)) in path_edges else "black"
    for edge in G.edges()
]

# Visualize the graph
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_edges(G, pos, edge_color=edge_colors)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edge_labels(
    G, pos, edge_labels={(u, v): d["weight"] for u, v, d in G.edges(data=True)}
)

plt.show()
