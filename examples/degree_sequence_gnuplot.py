#!/usr/bin/env python
"""
Random graph from given degree sequence.
Draw degree histogram with gnuplot.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2004-11-03 10:59:33 -0700 (Wed, 03 Nov 2004) $"
__credits__ = """"""
__revision__ = "$Revision: 504 $"
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from NX import *
from NX.generators.degree_seq import *
import sys


z=create_degree_sequence(1000,powerlaw_sequence)
is_valid_degree_sequence(z)
is_valid_degree_sequence(z)

print "Configuration model"
G=configuration_model(z)  # configuration model
degree_sequence=degree(G) # degree sequence
#print "Degree sequence", degree_sequence
hist={}
for d in degree_sequence:
    if hist.has_key(d):
        hist[d]+=1
    else:
        hist[d]=1

# write gnuplot command file
fh=open("degree.gnu",'w')
fh.write("set logscale xy\n")
fh.write("set xlabel 'degree'\n")
fh.write("set ylabel 'number of nodes'\n")
fh.write("set title 'Degree distribution'\n")
fh.write("plot 'degree.dat' \n")
fh.write("pause -1 \n")
fh.close()
# wrte the data
fh=open("degree.dat",'w')
fh.write("# degree #nodes\n")
for d in hist:
    fh.write("%s %s\n"%(d,hist[d]))
fh.close()

sys.stderr.write("Now run 'gnuplot degree.gnu'\n")
