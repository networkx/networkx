"""
Laplacian, adjacency matrix, and spectrum of graphs.

Needs numpy array package: numpy.scipy.org.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

try:
    import numpy as N
except:
    raise ImportError

import networkx

def adj_matrix(G,nodelist=None):
    """Return adjacency matrix of graph as a numpy matrix.

    This just calls networkx.convert.to_numpy_matrix.

    If you want a pure python adjacency matrix represntation try
    networkx.convert.to_dict_of_dicts
    which will return a dictionary-of-dictionaries format that
    can be addressed as a sparse matrix.

    """
    return networkx.to_numpy_matrix(G,nodelist=nodelist)


def laplacian(G,nodelist=None):
    """Return standard combinatorial Laplacian of G as a numpy matrix.

    Return the matrix L = D - A, where

       D is the diagonal matrix in which the i'th entry is the degree of node i
       A is the adjacency matrix.

    """
    # this isn't the most efficient way to do this...
    n=G.order()
    I=N.identity(n)
    A=N.asarray(networkx.to_numpy_matrix(G,nodelist=nodelist))
    D=I*N.sum(A,axis=1)
    L=D-A
    return L


def normalized_laplacian(G,nodelist=None):
    """Return normalized Laplacian of G as a numpy matrix.

    See Spectral Graph Theory by Fan Chung-Graham.
    CBMS Regional Conference Series in Mathematics, Number 92,
    1997.

    """
    # FIXME: this isn't the most efficient way to do this...
    n=G.order()
    I=N.identity(n)
    A=N.asarray(networkx.to_numpy_matrix(G,nodelist=nodelist))
    d=N.sum(A,axis=1)
    L=I*d-A
    osd=N.zeros(len(d))
    for i in range(len(d)):
        if d[i]>0: osd[i]=N.sqrt(1.0/d[i])
    T=I*osd
    L=N.dot(T,N.dot(L,T))
    return L

def laplacian_spectrum(G):
    """Return eigenvalues of the Laplacian of G""" 
    return N.linalg.eigvals(laplacian(G))

def adjacency_spectrum(G):
    """Return eigenvalues of the adjacency matrix of G""" 
    return N.linalg.eigvals(adj_matrix(G))


combinatorial_laplacian=laplacian
generalized_laplacian=normalized_laplacian


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/spectrum.txt',package='networkx')
    return suite


if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    
