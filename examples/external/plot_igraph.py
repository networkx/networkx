"""
======
igraph
======

igraph (https://igraph.org/) is a popular network analysis package that
provides (among many other things) functions to convert to/from NetworkX.
"""

import matplotlib.pyplot as plt
import networkx as nx
import igraph as ig

# %%
# NetworkX to igraph
# ------------------

G = nx.dense_gnm_random_graph(1000, 2000)

# largest connected component
components = nx.connected_components(G)
largest_component = max(components, key=len)
H = G.subgraph(largest_component)

# networkx draw
nx.draw(H)
plt.show()

# convert to igraph
g = ig.Graph.from_networkx(G)

## TODO: uncomment this once python-igraph 0.9 is released
# igraph draw
# layout = g.layout()
# ig.plot(g, layout=layout)

# %%
# igraph to NetworkX
# ------------------

g = ig.Graph.GRG(100, 0.2)
G = g.to_networkx()
nx.draw(G)
plt.show()
