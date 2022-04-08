"""
======================
DAG in Various Layouts
======================
Creates a Directed Acyclic Graph and shows the Graph in various layouts. 
This can give an idea as to which layout can be chosen for these types of datasets.
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


fig, axes = plt.subplots(2, 4, figsize=(25, 12))
lay = {
    "Spring Layout - Default when given pos = None": nx.spring_layout,
    "Circular Layout": nx.circular_layout,
    "Kamada Kawai Layout": nx.kamada_kawai_layout,
    "Planar Layout": nx.planar_layout,
    "Random Layout": nx.random_layout,
    "Shell Layout": nx.shell_layout,
    "Spectral Layout": nx.spectral_layout,
    "Spiral Layout": nx.spiral_layout,
}

for (title, layout), ax in zip(lay.items(), axes.flatten()):
    pos = layout(G)
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
