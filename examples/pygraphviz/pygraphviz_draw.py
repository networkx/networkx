#!/usr/bin/env python
"""
An example showing how to use the interface to the pygraphviz
AGraph class to draw a graph.

Also see the pygraphviz documentation and examples at
https://networkx.lanl.gov/pygraphviz/


"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from networkx import *

# plain graph

G=complete_graph(5)   # start with K5 in networkx
A=to_agraph(G)        # convert to a graphviz graph
A.layout()            # neato layout
A.draw("k5.ps")       # write postscript in k5.ps with neato layout

