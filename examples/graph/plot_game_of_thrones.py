"""
===============
Game of Thrones
===============

This script visualizes character relationships in the
Game of Thrones Books 1 to 5. The data can be downloaded from here - 
https://www.kaggle.com/datasets/mmmarchetti/game-of-thrones-dataset

"""


import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Reading in datasets/book1.csv
book1 = pd.read_csv("book1.csv")

# Creating an empty graph object
G_book1 = nx.Graph()

# Iterating through the DataFrame to add edges
for _, edge in book1.iterrows():
    G_book1.add_edge(edge["Source"], edge["Target"], weight=edge["weight"] * 5)

# Calculate degree centrality
degree_centrality = nx.degree_centrality(G_book1)

# Set threshold for degree centrality
threshold = 0.03

# Get nodes to keep
nodes_to_keep = [n for n in G_book1.nodes() if degree_centrality[n] >= threshold]

# Create subgraph with only selected nodes
G_book1_sub = G_book1.subgraph(nodes_to_keep)

# Define node sizes and colors
node_sizes = [degree_centrality[n] * 12000 for n in G_book1_sub.nodes()]
node_colors = [
    "lightblue" if "Stark" in n else "lightgreen" if "Lannister" in n else "pink"
    for n in G_book1_sub.nodes()
]

# Define edge colors and widths
edge_colors = ["grey" for u, v, d in G_book1_sub.edges(data=True)]

# Create plot figure
fig, ax = plt.subplots(figsize=(25, 20))

# Draw nodes and edges
pos = nx.spring_layout(G_book1_sub, k=2.2)
nx.draw_networkx_nodes(
    G_book1_sub, pos, node_size=node_sizes, node_color=node_colors, alpha=0.7
)
nx.draw_networkx_edges(G_book1_sub, pos, edge_color=edge_colors)

# Add node labels
node_labels = {n: n.split(" ")[-1] for n in G_book1_sub.nodes()}
nx.draw_networkx_labels(
    G_book1_sub, pos, labels=node_labels, font_size=10, font_weight="bold"
)

# Set plot limits and remove axes
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_xticks([])
ax.set_yticks([])

# Add plot title
plt.title("Game of Thrones - Book 1", fontsize=16, fontweight="bold")

# Show plot
plt.show()
