"""
Generators for geometric graphs.

"""
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
__author__ ="""Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)"""
__date__ = "$Date: 2005-06-15 12:44:45 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1038 $"

import networkx
import random,sys


#---------------------------------------------------------------------------
#  Random Geometric Graphs
#---------------------------------------------------------------------------
        
def random_geometric_graph(n, radius, create_using=None, repel=0.0, verbose=False, dim=2):
    """Random geometric graph in the unit cube

    Returned Graph has added attribute G.pos which is a 
    dict keyed by node to the position tuple for the node.
    """
    if create_using is None:    
        G=networkx.Graph()
    else:
        G=create_using
        G.clear()
    G.name="Random Geometric Graph"
    G.add_nodes_from([v for v in range(n)])  # add n nodes
    # position them randomly in the unit cube in n dimensions
    # but not any two within "repel" distance of each other
    # pick n random positions
    positions=[]
    while(len(positions)< n):
        pnew=[]
        [pnew.append(random.random()) for i in xrange(0,dim)]
        reject=False
        # avoid existing nodes
        if repel > 0.0 :
            for pold in positions:
                m2=map(lambda x,y: (x-y)**2, pold,pnew)
                r2=reduce(lambda x, y: x+y, m2, 0.)
                if r2 < repel**2 :
                    reject=True
                    print >>sys.stderr,"rejecting", len(positions),pnew
                    break
            if(reject):
                reject=False
                continue
        if(verbose):
            print >>sys.stderr,"accepting", len(positions),pnew
        positions.append(pnew)    

    # add positions to nodes        
    G.pos={}
    for v in G.nodes():
        G.pos[v]=positions.pop()

    # connect nodes within "radius" of each other
    # n^2 algorithm, oh well, should work in n dimensions anyway...
    for u in G.nodes():
        p1=G.pos[u]
        for v in G.nodes():
            if u==v:  # no self loops
                continue
            p2=G.pos[v]
            m2=map(lambda x,y: (x-y)**2, p1,p2)
            r2=reduce(lambda x, y: x+y, m2, 0.)
            if r2 < radius**2 :
                G.add_edge(u,v)
    return G


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/generators/geometric.txt',
                                 package='networkx')
    return suite

if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    

