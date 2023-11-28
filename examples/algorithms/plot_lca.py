"""
=======================
Lowest Common Ancestors
=======================

Compute and visualize LCA for node pairs

In a randomly generated directed tree, the lowest common 
ancestors are computed for certain node pairs. These node 
pairs and their LCA are then visualized with a chosen 
color scheme.

"""
import networkx as nx
import matplotlib.pyplot as plt

# Generate a random tree with its node positions
G = nx.random_tree(14, seed=100, create_using=nx.DiGraph)
pos = nx.nx_agraph.graphviz_layout(G, prog="dot")

# Compute lowest-common ancestors for certain node pairs
ancestors = list(nx.all_pairs_lowest_common_ancestor(G, ((1, 3), (4, 9), (13, 10))))

# Create node color and edge color lists
node_color_map = []
edge_color_map = []
for i in range(14):
    node_color_map.append("#D5D7D8")
    edge_color_map.append("None")
template = ["#FFE799", "#FFD23F", "#CEB6E2", "#A77CCB", "#88DFE7", "#45CDD9"]
x = 0
for i in ancestors:
    for j in i[0]:
        node_color_map[j] = template[x]
    x += 1
    node_color_map[i[1]] = template[x]
    edge_color_map[i[1]] = "black"
    x += 1

# Plot tree
plt.figure(figsize=(15, 15))
plt.title("Visualize Lowest Common Ancestors of node pairs")
nx.draw_networkx_nodes(
    G, pos, node_color=node_color_map, node_size=2000, edgecolors=edge_color_map
)
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos, font_size=15)
plt.show()
