#!/usr/bin/env python
"""
Compute some network properties for the lollipop graph.
"""
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

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
print "eccentricity: ",eccentricity(G)
print "center: ",center(G)
print "periphery: ",periphery(G)
print "density: ", density(G)

