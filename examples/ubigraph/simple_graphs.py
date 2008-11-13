#!/usr/bin/env python

from networkx import *
import time

# ubigraph server should already be running

print "Pappus Graph"
G=UbiGraph(pappus_graph())
time.sleep(5)
print "4D Hypercube Graph"
G=UbiGraph(hypercube_graph(4))
time.sleep(5)
print "50 node circular ladder graph"
G=UbiGraph(circular_ladder_graph(50))
time.sleep(5)
