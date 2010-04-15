#!/usr/bin/env python
"""
Random graph from given degree sequence.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2004-11-03 08:11:09 -0700 (Wed, 03 Nov 2004) $"
__credits__ = """"""
__revision__ = "$Revision: 503 $"
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from networkx import *
from networkx.generators.degree_seq import *

z=[5,3,3,3,3,2,2,2,1,1,1]
is_valid_degree_sequence(z)

print "Configuration model"
G=configuration_model(z)  # configuration model
degree_sequence=degree(G).values() # degree sequence
print "Degree sequence", degree_sequence
print "Degree histogram"
hist={}
for d in degree_sequence:
    if hist.has_key(d):
        hist[d]+=1
    else:
        hist[d]=1
print "degree #nodes"
for d in hist:
    print d,hist[d]


