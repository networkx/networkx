#!/usr/bin/env python
"""
An example showing how to use the interface to the pygraphviz
AGraph class to convert to and from graphviz. 

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
X1=from_agraph(A)     # convert back to networkx (but as Graph)
X2=Graph(A)          # fancy way to do conversion
G1=Graph(X1)          # now make it a Graph 

A.write('k5.dot')     # write to dot file
X3=read_dot('k5.dot') # read from dotfile

