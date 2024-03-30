"""
Attributes
==========

Example illustrating how attributes of nodes, edges, and graphs are handled
during conversion to/from `~pygraphviz.AGraph`.
"""

import networkx as nx

G = nx.Graph()
G.add_edge(1, 2, color="red")
G.add_edge(2, 3, color="red")
G.add_node(3)
G.add_node(4)

A = nx.nx_agraph.to_agraph(G)  # convert to a graphviz graph
A.draw("attributes.png", prog="neato")  # Draw with pygraphviz

# convert back to networkx Graph with attributes on edges and
# default attributes as dictionary data
X = nx.nx_agraph.from_agraph(A)
print("edges")
print(list(X.edges(data=True)))
print("default graph attributes")
print(X.graph)
print("node node attributes")
print(X.nodes.data(True))
