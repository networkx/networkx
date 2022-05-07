"""
======
Triads
======
According to the paper by Snijders, T. (2012). “Transitivity and triads.” 
University of Oxford, there are 16 Triad types possible. This plot creates 
a visualization of the 16 Triad Types that can be identified within directed networks.
Triadic relationships are especially useful when analysing Social Networks. The first 
three digits refers to numbers of mutual, asymmetric and null dyads and the letter gives 
the Orientation as Up (U), Down (D) , Cycclical (C) and Transitive (T).
"""

import networkx as nx
import matplotlib.pyplot as plt

fig, axes = plt.subplots(4, 4, figsize=(10, 10))
triads = {
    "003": [],
    "012": [(1, 3)],
    "102": [(1, 3), (3, 1)],
    "021D": [(3, 1), (3, 2)],
    "021U": [(1, 3), (2, 3)],
    "021C": [(1, 3), (3, 2)],
    "111D": [(1, 2), (2, 1), (3, 2)],
    "111U": [(1, 2), (2, 1), (2, 3)],
    "030T": [(1, 2), (3, 2), (3, 1)],
    "030C": [(1, 2), (2, 3), (3, 1)],
    "201": [(1, 2), (2, 1), (3, 1), (1, 3)],
    "120D": [(1, 2), (2, 1), (3, 1), (3, 2)],
    "120U": [(1, 2), (2, 1), (1, 3), (2, 3)],
    "120C": [(1, 2), (2, 1), (1, 3), (3, 2)],
    "210": [(1, 2), (2, 1), (1, 3), (3, 2), (2, 3)],
    "300": [(1, 2), (2, 1), (2, 3), (3, 2), (1, 3), (3, 1)],
}

for (title, triad), ax in zip(triads.items(), axes.flatten()):
    G = nx.DiGraph()
    G.add_nodes_from([1, 2, 3])
    G.add_edges_from(triad)
    nx.draw_networkx(
        G,
        ax=ax,
        with_labels=False,
        font_color="white",
        node_size=300,
        font_size=10,
        arrowsize=30,
        width=3,
        pos=nx.planar_layout(G),
        font_weight="bold",
    )
    # ax.set_title(title, fontsize=15, fontweight="bold")
    ax.set_xlim((val * 1.3 for val in ax.get_xlim()))
    ax.set_ylim((val * 1.3 for val in ax.get_ylim()))
    ax.text(
        -1.2,
        0.75,
        title,
        color="black",
        fontweight="bold",
        fontsize=12,
        bbox=dict(facecolor="none", edgecolor="blue", pad=3),
    )

fig.subplots_adjust(left=3, bottom=3, right=4, top=4, wspace=0.5, hspace=0.5)
plt.show()
