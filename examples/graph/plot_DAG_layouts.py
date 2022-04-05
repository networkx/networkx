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


fig, axes = plt.subplots(2, 4, figsize=(25, 12))
layouts = [
    nx.spring_layout(G),
    nx.circular_layout(G),
    nx.kamada_kawai_layout(G),
    nx.planar_layout(G),
    nx.random_layout(G),
    nx.shell_layout(G),
    nx.spectral_layout(G),
    nx.spiral_layout(G),
]
titles = [
    "Spring Layout - Default when given pos = None",
    "Circular Layout",
    "Kamada Kawai Layout",
    "Planar Layout",
    "Random Layout",
    "Shell Layout",
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
