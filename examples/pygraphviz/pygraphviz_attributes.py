#!/usr/bin/env python
"""
An example showing how to use the interface to the pygraphviz
AGraph class to convert to and from graphviz. 

Also see the pygraphviz documentation and examples at
https://networkx.lanl.gov/pygraphviz/

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2006-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as nx

# networkx graph
X=nx.Graph()
# ad edges with red color
X.add_edge(1,2,{'color':'red'})
X.add_edge(2,3,{'color':'red'})
# add nodes 3 and 4
X.add_node(3)
X.add_node(4)

# convert to a graphviz graph, 
# use edge attributes from Graph edge data
# no node attributes, or default graph, node, or edge attributes
A=nx.to_agraph(X)   

# set some default attributes for pygraphviz
default_attributes={'graph':{},'node':{},'edge':{}}
default_attributes['graph']['label']='pygraphviz graph'
default_attributes['node']['shape']='circle'

# set some node attributes
node_attributes={}
node_attributes[3]={'color':'green','shape':'box'}

# convert to AGraph, override any attributes with those on given command line 
A1=nx.to_agraph(X,
             graph_attr=default_attributes,
             node_attr=node_attributes,
             )

# write to dot file
A1.write('k5_attributes.dot')   

# convert back to networkx Graph with attributes on edges and
# default attributes as dictionary data
X=nx.from_agraph(A1)
print "edges"
print X.edges(data=True)
print "default attributes"
print X.graph_attr
print "node attributes"
print X.node_attr
