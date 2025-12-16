"""
Basic example of Breadth-First Search (BFS) using NetworkX.
"""

import networkx as nx

# Create a simple graph
G = nx.Graph()
G.add_edges_from([
    (1, 2),
    (1, 3),
    (2, 4),
    (3, 5),
])

# Perform BFS starting from node 1
bfs_nodes = list(nx.bfs_tree(G, source=1))

print("BFS traversal order:", bfs_nodes)
