"""
=====================
Greedy Coloring Algorithm
=====================
We attempt to color a graph using as few colors as possible, where no neighbours of a node can have same color as the node itself.We use the function nx.greedy_color that implements the greedy coloring algorithm for a given graph.The function returns a dictionary that maps each node to its assigned color.
"""
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Create a dodecahedral graph
G = nx.generators.small.dodecahedral_graph()

# Apply greedy coloring
color_map = nx.greedy_color(G)

# Define warm color tones
colors = list(mcolors.TABLEAU_COLORS.values())

# Define the position of each node, Specify seed for reproducibility
pos = nx.spring_layout(G, seed=14)

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
    width=2,
)

# Show the graph
plt.show()
