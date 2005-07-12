"""
Generate graphs with a given degree sequence.

"""
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-15 12:42:59 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1037 $"

import random
import NX
import NX.utils
#---------------------------------------------------------------------------
#  Generating Graphs with a given degree sequence
#---------------------------------------------------------------------------

def configuration_model(deg_sequence,seed=None):
    """Return a pseudograph with given degree sequence.

      - `deg_sequence`: degree sequence, a list of integers with each entry
                        corresponding to the degree of a node (need not be
                        sorted). A non-graphical degree sequence (i.e. one
                        not realizable by some simple graph) will raise an
                        Exception.
      - `seed`: seed for random number generator (default=None)

    Steps:
     - Check if deg_sequence is a valid degree sequence.
     - Create N nodes with stubs of given degree.
     - Randomly select two available stubs and connect them with an edge.

    As described by Newman [newman-2003-structure].
    
    Nodes are labeled 1,.., len(deg_sequence),
    corresponding to their position in deg_sequence.

    This process can lead to duplicate edges and loops, and therefore
    returns a pseudograph type.  You can call remove_parallel() and
    remove_selfloops() to get a simple graph (but likely without
    the exact specified degree sequence). This "finite-size effect"
    decreases as the size of the graph increases.

    References:
    
    [newman-2003-structure]  M.E.J. Newman, "The structure and function
    of complex networks", SIAM REVIEW 45-2, pp 167-256, 2003.
        
    """
    if not is_valid_degree_sequence(deg_sequence):
        raise NX.NetworkXError, 'Invalid degree sequence'

    if not seed is None:
        random.seed(seed)

    # start with empty N-node graph
    N=len(deg_sequence)
    G=NX.empty_graph(N,create_using=NX.Graph()) # no multiedges or selfloops
    #G=empty_graph(N,create_using=XGraph(multiedges=True, selfloops=True))

    if N==0 or max(deg_sequence)==0: # done if no edges
        return G 

    # build stublist, a list of available degree-repeated stubs
    # e.g. for deg_sequence=[3,2,1,1,1]
    # initially, stublist=[1,1,1,2,2,3,4,5]
    #     i.e., node 1 has degree=3 and is repeated 3 times, etc.
    stublist=[]
    for n in G:
        for i in range(deg_sequence[n-1]):
            stublist.append(n)

    # while there are stubs in the sublist, randomly select two stubs,
    # connect them to make an edge, then pop them from the stublist    
    while stublist:
       source=random.choice(stublist)
       stublist.remove(source)
       target=random.choice(stublist)
       stublist.remove(target)
       G.add_edge(source,target)

    G.name="configuration_model %d nodes %d edges"%(G.order(),G.size())
    return G


def havel_hakimi_graph(deg_sequence,seed=None):
    """Return a simple graph with given degree sequence, constructed using the
    Havel-Hakimi algorithm.

      - `deg_sequence`: degree sequence, a list of integers with each entry
         corresponding to the degree of a node (need not be sorted).
         A non-graphical degree sequence (not sorted).
         A non-graphical degree sequence (i.e. one
         not realizable by some simple graph) raises an Exception.    
      - `seed`: seed for random number generator (default=None)

    The Havel-Hakimi algorithm constructs a simple graph by
    successively connecting the node of highest degree to other nodes
    of highest degree, resorting remaining nodes by degree, and
    repeating the process. The resulting graph has a high
    degree-associativity.  Nodes are labeled 1,.., len(deg_sequence),
    corresponding to their position in deg_sequence.

    See Theorem 1.4 in [chartrand-graphs-1996].
    This algorithm is also used in the function is_valid_degree_sequence.

    References:

    [chartrand-graphs-1996] G. Chartrand and L. Lesniak, "Graphs and Digraphs",
                            Chapman and Hall/CRC, 1996.

    """
    if not is_valid_degree_sequence(deg_sequence):
        raise NX.NetworkXError, 'Invalid degree sequence'

    if not seed is None:
        random.seed(seed)

    N=len(deg_sequence)
    G=NX.empty_graph(N) # always return a simple graph

    if N==0 or max(deg_sequence)==0: # done if no edges
        return G 
 
    # form list of [stubs,name] for each node.
    stublist=[ [deg_sequence[n-1],n] for n in G]
    #  Now connect the stubs
    while stublist:
        stublist.sort()
        if stublist[0][0]<0: # took too many off some vertex
            return False     # should not happen if deg_seq is valid

        (freestubs,source) = stublist.pop() # the node with the most stubs
        if freestubs==0: break          # the rest must also be 0 --Done!
        if freestubs > len(stublist):  # Trouble--can't make that many edges
            return False               # should not happen if deg_seq is valid

        # attach edges to biggest nodes
        for stubtarget in stublist[-freestubs:]:
            G.add_edge(source, stubtarget[1])  
            stubtarget[0] -= 1  # updating stublist on the fly
    
    G.name="havel_hakimi_graph %d nodes %d edges"%(G.order(),G.size())
    return G

