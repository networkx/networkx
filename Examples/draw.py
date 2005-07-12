#!/usr/bin/env python
"""
Draw a graph with matplotlib.
You must have matplotlib for this to work
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

from pylab import *
from NX import *


G=grid_2d_graph(4,4)  #4x4 grid
draw_circular(G)  # circular layout 
savefig("grid_circular.png") # save as png
hold(False) # clear axes
draw_nxpydot(G) # neato (graphviz) layout
savefig("grid_nxpydot.ps") # save as postscript

pos=spring_layout(G)
subplot(221)
draw_nx(G,pos) 
subplot(222)
draw_nx(G,pos,node_color='k',node_size=20,node_labels=False) 
subplot(223)
draw_nx(G,pos,node_color='g',node_size=20,node_labels=False) 
subplot(224)
H=G.to_directed()
draw_nx(H,pos,node_color='b',node_size=20,node_labels=False) 

show()
