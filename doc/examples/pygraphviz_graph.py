#!/usr/bin/env python
"""
An example using pygraphviz to read a dot file, translate to a
NetworkX Graph and then back to a dot file.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx as NX
import pygraphviz
import sys
import os

A=pygraphviz.Agraph()
fh=open(sys.argv[1],'r') #
A.read(fh)
fh.close()
node_attr={}
edge_attr={}
graph_attr={}
G=NX.networkx_from_pygraphviz(A,
                           graph_attr=graph_attr,
                           node_attr=node_attr,
                           edge_attr=edge_attr
                           )
#                           create_using=XDiGraph(multiedges=True,selfloops=True))

A1=NX.pygraphviz_from_networkx(G,
                            graph_attr=graph_attr,
                            node_attr=node_attr,
                            edge_attr=edge_attr
                            )


fh=open('pygraphviz_graph.dot','w')
A1.write(fh)
