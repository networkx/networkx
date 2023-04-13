"""
=====================
Greedy Coloring Algorithm
=====================
We attempt to color a graph using as few colors as possible, where no neighbours of a node can have same color as the node itself.The `minimum_spanning_tree`
function is used to compare the original graph with its MST.We use the function nx.greedy_color that implements the greedy coloring algorithm for a given graph.
The function returns a dictionary that maps each node to its assigned color.
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Create a new graph
G = nx.Graph()

# Add nodes
G.add_nodes_from(range(1, 21))

# Add edges
G.add_edges_from(
    [
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 7),
        (1, 8),
        (2, 3),
        (2, 9),
        (2, 10),
        (3, 4),
        (3, 10),
        (3, 11),
        (4, 5),
        (4, 11),
        (4, 12),
        (5, 6),
        (5, 13),
        (5, 14),
        (6, 7),
        (6, 14),
        (6, 15),
        (7, 8),
        (7, 15),
        (7, 16),
        (8, 9),
        (8, 16),
        (8, 17),
        (9, 10),
        (9, 18),
        (10, 11),
        (10, 18),
        (10, 19),
        (11, 12),
        (11, 20),
        (12, 13),
        (12, 20),
        (13, 14),
        (14, 15),
        (15, 16),
        (16, 17),
        (17, 18),
        (18, 19),
        (19, 20),
    ]
)

# Define the position of each node, Specify seed for reproducibility
pos = nx.spring_layout(G, seed=18)

# Apply greedy coloring
color_map = nx.greedy_color(G)

# Define warm color tones
colors = list(mcolors.TABLEAU_COLORS.values())

# Assign colors to nodes based on the greedy coloring
node_colors = [colors[color_map.get(node) % len(colors)] for node in G.nodes()]

# Draw the graph with node colors based on the greedy coloring
nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=500,
    node_color=node_colors,
    edge_color="grey",
    font_size=12,
    font_color="#333333",
    font_family="sans-serif",
    width=2,
)

# Set the title
plt.title("Greedy Coloring")

# Show the graph
plt.show()
