"""
======
Atlas2
======

Write first 20 graphs from the graph atlas as graphviz dot files
Gn.dot where n=0,19.
"""

import networkx as nx
from networkx.generators.atlas import graph_atlas_g

atlas = graph_atlas_g()[0:20]

for G in atlas:
    print(
        f"{G.name} has {nx.number_of_nodes(G)} nodes with {nx.number_of_edges(G)} edges"
    )
    A = nx.nx_agraph.to_agraph(G)
    A.graph_attr["label"] = G.name
    # set default node attributes
    A.node_attr["color"] = "red"
    A.node_attr["style"] = "filled"
    A.node_attr["shape"] = "circle"
    A.write(G.name + ".dot")
