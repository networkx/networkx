"""
Atlas
=====

An example showing how to write first 20 graphs from the graph atlas as
graphviz dot files Gn.dot where n=0,19.

TODO: does nx_agraph.draw support multiple graphs in one png?
"""

import networkx as nx

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

# Draw the 20th graph from the atlas to png
A.draw("A20.png", prog="neato")
