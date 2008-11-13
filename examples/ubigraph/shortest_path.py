#!/usr/bin/env python

import networkx
import time

# ubigraph server should already be running

#G=UbiGraph(networkx.generators.pappus_graph())
G=networkx.UbiGraph(networkx.generators.moebius_kantor_graph())


G.node_labels() # turn on node labels
G.set_edge_attr(color='#3f3f3f') # dark grey edges

time.sleep(2)

# get edges in shortest path between 0 and 8
s=networkx.shortest_path(G,0,8)
print "shortest path between 0-8",s
e=zip(s[0:-1],s[1:])
epath=[(u,v,G.get_edge(u,v)) for u,v in e]

wideyellow=G.new_edge_style(color='#ffff00',width='6.0')
for edge in epath:
    G.set_edge_attr(edge,style=wideyellow)
    time.sleep(2)

