"""
==========
Javascript
==========

Example of writing JSON format graph data and using the D3 Javascript library
to produce an HTML/Javascript drawing.

The relevant JavaScript and HTMl can be found at:

https://github.com/networkx/networkx/tree/master/examples/external/force

"""
import json
import networkx as nx


G = nx.barbell_graph(6, 3)
# this d3 example uses the name attribute for the mouse-hover value,
# so add a name to each node
for n in G:
    G.nodes[n]["name"] = n

# write json formatted data
d = nx.json_graph.node_link_data(G)  # node-link format to serialize

# write json
json.dump(d, open("force/force.json", "w"))
print("Wrote node-link JSON data to force/force.json")

nx.drawing.display_d3js("force/force.json", "force/force.js", "force/force.html")
