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
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx as NX
from networkx.generators.atlas import *

atlas=graph_atlas_g()[0:20]

for G in atlas:
    print "graph %s has %d nodes with %d edges"\
          %(G.name,NX.number_of_nodes(G),NX.number_of_edges(G))
    A=NX.pygraphviz_from_networkx(G)
    A.set_attr(label=G.name) # set label to graph n ame
    # set default node attributes
    A.set_node_attr(color='red',style='filled',shape='circle') 
    
    fh=open(G.name+'.dot','w')
    A.write(fh)
