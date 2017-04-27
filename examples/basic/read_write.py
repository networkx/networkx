#!/usr/bin/env python
"""
Read and write graphs.
"""
# Author: Aric Hagberg (hagberg@lanl.gov)

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from networkx import *
import sys
G=grid_2d_graph(5,5)  # 5x5 grid
try: # Python 2.6+
    write_adjlist(G,sys.stdout) # write adjacency list to screen
except TypeError: # Python 3.x
    write_adjlist(G,sys.stdout.buffer) # write adjacency list to screen
# write edgelist to grid.edgelist
write_edgelist(G,path="grid.edgelist",delimiter=":")
# read edgelist from grid.edgelist
H=read_edgelist(path="grid.edgelist",delimiter=":")

