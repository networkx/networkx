# -*- coding: utf-8 -*-
"""Generate graphs with a given degree sequence or expected degree sequence.
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import heapq
import math
import random
import networkx as nx
import networkx.utils
from networkx.generators.classic import empty_graph
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult (dschult@colgate.edu)'
                        'Joel Miller (joel.c.miller.research@gmail.com)'
                        'Ben Edwards'])
__all__ = ['configuration_model',
           'directed_configuration_model',
           'expected_degree_graph',
           'havel_hakimi_graph',
           'degree_sequence_tree',
           'random_clustered_graph',
           'is_valid_degree_sequence',
           'is_valid_degree_sequence_erdos_gallai',
           'is_valid_degree_sequence_havel_hakimi',
           'create_degree_sequence',
           'double_edge_swap',
           'connected_double_edge_swap',
           'li_smax_graph']


def configuration_model(deg_sequence,create_using=None,seed=None):
    """Return a random graph with the given degree sequence.

    The configuration model generates a random pseudograph (graph with
    parallel edges and self loops) by randomly assigning edges to
    match the given degree sequence.

    Parameters
    ----------
    deg_sequence :  list of integers 
        Each list entry corresponds to the degree of a node.
    create_using : graph, optional (default MultiGraph)
       Return graph of this type. The instance will be cleared.
    seed : hashable object, optional
        Seed for random number generator.   

    Returns
    -------
    G : MultiGraph
        A graph with the specified degree sequence.
        Nodes are labeled starting at 0 with an index
        corresponding to the position in deg_sequence.

    Raises
    ------
    NetworkXError
        If the degree sequence does not have an even sum.

    See Also
    --------
    is_valid_degree_sequence
    
    Notes
    -----
    As described by Newman [1]_.

    A non-graphical degree sequence (not realizable by some simple
    graph) is allowed since this function returns graphs with self
    loops and parallel edges.  An exception is raised if the degree
    sequence does not have an even sum.

    This configuration model construction process can lead to
    duplicate edges and loops.  You can remove the self-loops and
    parallel edges (see below) which will likely result in a graph
    that doesn't have the exact degree sequence specified.  This
    "finite-size effect" decreases as the size of the graph increases.

    References
    ----------
    .. [1] M.E.J. Newman, "The structure and function of complex networks", 
       SIAM REVIEW 45-2, pp 167-256, 2003.
        
    Examples
    --------
    >>> from networkx.utils import powerlaw_sequence
    >>> z=nx.create_degree_sequence(100,powerlaw_sequence)
    >>> G=nx.configuration_model(z)

    To remove parallel edges:

    >>> G=nx.Graph(G)

    To remove self loops:
    
    >>> G.remove_edges_from(G.selfloop_edges())
    """
    if not sum(deg_sequence)%2 ==0:
        raise nx.NetworkXError('Invalid degree sequence')

    if create_using is None:
        create_using = nx.MultiGraph()
    elif create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")

    if not seed is None:
        random.seed(seed)

    # start with empty N-node graph
    N=len(deg_sequence)

    # allow multiedges and selfloops
    G=nx.empty_graph(N,create_using)

    if N==0 or max(deg_sequence)==0: # done if no edges
        return G 

    # build stublist, a list of available degree-repeated stubs
    # e.g. for deg_sequence=[3,2,1,1,1]
    # initially, stublist=[1,1,1,2,2,3,4,5]
    # i.e., node 1 has degree=3 and is repeated 3 times, etc.
    stublist=[]
    for n in G:
        for i in range(deg_sequence[n]):
            stublist.append(n)

    # shuffle stublist and assign pairs by removing 2 elements at a time      
    random.shuffle(stublist)
    while stublist:
        n1 = stublist.pop()
        n2 = stublist.pop()
        G.add_edge(n1,n2)

    G.name="configuration_model %d nodes %d edges"%(G.order(),G.size())
    return G


def directed_configuration_model(in_degree_sequence,
                                 out_degree_sequence,
                                 create_using=None,seed=None):
    """Return a directed_random graph with the given degree sequences.

    The configuration model generates a random directed pseudograph
    (graph with parallel edges and self loops) by randomly assigning
    edges to match the given degree sequences.

    Parameters
    ----------
    in_degree_sequence :  list of integers 
       Each list entry corresponds to the in-degree of a node.
    out_degree_sequence :  list of integers 
       Each list entry corresponds to the out-degree of a node.
    create_using : graph, optional (default MultiDiGraph)
       Return graph of this type. The instance will be cleared.
    seed : hashable object, optional
        Seed for random number generator.   

    Returns
    -------
    G : MultiDiGraph
        A graph with the specified degree sequences.
        Nodes are labeled starting at 0 with an index
        corresponding to the position in deg_sequence.

    Raises
    ------
    NetworkXError
        If the degree sequences do not have the same sum.

    See Also
    --------
    configuration_model
    
    Notes
    -----
    Algorithm as described by Newman [1]_.

    A non-graphical degree sequence (not realizable by some simple
    graph) is allowed since this function returns graphs with self
    loops and parallel edges.  An exception is raised if the degree
    sequences does not have the same sum.

    This configuration model construction process can lead to
    duplicate edges and loops.  You can remove the self-loops and
    parallel edges (see below) which will likely result in a graph
    that doesn't have the exact degree sequence specified.  This
    "finite-size effect" decreases as the size of the graph increases.

    References
    ----------
    .. [1] Newman, M. E. J. and Strogatz, S. H. and Watts, D. J.
       Random graphs with arbitrary degree distributions and their applications
       Phys. Rev. E, 64, 026118 (2001)
        
    Examples
    --------
    >>> D=nx.DiGraph([(0,1),(1,2),(2,3)]) # directed path graph
    >>> din=list(D.in_degree().values())
    >>> dout=list(D.out_degree().values())
    >>> din.append(1) 
    >>> dout[0]=2
    >>> D=nx.directed_configuration_model(din,dout)

    To remove parallel edges:

    >>> D=nx.DiGraph(D)

    To remove self loops:
    
    >>> D.remove_edges_from(D.selfloop_edges())
    """
    if not sum(in_degree_sequence) == sum(in_degree_sequence):
        raise nx.NetworkXError(
            'Invalid degree sequences. Sequences must have equal sums.')

    if create_using is None:
        create_using = nx.MultiDiGraph()

    if not seed is None:
        random.seed(seed)

    nin=len(in_degree_sequence)
    nout=len(out_degree_sequence)

    # pad in- or out-degree sequence with zeros to match lengths
    if nin>nout:
        out_degree_sequence.extend((nin-nout)*[0])
    else:
        in_degree_sequence.extend((nout-nin)*[0])                             

    # start with empty N-node graph
    N=len(in_degree_sequence)

    # allow multiedges and selfloops
    G=nx.empty_graph(N,create_using)

    if N==0 or max(in_degree_sequence)==0: # done if no edges
        return G 

    # build stublists of available degree-repeated stubs
    # e.g. for degree_sequence=[3,2,1,1,1]
    # initially, stublist=[1,1,1,2,2,3,4,5]
    # i.e., node 1 has degree=3 and is repeated 3 times, etc.
    in_stublist=[]
    for n in G:
        for i in range(in_degree_sequence[n]):
            in_stublist.append(n)

    out_stublist=[]
    for n in G:
        for i in range(out_degree_sequence[n]):
            out_stublist.append(n)

    # shuffle stublists and assign pairs by removing 2 elements at a time      
    random.shuffle(in_stublist)
    random.shuffle(out_stublist)
    while in_stublist and out_stublist:
        source = out_stublist.pop()
        target = in_stublist.pop()
        G.add_edge(source,target)

    G.name="directed configuration_model %d nodes %d edges"%(G.order(),G.size())
    return G


def expected_degree_graph(w, seed=None, selfloops=True):
    r"""Return a random graph with given expected degrees.

    Given a sequence of expected degrees `W=(w_0,w_1,\ldots,w_{n-1}`)
    of length `n` this algorithm assigns an edge between node `u` and
    node `v` with probability

    .. math::

       p_{uv} = \frac{w_u w_v}{\sum_k w_k} .

    Parameters
    ----------
    w : list 
        The list of expected degrees.
    selfloops: bool (default=True)
        Set to False to remove the possibility of self-loop edges.
    seed : hashable object, optional
        The seed for the random number generator.

    Returns
    -------
    Graph

    Examples
    --------
    >>> z=[10 for i in range(100)]
    >>> G=nx.expected_degree_graph(z)

    Notes
    -----
    The complexity of this algorithm is `\mathcal{O}(n+m)` where `n` is the
    number of nodes and `m` is the expected number of edges.

    The model in [1]_ includes the possibility of self-loop edges.
    Set selfloops=False to produce a graph without self loops.
    
    For finite graphs this model doesn't produce exactly the given 
    expected degree sequence.  Instead the expected degrees are as
    follows.

    For the case without self loops (selfloops=False),

    .. math::

       E[deg(u)] = \sum_{v \ne u} p_{uv} 
                = w_u \left( 1 - \frac{w_u}{\sum_k w_k} \right) .


    NetworkX uses the standard convention that a self-loop edge counts 2 
    in the degree of a node, so with self loops (selfloops=True),

    .. math::

       E[deg(u)] =  \sum_{v \ne u} p_{uv}  + 2 p_{uu} 
                = w_u \left( 1 + \frac{w_u}{\sum_k w_k} \right) .

    References
    ----------
    .. [1] Fan Chung and L. Lu, Connected components in random graphs with  
       given expected degree sequences, Ann. Combinatorics, 6, 
       pp. 125-145, 2002.
    .. [2] Joel Miller and Aric Hagberg, 
       Efficient generation of networks with given expected degrees,
       in Algorithms and Models for the Web-Graph (WAW 2011), 
       Alan Frieze, Paul Horn, and Paweł Prałat (Eds), LNCS 6732,
       pp. 115-126, 2011.
    """
    n = len(w)
    G=nx.empty_graph(n)
    if n==0 or max(w)==0: # done if no edges
        return G 
    if seed is not None:
        random.seed(seed)
    rho = 1/float(sum(w))
    seq = sorted(w, reverse=True)
    last=n
    if not selfloops:
        last-=1
    for u in range(last):
        v = u 
        if not selfloops:
            v += 1
        factor = seq[u] * rho
        p = seq[v]*factor  
        if p>1:
            p = 1
        while v<n and p>0:
            if p != 1:
                r = random.random()
                v += int(math.floor(math.log(r)/math.log(1-p)))
            if v < n:
                q = seq[v]*factor
                if q>1:
                    q = 1
                if random.random() < q/p: 
                    G.add_edge(u,v)
                v += 1
                p = q 
    return G

def havel_hakimi_graph(deg_sequence,create_using=None):
    """Return a simple graph with given degree sequence and constructed 
    using the Havel-Hakimi algorithm.

    Parameters
    ----------
    deg_sequence: list of integers
        Each integer corresponds to the degree of a node (need not be sorted).
    create_using : graph, optional (default Graph)
        Return graph of this type. The instance will be cleared.
        Multigraphs and directed graphs are not allowed.

    Raises
    ------
    NetworkXException
        For a non-graphical degree sequence (i.e. one
        not realizable by some simple graph).

    Notes
    -----
    The Havel-Hakimi algorithm constructs a simple graph by
    successively connecting the node of highest degree to other nodes
    of highest degree, resorting remaining nodes by degree, and
    repeating the process. The resulting graph has a high
    degree-associativity.  Nodes are labeled 1,.., len(deg_sequence),
    corresponding to their position in deg_sequence.

    See Theorem 1.4 in [1]_.
    This algorithm is also used in the function is_valid_degree_sequence.

    References
    ----------
    .. [1] G. Chartrand and L. Lesniak, "Graphs and Digraphs",
           Chapman and Hall/CRC, 1996.
    """
    if not is_valid_degree_sequence(deg_sequence):
        raise nx.NetworkXError('Invalid degree sequence')
    if create_using is not None:
        if create_using.is_directed():
            raise nx.NetworkXError("Directed Graph not supported")
        if create_using.is_multigraph():
            raise nx.NetworkXError("Havel-Hakimi requires simple graph")

    N=len(deg_sequence)
    G=nx.empty_graph(N,create_using) 

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

def random_clustered_graph(joint_degree_sequence, create_using=None, seed=None):
    """Generate a random graph with the given joint degree and triangle
    degree sequence.
	
    This uses a configuration model-like approach to generate a
    random pseudograph (graph with parallel edges and self loops) by
    randomly assigning edges to match the given indepdenent edge 
    and triangle degree sequence.

    Parameters 
    ---------- 
    joint_degree_sequence : list of integer pairs
        Each list entry corresponds to the independent edge degree and
        triangle degree of a node.
    create_using : graph, optional (default MultiGraph)
        Return graph of this type. The instance will be cleared.
    seed : hashable object, optional
        The seed for the random number generator.

    Returns
    -------
    G : MultiGraph
        A graph with the specified degree sequence. Nodes are labeled
        starting at 0 with an index corresponding to the position in
        deg_sequence.
	
    Raises
    ------
    NetworkXError
        If the independent edge degree sequence sum is not even
        or the triangle degree sequence sum is not divisible by 3.

    Notes
    -----
    As described by Miller [1]_ (see also Newman [2]_ for an equivalent
    description).
	
    A non-graphical degree sequence (not realizable by some simple
    graph) is allowed since this function returns graphs with self
    loops and parallel edges.  An exception is raised if the
    independent degree sequence does not have an even sum or the
    triangle degree sequence sum is not divisible by 3.
	
    This configuration model-like construction process can lead to
    duplicate edges and loops.  You can remove the self-loops and
    parallel edges (see below) which will likely result in a graph
    that doesn't have the exact degree sequence specified.  This
    "finite-size effect" decreases as the size of the graph increases.

    References
    ----------
    .. [1] J. C. Miller "Percolation and Epidemics on Random Clustered Graphs."
        Physical Review E, Rapid Communication (to appear).
    .. [2] M.E.J. Newman, "Random clustered networks".
        Physical Review Letters (to appear).
	       
    Examples
    --------
    >>> deg_tri=[[1,0],[1,0],[1,0],[2,0],[1,0],[2,1],[0,1],[0,1]]
    >>> G = nx.random_clustered_graph(deg_tri)

    To remove parallel edges:

    >>> G=nx.Graph(G)
	
    To remove self loops:

    >>> G.remove_edges_from(G.selfloop_edges())

    """
    if create_using is None:
        create_using = nx.MultiGraph()
    elif create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")

    if not seed is None:
        random.seed(seed)

    # In Python 3, zip() returns an iterator. Make this into a list.
    joint_degree_sequence = list(joint_degree_sequence)

    N = len(joint_degree_sequence)
    G = nx.empty_graph(N,create_using)

    ilist = []
    tlist = []
    for n in G:
        degrees = joint_degree_sequence[n]
        for icount in range(degrees[0]):
            ilist.append(n)
        for tcount in range(degrees[1]):
            tlist.append(n)

    if len(ilist)%2 != 0 or len(tlist)%3 != 0:
        raise nx.NetworkXError('Invalid degree sequence')

    random.shuffle(ilist)
    random.shuffle(tlist)
    while ilist:
        G.add_edge(ilist.pop(),ilist.pop())
    while tlist:
        n1 = tlist.pop()
        n2 = tlist.pop()
        n3 = tlist.pop()
        G.add_edges_from([(n1,n2),(n1,n3),(n2,n3)])
    G.name = "random_clustered %d nodes %d edges"%(G.order(),G.size())
    return G



def degree_sequence_tree(deg_sequence,create_using=None):
    """Make a tree for the given degree sequence.

    A tree has #nodes-#edges=1 so
    the degree sequence must have
    len(deg_sequence)-sum(deg_sequence)/2=1
    """

    if not len(deg_sequence)-sum(deg_sequence)/2.0 == 1.0:
        raise nx.NetworkXError("Degree sequence invalid")
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")

    # single node tree
    if len(deg_sequence)==1:
        G=empty_graph(0,create_using)
        return G

    # all degrees greater than 1
    deg=[s for s in deg_sequence if s>1] 
    deg.sort(reverse=True)

    # make path graph as backbone
    n=len(deg)+2
    G=nx.path_graph(n,create_using)
    last=n

    # add the leaves
    for source in range(1,n-1):
        nedges=deg.pop()-2
        for target in range(last,last+nedges):
            G.add_edge(source, target)
        last+=nedges
        
    # in case we added one too many 
    if len(G.degree())>len(deg_sequence): 
        G.remove_node(0)
    return G
        

def is_valid_degree_sequence(deg_sequence, method='hh'):
    """Returns True if deg_sequence is a valid degree sequence.
    
    A degree sequence is valid if some graph can realize it.
    
    Parameters
    ----------
    deg_sequence : list
        A list of integers where each element specifies the degree of a node
        in a graph.
    method : "eg" | "hh"
        The method used to validate the degree sequence.  
        "eg" corresponds to the Erdős-Gallai algorithm, and 
        "hh" to the Havel-Hakimi algorithm.

    Returns
    -------
    valid : bool
        True if deg_sequence is a valid degree sequence and False if not.
    
    References
    ----------
    Erdős-Gallai
        [EG1960]_, [choudum1986]_
    
    Havel-Hakimi
        [havel1955]_, [hakimi1962]_, [CL1996]_
    
    """
    if method == 'eg':
        valid = is_valid_degree_sequence_erdos_gallai(deg_sequence)
    elif method == 'hh':
        valid = is_valid_degree_sequence_havel_hakimi(deg_sequence)
    else:
        msg = "`method` must be 'eg' or 'hh'"
        raise nx.NetworkXException(msg)
    
    return valid


def is_valid_degree_sequence_havel_hakimi(deg_sequence):
    """Returns True if deg_sequence is a valid degree sequence.
    
    A degree sequence is valid if some graph can realize it. 
    Validation proceeds via the Havel-Hakimi algorithm.
    
    Worst-case run time is: O( n**(log n) )
    
    Parameters
    ----------
    deg_sequence : list
        A list of integers where each element specifies the degree of a node
        in a graph.

    Returns
    -------
    valid : bool
        True if deg_sequence is a valid degree sequence and False if not.
    
    References
    ----------
    [havel1955]_, [hakimi1962]_, [CL1996]_
    
    """
    # some simple tests 
    if deg_sequence==[]:
        return True # empty sequence = empty graph 
    if not nx.utils.is_list_of_ints(deg_sequence):
        return False   # list of ints
    if min(deg_sequence)<0:
        return False      # each int not negative
    if sum(deg_sequence)%2:
        return False      # must be even
    
    # successively reduce degree sequence by removing node of maximum degree
    # as in Havel-Hakimi algorithm
        
    s=deg_sequence[:]  # copy to s
    while s:      
        s.sort()    # sort in increasing order
        if s[0]<0: 
            return False  # check if removed too many from some node

        d=s.pop()             # pop largest degree 
        if d==0: return True  # done! rest must be zero due to ordering

        # degree must be <= number of available nodes
        if d>len(s):   return False

        # remove edges to nodes of next higher degrees
        #s.reverse()  # to make it easy to get at higher degree nodes.
        for i in range(len(s)-1,len(s)-(d+1),-1):
            s[i]-=1

    # should never get here b/c either d==0, d>len(s) or d<0 before s=[]
    return False


def is_valid_degree_sequence_erdos_gallai(deg_sequence):
    """Returns True if deg_sequence is a valid degree sequence.
    
    A degree sequence is valid if some graph can realize it. 
    Validation proceeds via the Erdős-Gallai algorithm.
    
    Worst-case run time is: O( n**2 )
    
    Parameters
    ----------
    deg_sequence : list
        A list of integers where each element specifies the degree of a node
        in a graph.

    Returns
    -------
    valid : bool
        True if deg_sequence is a valid degree sequence and False if not.
    
    References
    ----------
    [EG1960]_, [choudum1986]_    

    """
    # some simple tests 
    if deg_sequence==[]:
        return True # empty sequence = empty graph 
    if not nx.utils.is_list_of_ints(deg_sequence):
        return False   # list of ints
    if min(deg_sequence)<0:
        return False      # each int not negative
    if sum(deg_sequence)%2:
        return False      # must be even

    n = len(deg_sequence)
    deg_seq = sorted(deg_sequence,reverse=True)
    sigk = [i for i in range(1, len(deg_seq)) if deg_seq[i] < deg_seq[i-1]]
    for k in sigk:
        sum_deg = sum(deg_seq[0:k])
        sum_min = k*(k-1) + sum([min([k,deg_seq[i]]) 
                                 for i in range(k,n)])
        if sum_deg>sum_min:
            return False
    return True
 
def create_degree_sequence(n, sfunction=None, max_tries=50, **kwds):
    """ Attempt to create a valid degree sequence of length n using
    specified function sfunction(n,**kwds).

    Parameters
    ----------
    n : int
        Length of degree sequence = number of nodes
    sfunction: function
        Function which returns a list of n real or integer values.
        Called as "sfunction(n,**kwds)".
    max_tries: int
        Max number of attempts at creating valid degree sequence.

    Notes
    -----
    Repeatedly create a degree sequence by calling sfunction(n,**kwds)
    until achieving a valid degree sequence. If unsuccessful after
    max_tries attempts, raise an exception.
    
    For examples of sfunctions that return sequences of random numbers,
    see networkx.Utils.

    Examples
    --------
    >>> from networkx.utils import uniform_sequence
    >>> seq=nx.create_degree_sequence(10,uniform_sequence)
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
    raise nx.NetworkXError(\
          "Exceeded max (%d) attempts at a valid sequence."%max_tries)

