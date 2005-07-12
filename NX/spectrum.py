"""
Laplacian, adjacency matrix, and spectrum of graphs.

Uses Numeric.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-15 14:18:07 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1044 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html


try:
    import Numeric
except ImportError:
#    print "Import Error: Not able to import Python module Numeric"
    raise


def adj_matrix(G,u=None):
    """Return adjacency matrix of graph
    If u is defined return row of adjacency matrix at row u.
    """
    n=G.order()
    # make an dictionary that maps vertex name to position
    index={}
    count=0
    for a in G.nodes():
        index[a]=count
        count = count+1
    # the entire adjacency matrix
    if u == None:
        a = Numeric.zeros((n,n))
        for x in G.nodes():
            for y in G.neighbors(x):
                a[index[x],index[y]]=1
                a[index[y],index[x]]=1
    # one row of the adjacency matrix
    else:
        a = Numeric.zeros((n))
        for y in G.neighbors(u): 
            a[index[y]]=1
    return a            

def laplacian(G):
    """Return standard Laplacian of graph"""
    n=G.order()
    I=Numeric.identity(n)
    d=Numeric.array(G.degree())
    l=I*d-adj_matrix(G)
    return l            

def generalized_laplacian(G):
    """Return generalized Laplacian of graph

    See Spectral Graph Theory by Fan Chung-Graham.

    """
    l=laplacian(G) # standard laplacian
    # build S=1/sqrt(T) matrix
    n=G.order()
    I=Numeric.identity(n)
    d=Numeric.array(G.degree())
    tmhalf=Numeric.where(d, 1/Numeric.sqrt(d),0)
    S=I*tmhalf
    # multiply L = S l S
    L=Numeric.matrixmultiply(Numeric.matrixmultiply(S,l),S)
    return L 


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/spectrum.txt',package='NX')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
