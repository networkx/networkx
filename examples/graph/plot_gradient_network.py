"""
================
Gradient Network
================

Demonstrate static and dynamic gradient networks on graphs.

A gradient network directs edges of an undirected substrate graph along the steepest
ascent of a scalar potential field defined on the nodes.

This example illustrates:
1. Constructing a static gradient network on a 2D grid graph with an elevation potential field.
2. Generating a time-evolving gradient network sequence with a traveling potential wave.
"""

import matplotlib.pyplot as plt
import networkx as nx

# %%
# Static Gradient Network
# -----------------------
# First, create a 2D grid graph representing a spatial terrain.
# Assign an elevation potential to each node where the peak is near the center.

m, n = 4, 4
G = nx.grid_2d_graph(m, n)

# Set node positions for visualization
pos = {node: (node[0], node[1]) for node in G.nodes()}

# Assign scalar field values (elevation) to nodes: peak at (1.5, 1.5)
for x, y in G.nodes():
    G.nodes[(x, y)]["elevation"] = -((x - 1.5) ** 2 + (y - 1.5) ** 2)

# Generate directed gradient network pointing towards steepest ascent
H = nx.gradient_network(G, scalar_field_value="elevation")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")

# Subplot 1: Substrate graph with scalar field potential
node_potentials = [G.nodes[node]["elevation"] for node in G.nodes()]
nx.draw_networkx_edges(G, pos=pos, ax=ax1, edge_color="lightgray", width=1.5)
nodes1 = nx.draw_networkx_nodes(
    G, pos=pos, ax=ax1, node_color=node_potentials, cmap=plt.cm.viridis, node_size=500
)
nx.draw_networkx_labels(G, pos=pos, ax=ax1, font_color="white", font_size=8)
ax1.set_title("Substrate Graph & Potential Field")
ax1.axis("off")
fig.colorbar(nodes1, ax=ax1, label="Elevation Potential", shrink=0.8)

# Subplot 2: Resulting directed gradient network
in_degrees = dict(H.in_degree())
node_sizes = [300 + 150 * in_degrees[node] for node in H.nodes()]
nx.draw_networkx_edges(
    H,
    pos=pos,
    ax=ax2,
    edge_color="steelblue",
    arrows=True,
    arrowstyle="-|>",
    arrowsize=16,
    width=2.0,
    connectionstyle="arc3,rad=0.05",
)
nx.draw_networkx_nodes(
    H,
    pos=pos,
    ax=ax2,
    node_color=node_potentials,
    cmap=plt.cm.viridis,
    node_size=node_sizes,
)
nx.draw_networkx_labels(H, pos=pos, ax=ax2, font_color="white", font_size=8)
ax2.set_title("Gradient Network (Flow toward Peak)")
ax2.axis("off")

plt.show()

# %%
# Dynamic Gradient Network Sequence
# ---------------------------------
# When scalar fields evolve over time (e.g. traveling waves, shifting congestion,
# or dynamic signals), `gradient_network_sequence` yields directed graph snapshots
# at specified time points.

P = nx.path_graph(6)
pos_path = {i: (i, 0) for i in P.nodes()}
times = [0, 2, 4]


def wave_potential(node, t):
    # Gaussian wave packet traveling along the path graph over time
    return -((node - t) ** 2)


fig, axes = plt.subplots(len(times), 1, figsize=(8, 6), layout="constrained")

for ax, (t, H_t) in zip(
    axes,
    nx.gradient_network_sequence(P, times=times, scalar_field_value=wave_potential),
):
    node_vals = [wave_potential(n, t) for n in P.nodes()]
    nx.draw_networkx_edges(
        H_t,
        pos=pos_path,
        ax=ax,
        edge_color="crimson",
        arrows=True,
        arrowstyle="-|>",
        arrowsize=18,
        width=2.0,
        connectionstyle="arc3,rad=0.15",
    )
    nodes_t = nx.draw_networkx_nodes(
        H_t,
        pos=pos_path,
        ax=ax,
        node_color=node_vals,
        cmap=plt.cm.coolwarm,
        node_size=600,
    )
    nx.draw_networkx_labels(H_t, pos=pos_path, ax=ax, font_size=9)
    ax.set_title(f"Gradient Network Snapshot at t = {t} (Peak at node {t})")
    ax.axis("off")
    ax.margins(0.15)

fig.colorbar(
    nodes_t, ax=axes, orientation="horizontal", label="Scalar Potential", shrink=0.5
)
plt.show()