def degree_sequence_tree(deg_sequence):
    """
    Make a tree for the given degree sequence.

    A tree has #nodes-#edges=1 so
    the degree sequence must have
    len(deg_sequence)-sum(deg_sequence)/2=1
    """

    if not len(deg_sequence)-sum(deg_sequence)/2.0 == 1.0:
        raise NX.NetworkXError,"Degree sequence not a tree"

    G=NX.Graph()
    # single node tree
    if len(deg_sequence)==1:
        G.add_node(1)
        return G

    deg=[s for s in deg_sequence if s>1] # all degrees greater than 1
    deg.sort(reverse=True)

    # make path graph as backbone
    n=len(deg)+2
    G=NX.path_graph(n)
    last=n

    # add the leaves
    for source in range(2,n):
        nedges=deg.pop()-1
        for target in range(1,nedges):
            G.add_edge(source, last+target)
        last+=nedges
        
    # in case we added one too many 
    if len(G.degree())>len(deg_sequence): 
        G.delete_node(1)
    return G
        

def is_valid_degree_sequence(deg_sequence):
    """Return True if deg_sequence is a valid sequence of integer degrees
    equal to the degree sequence of some simple graph.
       
      - `deg_sequence`: degree sequence, a list of integers with each entry
         corresponding to the degree of a node (need not be sorted).
         A non-graphical degree sequence (i.e. one not realizable by some
         simple graph) will raise an exception.
                        
    See Theorem 1.4 in [chartrand-graphs-1996]. This algorithm is also used
    in havel_hakimi_graph()

    References:

    [chartrand-graphs-1996] G. Chartrand and L. Lesniak, "Graphs and Digraphs",
                            Chapman and Hall/CRC, 1996.

    """
    # some simple tests 
    if deg_sequence==[]:
        return True # empty sequence = empty graph 
    if not NX.utils.is_list_of_ints(deg_sequence):
        return False   # list of ints
    if min(deg_sequence)<0:
        return False      # each int not negative
    if sum(deg_sequence)%2:
        return False      # must be even
    
    # successively reduce degree sequence by removing node of maximum degree
    # as in Havel-Hakimi algorithm
        
    s=deg_sequence[:]  # copy to s
    while s:      
        s.sort()    # sort in non-increasing order
        if s[0]<0: 
            return False  # check if removed too many from some node

        d=s.pop()             # pop largest degree 
        if d==0: return True  # done! rest must be zero due to ordering

        # degree must be <= number of available nodes
        if d>len(s):   return False

        # remove edges to nodes of next higher degrees
        s.reverse()  # to make it easy to get at higher degree nodes.
        for i in range(d):
            s[i]-=1

    # should never get here b/c either d==0, d>len(s) or d<0 before s=[]
    return False


def create_degree_sequence(n, sfunction=None, max_tries=50, **kwds):
    """ Attempt to create a valid degree sequence of length n using
    specified function sfunction(n,kwds).

      - `n`: length of degree sequence = number of nodes
      - `sfunction`: a function, called as "sfunction(n,kwds)",
         that returns a list of n real or integer values.
      - `max_tries`: max number of attempts at creating valid degree
         sequence.

    Repeatedly create a degree sequence by calling sfunction(n,kwds)
    until achieving a valid degree sequence. If unsuccessful after
    max_tries attempts, raise an exception.
    
    For examples of sfunctions that return sequences of random numbers,
    see NX.Utils.

    >>> from NX.utils import *
    >>> seq=create_degree_sequence(10,uniform_sequence)

    """
    tries=0
    max_deg=n
    while tries < max_tries:
        trialseq=sfunction(n,**kwds)
        # round to integer values in the range [0,max_deg]
        seq=[min(max_deg, max( int(round(s)),0 )) for s in trialseq]
        # if graphical return, else throw away and try again
        if is_valid_degree_sequence(seq):
            return seq
        tries+=1
    raise NX.NetworkXError, "Exceeded max (%d) attempts at a valid sequence."%max_tries


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/generators_degree_seq.txt',package='NX')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
