"""
======
Triads
======
According to the paper by Snijders, T. (2012). “Transitivity and triads.” 
University of Oxford, there are 16 Triad types possible. This plot creates 
Visualisation of the 16 Triad Types that can be identified within Networks.
For Example it will be especially useful when analysing Social Networks.
"""

import networkx as nx
import matplotlib.pyplot as plt

fig, axes = plt.subplots(4, 4, figsize=(10, 10))
triads = {
    "003": [],
    "012": [(1, 2)],
    "102": [(1, 2), (2, 1)],
    "021D": [(2, 1), (2, 3)],
    "021U": [(1, 2), (3, 1)],
    "021C": [(1, 2), (2, 3)],
    "111D": [(1, 2), (2, 1), (3, 2)],
    "111U": [(1, 2), (2, 1), (2, 3)],
    "030T": [(1, 2), (3, 2), (1, 3)],
    "030C": [(2, 1), (3, 2), (1, 3)],
    "201": [(1, 2), (2, 1), (2, 3), (3, 2)],
    "120D": [(2, 1), (2, 3), (1, 3), (3, 1)],
    "120U": [(1, 2), (3, 2), (1, 3), (3, 1)],
    "120C": [(1, 2), (2, 3), (1, 3), (3, 1)],
    "210": [(1, 2), (2, 3), (3, 2), (1, 3), (3, 1)],
    "300": [(1, 2), (2, 1), (2, 3), (3, 2), (1, 3), (3, 1)],
}

for (title, triad), ax in zip(triads.items(), axes.flatten()):
    G = nx.DiGraph()
    G.add_nodes_from([1, 2, 3])
    G.add_edges_from(triad)
    nx.draw_networkx(
        G,
        ax=ax,
        with_labels=True,
        node_color="maroon",
        font_color="white",
        node_size=300,
        font_size=10,
        arrowsize=20,
        pos=nx.planar_layout(G),
        font_weight="bold",
    )
    ax.set_title(title, fontsize=15)
fig.tight_layout()
plt.show()
