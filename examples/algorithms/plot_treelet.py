"""
========
Treelets
========
This example illustrates the extraction and visualization of treelets in a
graph, as well as the extraction of distributions of both unlabeled and labeled
treelets.

Treelets represent bounded-size (up to 6 nodes) acyclic subgraphs extracted
from a graph. They are used in various contexts, such as graph kernels in
chemoinformatics (see B. Gaüzère, L. Brun, D. Villemin (2012) `"Two new graphs
kernels in chemoinformatics" <https://hal.science/hal-00773283/document>`_.
"""

from math import sqrt, cos, sin, pi
import matplotlib.pyplot as plt
import networkx as nx

###############################################################################
# List of all treelets (for understanding only – not to be reproduced)
# ---------------------------------------------------------------------
#
# In accordance with `Gaüzère et al. (2012) <https://hal.science/hal-00773283/
# document>`_, the complete set of acyclic graphs (treelets) with up to
# 6 vertices is known to consist of 14 distinct patterns. These patterns are
# denoted by :math:`G_0` to :math:`G_{13}`.
#
# Treelets :math:`G_0` to :math:`G_5` correspond to simple path structures.
# In these cases, the treelet is associated with one of the endpoints of the
# path (in the undirected case) or with the source endpoint (in the directed
# case).
#
# The remaining treelets (:math:`G_6` to :math:`G_{13}`) are star-based
# treelets. For these treelets, the red nodes in the visualization indicate
# the center of the star pattern; that is, the treelet is associated with that
# central node. In the special case of labeled treelet :math:`G_{12}`, which
# has two candidate central nodes, the canonical key (see the section
# *Labeled Treelets*) chosen is the smallest between the two, ensuring a
# unique representation for the treelet.


# Function to draw treelets
def plot_treelet(ax, G, title, pos):
    """Draws the treelet G on the axis 'ax' using the positions 'pos'."""
    # List of colors: all star-center nodes are red
    if title in ["G_" + str(i) for i in range(6)]:
        red_nodes = []
    elif title == "G_12":
        red_nodes = [0, 3]
    else:
        red_nodes = [0]
    node_colors = ["red" if node in red_nodes else "black" for node in G.nodes()]

    # Draw the graph with manual positions
    nx.draw(
        G,
        pos,
        ax=ax,
        node_color=node_colors,
        font_weight="bold",
        node_size=500,
        font_size=12,
    )
    title = "$G_{" + title.removeprefix("G_") + "}$" if title != "" else ""
    ax.set_title(title, fontsize=32)
    ax.axis("equal")


# Definition of manual positions for each graph
sq = sqrt(3) / 2
positions = {
    "G_0": {0: (0, 0)},
    "G_1": {0: (0, 0), 1: (1, 0)},
    "G_2": {0: (0, 0), 1: (1, 0), 2: (2, 0)},
    "G_3": {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0)},
    "G_4": {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0), 4: (4, 0)},
    "G_5": {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0), 4: (4, 0), 5: (5, 0)},
    "G_6": {0: (0, 0), 1: (1, 0), 2: (-0.5, sq), 3: (-0.5, -sq)},
    "G_7": {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (-0.5, sq), 4: (-0.5, -sq)},
    "G_8": {0: (0, 0), 1: (-1, 0), 2: (0, -1), 3: (1, 0), 4: (0, 1)},
    "G_9": {0: (0, 0), 1: (-1, 0), 2: (-2, 0), 3: (1, 0), 4: (0, 1), 5: (2, 0)},
    "G_10": {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0), 4: (-0.5, sq), 5: (-0.5, -sq)},
    "G_11": {0: (0, 0), 1: (0, -1), 2: (1, 0), 3: (0, 1), 4: (-1, 0), 5: (2, 0)},
    "G_12": {
        0: (0, 0),
        1: (-0.5, sq),
        2: (-0.5, -sq),
        3: (1, 0),
        4: (1.5, sq),
        5: (1.5, -sq),
    },
    "G_13": {
        0: (0, 0),
        1: (1, 0),
        2: (cos(2 * pi / 5), sin(2 * pi / 5)),
        3: (cos(4 * pi / 5), sin(4 * pi / 5)),
        4: (cos(6 * pi / 5), sin(6 * pi / 5)),
        5: (cos(8 * pi / 5), sin(8 * pi / 5)),
    },
}

