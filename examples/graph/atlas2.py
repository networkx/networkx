#!/usr/bin/env python
"""
Write first 20 graphs from the graph atlas as graphviz dot files
Gn.dot where n=0,19.
Requires pygraphviz and graphviz.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-05-19 14:23:02 -0600 (Thu, 19 May 2005) $"
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as NX
from networkx.generators.atlas import *
from pygraphviz import *

atlas=graph_atlas_g()[0:20]


for G in atlas:
    print("graph %s has %d nodes with %d edges"
          %(G.name,NX.number_of_nodes(G),NX.number_of_edges(G)))
    A=NX.to_agraph(G)
    A.graph_attr['label']=G.name 
    # set default node attributes
    A.node_attr['color']='red'
    A.node_attr['style']='filled'
    A.node_attr['shape']='circle'
    A.write(G.name+'.dot')
