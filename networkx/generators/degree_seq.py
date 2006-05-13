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
import networkx
import networkx.utils
from networkx.generators.classic import empty_graph
#---------------------------------------------------------------------------
#  Generating Graphs with a given degree sequence
#---------------------------------------------------------------------------

def configuration_model(deg_sequence,seed=None):
    """Return a random pseudograph with the given degree sequence.

      - `deg_sequence`: degree sequence, a list of integers with each entry
                        corresponding to the degree of a node (need not be
                        sorted). A non-graphical degree sequence (i.e. one
                        not realizable by some simple graph) will raise an
                        Exception.
      - `seed`: seed for random number generator (default=None)


    >> z=create_degree_sequence(100,powerlaw_sequence)
    >> G=configuration_model(z)

    The pseudograph G is a networkx.XGraph that allows multiple (parallel) edges
    between nodes and edges that connect nodes to themseves (self loops).

    To remove self-loops:

    >> G.ban_selfloops()
    
    To remove parallel edges:

    >> G.ban_multiedges()

    Steps:

     - Check if deg_sequence is a valid degree sequence.
     - Create N nodes with stubs for attaching edges
     - Randomly select two available stubs and connect them with an edge.

    As described by Newman [newman-2003-structure].
    
    Nodes are labeled 1,.., len(deg_sequence),
    corresponding to their position in deg_sequence.

    This process can lead to duplicate edges and loops, and therefore
    returns a pseudograph type.  You can remove the self-loops and
    parallel edges (see above) with the likely result of
    not getting the exat degree sequence specified.
    This "finite-size effect" decreases as the size of the graph increases.

    References:
    
    [newman-2003-structure]  M.E.J. Newman, "The structure and function
    of complex networks", SIAM REVIEW 45-2, pp 167-256, 2003.
        
    """
    if not is_valid_degree_sequence(deg_sequence):
        raise networkx.NetworkXError, 'Invalid degree sequence'

    if not seed is None:
        random.seed(seed)

    # start with empty N-node graph
    N=len(deg_sequence)
#    G=networkx.empty_graph(N,create_using=networkx.Graph()) # no multiedges or selfloops

    # allow multiedges and selfloops
    G=networkx.empty_graph(N,create_using=networkx.XGraph(multiedges=True, \
                                                          selfloops=True))

    if N==0 or max(deg_sequence)==0: # done if no edges
        return G 

    # build stublist, a list of available degree-repeated stubs
    # e.g. for deg_sequence=[3,2,1,1,1]
    # initially, stublist=[1,1,1,2,2,3,4,5]
    # i.e., node 1 has degree=3 and is repeated 3 times, etc.
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
        raise networkx.NetworkXError, 'Invalid degree sequence'

    if not seed is None:
        random.seed(seed)

    N=len(deg_sequence)
    G=networkx.empty_graph(N) # always return a simple graph

    if N==0 or max(deg_sequence)==0: # done if no edges
        return G 
 
    # form list of [stubs,name] for each node.
    stublist=[ [deg_sequence[n],n] for n in G]
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
        raise networkx.NetworkXError,"Degree sequence invalid"

    G=empty_graph(0)
    # single node tree
    if len(deg_sequence)==1:
        return G
    deg=[s for s in deg_sequence if s>1] # all degrees greater than 1
    deg.sort(reverse=True)

    # make path graph as backbone
    n=len(deg)+2
    G=networkx.path_graph(n)
    last=n

    # add the leaves
    for source in range(1,n-1):
        nedges=deg.pop()-2
        for target in range(last,last+nedges):
            G.add_edge(source, target)
        last+=nedges
        
    # in case we added one too many 
    if len(G.degree())>len(deg_sequence): 
        G.delete_node(0)
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
    if not networkx.utils.is_list_of_ints(deg_sequence):
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
    see networkx.Utils.

    >>> from networkx.utils import *
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
    raise networkx.NetworkXError, \
          "Exceeded max (%d) attempts at a valid sequence."%max_tries

def random_rewire_connected(graph, num_iterations):
    """
       Switches the edges of a connected graphs.
       
       Optimization proposed in:
       @misc{ gkantsidis03markov,
        author = "C. Gkantsidis and M. Mihail and E. Zegura",
        title = "The markov chain simulation method for generating connected power law random
        graphs",
        text = "C. Gkantsidis, M. Mihail, and E. Zegura. The markov chain simulation method
        for generating connected power law random graphs. In Proc. 5th Workshop
        on Algorithm Engineering and Experiments (ALENEX). SIAM, January 2003.",
        year = "2003",
        url = "citeseer.ist.psu.edu/gkantsidis03markov.html" }
    """
    if not networkx.is_connected(graph):
       raise NetworkXException()
    import math
    typenr = 0
    rnd = random.Random()
    window = 1
    window_counter = 0
    graph2 = graph.copy()
    edges = graph.edges()
    if len(edges)<2 : return
    iters = 0
    noupdate = 0
    while iters < num_iterations:
         window_counter += 1
         iters += 1
         counter = 0
         edges = graph2.edges()
         [xy, (u,v)] = rnd.sample(edges, 2) 
     #There needs to be a (x,y) and an (u,v) edge and the endpoints must be distincts
         (x,y) = xy
         while (u in xy or v in xy) and counter < num_iterations*2 :
             [(u,v)] = rnd.sample(edges,1)
             counter += 1
         if counter >= num_iterations*2:
             break
         if noupdate > num_iterations *4:
             break
         if graph2.has_edge(u,x) or graph2.has_edge(v,y):
             window_counter -=1
             iters -=1
             noupdate += 1 
             continue
         
         graph2.delete_edge(x,y)
         graph2.delete_edge(u,v)
         graph2.add_edge(u,x)
         graph2.add_edge(v,y)
         if window_counter >= window:
            newrnd = rnd.random()
            if networkx.is_connected(graph2):
                graph = graph2.copy()
                window_counter = 0
                window += 1
            else :
                graph2 = graph.copy()
                window_counter = 0
                window = math.ceil(float(window)/2)

    if networkx.is_connected(graph2):
       return graph2
    else:
       return graph

def random_rewire(graph, num_iterations=10):
    """
       Randomly rewire the edges of a graphs a set number of times.
    """
    rnd = random.Random()
    window = 1
    window_counter = 0
    graph2 = graph.copy()
    edges = graph.edges()
    if len(edges)<2 : return
    iters = 0
    noupdate = 0
    while iters < num_iterations:
         window_counter += 1
         iters += 1
         counter = 0
         edges = graph2.edges()
         [xy, (u,v)] = rnd.sample(edges, 2) 
     #There needs to be a (x,y) and an (u,v) edge and the endpoints must be distincts
         (x,y) = xy
         while (u in xy or v in xy) and counter < num_iterations*2 :
             [(u,v)] = rnd.sample(edges,1)
             counter += 1
         if counter >= num_iterations*2:
             break
         if noupdate > num_iterations *4:
             break
         if graph2.has_edge(u,x) or graph2.has_edge(v,y):
             window_counter -=1
             iters -=1
             noupdate += 1 
             continue
         
         graph2.delete_edge(x,y)
         graph2.delete_edge(u,v)
         graph2.add_edge(u,x)
         graph2.add_edge(v,y)
    return graph2
   
def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/generators/degree_seq.txt',
                                 package='networkx')
    return suite


if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required (%d.%d detected)." \
              %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    
