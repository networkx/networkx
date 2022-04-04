"""
======================
DAG in Various Layouts
======================
Creates a Directed Acyclic Graph and shows the Graph in various layouts. 
This can give an idea as to which layout can be chosen for these types of datasets.
"""

import networkx as nx
import matplotlib.pyplot as plt


G = nx.DiGraph()
G.add_edges_from(
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


fig, axes = plt.subplots(3, 3, figsize=(25, 12))
layouts = [
    None,
    nx.circular_layout(G),
    nx.kamada_kawai_layout(G),
    nx.planar_layout(G),
    nx.random_layout(G),
    nx.shell_layout(G),
    nx.spring_layout(G),
    nx.spectral_layout(G),
    nx.spiral_layout(G),
]
titles = [
    "No Layout",
    "Circular Layout",
    "Kamada Kawai Layout",
    "Planar Layout",
    "Random Layout",
    "Shell Layout",
    "Spring Layout",
    "Spectral Layout",
    "Spiral Layout",
]
for layout, title, ax in zip(layouts, titles, axes.flatten()):
    pos = layout
    nx.draw_networkx(
        G,
        ax=ax,
        with_labels=True,
        node_color="maroon",
        font_color="white",
        node_size=500,
        font_size=14,
        pos=pos,
    )
    ax.set_title(title)
plt.show()
