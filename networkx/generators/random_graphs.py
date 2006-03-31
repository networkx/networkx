# -*- coding: utf-8 -*-
"""
Generators for random graphs

"""
#    Copyright (C) 2004,2005,2006 by 
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
import math
import networkx
from networkx.generators.classic import empty_graph, path_graph, complete_graph

#-------------------------------------------------------------------------
#  Some Famous Random Graphs
#-------------------------------------------------------------------------


def fast_gnp_random_graph(n,p,seed=None):
    """
    Return a random graph G_{n,p}.

    The G_{n,p} graph choses each of the possible [n(n-1)]/2 edges
    with probability p.

    Sometimes called Erdős-Rényi graph, or binomial graph.

    :Parameters:
      - `n`: the number of nodes
      - `p`: probability for edge creation
      - `seed`: seed for random number generator (default=None)
      
    This algorithm is O(n+m) where m is the expected number of
    edges m=p*n*(n-1)/2.
    
    It should be faster than gnp_random_graph when p is small, and
    the expected number of edges is small, (sparse graph).

    See:

    Batagelj and Brandes, "Efficient generation of large random networks",
    Phys. Rev. E, 71, 036113, 2005.

    """
    G=empty_graph(n)
    G.name="fast_gnp_random_graph(%s,%s)"%(n,p)

    if not seed is None:
        random.seed(seed)

    v=1  # Nodes in graph are from 0,n-1 (this is the second node index).
    w=-1
    lp=math.log(1.0-p)  

    while v<n:
        lr=math.log(1.0-random.random())
        w=w+1+int(lr/lp)
        while w>=v and v<n:
            w=w-v
            v=v+1
        if v<n:
            G.add_edge(v,w)
    return G


def gnp_random_graph(n,p,seed=None):
    """
    Return a random graph G_{n,p}.

    Choses each of the possible [n(n-1)]/2 edges with probability p.
    This is the same as binomial_graph and erdos_renyi_graph. 

    Sometimes called Erdős-Rényi graph, or binomial graph.

    :Parameters:
      - `n`: the number of nodes
      - `p`: probability for edge creation
      - `seed`: seed for random number generator (default=None)
      
    This is an O(n^2) algorithm.  For sparse graphs (small p) see
    fast_gnp_random_graph. 

    P. Erdős and A. Rényi, On Random Graphs, Publ. Math. 6, 290 (1959).
    E. N. Gilbert, Random Graphs, Ann. Math. Stat., 30, 1141 (1959).

    """
    G=empty_graph(n)
    G.name="gnp_random_graph(%s,%s)"%(n,p)

    if not seed is None:
        random.seed(seed)

    for u in xrange(n):
        for v in xrange(u+1,n):
            if random.random() < p:
                G.add_edge(u,v)
    return G

# add some aliases to common names
binomial_graph=gnp_random_graph
erdos_renyi_graph=gnp_random_graph

def dense_gnm_random_graph(n,m,seed=None):
  """
  Return the random graph G_{n,m}.

  Gives a graph picked randomly out of the set of all graphs
  with n nodes and m edges.  .

  :Parameters:
      - `n`: the number of nodes
      - `m`: the number of edges
      - `seed`: seed for random number generator (default=None)

  This algorithms should be faster than gnm_random_graph
  for dense graphs.

  Algorithm by Keith M. Briggs Mar 31, 2006.
  Inspired by Knuth's Algorithm S (Selection sampling technique),
  in section 3.4.2
  The Art of Computer Programming by Donald E. Knuth
  Volume 2 / Seminumerical algorithms
  Third Edition, Addison-Wesley, 1997.
 
  """
  mmax=n*(n-1)/2
  if m>=mmax:
      G=complete_graph(n)
  else:
      G=empty_graph(n)
  G.name="gnm_random_graph(%s,%s)"%(n,m)
  
  if n==1 or m>=mmax:
      return G
  
  if seed is not None:
      random.seed(seed)

  u=0
  v=1
  t=0
  k=0
  while True:
    if random.randrange(mmax-t)<m-k:
      G.add_edge(u,v)
      k+=1
      if k==m:
          return G
    t+=1
    v+=1
    if v==n: # go to next row of adjacency matrix
      u+=1
      v=u+1


