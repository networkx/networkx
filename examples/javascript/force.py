"""Example of writing JSON format graph data and using the D3 Javascript library to produce an HTML/Javascript drawing.
"""
# Author: Aric Hagberg <aric.hagberg@gmail.com>

#    Copyright (C) 2011-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import json
import networkx as nx
from networkx.readwrite import json_graph

G = nx.barbell_graph(6,3)
# this d3 example uses the name attribute for the mouse-hover value,
# so add a name to each node
for n in G:
    G.node[n]['name'] = n
# write json formatted data
d = json_graph.node_link_data(G) # node-link format to serialize
# write json
json.dump(d, open('force/force.json','w'))
print('Wrote node-link JSON data to force/force.json')
print('Open force/force.html in a web browser')