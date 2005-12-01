"""
Generators for random graphs

"""
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-17 08:06:22 -0600 (Fri, 17 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1049 $"
import random
import networkx
from networkx.generators.classic import empty_graph, path_graph, complete_graph

#-------------------------------------------------------------------------
#  Some Famous Random Graphs
#-------------------------------------------------------------------------

def binomial_graph(n,p,seed=None):
    """
    Return a binomial random graph G_{n,p}.

    :Parameters:
      - `n`: the number of nodes
      - `p`: probability that any given edge exist
      - `seed`: seed for random number generator (default=None)
      
    """
    G=empty_graph(n)
    G.name="Binomial Graph"

    if not seed is None:
        random.seed(seed)

    for u in xrange(1,n+1):
        for v in xrange(u+1,n+1):
            if random.random() < p: G.add_edge(u,v)
    return G

def erdos_renyi_graph(n,m,seed=None):
    """
    Return the Erdos-Renyi random graph  G_{n,m}.

    :Parameters:
      - `n`: the number of nodes
      - `m`: the number of edges
      - `seed`: seed for random number generator (default=None)
      
    """
    G=empty_graph(n)
    G.name="Erdos-Renyi Graph"

    if not seed is None:
        random.seed(seed)

    if n==1: return G

    if m>=n*(n-1)/2: return complete_graph(n)

    nlist=G.nodes()
    edge_count=0
    while edge_count < m:
        # generate random edge
        u = random.choice(nlist)
        v = random.choice(nlist)
        if u==v or G.has_edge(u,v):
            continue
        else:
            G.add_edge(u,v)
            edge_count=edge_count+1
    return G

def newman_watts_strogatz_graph(n,k,p,seed=None):
    """
    Return a Newman-Watts-Strogatz small world graph.

    The graph is a ring with k neighbors with new edges (shortcuts)
    *added* randomly with probability p for each edge.  No edges
    are removed.

    :Parameters:
      - `n`: the number of nodes
      - `k`: each vertex is connected to k neighbors in the circular topology
      - `p`: the probability of adding a new edge for each edge
      - `seed`: seed for random number generator (default=None)
      
    """
    if not seed is None:
        random.seed(seed)
    G=empty_graph(n)
    G.name="Newmann-Watts-Strogatz Graph"
    nlist = G.nodes()
    fromv = nlist
    # connect the k/2 neighbors
    for n in range(1, k/2+1):
        tov = fromv[n:] + fromv[0:n] # the first n are now last
        for i in range(len(fromv)):
            G.add_edge(fromv[i], tov[i])
    # randomly connect nodes with probability p
    e = G.edges()
    for (u, v) in e:
        if random.random() < p:
            v = random.choice(nlist)
            # no G loops and we want a new edge
            # is that the correct NWS model?
            while v == u or G.has_edge(u, v): 
                v = random.choice(nlist)
            G.add_edge(u,v)
    return G            

def watts_strogatz_graph(n,k,p,seed=None):
    """
    Return a Watts-Strogatz small world graph.

    The graph is a ring with k neighbors with
    edges rewired randomly with probability p.

    :Parameters:
      - `n`: the number of nodes
      - `k`: each vertex is connected to k neighbors in the circular topology
      - `p`: the probability of rewiring an edge
      - `seed`: seed for random number generator (default=None)
      
    """
    if not seed is None:
        random.seed(seed)
    G=empty_graph(n)
    G.name="Watts-Strogatz Graph"
    nlist = G.nodes()
    fromv = nlist
    # connect the k/2 neighbors
    for n in range(1, k/2+1):
        tov = fromv[n:] + fromv[0:n] # the first n are now last
        for i in range(len(fromv)):
            G.add_edge(fromv[i], tov[i])
    # randomly rewire nodes with probability p
    e = G.edges()
    for (u, v) in e:
        if random.random() < p:
            newv = random.choice(nlist)
            # no G loops and we want a new edge
            # is that the correct WS model?
            while newv == u or G.has_edge(u, newv): 
                newv = random.choice(nlist)
            G.delete_edge(u,v)
            G.add_edge(u,newv)
    return G            



def random_regular_graph(d,n,seed=None):
    """Return a random regular graph of n nodes each with degree d, G_{n,d}.
    Return False if unsuccessful.
    
    n*d must be even

    Nodes are numbered 0...n-1. 
    To get a uniform sample from the space of random graphs
    you should chose d<n^{1/3}.
    .
    For algorith see Kim and Vu's paper.

    Reference::

       @inproceedings{kim-2003-generating,
       author = {Jeong Han Kim and Van H. Vu},
       title = {Generating random regular graphs},
       booktitle = {Proceedings of the thirty-fifth ACM symposium on Theory of computing},
       year = {2003},
       isbn = {1-58113-674-9},
       pages = {213--222},
       location = {San Diego, CA, USA},
       doi = {http://doi.acm.org/10.1145/780542.780576},
       publisher = {ACM Press},
       }

    The algorithm is based on an earlier paper::

       @misc{ steger-1999-generating,
       author = "A. Steger and N. Wormald",
       title = "Generating random regular graphs quickly",
       text = "Probability and Computing 8 (1999), 377-396.",
       year = "1999",
       url = "citeseer.ist.psu.edu/steger99generating.html",
       }

    """
    # helper subroutine to check for suitable edges
    def _suitable(stubs):
        for s in stubs:
            for t in stubs:
                if not seen_edges[s].has_key(t) and s!=t:
                    return True

        # else no suitable possible edges
        return False  
    
    if not n*d%2==0:
        raise networkx.NetworkXError, "n * d must be even"

    if not seed is None:
        random.seed(seed)    

    G=empty_graph(0)

    nlist=range(0,n)
    G.add_nodes_from(nlist)

    # keep track of the edges we have seen
    seen_edges={}
    [seen_edges.setdefault(v,{}) for v in nlist]

    vv=[ [v]*d for v in nlist ]   # List of degree-repeated vertex numbers
    stubs=reduce(lambda x,y: x+y ,vv)  # flatten the list of lists to a list

    while len(stubs) > 0:
       source=random.choice(stubs)
       target=random.choice(stubs)
       if source!=target and not seen_edges[source].has_key(target):
           stubs.remove(source)
           stubs.remove(target)
           seen_edges[source][target]=1
           seen_edges[target][source]=1
           G.add_edge(source,target)
       else:
           # further check to see if suitable 
           s=_suitable(stubs)
           if not s:                   
#               print "Warning: not a regular graph"
#               print "unsuitable stubs left",stubs," with existing edges:"
#               for s in stubs:
#                   print s,G.edges(s)
               return False
               
       
    return G



def barabasi_albert_graph(n,m,seed=None):
    """Return random graph using Barabasi-Albert preferential attachment model.
    
    A graph of n nodes is grown by attaching new nodes
    each with m edges that are preferentially attached
    to existing nodes with high degree.
    
    :Parameters:
      - `n`: the number of nodes
      - `m`: average degree and must be an positive integer
      - `seed`: seed for random number generator (default=None)

    The initialization is a graph with with m nodes.

    Reference::

      @ARTICLE{barabasi-1999-emergence,
      TITLE = {Emergence of scaling in random networks},
      AUTHOR = {A. L. Barabasi and R. Albert},
      JOURNAL = {SCIENCE},
      VOLUME = {286},
      NUMBER = {5439},
      PAGES = {509 -- 512},
      MONTH = {OCT},
      YEAR = {1999},
      }


    """
        
    if m < 1 or n < m:
        raise networkx.NetworkXError,\
              "NetworkXError must have m>1 and m<n, m=%d,n=%d"%(m,n)

    if not seed is None:
        random.seed(seed)    

    G=empty_graph(0)
    edge_targets=range(0,m)  
    G.add_nodes_from(edge_targets) # add m initial nodes (m0 in barabasi-speak)
    # list of existing nodes, with nodes repeated once for each adjacent edge 
    existing_nodes=[]
    source=m            # next node is m
    while source<n:     # Now add the other n-1 nodes
        G.add_edges_from(zip([source]*m,edge_targets))
        existing_nodes.extend(edge_targets) 
        existing_nodes.extend([source]*m)
        # choose m nodes randomly from existing nodes
        edge_targets=random.sample(existing_nodes,m) 
        source += 1
    return G

def powerlaw_cluster_graph(n,m,p,seed=None):
    """
    Holme and Kim algorithm for growing graphs with powerlaw
    degree distribution and approximate average clustering. 

    :Parameters:
      - `n`: the number of nodes
      - `m`: the number of random edges to add for each new node
      - `p`: probability of adding a triangle after adding a random edge
      - `seed`: seed for random number generator (default=None)
      
    Reference::

       @Article{growing-holme-2002,
       author = 	 {P. Holme and B. J. Kim},
       title = 	 {Growing scale-free networks with tunable clustering},
       journal = 	 {Phys. Rev. E},
       year = 	 {2002},
       volume = 	 {65},
       number = 	 {2},
       pages = 	 {026107},
       }

    The average clustering has a hard time getting above 
    a certain cutoff that depends on m.  This cutoff is often quite low.

    It is essentially the Barabasi-Albert growth model with an
    extra step that each random edge is followed by a chance of
    making an edge to one of its neighbors too (and thus a triangle).
    
    This algorithm improves on B-A in the sense that it enables a
    higher average clustering to be attained if desired. The largest
    average clustering seems to be independent of n and attained with
    m=1 and p=1 (cc=0.74 or so).

    """
    if not seed is None:
        random.seed(seed)    

    G=empty_graph(0)

    # initialize
    lookupstub=[0]
    # add m initial nodes (m0 in barabasi-speak)
    m0=m
    G.add_nodes_from(range(0,m0))
    count=m0
    # initialize
    lookupstub=range(0,m0)
    # Now add the other n-1 nodes
    while count<n:
        for mm in xrange(m):
            pick=random.choice(lookupstub)
            lookupstub.extend([pick,count])
            if random.random()<p:
                nbrs=G.neighbors(pick)
                if nbrs:   # any neighbors?
                    pickpick=random.choice(G.neighbors(pick))
                    lookupstub.extend([pickpick,count])
                    G.add_edge(count,pickpick)
            G.add_edge(count,pick)
        count += 1
    return G

def random_lobster(n,p1,p2,seed=None):
    """Return a random lobster.

     A caterpillar is a tree that reduces to a path graph when pruning
     all leave nodes. A lobster is a tree that reduces to a caterpillar
     when pruning all leave nodes.
     
    :Parameters:
      - `n`: the expected number of nodes in the backbone
      - `p1`: probability of adding an edge to the backbone
      - `p2`: probability of adding an edge one level beyond backbone
      - `seed`: seed for random number generator (default=None)

"""
    if not seed is None:
        random.seed(seed)
    L=networkx.Graph()
    len=int(2*random.random()*n + 0.5)
    L=path_graph(len)
    L.name="random_lobster(%d, %5.3f, %5.3f)"%(n,p1,p2)
    # build caterpillar: add edges to path graph with probability p1
    current_node=len
    for n in xrange(1,len+1):
        if random.random()<p1:
            current_node+=1
            L.add_edge(n,current_node)
    # build lobster
    len2=current_node
    for n in xrange(len,len2+1):
        if random.random()<p2:
            current_node+=1
            L.add_edge(n,current_node)
    return L # voila, un lobster!

def random_shell_graph(constructor,seed=None):
    """
    Return a random shell graph for the constructor given.

      - constructor: a list of three-tuples [(n1,m1,d1),(n2,m2,d2),..]
        one for each shell, starting at the center shell.
      - n : the number of nodes in the shell
      - m : the number or edges in the shell
      - d : the ratio of inter (next) shell edges to intra shell edges.
              d=0 means no intra shell edges.
              d=1 for the last shell
      - `seed`: seed for random number generator (default=None)
      
    >>> constructor=[(10,20,0.8),(20,40,0.8)]
    >>> G=random_shell_graph(constructor)        

    """
    G=empty_graph(0)
    G.name="random_shell_graph"

    if not seed is None:
        random.seed(seed)

    glist=[]        
    intra_edges=[]
    nnodes=0
    # create erdos-renyi graphs for each shell
    for (n,m,d) in constructor:
        inter_edges=int(m*d)
        intra_edges.append(m-inter_edges)
        g=networkx.operators.convert_node_labels_to_integers(
                     erdos_renyi_graph(n,inter_edges),
                     first_label=nnodes)
        glist.append(g)
        nnodes+=n                     
        G=networkx.operators.union(G,g)

    # connect the shells randomly         
    for gi in range(len(glist)-1):
        nlist1=glist[gi].nodes()
        nlist2=glist[gi+1].nodes()
        total_edges=intra_edges[gi]
        edge_count=0
        while edge_count < total_edges:
            u = random.choice(nlist1)
            v = random.choice(nlist2)
            if u==v or G.has_edge(u,v):
                continue
            else:
                G.add_edge(u,v)
                edge_count=edge_count+1
    return G


def random_powerlaw_tree(n, gamma=3, seed=None, tries=100):
    """
    Return a tree with a powerlaw degree distribution.

    A trial powerlaw degree sequence is chosen and then elements are
    swapped with new elements from a powerlaw distribution until
    the sequence makes a tree (#edges=#nodes-1).  

    :Parameters:
      - `n`: the number of nodes
      - `gamma`: exponent of power law is gamma
      - `tries`: number of attempts to adjust sequence to make a tree 
      - `seed`: seed for random number generator (default=None)
      
    """
    from networkx.generators.degree_seq import degree_sequence_tree
    try:
        s=random_powerlaw_tree_sequence(n,
                                        gamma=gamma,
                                        seed=seed,
                                        tries=tries)
    except:
        raise networkx.NetworkXError,\
              "Exceeded max (%d) attempts for a valid tree sequence."%tries

    return degree_sequence_tree(s)


def random_powerlaw_tree_sequence(n, gamma=3, seed=None, tries=100):
    """
    Return a degree sequence for a tree with a powerlaw distribution.

    A trial powerlaw degree sequence is chosen and then elements are
    swapped with new elements from a powerlaw distribution until
    the sequence makes a tree (#edges=#nodes-1).  

    :Parameters:
      - `n`: the number of nodes
      - `gamma`: exponent of power law is gamma
      - `tries`: number of attempts to adjust sequence to make a tree 
      - `seed`: seed for random number generator (default=None)
      
    """
    if not seed is None:
        random.seed(seed)

    # get trial sequence        
    z=networkx.utils.powerlaw_sequence(n,exponent=gamma)
    # round to integer values in the range [0,n]
    zseq=[min(n, max( int(round(s)),0 )) for s in z]
    
    # another sequence to swap values from
    z=networkx.utils.powerlaw_sequence(tries,exponent=gamma)
    # round to integer values in the range [0,n]
    swap=[min(n, max( int(round(s)),0 )) for s in z]

    for deg in swap:
        if n-sum(zseq)/2.0 == 1.0: # is a tree, return sequence
            return zseq
        index=random.randint(0,n-1)
        zseq[index]=swap.pop()
        
    raise networkx.NetworkXError, "Exceeded max (%d) attempts for a valid tree sequence."%tries
    return False





def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/generators/random_graphs.txt',package='networkx')
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
    