def double_edge_swap(G, nswap=1, max_tries=100):
    """Swap two edges in the graph while keeping the node degrees fixed.

    A double-edge swap removes two randomly chosen edges u-v and x-y
    and creates the new edges u-x and v-y::

     u--v            u  v
            becomes  |  |
     x--y            x  y

    If either the edge u-x or v-y already exist no swap is performed 
    and another attempt is made to find a suitable edge pair.
    
    Parameters
    ----------
    G : graph
       A NetworkX (undirected) Graph.

    nswap : integer (optional)
       Number of double-edge swaps to perform 

    max_tries : integer (optional)
       Maximum number of attempts to swap nswap edges.

    Returns
    -------
    G : graph
       The graph after nswap double edge swaps.

    Notes
    -----
    Does not enforce any connectivity constraints.

    The graph G is modified in place.
    """
    if G.is_directed():
        raise nx.NetworkXError(\
            "double_edge_swap() not defined for directed graphs.")
    # Instead of choosing uniformly at random from a generated edge list, 
    # this algorithm chooses nonuniformly from the set of nodes with
    # probability weighted by degree.
    n=0
    swapcount=0
    keys,degrees=zip(*G.degree().items()) # keys, degree
    cdf=nx.utils.cumulative_distribution(degrees)  # cdf of degree
    if len(cdf)<4:
        raise nx.NetworkXError("Graph has less than four nodes.")
    while swapcount < nswap:
#        if random.random() < 0.5: continue # trick to avoid periodicities?
        # pick two randon edges without creating edge list
        # choose source node indices from discrete distribution
        (ui,xi)=nx.utils.discrete_sequence(2,cdistribution=cdf) 
        if ui==xi: 
            continue # same source, skip
        u=keys[ui] # convert index to label
        x=keys[xi] 
        # choose target uniformly from neighbors
        v=random.choice(list(G[u]))
        y=random.choice(list(G[x]))
        if v==y: 
            continue # same target, skip
        if (x not in G[u]) and (y not in G[v]): # don't create parallel edges
            G.add_edge(u,x)
            G.add_edge(v,y)
            G.remove_edge(u,v)
            G.remove_edge(x,y)
            swapcount+=1
        if n > max_tries:
            e=('Maximum number of swap attempts (%s) exceeded '%n +
            'before desired swaps achieved (%s).'%nswap)
            raise nx.NetworkXAlgorithmError(e)
        n+=1
    return G

def connected_double_edge_swap(G, nswap=1):
    """Attempt nswap double-edge swaps on the graph G.

    Returns the count of successful swaps.  Enforces connectivity.
    The graph G is modified in place.

    Notes
    -----
    A double-edge swap removes two randomly choseen edges u-v and x-y
    and creates the new edges u-x and v-y::

     u--v            u  v
            becomes  |  |
     x--y            x  y


    If either the edge u-x or v-y already exist no swap is performed so
    the actual count of swapped edges is always <= nswap

    The initial graph G must be connected and the resulting graph is connected.

    References
    ----------
    .. [1] C. Gkantsidis and M. Mihail and E. Zegura,
           The Markov chain simulation method for generating connected
           power law random graphs, 2003.
           http://citeseer.ist.psu.edu/gkantsidis03markov.html
    """
    import math
    if not nx.is_connected(G):
       raise nx.NetworkXException("Graph not connected")

    n=0
    swapcount=0
    deg=G.degree()
    dk=list(deg.keys()) # Label key for nodes
    cdf=nx.utils.cumulative_distribution(list(G.degree().values())) 
    if len(cdf)<4:
        raise nx.NetworkXError("Graph has less than four nodes.")
    window=1
    while n < nswap:
        wcount=0
        swapped=[]
        while wcount < window and n < nswap:
            # Pick two random edges without creating edge list
            # Choose source nodes from discrete degree distribution
            (ui,xi)=nx.utils.discrete_sequence(2,cdistribution=cdf) 
            if ui==xi: continue # same source, skip
            u=dk[ui] # convert index to label
            x=dk[xi] 
            # Choose targets uniformly from neighbors
            v=random.choice(G.neighbors(u)) 
            y=random.choice(G.neighbors(x)) #
            if v==y: continue # same target, skip
            if (not G.has_edge(u,x)) and (not G.has_edge(v,y)):
                G.remove_edge(u,v)
                G.remove_edge(x,y)
                G.add_edge(u,x)
                G.add_edge(v,y)
                swapped.append((u,v,x,y))
                swapcount+=1
            n+=1
            wcount+=1
        if nx.is_connected(G):
            window+=1
        else:
            # not connected, undo changes from previous window, decrease window
            while swapped:
                (u,v,x,y)=swapped.pop()
                G.add_edge(u,v)
                G.add_edge(x,y)
                G.remove_edge(u,x)
                G.remove_edge(v,y)
                swapcount-=1
            window = int(math.ceil(float(window)/2))
    return swapcount



