"""
Visualise a graph given an explicit edge list.
"""

import networkx as nx
import matplotlib.pyplot as plt

# ── 1) hard-coded edges ──────────────────────────────────────────────────────
edges = [
    (0, 5), (1, 15), (1, 25), (2, 6), (2, 8), (3, 4), (3, 13), (3, 28),
    (3, 29), (4, 5), (4, 12), (4, 13), (4, 14), (4, 28), (5, 9), (5, 12),
    (5, 23), (6, 20), (6, 25), (6, 26), (7, 13), (7, 18), (7, 28), (8, 11),
    (8, 12), (8, 29), (9, 11), (9, 27), (10, 15), (10, 20), (10, 21),
    (11, 16), (11, 18), (11, 20), (11, 28), (12, 14), (12, 16), (12, 17),
    (12, 20), (12, 28), (13, 18), (13, 23), (13, 29), (14, 22), (14, 25),
    (15, 28), (16, 26), (16, 29), (17, 28), (18, 27), (19, 21), (19, 29),
    (21, 28)
]

# ── 2) build the graph ───────────────────────────────────────────────────────
G = nx.Graph()
G.add_edges_from(edges)

# ── 3) choose a layout & draw ────────────────────────────────────────────────
pos = nx.spring_layout(G, seed=42)        # layout: Fruchterman-Reingold
plt.figure(figsize=(8, 6))
nx.draw_networkx_nodes(G, pos, node_size=300, node_color="lightsteelblue")
nx.draw_networkx_edges(G, pos, width=1.2)
nx.draw_networkx_labels(G, pos, font_size=8)

plt.axis("off")
plt.tight_layout()
plt.savefig("graph_visualisation.png", dpi=300)
plt.show()

print("Saved figure as graph_visualisation.png")