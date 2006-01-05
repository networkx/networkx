#!/usr/bin/env python
"""
An example using XGraph as a weighted network.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = ""
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

try:
    from pylab import *
except:
    print "pylab not found: see https://networkx.lanl.gov/Drawing.html for info"
    raise 
    
from networkx import *

G=XGraph()

G.add_edge('a','b',0.6)
G.add_edge('a','c',0.2)
G.add_edge('c','d',0.1)
G.add_edge('c','e',0.7)
G.add_edge('c','f',0.9)
G.add_edge('a','d',0.3)

elarge=[(u,v) for (u,v,d) in G.edges() if d >0.5]
esmall=[(u,v) for (u,v,d) in G.edges() if d <=0.5]

pos=spring_layout(G) # positions for all nodes

# nodes
draw_networkx_nodes(G,pos,node_size=700)

# edges
draw_networkx_edges(G,pos,edgelist=elarge,
                    width=6)
draw_networkx_edges(G,pos,edgelist=esmall,
                    width=6,alpha=0.5,edge_color='b',style='dashed')

# labels
draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

# turn off x and y axes labels in pylab
xticks([])
yticks([]) 

savefig("weighted.png") # save as png
show() # display