def gnm_random_graph(n,m,seed=None):
    """
    Return the random graph G_{n,m}.

    Gives a graph picked randomly out of the set of all graphs
    with n nodes and m edges.

    :Parameters:
        - `n`: the number of nodes
        - `m`: the number of edges
        - `seed`: seed for random number generator (default=None)
    """
    G=empty_graph(n)
    G.name="gnm_random_graph(%s,%s)"%(n,m)

    if seed is not None:
        random.seed(seed)

    if n==1:
        return G

    if m>=n*(n-1)/2:
        return complete_graph(n)

    nlist=G.nodes()
    edge_count=0
    while edge_count < m:
        # generate random edge,u,v
        u = random.choice(nlist)
        v = random.choice(nlist)
        if u==v or G.has_edge(u,v):
            continue
        # is this faster?
        # (u,v)=random.sample(nlist,2)
        #  if G.has_edge(u,v):
        #      continue
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
    if seed is not None:
        random.seed(seed)
    G=empty_graph(n)
    G.name="newman_watts_strogatz_graph(%s,%s,%s)"%(n,k,p)
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
    if seed is not None:
        random.seed(seed)
    G=empty_graph(n)
    G.name="watts_strogatz_graph(%s,%s,%s)"%(n,k,p)
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

    if seed is not None:
        random.seed(seed)    

        
    G=empty_graph(n)
    G.name="random_regular_graph(%s,%s)"%(d,n)

    # keep track of the edges we have seen
    seen_edges={}
    [seen_edges.setdefault(v,{}) for v in range(n)]

    vv=[ [v]*d for v in range(n)]   # List of degree-repeated vertex numbers
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
                return False
    return G



