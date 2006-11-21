"""
Functional interface to graph properties.
    
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

# functional style helpers

def nodes(G):
    """Return a copy of the graph nodes in a list."""
    return G.nodes()

def nodes_iter(G):
    """Return an iterator over the graph nodes."""
    return G.nodes_iter()

def edges(G,nbunch=None):
    """Return list of  edges adjacent to nodes in nbunch.

    Return all edges if nbunch is unspecified or nbunch=None.

    For digraphs, edges=out_edges

    """
    return G.edges(nbunch)

def edges_iter(G,nbunch=None):
    """Return iterator over  edges adjacent to nodes in nbunch.

    Return all edges if nbunch is unspecified or nbunch=None.

    For digraphs, edges=out_edges
    
    """
    return G.edges_iter(nbunch)

def degree(G,nbunch=None,with_labels=False):
    """Return degree of single node or of nbunch of nodes.
    If nbunch is ommitted, then return degrees of *all* nodes.
    """
    return G.degree(nbunch,with_labels=with_labels)

def neighbors(G,n):
    """Return a list of nodes connected to node n. """
    return G.neighbors(n)

def number_of_nodes(G):
    """Return the order of a graph = number of nodes."""
    return G.number_of_nodes()

def number_of_edges(G):
    """Return the size of a graph = number of edges. """
    return G.number_of_edges()
    
def density(G):
    """Return the density of a graph.
    
    density = size/(order*(order-1)/2)
    density()=0.0 for an edge-less graph and 1.0 for a complete graph.
    """
    n=number_of_nodes(G)
    e=number_of_edges(G)
    if e==0: # includes cases n==0 and n==1
        return 0.0
    else:
        return e*2.0/float(n*(n-1))

def degree_histogram(G):
    """Return a list of the frequency of each degree value.
    
    The degree values are the index in the list.
    Note: the bins are width one, hence len(list) can be large
    (Order(number_of_edges))
    """
    degseq=G.degree()
    dmax=max(degseq)+1
    freq= [ 0 for d in xrange(dmax) ]
    for d in degseq:
        freq[d] += 1
    return freq

def is_directed(G):
    """ Return True if graph is directed."""
    return G.is_directed()


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/function.txt',
                                 package='networkx')
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
    
