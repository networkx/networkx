#!/usr/bin/env python
"""
An example showing how to use the interface to the pygraphviz
AGraph class to convert to and from graphviz. 

Also see the pygraphviz documentation and examples at
https://networkx.lanl.gov/pygraphviz/

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2006-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as nx

# networkx graph
G=nx.Graph()
# ad edges with red color
G.add_edge(1,2,color='red')
G.add_edge(2,3,color='red')
# add nodes 3 and 4
G.add_node(3)
G.add_node(4)

# convert to a graphviz agraph 
A=nx.to_agraph(G)   

# write to dot file
A.write('k5_attributes.dot')   

# convert back to networkx Graph with attributes on edges and
# default attributes as dictionary data
X=nx.from_agraph(A)
print("edges")
print(X.edges(data=True))
print("default graph attributes")
print(X.graph)
print("node node attributes")
print(X.node)
