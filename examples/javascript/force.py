"""Example of writing JSON format graph data and using the D3 Javascript library to produce an HTML/Javascript drawing.
"""
#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg <aric.hagberg@gmail.com>"""
import json
import networkx as nx
from networkx.readwrite import json_graph
import http_server

G = nx.barbell_graph(6,3)
# write json formatted data
d = json_graph.node_link_data(G) # node-link format to serialize
# write json 
json.dump(d, open('force/force.json','w'))
print('Wrote node-link JSON data to force/force.json')
# open URL in running web browser
http_server.load_url('force/force.html')
print('Or copy all files in force/ to webserver and load force/force.html')

