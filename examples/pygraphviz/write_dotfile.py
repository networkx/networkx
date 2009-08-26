#!/usr/bin/env python
"""
Write a dot file from a networkx graph for further processing with graphviz.

You need to have either pygraphviz or pydot for this example.

See https://networkx.lanl.gov/drawing.html for more info.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as NX

# and the following code block is not needed
# but we want to see which module is used and
# if and why it fails
try:
    m=NX.drawing.write_dot.__module__
except:
    print
    print "pygraphviz or pydot were not found "
    print "see https://networkx.lanl.gov/Drawing.html for info"
    print
    raise

print "using module", m


G=NX.grid_2d_graph(5,5)  # 5x5 grid
NX.write_dot(G,"grid.dot")
print "Now run: neato -Tps grid.dot >grid.ps"
