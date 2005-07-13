#!/usr/bin/env python
"""
Draw a graph with neato layout using pydot to create dot graph object
with node colors.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-03-28 13:05:55 -0700 (Mon, 28 Mar 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 882 $"
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from networkx import *
#from NX.drawing.nx_pydot import *

G=grid_2d_graph(5,5)  # 5x5 grid
P=pydot_from_networkx(G)
for n in P.node_list:
    if int(n.name)>10:
        n.color="red"
        n.style="filled"
    if int(n.name)>20:
        n.shape="circle"
        n.style="filled"
        n.color="blue"

P.write("grid.dot")
print "Now run: neato -Tps grid.dot >grid.ps"
