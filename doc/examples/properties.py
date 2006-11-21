#!/usr/bin/env python
"""
Read and write graphs.
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

G = lollipop_graph(4,6)

pathlengths=[]

print "source vertex {target:length, }"
for v in G.nodes():
    spl=single_source_shortest_path_length(G,v)
    print v,spl
    for p in spl.values():
        pathlengths.append(p)

print
print "average shortest path length ", sum(pathlengths)/len(pathlengths)

# histogram of path lengths 
dist={}
for p in pathlengths:
    if dist.has_key(p):
        dist[p]+=1
    else:
        dist[p]=1

print
print "length #paths"
verts=dist.keys()
verts.sort()
for d in verts:
    print d,dist[d]

print "radius: ",radius(G)
print "diameter: ",diameter(G)
print "eccentricity: ",eccentricity(G,with_labels=True)
print "center: ",center(G)
print "periphery: ",periphery(G)
print "density: ", density(G)

