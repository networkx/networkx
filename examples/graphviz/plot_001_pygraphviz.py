"""
============
Introduction
============

See the pygraphviz documentation and examples at
http://pygraphviz.github.io/
"""

import matplotlib.pyplot as plt
import networkx as nx

# %%
# An example showing how to use the interface to the pygraphviz
# AGraph class to convert to and from graphviz.


G = nx.complete_graph(5)
A = nx.nx_agraph.to_agraph(G)  # convert to a graphviz graph
X1 = nx.nx_agraph.from_agraph(A)  # convert back to networkx (but as Graph)
X2 = nx.Graph(A)  # fancy way to do conversion
G1 = nx.Graph(X1)  # now make it a Graph

A.write("k5.dot")  # write to dot file
X3 = nx.nx_agraph.read_dot("k5.dot")  # read from dotfile

# %%
# Write a dot file from a networkx graph for further processing with graphviz.

G = nx.grid_2d_graph(5, 5)  # 5x5 grid
# This example needs Graphviz and PyGraphviz
nx.nx_agraph.write_dot(G, "grid.dot")
print("Now run: neato -Tps grid.dot >grid.ps")

# %%G
# An example showing how to use the interface to the pygraphviz
# AGraph class to convert to and from graphviz.

G = nx.Graph()
G.add_edge(1, 2, color="red")
G.add_edge(2, 3, color="red")
G.add_node(3)
G.add_node(4)

A = nx.nx_agraph.to_agraph(G)  # convert to a graphviz graph
A.write("k5_attributes.dot")  # write to dot file

# convert back to networkx Graph with attributes on edges and
# default attributes as dictionary data
X = nx.nx_agraph.from_agraph(A)
print("edges")
print(list(X.edges(data=True)))
print("default graph attributes")
print(X.graph)
print("node node attributes")
print(X.nodes.data(True))

# %%
# An example showing how to write first 20 graphs from the graph atlas as
# graphviz dot files Gn.dot where n=0,19.

atlas = nx.graph_atlas_g()[0:20]

for G in atlas:
    print(G)
    A = nx.nx_agraph.to_agraph(G)
    A.graph_attr["label"] = G.name
    # set default node attributes
    A.node_attr["color"] = "red"
    A.node_attr["style"] = "filled"
    A.node_attr["shape"] = "circle"
    A.write(G.name + ".dot")


# %%
# An example showing how to use the interface to the pygraphviz
# AGraph class to draw a graph.

G = nx.complete_graph(5)
A = nx.nx_agraph.to_agraph(G)  # convert to a graphviz graph
A.layout()  # neato layout
A.draw("k5.ps")  # write postscript in k5.ps with neato layout


# %%
# An example showing how to use matplotlib to draw the graph
# with a graphviz layout

pos = nx.nx_agraph.graphviz_layout(G)
nx.draw(G, pos=pos)
plt.show()
