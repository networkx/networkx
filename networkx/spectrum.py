"""
Laplacian, adjacency matrix, and spectrum of graphs.

Needs either numpy or Numeric.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html


# try numpy first and Numeric second.
# Fail if neither is available. 
try:
    import numpy as N
except ImportError:
    try:
        import Numeric as N
    except ImportError:
        raise ImportError,"Neither Numeric nor numpy can be imported."

def adj_matrix(G,nodelist=None,weighted=False):
    """Return adjacency matrix of graph

    If nodelist is defined return adjacency matrix with nodes in nodelist
    in the order specified.

    If weighted is False, then the value of the entry in the adjacency
    matrix is zero or one.  E.g. self-loops, multi-edges, or weighted
    graphs are not handled.  If weighted is True, the weight matrix is
    returned.  Note, however, that the weighted representation can not
    distinguish between between zero weight edges and absent edges.

    The returned matrix is a numpy or Numeric array. 

    """
    if nodelist is None:
        nodelist=G.nodes()
    if weighted:
        if not hasattr(G,"get_edge"):
            w=lambda x,y:1
        else:
            w=lambda x,y:G.get_edge(x,y)
    else:
        w=lambda x,y:1
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    a = N.zeros((nlen,nlen))
    for n1 in nodelist:
        nbrs=[n for n in G.neighbors(n1) if n in nodelist]
        for n2 in nbrs:
            a[index[n1],index[n2]]=w(n1,n2)
            a[index[n2],index[n1]]=w(n1,n2)
    return a            

def laplacian(G,nodelist=None):
    """Return standard combinatorial Laplacian of G.

    Return the matrix L = D - A, where

       D is the diagonal matrix in which the i'th entry is the degree of node i
       A is the adjacency matrix.

    The returned matrix is a numpy or Numeric array. 

    """
    # this isn't the most efficient way to do this...
    n=G.order()
    I=N.identity(n)
    A=adj_matrix(G,nodelist=nodelist)
    D=I*N.sum(A,axis=1)
    L=D-A
    return L


def normalized_laplacian(G,nodelist=None):
    """Return normalized Laplacian of G.

    See Spectral Graph Theory by Fan Chung-Graham.
    CBMS Regional Conference Series in Mathematics, Number 92,
    1997.

    The returned matrix is a numpy or Numeric array. 

    """
    # FIXME: this isn't the most efficient way to do this...
    n=G.order()
    I=N.identity(n)
    A=adj_matrix(G,nodelist=nodelist)
    D=I*N.sum(A,axis=1)
    L=D-A
    d=N.sum(A,axis=1)
    T=I*(N.where(d,N.sqrt(1./d),0))
    L=N.dot(T,N.dot(L,T))
    return L

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
    
