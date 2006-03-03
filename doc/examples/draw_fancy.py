#!/usr/bin/env python
"""
Draw a graph with matplotlib, color by degree.
You must have matplotlib for this to work.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-03-22 13:57:46 -0700 (Tue, 22 Mar 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 831 $"
#    Copyright (C) 2004 by 
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


G=grid_2d_graph(4,4) # 4x4 grid
pos=spring_layout(G) # positions for all nodes

# nodes
greennodes=[1,2,3,4]
bluenodes=[5,6,7,8]
othernodes=[v for v in G if v not in greennodes+bluenodes]
draw_networkx_nodes(G,pos,nodelist=greennodes,node_color='g',
                    node_size=500)
draw_networkx_nodes(G,pos,nodelist=bluenodes,node_color='b',
                    alpha=0.5,node_size=100)
draw_networkx_nodes(G,pos,nodelist=othernodes)

# edges
draw_networkx_edges(G,pos,width=2.0)
draw_networkx_edges(G,pos,edgelist=[(1,2),(3,4)],
                    width=8,alpha=0.5,edge_color='g')

# labels
labels={}
labels[1]='one'
labels[10]='ten'
draw_networkx_labels(G,pos,labels,font_color='w',font_family='sans-serif')

# math labels
labels={}
labels[12]='$\pi$'
labels[13]='$\mu$'
labels[14]='$\epsilon$'
draw_networkx_labels(G,pos,labels,font_size=16)

savefig("draw_fancy.png") # save as png
show() # display
