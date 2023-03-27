"""
===============
Cycle Detection
===============

The cycle is a list of edges indicating the cyclic path. This script
uses the `find_cycle` function to highlight cycle present in a directed
graph.

"""


import networkx as nx
import matplotlib.pyplot as plt

# Create a simple directed graph with a cycle
G = nx.DiGraph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 2), (3, 5), (3, 2), (1, 5)])

# Draw the graph
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True)

# Find a cycle in the graph
cycle = nx.find_cycle(G, orientation="original")

# Print the cycle
print("Cycle:", cycle)

# Highlight the cycle in red
cycle_edges = [(cycle[i][0], cycle[i + 1][0]) for i in range(len(cycle) - 1)]
cycle_edges.append((cycle[-1][0], cycle[0][0]))
nx.draw_networkx_edges(G, pos, edgelist=cycle_edges, edge_color="r", width=2)

# Show the graph
plt.show()
