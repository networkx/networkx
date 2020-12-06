"""
================================
JavaScript InfoVis Toolkit (JIT)
================================

An example showing how to use the JavaScript InfoVis Toolkit (JIT)
JSON export

See the JIT documentation and examples at https://philogb.github.io/jit/
"""

import json

import matplotlib.pyplot as plt
import networkx as nx

# add some nodes to a graph
G = nx.Graph()

G.add_node("one", type="normal")
G.add_node("two", type="special")
G.add_node("solo")

# add edges
G.add_edge("one", "two")
G.add_edge("two", 3, type="extra special")

# convert to JIT JSON
jit_json = nx.jit_data(G, indent=4)
print(jit_json)

X = nx.jit_graph(json.loads(jit_json))
print(f"Nodes: {list(X.nodes(data=True))}")
print(f"Edges: {list(X.edges(data=True))}")

nx.draw(G, pos=nx.planar_layout(G), with_labels=True)
plt.show()
