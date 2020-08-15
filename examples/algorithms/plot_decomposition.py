"""
=============
Decomposition
=============

Example of creating a junction tree from a directed graph.
"""

import networkx as nx
from networkx.algorithms import moral
from networkx.algorithms.tree.decomposition import junction_tree
from networkx.drawing.nx_agraph import graphviz_layout as layout
import matplotlib.pyplot as plt

B = nx.DiGraph()
B.add_nodes_from(["A", "B", "C", "D", "E", "F"])
B.add_edges_from(
    [("A", "B"), ("A", "C"), ("B", "D"), ("B", "F"), ("C", "E"), ("E", "F")]
)

options = {"with_labels": True, "node_color": "white", "edgecolors": "blue"}

bayes_pos = layout(B, prog="neato")
ax1 = plt.subplot(1, 3, 1)
plt.title("Bayesian Network")
nx.draw_networkx(B, pos=bayes_pos, **options)

mg = moral.moral_graph(B)
plt.subplot(1, 3, 2, sharex=ax1, sharey=ax1)
plt.title("Moralized Graph")
nx.draw_networkx(mg, pos=bayes_pos, **options)

jt = junction_tree(B)
plt.subplot(1, 3, 3)
plt.title("Junction Tree")
nsize = [2000 * len(n) for n in list(jt.nodes())]
nx.draw_networkx(jt, pos=layout(jt, prog="neato"), node_size=nsize, **options)

plt.tight_layout()
plt.show()
