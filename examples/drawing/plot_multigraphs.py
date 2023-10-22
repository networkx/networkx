"""
======================================
Plotting MultiDiGraph Edges and Labels
======================================

This example shows how to plot edges and labels for a MultiDiGraph class object.
The same applies for DiGraph and MultiGraph class objects.
"""
import itertools as it
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def draw_labeled_multigraph(G, attr_name, ax=None):
    """
    Length of connectionstyle must be at least that of a maximum number of edges
    between pair of nodes. This number is maximum one-sided connections
    for directed graph and maximum total connections for undirected graph.
    """
    connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.15] * 4)]

    pos = nx.shell_layout(G)
    nx.draw_networkx_nodes(G, pos, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=20, ax=ax)
    nx.draw_networkx_edges(G, pos, connectionstyle=connectionstyle, ax=ax)

    labels = {
        tuple(edge): f"{attr_name}={attrs[attr_name]}"
        for *edge, attrs in G.edges(keys=True, data=True)
    }
    nx.draw_networkx_edge_labels(
        G,
        pos,
        labels,
        connectionstyle=connectionstyle,
        label_pos=0.3,
        bbox={"alpha": 0},
        ax=ax,
    )


nodes = "ABC"
pair_dict = {
    "Combinations": list(it.combinations(nodes, 2)),
    "Permutations": list(it.permutations(nodes, 2)),
    "Product": list(it.product(nodes, repeat=2)),
}
pair_dict["Product x 2"] = pair_dict["Product"] * 2


fig, axes = plt.subplots(2, 2)
for (name, pairs), ax in zip(pair_dict.items(), np.ravel(axes)):
    G = nx.MultiDiGraph()
    for i, (u, v) in enumerate(pairs):
        G.add_edge(u, v, weight=round(i / 3, 2))
    draw_labeled_multigraph(G, "weight", ax)
    ax.set_title(name)
fig.tight_layout()
plt.show()
