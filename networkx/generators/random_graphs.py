# -*- coding: utf-8 -*-
"""
Generators for random graphs.

"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult (dschult@colgate.edu)'])
import itertools
import random
import math
import networkx as nx
from networkx.generators.classic import empty_graph, path_graph, complete_graph

from collections import defaultdict

__all__ = ['fast_gnp_random_graph',
           'gnp_random_graph',
           'dense_gnm_random_graph',
           'gnm_random_graph',
           'erdos_renyi_graph',
           'binomial_graph',
           'newman_watts_strogatz_graph',
           'watts_strogatz_graph',
           'connected_watts_strogatz_graph',
           'random_regular_graph',
           'barabasi_albert_graph',
           'powerlaw_cluster_graph',
           'random_lobster',
           'random_shell_graph',
           'random_powerlaw_tree',
           'random_powerlaw_tree_sequence']


#-------------------------------------------------------------------------
#  Some Famous Random Graphs
#-------------------------------------------------------------------------


def fast_gnp_random_graph(n, p, seed=None, directed=False):
    """Return a random graph G_{n,p} (Erdős-Rényi graph, binomial graph).

    Parameters
    ----------
    n : int
        The number of nodes.
    p : float
        Probability for edge creation.
    seed : int, optional
        Seed for random number generator (default=None). 
    directed : bool, optional (default=False)
        If True return a directed graph 
      
    Notes
    -----
    The G_{n,p} graph algorithm chooses each of the [n(n-1)]/2
    (undirected) or n(n-1) (directed) possible edges with probability p.

    This algorithm is O(n+m) where m is the expected number of
    edges m=p*n*(n-1)/2.
    
    It should be faster than gnp_random_graph when p is small and
    the expected number of edges is small (sparse graph).

    See Also
    --------
    gnp_random_graph

    References
    ----------
    .. [1] Vladimir Batagelj and Ulrik Brandes, 
       "Efficient generation of large random networks",
       Phys. Rev. E, 71, 036113, 2005.
    """
    G = empty_graph(n)
    G.name="fast_gnp_random_graph(%s,%s)"%(n,p)

    if not seed is None:
        random.seed(seed)

    if p <= 0 or p >= 1:
        return nx.gnp_random_graph(n,p,directed=directed)

    v = 1  # Nodes in graph are from 0,n-1 (this is the second node index).
    w = -1
    lp = math.log(1.0 - p)  

    if directed:
        G=nx.DiGraph(G)
        while v < n:
            lr = math.log(1.0 - random.random())
            w = w + 1 + int(lr/lp)
            if v == w: # avoid self loops
                w = w + 1
            while  w >= n and v < n:
                w = w - n
                v = v + 1
                if v == w: # avoid self loops
                    w = w + 1
            if v < n:
                G.add_edge(v, w)
    else:
        while v < n:
            lr = math.log(1.0 - random.random())
            w = w + 1 + int(lr/lp)
            while w >= v and v < n:
                w = w - v
                v = v + 1
            if v < n:
                G.add_edge(v, w)
    return G


def gnp_random_graph(n, p, seed=None, directed=False):
    """Return a random graph G_{n,p} (Erdős-Rényi graph, binomial graph).

    Chooses each of the possible edges with probability p.

    This is also called binomial_graph and erdos_renyi_graph. 

    Parameters
    ----------
    n : int
        The number of nodes.
    p : float
        Probability for edge creation.
    seed : int, optional
        Seed for random number generator (default=None). 
    directed : bool, optional (default=False)
        If True return a directed graph 
    
    See Also  
    --------
    fast_gnp_random_graph

    Notes
    -----
    This is an O(n^2) algorithm.  For sparse graphs (small p) see
    fast_gnp_random_graph for a faster algorithm.

    References
    ----------
    .. [1] P. Erdős and A. Rényi, On Random Graphs, Publ. Math. 6, 290 (1959).
    .. [2] E. N. Gilbert, Random Graphs, Ann. Math. Stat., 30, 1141 (1959).
    """
    if directed:
        G=nx.DiGraph()
    else:
        G=nx.Graph()
    G.add_nodes_from(range(n))
    G.name="gnp_random_graph(%s,%s)"%(n,p)
    if p<=0:
        return G
    if p>=1:
        return complete_graph(n,create_using=G)

    if not seed is None:
        random.seed(seed)

    if G.is_directed():
        edges=itertools.permutations(range(n),2)
    else:
        edges=itertools.combinations(range(n),2)

    for e in edges:
        if random.random() < p:        
            G.add_edge(*e)
    return G


# add some aliases to common names
binomial_graph=gnp_random_graph
erdos_renyi_graph=gnp_random_graph

def dense_gnm_random_graph(n, m, seed=None):
    """Return the random graph G_{n,m}.

    Gives a graph picked randomly out of the set of all graphs
    with n nodes and m edges.
    This algorithm should be faster than gnm_random_graph for dense graphs.

    Parameters
    ----------
    n : int
        The number of nodes.
    m : int
        The number of edges.
    seed : int, optional
        Seed for random number generator (default=None). 
      
    See Also
    --------
    gnm_random_graph()

    Notes
    -----
    Algorithm by Keith M. Briggs Mar 31, 2006.
    Inspired by Knuth's Algorithm S (Selection sampling technique),
    in section 3.4.2 of [1]_.

    References
    ----------
    .. [1] Donald E. Knuth, The Art of Computer Programming,
        Volume 2/Seminumerical algorithms, Third Edition, Addison-Wesley, 1997.
    """
    mmax=n*(n-1)/2
    if m>=mmax:
        G=complete_graph(n)
    else:
        G=empty_graph(n)
    G.name="dense_gnm_random_graph(%s,%s)"%(n,m)
  
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
            if k==m: return G
        t+=1
        v+=1
        if v==n: # go to next row of adjacency matrix
            u+=1
            v=u+1

def gnm_random_graph(n, m, seed=None, directed=False):
    """Return the random graph G_{n,m}.

    Produces a graph picked randomly out of the set of all graphs
    with n nodes and m edges.

    Parameters
    ----------
    n : int
        The number of nodes.
    m : int
        The number of edges.
    seed : int, optional
        Seed for random number generator (default=None). 
    directed : bool, optional (default=False)
        If True return a directed graph 
    """
    if directed:
        G=nx.DiGraph()
    else:
        G=nx.Graph()
    G.add_nodes_from(range(n))
    G.name="gnm_random_graph(%s,%s)"%(n,m)

    if seed is not None:
        random.seed(seed)

    if n==1:
        return G
    max_edges=n*(n-1)
    if not directed:
        max_edges/=2.0
    if m>=max_edges:
        return complete_graph(n,create_using=G)

    nlist=G.nodes()
    edge_count=0
    while edge_count < m:
        # generate random edge,u,v
        u = random.choice(nlist)
        v = random.choice(nlist)
        if u==v or G.has_edge(u,v):
            continue
        else:
            G.add_edge(u,v)
            edge_count=edge_count+1
    return G


def newman_watts_strogatz_graph(n, k, p, create_using=None, seed=None):
    """Return a Newman-Watts-Strogatz small world graph.

    Parameters
    ----------
    n : int
        The number of nodes
    k : int
        Each node is connected to k nearest neighbors in ring topology
    p : float 
        The probability of adding a new edge for each edge
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : int, optional        
       seed for random number generator (default=None)

    Notes
    -----
    First create a ring over n nodes.  Then each node in the ring is
    connected with its k nearest neighbors (k-1 neighbors if k is odd).  
    Then shortcuts are created by adding new edges as follows: 
    for each edge u-v in the underlying "n-ring with k nearest neighbors" 
    with probability p add a new edge u-w with randomly-chosen existing 
    node w.  In contrast with watts_strogatz_graph(), no edges are removed.

    See Also
    --------
    watts_strogatz_graph()

    References
    ----------
    .. [1] M. E. J. Newman and D. J. Watts,
       Renormalization group analysis of the small-world network model,
       Physics Letters A, 263, 341, 1999.
       http://dx.doi.org/10.1016/S0375-9601(99)00757-4
    """
    if seed is not None:
        random.seed(seed)
    if k>=n // 2: 
        raise nx.NetworkXError("k>=n/2, choose smaller k or larger n")
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    G=empty_graph(n,create_using)
    G.name="newman_watts_strogatz_graph(%s,%s,%s)"%(n,k,p)
    nlist = G.nodes()
    fromv = nlist
    # connect the k/2 neighbors
    for n in range(1, k // 2+1):
        tov = fromv[n:] + fromv[0:n] # the first n are now last
        for i in range(len(fromv)):
            G.add_edge(fromv[i], tov[i])
    # for each edge u-v, with probability p, randomly select existing
    # node w and add new edge u-w 
    e = G.edges() 
    for (u, v) in e:
        if random.random() < p:
            w = random.choice(nlist)
            # no self-loops and reject if edge u-w exists
            # is that the correct NWS model?
            while w == u or G.has_edge(u, w): 
                w = random.choice(nlist)
            G.add_edge(u,w)
    return G            


def watts_strogatz_graph(n, k, p, create_using=None, seed=None):
    """Return a Watts-Strogatz small-world graph.


    Parameters
    ----------
    n : int
        The number of nodes
    k : int
        Each node is connected to k nearest neighbors in ring topology
    p : float 
        The probability of rewiring each edge 
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : int, optional        
        Seed for random number generator (default=None)

    See Also
    --------
    newman_watts_strogatz_graph()
    connected_watts_strogatz_graph()

    Notes
    -----
    First create a ring over n nodes.  Then each node in the ring is
    connected with its k nearest neighbors (k-1 neighbors if k is odd).  
    Then shortcuts are created by replacing some edges as follows: 
    for each edge u-v in the underlying "n-ring with k nearest neighbors" 
    with probability p replace it with a new edge u-w with uniformly 
    random choice of existing node w.  

    In contrast with newman_watts_strogatz_graph(), the random
    rewiring does not increase the number of edges. The rewired graph
    is not guaranteed to be connected as in  connected_watts_strogatz_graph().

    References
    ----------
    .. [1] Duncan J. Watts and Steven H. Strogatz,
       Collective dynamics of small-world networks,
       Nature, 393, pp. 440--442, 1998.
    """
    if k>=n/2: 
        raise nx.NetworkXError("k>=n/2, choose smaller k or larger n")
    if create_using is None:
        G = nx.Graph()
    elif create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    else:
        G = create_using
        G.clear()

    if seed is not None:
        random.seed(seed)

    G.name="watts_strogatz_graph(%s,%s,%s)"%(n,k,p)
    nodes = list(range(n)) # nodes are labeled 0 to n-1
    # connect each node to k/2 neighbors
    for j in range(1, k // 2+1):
        targets = nodes[j:] + nodes[0:j] # first j nodes are now last in list
        G.add_edges_from(zip(nodes,targets))
    # rewire edges from each node
    # loop over all nodes in order (label) and neighbors in order (distance)
    # no self loops or multiple edges allowed
    for j in range(1, k // 2+1): # outer loop is neighbors
        targets = nodes[j:] + nodes[0:j] # first j nodes are now last in list
        # inner loop in node order
        for u,v in zip(nodes,targets): 
            if random.random() < p:
                w = random.choice(nodes)
                # Enforce no self-loops or multiple edges
                while w == u or G.has_edge(u, w): 
                    w = random.choice(nodes)
                G.remove_edge(u,v)  
                G.add_edge(u,w)
    return G            

def connected_watts_strogatz_graph(n, k, p, tries=100, create_using=None, seed=None):
    """Return a connected Watts-Strogatz small-world graph.

    Attempt to generate a connected realization by repeated 
    generation of Watts-Strogatz small-world graphs.  
    An exception is raised if the maximum number of tries is exceeded.

    Parameters
    ----------
    n : int
        The number of nodes
    k : int
        Each node is connected to k nearest neighbors in ring topology
    p : float 
        The probability of rewiring each edge 
    tries : int
        Number of attempts to generate a connected graph.  
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : int, optional
         The seed for random number generator.

    See Also
    --------
    newman_watts_strogatz_graph()
    watts_strogatz_graph()

    """
    G = watts_strogatz_graph(n, k, p, create_using, seed)
    t=1
    while not nx.is_connected(G):
        G = watts_strogatz_graph(n, k, p, create_using, seed)
        t=t+1
        if t>tries:
            raise nx.NetworkXError("Maximum number of tries exceeded")
    return G


def random_regular_graph(d, n, create_using=None, seed=None):
    """Return a random regular graph of n nodes each with degree d.
    
    The resulting graph G has no self-loops or parallel edges.

    Parameters
    ----------
    d : int
      Degree
    n : integer
      Number of nodes. The value of n*d must be even.
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : hashable object
        The seed for random number generator.

    Notes
    -----
    The nodes are numbered form 0 to n-1.


    Kim and Vu's paper [2]_ shows that this algorithm samples in an
    asymptotically uniform way from the space of random graphs when
    d = O(n**(1/3-epsilon)).

    References
    ----------
    .. [1] A. Steger and N. Wormald,
       Generating random regular graphs quickly,
       Probability and Computing 8 (1999), 377-396, 1999.
       http://citeseer.ist.psu.edu/steger99generating.html

    .. [2] Jeong Han Kim and Van H. Vu,
       Generating random regular graphs,
       Proceedings of the thirty-fifth ACM symposium on Theory of computing,
       San Diego, CA, USA, pp 213--222, 2003.
       http://portal.acm.org/citation.cfm?id=780542.780576
    """
    if (n * d) % 2 != 0:
        raise nx.NetworkXError("n * d must be even")

    if not 0 <= d < n:
        raise nx.NetworkXError("the 0 <= d < n inequality must be satisfied")

    if create_using is None:
        G = nx.Graph()
    elif create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    else:
        G = create_using
        G.clear()

    if seed is not None:
        random.seed(seed)

    def _suitable(edges, potential_edges):
    # Helper subroutine to check if there are suitable edges remaining 
    # If False, the generation of the graph has failed         
        if not potential_edges:
            return True
        for s1 in potential_edges:
            for s2 in potential_edges:
                # Two iterators on the same dictionary are guaranteed
                # to visit it in the same order if there are no
                # intervening modifications.
                if s1 == s2:
                    # Only need to consider s1-s2 pair one time
                    break
                if s1 > s2:
                    s1, s2 = s2, s1
                if (s1, s2) not in edges:
                    return True
        return False

    def _try_creation():
        # Attempt to create an edge set

        edges = set()
        stubs = list(range(n)) * d

        while stubs:
            potential_edges = defaultdict(lambda: 0)
            random.shuffle(stubs)
            stubiter = iter(stubs)
            for s1, s2 in zip(stubiter, stubiter):
                if s1 > s2:
                    s1, s2 = s2, s1
                if s1 != s2 and ((s1, s2) not in edges):
                    edges.add((s1, s2))
                else:
                    potential_edges[s1] += 1
                    potential_edges[s2] += 1

            if not _suitable(edges, potential_edges):
                return None # failed to find suitable edge set

            stubs = [node for node, potential in potential_edges.items()
                     for _ in range(potential)]
        return edges 

    # Even though a suitable edge set exists, 
    # the generation of such a set is not guaranteed. 
    # Try repeatedly to find one.
    edges = _try_creation()
    while edges is None:
        edges = _try_creation()
    
    G.name = "random_regular_graph(%s, %s)" % (d, n)
    G.add_edges_from(edges)

    return G

def _random_subset(seq,m):
    """ Return m unique elements from seq.

    This differs from random.sample which can return repeated
    elements if seq holds repeated elements.
    """
    targets=set()
    while len(targets)<m:
        x=random.choice(seq)
        targets.add(x)
    return targets
    
def barabasi_albert_graph(n, m, create_using=None, seed=None):
    """Return random graph using Barabási-Albert preferential attachment model.
        
    A graph of n nodes is grown by attaching new nodes each with m
    edges that are preferentially attached to existing nodes with high
    degree.
    
    Parameters
    ----------
    n : int
        Number of nodes
    m : int
        Number of edges to attach from a new node to existing nodes
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : int, optional
        Seed for random number generator (default=None).   

    Returns
    -------
    G : Graph
        
    Notes
    -----
    The initialization is a graph with with m nodes and no edges.

    References
    ----------
    .. [1] A. L. Barabási and R. Albert "Emergence of scaling in
       random networks", Science 286, pp 509-512, 1999.
    """
        
    if m < 1 or  m >=n:
        raise nx.NetworkXError(\
              "Barabási-Albert network must have m>=1 and m<n, m=%d,n=%d"%(m,n))

    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")

    if seed is not None:
        random.seed(seed)    

    # Add m initial nodes (m0 in barabasi-speak) 
    G=empty_graph(m,create_using)  
    G.name="barabasi_albert_graph(%s,%s)"%(n,m)
    # Target nodes for new edges
    targets=list(range(m))
    # List of existing nodes, with nodes repeated once for each adjacent edge 
    repeated_nodes=[]     
    # Start adding the other n-m nodes. The first node is m.
    source=m 
    while source<n: 
        # Add edges to m nodes from the source.
        G.add_edges_from(zip([source]*m,targets)) 
        # Add one node to the list for each new edge just created.
        repeated_nodes.extend(targets)
        # And the new node "source" has m edges to add to the list.
        repeated_nodes.extend([source]*m) 
        # Now choose m unique nodes from the existing nodes 
        # Pick uniformly from repeated_nodes (preferential attachement) 
        targets = _random_subset(repeated_nodes,m)
        source += 1
    return G

def powerlaw_cluster_graph(n, m, p, create_using=None, seed=None):
    """Holme and Kim algorithm for growing graphs with powerlaw
    degree distribution and approximate average clustering. 

    Parameters
    ----------
    n : int
        the number of nodes
    m : int
        the number of random edges to add for each new node
    p : float,
        Probability of adding a triangle after adding a random edge
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : int, optional
        Seed for random number generator (default=None).   
      
    Notes
    -----
    The average clustering has a hard time getting above 
    a certain cutoff that depends on m.  This cutoff is often quite low.
    Note that the transitivity (fraction of triangles to possible
    triangles) seems to go down with network size. 

    It is essentially the Barabási-Albert (B-A) growth model with an
    extra step that each random edge is followed by a chance of
    making an edge to one of its neighbors too (and thus a triangle).
    
    This algorithm improves on B-A in the sense that it enables a
    higher average clustering to be attained if desired. 

    It seems possible to have a disconnected graph with this algorithm
    since the initial m nodes may not be all linked to a new node
    on the first iteration like the B-A model.

    References
    ----------
    .. [1] P. Holme and B. J. Kim,
       "Growing scale-free networks with tunable clustering",
       Phys. Rev. E, 65, 026107, 2002.
    """

    if m < 1 or n < m:
        raise nx.NetworkXError(\
              "NetworkXError must have m>1 and m<n, m=%d,n=%d"%(m,n))

    if p > 1 or p < 0:
        raise nx.NetworkXError(\
              "NetworkXError p must be in [0,1], p=%f"%(p))

    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")

    if seed is not None:
        random.seed(seed)    

    G=empty_graph(m,create_using) # add m initial nodes (m0 in barabasi-speak)
    G.name="Powerlaw-Cluster Graph"
    repeated_nodes=G.nodes()  # list of existing nodes to sample from
                           # with nodes repeated once for each adjacent edge 
    source=m               # next node is m
    while source<n:        # Now add the other n-1 nodes
        possible_targets = _random_subset(repeated_nodes,m)
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

def random_lobster(n, p1, p2, create_using=None, seed=None):
    """Return a random lobster.

     A lobster is a tree that reduces to a caterpillar when pruning all
     leaf nodes.

     A caterpillar is a tree that reduces to a path graph when pruning
     all leaf nodes (p2=0).
     
    Parameters
    ----------
    n : int
        The expected number of nodes in the backbone
    p1 : float
        Probability of adding an edge to the backbone
    p2 : float
        Probability of adding an edge one level beyond backbone
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : int, optional
        Seed for random number generator (default=None).   
    """
    # a necessary ingredient in any self-respecting graph library
    if seed is not None:
        random.seed(seed)
    llen=int(2*random.random()*n + 0.5)
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    L=path_graph(llen,create_using)
    L.name="random_lobster(%d,%s,%s)"%(n,p1,p2)
    # build caterpillar: add edges to path graph with probability p1
    current_node=llen-1
    for n in range(llen):
        if random.random()<p1: # add fuzzy caterpillar parts
            current_node+=1
            L.add_edge(n,current_node)
            if random.random()<p2: # add crunchy lobster bits
                current_node+=1
                L.add_edge(current_node-1,current_node)
    return L # voila, un lobster!

def random_shell_graph(constructor, create_using=None, seed=None):
    """Return a random shell graph for the constructor given.

    Parameters
    ----------
    constructor: a list of three-tuples 
        (n,m,d) for each shell starting at the center shell.
    n : int
        The number of nodes in the shell
    m : int
        The number or edges in the shell
    d : float
        The ratio of inter-shell (next) edges to intra-shell edges.
        d=0 means no intra shell edges, d=1 for the last shell
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : int, optional
        Seed for random number generator (default=None).   
      
    Examples
    --------
    >>> constructor=[(10,20,0.8),(20,40,0.8)]
    >>> G=nx.random_shell_graph(constructor)        

    """
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    G=empty_graph(0,create_using)
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
        g=nx.convert_node_labels_to_integers(
            gnm_random_graph(n,inter_edges),
            first_label=nnodes)
        glist.append(g)
        nnodes+=n                     
        G=nx.operators.union(G,g)

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


def random_powerlaw_tree(n, gamma=3, create_using=None, seed=None, tries=100):
    """Return a tree with a powerlaw degree distribution.

    Parameters
    ----------
    n : int,
        The number of nodes
    gamma : float
        Exponent of the power-law
    create_using : graph, optional (default Graph)
        The graph instance used to build the graph.
    seed : int, optional
        Seed for random number generator (default=None).   
    tries : int
        Number of attempts to adjust sequence to make a tree 

    Notes
    -----
    A trial powerlaw degree sequence is chosen and then elements are
    swapped with new elements from a powerlaw distribution until
    the sequence makes a tree (#edges=#nodes-1).  

    """
    from networkx.generators.degree_seq import degree_sequence_tree
    try:
        s=random_powerlaw_tree_sequence(n,
                                        gamma=gamma,
                                        seed=seed,
                                        tries=tries)
    except:
        raise nx.NetworkXError(\
              "Exceeded max (%d) attempts for a valid tree sequence."%tries)
    G=degree_sequence_tree(s,create_using)
    G.name="random_powerlaw_tree(%s,%s)"%(n,gamma)
    return G


def random_powerlaw_tree_sequence(n, gamma=3, seed=None, tries=100):
    """ Return a degree sequence for a tree with a powerlaw distribution.

    Parameters
    ----------
    n : int,
        The number of nodes
    gamma : float
        Exponent of the power-law
    seed : int, optional
        Seed for random number generator (default=None).   
    tries : int
        Number of attempts to adjust sequence to make a tree 

    Notes
    -----
    A trial powerlaw degree sequence is chosen and then elements are
    swapped with new elements from a powerlaw distribution until
    the sequence makes a tree (#edges=#nodes-1).  


    """
    if seed is not None:
        random.seed(seed)

    # get trial sequence        
    z=nx.utils.powerlaw_sequence(n,exponent=gamma)
    # round to integer values in the range [0,n]
    zseq=[min(n, max( int(round(s)),0 )) for s in z]
    
    # another sequence to swap values from
    z=nx.utils.powerlaw_sequence(tries,exponent=gamma)
    # round to integer values in the range [0,n]
    swap=[min(n, max( int(round(s)),0 )) for s in z]

    for deg in swap:
        if n-sum(zseq)/2.0 == 1.0: # is a tree, return sequence
            return zseq
        index=random.randint(0,n-1)
        zseq[index]=swap.pop()
        
    raise nx.NetworkXError(\
          "Exceeded max (%d) attempts for a valid tree sequence."%tries)
    return False

