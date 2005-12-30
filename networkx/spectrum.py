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


def adj_matrix(G,nodelist=None):
    """Return adjacency matrix of graph

    If nodelist is defined return adjacency matrix with nodes in nodelist
    in the order specified.

    The value of the entry in the adjacency matrix is zero or one.
    E.g. self-loops, multi-edges, or weighted graphs are not handled.

    """
    if nodelist is None:
        nodelist=G.nodes()
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    a = Numeric.zeros((nlen,nlen))
    for n1 in nodelist:
        nbrs=[n for n in G.neighbors(n1) if n in nodelist]
        for n2 in nbrs:
            a[index[n1],index[n2]]=1
            a[index[n2],index[n1]]=1
    return a            

def laplacian(G):
    """Return standard Laplacian of graph"""
    # this isn't the most efficient way to do this...
    n=G.order()
    I=Numeric.identity(n)
    A=adj_matrix(G)
    D=I*Numeric.sum(A)
    L=D-A
    return L

def generalized_laplacian(G):
    """Return generalized Laplacian of graph

    See Spectral Graph Theory by Fan Chung-Graham.

    """
    # this isn't the most efficient way to do this...
    n=G.order()
    I=Numeric.identity(n)
    A=adj_matrix(G)
    D=I*Numeric.sum(A)
    L=D-A
    d=sum(A)
    T=I*(Numeric.where(d,Numeric.sqrt(1./d),0))
    L=Numeric.dot(T,Numeric.dot(L,T))
    return L

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
    