def barabasi_albert_graph(n,m,seed=None):
    """Return random graph using Barabási-Albert preferential attachment model.
    
    A graph of n nodes is grown by attaching new nodes
    each with m edges that are preferentially attached
    to existing nodes with high degree.
    
    :Parameters:
      - `n`: the number of nodes
      - `m`: number of edges to attach from a new node to existing nodes
      - `seed`: seed for random number generator (default=None)

    The initialization is a graph with with m nodes and no edges.

    Reference::

      @article{barabasi-1999-emergence,
      title   = {Emergence of scaling in random networks},
      author  = {A. L. Barabási and R. Albert},
      journal = {Science},
      volume  = {286},
      number  = {5439},
      pages   = {509 -- 512},
      year = {1999},
      }


    """
        
    if m < 1 or n < m:
        raise networkx.NetworkXError,\
              "NetworkXError must have m>1 and m<n, m=%d,n=%d"%(m,n)

    if seed is not None:
        random.seed(seed)    

    G=empty_graph(m)       # add m initial nodes (m0 in barabasi-speak)
    G.name="barabasi_albert_graph(%s,%s)"%(n,m)
    edge_targets=range(m)  # possible targets for new edges
    repeated_nodes=[]      # list of existing nodes,
                           # with nodes repeated once for each adjacent edge 
    source=m               # next node is m
    while source<n:        # Now add the other n-1 nodes
        G.add_edges_from(zip([source]*m,edge_targets)) # add links to m nodes
        repeated_nodes.extend(edge_targets) # add one node for each new link
        repeated_nodes.extend([source]*m) # and new node "source" has m links
        # choose m nodes randomly from existing nodes
        # N.B. during each step of adding a new node the probabilities
        # are fixed, is this correct? or should they be updated.
        # Also, random sampling prevents some parallel edges. 
        edge_targets=random.sample(repeated_nodes,m) 
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
    Note that the transitivity (fraction of triangles to possible
    triangles) seems to go down with network size. 

    It is essentially the Barabási-Albert growth model with an
    extra step that each random edge is followed by a chance of
    making an edge to one of its neighbors too (and thus a triangle).
    
    This algorithm improves on B-A in the sense that it enables a
    higher average clustering to be attained if desired. 

    It seems possible to have a disconnected graph with this algorithm
    since the initial m nodes may not be all linked to a new node
    on the first iteration like the BA model.

    """

    if m < 1 or n < m:
        raise networkx.NetworkXError,\
              "NetworkXError must have m>1 and m<n, m=%d,n=%d"%(m,n)

    if p > 1 or p < 0:
        raise networkx.NetworkXError,\
              "NetworkXError p must be in [0,1], p=%f"%(p)


    if seed is not None:
        random.seed(seed)    

    G=empty_graph(m)       # add m initial nodes (m0 in barabasi-speak)
    G.name="Powerlaw-Cluster Graph"
    repeated_nodes=G.nodes()  # list of existing nodes to sample from
                           # with nodes repeated once for each adjacent edge 
    source=m               # next node is m
    while source<n:        # Now add the other n-1 nodes
        possible_targets=random.sample(repeated_nodes,m)
        # do one preferential attachment for new node
        target=possible_targets.pop()
        G.add_edge(source,target)  
        repeated_nodes.append(target) # add one node to list for each new link
        count=1
        while count<m:  # add m-1 more new links
            if random.random()<p: # clustering step: add triangle 
                neighborhood=[nbr for nbr in G.neighbors(target) \
                               if not G.has_edge(source,nbr) \
                               and not nbr==source]
                if neighborhood: # if there is a neighbor without a link
                    nbr=random.choice(neighborhood)
                    G.add_edge(source,nbr) # add triangle
                    repeated_nodes.append(nbr) 
                    count=count+1
                    continue # go to top of while loop
            # else do preferential attachment step if above fails
            target=possible_targets.pop()
            G.add_edge(source,target) 
            repeated_nodes.append(target) 
            count=count+1

        repeated_nodes.extend([source]*m)  # add source node to list m times
        source += 1
    return G

def random_lobster(n,p1,p2,seed=None):
    """Return a random lobster.

     A caterpillar is a tree that reduces to a path graph when pruning
     all leaf nodes (p2=0).
     A lobster is a tree that reduces to a caterpillar when pruning all
     leaf nodes.
     
    :Parameters:
      - `n`: the expected number of nodes in the backbone
      - `p1`: probability of adding an edge to the backbone
      - `p2`: probability of adding an edge one level beyond backbone
      - `seed`: seed for random number generator (default=None)

"""
    if seed is not None:
        random.seed(seed)
    llen=int(2*random.random()*n + 0.5)
    L=path_graph(llen)
    L.name="random_lobster(%d,%s,%s)"%(n,p1,p2)
    # build caterpillar: add edges to path graph with probability p1
    current_node=llen-1
    for n in xrange(llen):
        if random.random()<p1: # add fuzzy caterpillar parts
            current_node+=1
            L.add_edge(n,current_node)
            if random.random()<p2: # add crunchy lobster bits
                current_node+=1
                L.add_edge(current_node-1,current_node)
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
    G.name="random_shell_graph(constructor)"

    if seed is not None:
        random.seed(seed)

    glist=[]        
    intra_edges=[]
    nnodes=0
    # create gnm graphs for each shell
    for (n,m,d) in constructor:
        inter_edges=int(m*d)
        intra_edges.append(m-inter_edges)
        g=networkx.operators.convert_node_labels_to_integers(
                     gnm_random_graph(n,inter_edges),
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
    G=degree_sequence_tree(s)
    G.name="random_powerlaw_tree(%s,%s)"%(n,gamma)
    return G


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
    if seed is not None:
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
        
    raise networkx.NetworkXError, \
          "Exceeded max (%d) attempts for a valid tree sequence."%tries
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
    

