"""
========================
DAG - Topological Layout
========================

This example combines the `topological_generations` generator with
`multipartite_layout` to show how to visualize a DAG in topologically-sorted
order.
"""

import networkx as nx
import matplotlib.pyplot as plt


G = nx.DiGraph(
    [
        ("f", "a"),
        ("a", "b"),
        ("a", "e"),
        ("b", "c"),
        ("b", "d"),
        ("d", "e"),
        ("f", "c"),
        ("f", "g"),
        ("h", "f"),
    ]
)

# Layout the nodes according to their topological generation
layers = dict(enumerate(nx.topological_generations(G)))
pos = nx.multipartite_layout(G, subset_key=layers)

fig, ax = plt.subplots()
nx.draw(G, pos=pos, ax=ax, with_labels=True)
ax.set_title("DAG layout in topological order")
fig.tight_layout()
plt.show()
