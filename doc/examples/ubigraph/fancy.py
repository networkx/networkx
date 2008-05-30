#!/usr/bin/env python

import networkx
import time

# ubigraph server should already be running

G=networkx.UbiGraph(multiedges=True)
G.add_node('a')
G.add_node('b')
G.add_edge('a','b','edge a-b 1')
G.add_edge('a','b','edge a-b 2')
G.add_edge('b','c')
G.add_edge('c','a')

G.splines() # turn on splines
G.node_labels() # turn on node labels


G.set_node_attr(color='#00ff00') # green nodes
G.set_node_attr('a',color='#0000ff') # node 'a' blue
G.set_node_attr('a',shape='torus') # node 'a' torus

G.set_edge_attr(color='#00ff00') # green edges

# set node style 
purplecube=G.new_node_style(color='#ff00ff',shape='cube')
G.set_node_attr(style=purplecube)

