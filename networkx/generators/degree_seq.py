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
from operator import itemgetter
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
           'degree_sequence_tree']


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
    >>> z=nx.utils.create_degree_sequence(100,powerlaw_sequence)
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
    The nodes have integer labels corresponding to index of expected degrees
    input sequence.

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
    # sort weights, largest first
    # preserve order of weights for integer node label mapping
    order = sorted(enumerate(w),key=itemgetter(1),reverse=True)
    mapping = dict((c,uv[0]) for c,uv in enumerate(order))
    seq = [v for u,v in order]
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
                    G.add_edge(mapping[u],mapping[v])
                v += 1
                p = q 
    return G

def havel_hakimi_graph(deg_sequence,create_using=None):
    """Return a simple graph with given degree sequence constructed 
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
    if not nx.is_valid_degree_sequence(deg_sequence):
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
        
 
