#!/usr/bin/env python
"""
Read and write graphs.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2004-11-03 08:11:09 -0700 (Wed, 03 Nov 2004) $"
__credits__ = """"""
__revision__ = "$Revision: 503 $"
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from NX import *
G=grid_2d_graph(5,5)  # 5x5 grid
write_adjlist(G) # write adjacency list to screen
write_edgelist(G,path="grid.edgelist") # write edgelist to grid.edgelist
H=read_edgelist(path="grid.edgelist") # read edgelist from grid.edgelist

try:
    from NX.drawing.nxpydot import *
    write_dot(G,path="grid.dot") # write dotfile
except:
    pass # skipping write_dot since pydot,pyparsing, or graphviz not available 
