"""
===============
Giant Component
===============

This example illustrates the sudden appearance of a
giant connected component in a binomial random graph.
"""

import math

import matplotlib.pyplot as plt
import networkx as nx

# This example needs Graphviz and either PyGraphviz or pydot.
# from networkx.drawing.nx_pydot import graphviz_layout as layout
# If you don't have pygraphviz or pydot, the script will fall back to
# a built-in layout
try:
    from networkx.drawing.nx_agraph import graphviz_layout as layout
except ImportError:
    layout = nx.spring_layout


n = 150  # 150 nodes
# p value at which giant component (of size log(n) nodes) is expected
p_giant = 1.0 / (n - 1)
# p value at which graph is expected to become completely connected
p_conn = math.log(n) / n

# the following range of p values should be close to the threshold
pvals = [0.003, 0.006, 0.008, 0.015]

fig, axes = plt.subplots(2, 2)
for p, ax in zip(pvals, axes.ravel()):
    G = nx.binomial_graph(n, p)
    pos = layout(G)
    ax.set_title(f"p = {p:.3f}")
    # Draw connected/disconnected nodes with different alpha values
    connected = [n for n, d in G.degree() if d > 0]
    disconnected = list(set(G.nodes()) - set(connected))
    nx.draw(G, pos, ax=ax, nodelist=connected, with_labels=False, node_size=10)
    nx.draw(G, pos, ax=ax, nodelist=disconnected, node_size=10, alpha=0.25)
    # identify largest connected component
    Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
    G0 = G.subgraph(Gcc[0])
    nx.draw_networkx_edges(G0, pos, ax=ax, edge_color="r", width=6.0)
    # show other connected components
    for Gi in Gcc[1:]:
        if len(Gi) > 1:
            nx.draw_networkx_edges(
                G.subgraph(Gi),
                pos,
                ax=ax,
                edge_color="r",
                alpha=0.3,
                width=5.0,
            )
fig.tight_layout()
plt.show()
