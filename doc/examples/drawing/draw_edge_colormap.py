#!/usr/bin/env python
"""
Draw a graph with matplotlib, color edges.
You must have matplotlib>=87.7 for this to work.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

try:
    from pylab import *
except:
    raise ImportError("""pylab not found:
See https://networkx.lanl.gov/Drawing.html for info""")
    
from networkx import *

G=star_graph(20)  # 11 nodes, 10 edges
pos=spring_layout(G)
colors=arange(20) # 10 edges
draw(G,pos,node_color='b',edge_color=colors,width=4,edge_cmap=cm.Blues)
savefig("star.png") # save as png
show() # display
