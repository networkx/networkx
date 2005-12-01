#!/usr/bin/env python
"""
Create an Erdos-Renyi random graph and report some properties.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2004-11-03 08:11:09 -0700 (Wed, 03 Nov 2004) $"
__credits__ = """"""
__revision__ = "$Revision: 503 $"
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from networkx import *

n=10 # 10 nodes
m=20 # 20 edges

G=erdos_renyi_graph(n,m)

# some properties
print "node degree clustering"
for v in nodes(G):
    print v,degree(G,v),clustering(G,v)

# print the adjacency list 
write_adjlist(G)