# Creation of graphs
G_0 = nx.path_graph(1)
G_1 = nx.path_graph(2)
G_2 = nx.path_graph(3)
G_3 = nx.path_graph(4)
G_4 = nx.path_graph(5)
G_5 = nx.path_graph(6)
G_6 = nx.star_graph(3)
G_7 = nx.Graph()
G_7.add_edges_from([(0, 1), (1, 2), (0, 3), (0, 4)])
G_8 = nx.star_graph(4)
G_9 = nx.Graph()
G_9.add_edges_from([(0, 1), (1, 2), (0, 3), (0, 4), (3, 5)])
G_10 = nx.Graph()
G_10.add_edges_from([(0, 1), (1, 2), (2, 3), (0, 4), (0, 5)])
G_11 = nx.Graph()
G_11.add_edges_from([(1, 0), (0, 2), (0, 3), (0, 4), (2, 5)])
G_12 = nx.Graph()
G_12.add_edges_from([(1, 0), (0, 2), (3, 4), (3, 5), (0, 3)])
G_13 = nx.star_graph(5)

# List of graphs and their titles
graphs = [
    (G_0, "G_0"),
    (G_1, "G_1"),
    (G_2, "G_2"),
    (G_3, "G_3"),
    (G_4, "G_4"),
    (G_5, "G_5"),
    (G_6, "G_6"),
    (G_7, "G_7"),
    (G_8, "G_8"),
    (G_9, "G_9"),
    (G_10, "G_10"),
    (G_11, "G_11"),
    (G_12, "G_12"),
    (G_13, "G_13"),
]

# For each graph and its title, draw it on a subplot with its manual positions
fig, axes = plt.subplots(4, 4, figsize=(15, 15))
for i, (G, title) in enumerate(graphs):
    row, col = divmod(i, 4)
    ax = axes[row, col]

    if title == "G_12":
        ax = axes[3, 1]
    elif title == "G_13":
        ax = axes[3, 2]

    plot_treelet(ax, G, title, positions[title])

for row, col in zip((3, 3), (0, 3)):
    ax = axes[row, col]
    plot_treelet(ax, nx.Graph(), "", {})

plt.tight_layout()
plt.show()

###############################################################################
# Example graph
# -------------
#
# Example of creating and visualizing a chemical graph representing a sulfuric
# acid :math:`(H_2SO_4)` molecule. Nodes represent atoms, and edges represent
# bonds between them, with attributes indicating bond type.

# Create the chemical graph
G = nx.Graph()
atoms = {
    0: "S",  # Central sulfur
    1: "O",
    2: "O",  # Oxygens with double bonds
    3: "O",
    4: "O",  # Oxygens with single bonds (carrying H)
    5: "H",
    6: "H",  # Hydrogens bonded to single-bond oxygens
}
for node, symbol in atoms.items():
    G.add_node(node, atom_symbol=symbol)

# Add edges with their bond types
bonds = [
    (0, 1, 2),
    (0, 2, 2),  # Double bonds S=O
    (0, 3, 1),
    (0, 4, 1),  # Single bonds S-O
    (3, 5, 1),
    (4, 6, 1),  # Single bonds O-H
]
for a, b, bond_type in bonds:
    G.add_edge(a, b, bond_type=bond_type)

# Draw the graph
pos = {0: (0, 0), 1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0), 5: (2, 0), 6: (-2, -0)}
labels = nx.get_node_attributes(G, "atom_symbol")
edge_labels = nx.get_edge_attributes(G, "bond_type")
node_color = [
    "gold" if atoms[n] == "S" else "crimson" if atoms[n] == "O" else "lightblue"
    for n in G.nodes()
]

nx.draw(
    G,
    pos,
    with_labels=True,
    labels=labels,
    node_size=2000,
    node_color=node_color,
    font_size=12,
    font_weight="bold",
)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
plt.title("Sulfuric acid ($H_2SO_4$)")
plt.axis("equal")
plt.show()

###############################################################################
# Unlabeled Treelets
# ------------------
#
# Extract unlabeled treelets from the sulfuric acid graph using `treelets`.
# For each treelet, the script displays its index (key) and occurrence count.

G_treelets = nx.treelets(G)

for i, items in enumerate(sorted(G_treelets.items())):
    key, value = items
    print(f"Treelet {i + 1} :")
    print(f"\tIndex : '{key}'")
    print(f"\tOccurences : {value}")
    print()

###############################################################################
# Labeled Treelets
# ----------------
#
# Extract labeled treelets (considering node and edge labels) from
# the sulfuric acid graph using `labeled_treelets`.
# For each treelet, a unique canonical key is generated (see `Gaüzère et al.
# (2012) <https://hal.science/hal-00773283/document>`_ for the algorithms),
# and the number of occurrences is displayed.

G_labeled_treelets = nx.labeled_treelets(G)

for i, items in enumerate(sorted(G_labeled_treelets.items())):
    key, value = items
    print(f"Labeled Treelet {i + 1} :")
    print(f"\tCanonical key : {key}")
    print(f"\tOccurences : {value}")
    print()
