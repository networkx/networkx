#!/usr/bin/env python
"""
Random graph from given degree sequence.
Draw degree histogram with matplotlib.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-02-23 13:02:09 -0700 (Wed, 23 Feb 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 778 $"
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from matplotlib.pylab import *
import matplotlib.mlab as mlab
from networkx import *
from networkx.generators.degree_seq import *


z=create_degree_sequence(1000,powerlaw_sequence)
is_valid_degree_sequence(z)

print "Configuration model"
G=configuration_model(z)  # configuration model

degree_sequence=degree(G) # degree sequence
print "Degree sequence", degree_sequence
dmax=max(degree_sequence)
print "Degree histogram, max degree:",dmax
#h,bins=mlab.hist(degree_sequence,bins=dmax)
h,bins=mlab.hist(degree_sequence,bins=dmax)

# draw x-y plot
figure(2)
hmax=max(h)
axis([1,dmax,1,hmax]) # set ranges
x=compress(h,bins)    # remove bins with zero entries
y=compress(h,h)       # remove corresponding entries
loglog(x,y,'bo')
title("Degree distribution")
xlabel("degree")
ylabel("number of nodes")
show()

