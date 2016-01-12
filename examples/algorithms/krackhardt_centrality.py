#!/usr/bin/env python
"""
Centrality measures of Krackhardt social network.
"""
# Author: Aric Hagberg (hagberg@lanl.gov)
# Date: 2005-05-12 14:33:11 -0600 (Thu, 12 May 2005)
# Revision: 998

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from networkx import *

G=krackhardt_kite_graph()

print("Betweenness")
b=betweenness_centrality(G)
for v in G.nodes():
    print("%0.2d %5.3f"%(v,b[v]))

print("Degree centrality")
d=degree_centrality(G)
for v in G.nodes():
    print("%0.2d %5.3f"%(v,d[v]))

print("Closeness centrality")
c=closeness_centrality(G)
for v in G.nodes():
    print("%0.2d %5.3f"%(v,c[v]))
