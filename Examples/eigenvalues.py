#!/usr/bin/env python
"""
Create an Erdos-Renyi random graph and compute the eigenvalues.

Requires LinearAlgebra package from Numeric Python.

Uses optional pylab plotting to produce histogram of eigenvalues.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-06-17 11:38:54 -0600 (Fri, 17 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1055 $"
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from NX import *
import LinearAlgebra as LA
try:
    from pylab import *
except:
    pass

n=1000 # 1000 nodes
m=5000 # 5000 edges

G=erdos_renyi_graph(n,m)

L=generalized_laplacian(G) 
e=LA.eigenvalues(L)
print "Largest eigenvalue:",max(e)
print "Smallest eigenvalue:",min(e)
# plot with matplotlib if we have it
# shows "semicircle" distribution of eigenvalues 
try:
    hist(e,bins=100) # histogram with 100 bins
    xlim(0,2)  # eigenvalues between 0 and 2
    show()
except:
    pass