def li_smax_graph(degree_seq, create_using=None):
    """Generates a graph based with a given degree sequence and maximizing
    the s-metric.  Experimental implementation.

    Maximum s-metrix  means that high degree nodes are connected to high
    degree nodes. 
        
    - `degree_seq`: degree sequence, a list of integers with each entry
       corresponding to the degree of a node.
       A non-graphical degree sequence raises an Exception.    

    Reference::      
    
      @unpublished{li-2005,
       author = {Lun Li and David Alderson and Reiko Tanaka
                and John C. Doyle and Walter Willinger},
       title = {Towards a Theory of Scale-Free Graphs:
               Definition, Properties, and  Implications (Extended Version)},
       url = {http://arxiv.org/abs/cond-mat/0501169},
       year = {2005}
      }

    The algorithm::

     STEP 0 - Initialization
     A = {0}
     B = {1, 2, 3, ..., n}
     O = {(i; j), ..., (k, l),...} where i < j, i <= k < l and 
             d_i * d_j >= d_k *d_l 
     wA = d_1
     dB = sum(degrees)

     STEP 1 - Link selection
     (a) If |O| = 0 TERMINATE. Return graph A.
     (b) Select element(s) (i, j) in O having the largest d_i * d_j , if for 
             any i or j either w_i = 0 or w_j = 0 delete (i, j) from O
     (c) If there are no elements selected go to (a).
     (d) Select the link (i, j) having the largest value w_i (where for each 
             (i, j) w_i is the smaller of w_i and w_j ), and proceed to STEP 2.

     STEP 2 - Link addition
     Type 1: i in A and j in B. 
             Add j to the graph A and remove it from the set B add a link 
             (i, j) to the graph A. Update variables:
             wA = wA + d_j -2 and dB = dB - d_j
             Decrement w_i and w_j with one. Delete (i, j) from O
     Type 2: i and j in A.
         Check Tree Condition: If dB = 2 * |B| - wA. 
             Delete (i, j) from O, continue to STEP 3
         Check Disconnected Cluster Condition: If wA = 2. 
             Delete (i, j) from O, continue to STEP 3
         Add the link (i, j) to the graph A 
         Decrement w_i and w_j with one, and wA = wA -2
     STEP 3
         Go to STEP 1


    The article states that the algorithm will result in a maximal s-metric. 
    This implementation can not guarantee such maximality. I may have 
    misunderstood the algorithm, but I can not see how it can be anything 
    but a heuristic. Please contact me at sundsdal@gmail.com if you can 
    provide python code that can guarantee maximality.
    Several optimizations are included in this code and it may be hard to read.
    Commented code to come.

    A POSSIBLE ALTERNATIVE:

    For an 'unconstrained' graph, that is one they describe as having
    the sum of the degree sequence be even(ie all undirected graphs) they
    present a simpler algorithm. It is as follows

        "For each vertex i: if di is even then attach di/2 self-loops;
        if di is odd, then attach (di-1)/2 self-loops, leaving one
        available "stub". Second for all remaining vertices with "stubs"
        connect them in pairs according to decreasing values of di."[1]
    
    Since this only works for undirected graphs anyway, perhaps this is
    the better method? Note this also returns a graph with a larger
    s_metric than the other method, and it seems to have the same
    degree sequence, though I haven't tested it extensively.
    """
    if not is_valid_degree_sequence(degree_seq):
        raise nx.NetworkXError('Invalid degree sequence')
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")

    degree_seq.sort(reverse=True) # make sure it's sorted
   
    if not (sum(degree_seq) %2): #check if the sum of the degree sequence is even, Should be if it is undirected
        dseven = [di for di in degree_seq if (not di % 2)]
        dsodd = [di for di in degree_seq if (di % 2)]
        Gmax = nx.MultiGraph()
        i = 0
        for di in dseven:
            Gmax.add_node(i)
            for k in range(di // 2):
                Gmax.add_edge(i,i)
            i=i+1
        for j in range(0,len(dsodd),2): #do this iteratively to connect
            Gmax.add_node(i)            #node stubs as we go
            Gmax.add_node(i+1)
            for k in range((dsodd[j]-1) // 2):
                Gmax.add_edge(i,i)
            for k in range((dsodd[j+1]-1) // 2):
                Gmax.add_edge(i+1,i+1)
            Gmax.add_edge(i,i+1)
            i=i+2
        return Gmax
    else:
        degrees_left = degree_seq[:]
        A_graph = empty_graph(0,create_using)
        A_graph.add_node(0)
        a_list = [False]*len(degree_seq)
        b_set = set(range(1,len(degree_seq)))
        a_open = set([0])
        O = []
        for j in b_set:
            heapq.heappush(O, (-degree_seq[0]*degree_seq[j], (0,j))),
        wa = degrees_left[0] #stubs in a_graph
        db = sum(degree_seq) - degree_seq[0] #stubs in b-graph
        a_list[0] = True #node 0 is now in a_Graph
        bsize = len(degree_seq) -1 #size of b_graph
        selected = []
        weight = 0
        while O or selected:
            if len(selected) <1 :
                firstrun = True
                while O:
                    (newweight, (i,j)) = heapq.heappop(O)
                    if degrees_left[i] < 1 or degrees_left[j] < 1 :
                        continue
                    if firstrun:
                        firstrun = False
                        weight = newweight
                    if not newweight == weight:
                        break
                    heapq.heappush(selected, [-degrees_left[i], \
                                        -degrees_left[j], (i,j)])
                if not weight == newweight:
                    heapq.heappush(O,(newweight, (i,j)))
                weight *= -1
            if len(selected) < 1:
                break

            [w1, w2, (i,j)] = heapq.heappop(selected)
            if degrees_left[i] < 1 or degrees_left[j] < 1 :
                continue
            if a_list[i] and j in b_set:
                #TYPE1
                a_list[j] = True
                b_set.remove(j)
                A_graph.add_node(j)
                A_graph.add_edge(i, j)
                degrees_left[i] -= 1
                degrees_left[j] -= 1
                wa += degree_seq[j] - 2
                db -= degree_seq[j]
                bsize -= 1
                newweight = weight
                if not degrees_left[j] == 0:
                    a_open.add(j)
                    for k in b_set:
                        if A_graph.has_edge(j, k): continue
                        w = degree_seq[j]*degree_seq[k]
                        if w > newweight:
                            newweight = w
                        if weight == w and not newweight > weight:
                            heapq.heappush(selected, [-degrees_left[j], \
                                                -degrees_left[k], (j,k)])
                        else:
                            heapq.heappush(O, (-w, (j,k)))
                    if not weight == newweight:
                        while selected:
                            [w1,w2,(i,j)] = heapq.heappop(selected)
                            if degrees_left[i]*degrees_left[j] > 0:
                                heapq.heappush(O, [-degree_seq[i]*degree_seq[j],(i,j)])
                if degrees_left[i] == 0:
                    a_open.discard(i)

            else:
                #TYPE2
                if db == (2*bsize - wa):
                    #tree condition
                    #print "removing because tree condition    "
                    continue
                elif db < 2*bsize -wa:
                    raise nx.NetworkXError(\
                            "THIS SHOULD NOT HAPPEN!-not graphable")
                    continue
                elif wa == 2 and bsize > 0:
                    #print "removing because disconnected  cluster"
                    #disconnected cluster condition
                    continue
                elif wa == db - (bsize)*(bsize-1):
                    #print "MYOWN removing because disconnected  cluster"
                    continue
                A_graph.add_edge(i, j)
                degrees_left[i] -= 1
                degrees_left[j] -= 1
                if degrees_left[i] < 1:
                    a_open.discard(i)
                if degrees_left[j] < 1:
                    a_open.discard(j)
                wa -=  2
                if not degrees_left[i] < 0 and not degrees_left[j] < 0:
                    selected2 = (selected)
                    selected = []
                    while selected2:
                        [w1,w1, (i,j)] = heapq.heappop(selected2)
                        if degrees_left[i]*degrees_left[j] > 0:
                            heapq.heappush(selected, [-degrees_left[i], \
                                            -degrees_left[j], (i,j)])
        return A_graph 

def connected_smax_graph(degree_seq, create_using=None):
    """
    Not implemented.
    """
    # incomplete implementation
    
    if not is_valid_degree_sequence(degree_seq):
        raise nx.NetworkXError('Invalid degree sequence')
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
   
    # build dictionary of node id and degree, sorted by degree, largest first
    degree_seq.sort() 
    degree_seq.reverse()
    ddict=dict(zip(range(len(degree_seq)),degree_seq))

    G=empty_graph(1,create_using) # start with single node

    return False

