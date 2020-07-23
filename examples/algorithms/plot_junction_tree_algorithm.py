"""
=======================
Junction Tree Algorithm
=======================

Example of creating a junction tree from a directed graph.
"""

import networkx as nx
from networkx.algorithms.tree.junction_tree_algorithm import junction_tree
import matplotlib.pyplot as plt

B = nx.DiGraph()
B.add_nodes_from(["A", "B", "C", "D", "E", "F", "G"])
B.add_edges_from(
    [("A", "B"), ("A", "F"), ("C", "B"), ("B", "D"), ("F", "G"), ("E", "G")]
)

bayes_pos = nx.spring_layout(B, k=3)
plt.subplot(1, 2, 1)
plt.title("Bayesian Network")
nx.draw_networkx(B, with_labels=True)

jt = junction_tree(B)
plt.subplot(1, 2, 2)
plt.title("Junction Tree")
nx.draw_networkx(jt, with_labels=True)
plt.show()
