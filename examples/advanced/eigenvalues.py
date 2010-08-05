#!/usr/bin/env python
"""
Create an G{n,m} random graph and compute the eigenvalues.

Requires numpy or LinearAlgebra package from Numeric Python.

Uses optional pylab plotting to produce histogram of eigenvalues.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__credits__ = """"""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from networkx import *
try:
    import numpy.linalg
    eigenvalues=numpy.linalg.eigvals
except ImportError:
    raise ImportError("numpy can not be imported.")

try:
    from pylab import *
except:
    pass

n=1000 # 1000 nodes
m=5000 # 5000 edges

G=gnm_random_graph(n,m)

L=generalized_laplacian(G)
e=eigenvalues(L)
print("Largest eigenvalue:", max(e))
print("Smallest eigenvalue:", min(e))
# plot with matplotlib if we have it
# shows "semicircle" distribution of eigenvalues 
try:
    hist(e,bins=100) # histogram with 100 bins
    xlim(0,2)  # eigenvalues between 0 and 2
    show()
except:
    pass

