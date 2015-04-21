# -*- coding: utf-8 -*-
"""Generate graphs with a given degree sequence or expected degree sequence.
"""
#    Copyright (C) 2004-2015 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import heapq
from itertools import combinations, permutations
import math
from operator import itemgetter
import random
import networkx as nx
from networkx.utils import random_weighted_sample

__author__ = "\n".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                        'Pieter Swart <swart@lanl.gov>',
                        'Dan Schult <dschult@colgate.edu>'
                        'Joel Miller <joel.c.miller.research@gmail.com>',
                        'Nathan Lemons <nlemons@gmail.com>'
                        'Brian Cloteaux <brian.cloteaux@nist.gov>'])

__all__ = ['configuration_model',
           'directed_configuration_model',
           'expected_degree_graph',
           'havel_hakimi_graph',
           'directed_havel_hakimi_graph',
           'degree_sequence_tree',
           'random_degree_sequence_graph']


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
    that doesn't have the exact degree sequence specified.  
    
    The density of self-loops and parallel edges tends to decrease 
    as the number of nodes increases. However, typically the number 
    of self-loops will approach a Poisson distribution with a nonzero 
    mean, and similarly for the number of parallel edges.   Consider a 
    node with k stubs. The probability of being joined to another stub of 
    the same node is basically (k-1)/N where k is the degree and N is 
    the number of nodes. So the probability of a self-loop  scales like c/N 
    for some constant c.  As N grows, this means we expect c self-loops. 
    Similarly for parallel edges.

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
    if not sum(in_degree_sequence) == sum(out_degree_sequence):
        raise nx.NetworkXError('Invalid degree sequences. '
                               'Sequences must have equal sums.')

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
        Directed graphs are not allowed.

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

    The basic algorithm is from Hakimi [1]_ and was generalized by
    Kleitman and Wang [2]_.

    References
    ----------
    .. [1] Hakimi S., On Realizability of a Set of Integers as 
       Degrees of the Vertices of a Linear Graph. I,
       Journal of SIAM, 10(3), pp. 496-506 (1962)
    .. [2] Kleitman D.J. and Wang D.L.
       Algorithms for Constructing Graphs and Digraphs with Given Valences
       and Factors  Discrete Mathematics, 6(1), pp. 79-88 (1973) 
    """
    if not nx.is_valid_degree_sequence(deg_sequence):
        raise nx.NetworkXError('Invalid degree sequence')
    if create_using is not None:
        if create_using.is_directed():
            raise nx.NetworkXError("Directed graphs are not supported")

    p = len(deg_sequence)
    G=nx.empty_graph(p,create_using)
    num_degs = []
    for i in range(p):
        num_degs.append([])
    dmax, dsum, n = 0, 0, 0
    for d in deg_sequence:
        # Process only the non-zero integers
        if d>0:
            num_degs[d].append(n)
            dmax, dsum, n = max(dmax,d), dsum+d, n+1
    # Return graph if no edges
    if n==0:
        return G

    modstubs = [(0,0)]*(dmax+1)
    # Successively reduce degree sequence by removing the maximum degree
    while n > 0:
        # Retrieve the maximum degree in the sequence
        while len(num_degs[dmax]) == 0:
            dmax -= 1;
        # If there are not enough stubs to connect to, then the sequence is
        # not graphical
        if dmax > n-1:
            raise nx.NetworkXError('Non-graphical integer sequence')

        # Remove largest stub in list
        source = num_degs[dmax].pop()
        n -= 1
        # Reduce the next dmax largest stubs
        mslen = 0
        k = dmax
        for i in range(dmax):
            while len(num_degs[k]) == 0:
                k -= 1
            target = num_degs[k].pop()
            G.add_edge(source, target)
            n -= 1
            if k > 1:
                modstubs[mslen] = (k-1,target)
                mslen += 1
        # Add back to the list any nonzero stubs that were removed
        for i  in range(mslen):
            (stubval, stubtarget) = modstubs[i]
            num_degs[stubval].append(stubtarget)
            n += 1

    G.name="havel_hakimi_graph %d nodes %d edges"%(G.order(),G.size())
    return G

def directed_havel_hakimi_graph(in_deg_sequence,
                                out_deg_sequence,
                                create_using=None):
    """Return a directed graph with the given degree sequences.

    Parameters
    ----------
    in_deg_sequence :  list of integers 
       Each list entry corresponds to the in-degree of a node.
    out_deg_sequence : list of integers 
       Each list entry corresponds to the out-degree of a node.
    create_using : graph, optional (default DiGraph)
       Return graph of this type. The instance will be cleared.

    Returns
    -------
    G : DiGraph
        A graph with the specified degree sequences.
        Nodes are labeled starting at 0 with an index
        corresponding to the position in deg_sequence

    Raises
    ------
    NetworkXError
        If the degree sequences are not digraphical.

    See Also
    --------
    configuration_model
    
    Notes
    -----
    Algorithm as described by Kleitman and Wang [1]_.

    References
    ----------
    .. [1] D.J. Kleitman and D.L. Wang
       Algorithms for Constructing Graphs and Digraphs with Given Valences
       and Factors Discrete Mathematics, 6(1), pp. 79-88 (1973) 
    """
    assert(nx.utils.is_list_of_ints(in_deg_sequence))
    assert(nx.utils.is_list_of_ints(out_deg_sequence))

    if create_using is None:
        create_using = nx.DiGraph()

    # Process the sequences and form two heaps to store degree pairs with
    # either zero or nonzero out degrees
    sumin, sumout, nin, nout = 0, 0, len(in_deg_sequence), len(out_deg_sequence)
    maxn = max(nin, nout) 
    G = nx.empty_graph(maxn,create_using)
    if maxn==0:
        return G
    maxin = 0
    stubheap, zeroheap = [ ], [ ]
    for n in range(maxn):
        in_deg, out_deg = 0, 0
        if n<nout:
            out_deg = out_deg_sequence[n]
        if n<nin:
            in_deg = in_deg_sequence[n]
        if in_deg<0 or out_deg<0:
            raise nx.NetworkXError(
                'Invalid degree sequences. Sequence values must be positive.')
        sumin, sumout, maxin = sumin+in_deg, sumout+out_deg, max(maxin, in_deg)
        if in_deg > 0:
            stubheap.append((-1*out_deg, -1*in_deg,n)) 
        elif out_deg > 0:
            zeroheap.append((-1*out_deg,n)) 
    if sumin != sumout:
        raise nx.NetworkXError(
            'Invalid degree sequences. Sequences must have equal sums.')
    heapq.heapify(stubheap)
    heapq.heapify(zeroheap)

    modstubs = [(0,0,0)]*(maxin+1)
    # Successively reduce degree sequence by removing the maximum 
    while stubheap:
        # Remove first value in the sequence with a non-zero in degree
        (freeout, freein, target) =  heapq.heappop(stubheap)
        freein *= -1   
        if freein > len(stubheap)+len(zeroheap):
            raise nx.NetworkXError('Non-digraphical integer sequence')

        # Attach arcs from the nodes with the most stubs
        mslen = 0
        for i in range(freein):
            if zeroheap and (not stubheap or stubheap[0][0] > zeroheap[0][0]):
                (stubout, stubsource) = heapq.heappop(zeroheap)
                stubin = 0
            else:
                (stubout, stubin, stubsource) = heapq.heappop(stubheap)
            if stubout == 0:
                raise nx.NetworkXError('Non-digraphical integer sequence')
            G.add_edge(stubsource, target)
            # Check if source is now totally connected
            if stubout+1<0 or stubin<0:
                modstubs[mslen] = (stubout+1, stubin, stubsource)
                mslen += 1

        # Add the nodes back to the heaps that still have available stubs
        for i in range(mslen):
            stub = modstubs[i]
            if stub[1] < 0:
                heapq.heappush(stubheap, stub)
            else:
                heapq.heappush(zeroheap, (stub[0], stub[2]))
        if freeout<0:
            heapq.heappush(zeroheap, (freeout, target))

    G.name="directed_havel_hakimi_graph %d nodes %d edges"%(G.order(),G.size())
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
        G=nx.empty_graph(0,create_using)
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

def random_degree_sequence_graph(sequence, seed=None, tries=10):
    r"""Return a simple random graph with the given degree sequence.

    If the maximum degree `d_m` in the sequence is `O(m^{1/4})` then the
    algorithm produces almost uniform random graphs in `O(m d_m)` time
    where `m` is the number of edges.

    Parameters
    ----------
    sequence :  list of integers
        Sequence of degrees
    seed : hashable object, optional
        Seed for random number generator
    tries : int, optional
        Maximum number of tries to create a graph

    Returns
    -------
    G : Graph
        A graph with the specified degree sequence.
        Nodes are labeled starting at 0 with an index
        corresponding to the position in the sequence.

    Raises
    ------
    NetworkXUnfeasible
        If the degree sequence is not graphical.
    NetworkXError
        If a graph is not produced in specified number of tries

    See Also
    --------
    is_valid_degree_sequence, configuration_model

    Notes
    -----
    The generator algorithm [1]_ is not guaranteed to produce a graph.

    References
    ----------
    .. [1] Moshen Bayati, Jeong Han Kim, and Amin Saberi,
       A sequential algorithm for generating random graphs.
       Algorithmica, Volume 58, Number 4, 860-910,
       DOI: 10.1007/s00453-009-9340-1

    Examples
    --------
    >>> sequence = [1, 2, 2, 3]
    >>> G = nx.random_degree_sequence_graph(sequence)
    >>> sorted(G.degree().values())
    [1, 2, 2, 3]
    """
    DSRG = DegreeSequenceRandomGraph(sequence, seed=seed)
    for try_n in range(tries):
        try:
            return DSRG.generate()
        except nx.NetworkXUnfeasible:
            pass
    raise nx.NetworkXError('failed to generate graph in %d tries'%tries)

class DegreeSequenceRandomGraph(object):
    # class to generate random graphs with a given degree sequence
    # use random_degree_sequence_graph()
    def __init__(self, degree, seed=None):
        if not nx.is_valid_degree_sequence(degree):
            raise nx.NetworkXUnfeasible('degree sequence is not graphical')
        if seed is not None:
            random.seed(seed)
        self.degree = list(degree)
        # node labels are integers 0,...,n-1
        self.m = sum(self.degree)/2.0 # number of edges
        try:
            self.dmax = max(self.degree) # maximum degree
        except ValueError:
            self.dmax = 0

    def generate(self):
        # remaining_degree is mapping from int->remaining degree
        self.remaining_degree = dict(enumerate(self.degree))
        # add all nodes to make sure we get isolated nodes
        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.remaining_degree)
        # remove zero degree nodes
        for n,d in list(self.remaining_degree.items()):
            if d == 0:
                del self.remaining_degree[n]
        if len(self.remaining_degree) > 0:
        # build graph in three phases according to how many unmatched edges
            self.phase1()
            self.phase2()
            self.phase3()
        return self.graph

    def update_remaining(self, u, v, aux_graph=None):
        # decrement remaining nodes, modify auxilliary graph if in phase3
        if aux_graph is not None:
            # remove edges from auxilliary graph
            aux_graph.remove_edge(u,v)
        if self.remaining_degree[u] == 1:
            del self.remaining_degree[u]
            if aux_graph is not None:
                aux_graph.remove_node(u)
        else:
            self.remaining_degree[u] -= 1
        if self.remaining_degree[v] == 1:
            del self.remaining_degree[v]
            if aux_graph is not None:
                aux_graph.remove_node(v)
        else:
            self.remaining_degree[v] -= 1

    def p(self,u,v):
        # degree probability
        return 1 - self.degree[u]*self.degree[v]/(4.0*self.m)

    def q(self,u,v):
        # remaining degree probability
        norm = float(max(self.remaining_degree.values()))**2
        return self.remaining_degree[u]*self.remaining_degree[v]/norm

    def suitable_edge(self):
        # Check if there is a suitable edge that is not in the graph
        # True if an (arbitrary) remaining node has at least one possible 
        # connection to another remaining node
        nodes = iter(self.remaining_degree)
        u = next(nodes) # one arbitrary node
        for v in nodes: # loop over all other remaining nodes
            if not self.graph.has_edge(u, v):
                return True
        return False

    def phase1(self):
        # choose node pairs from (degree) weighted distribution
        while sum(self.remaining_degree.values()) >= 2 * self.dmax**2:
            u,v = sorted(random_weighted_sample(self.remaining_degree, 2))
            if self.graph.has_edge(u,v):
                continue
            if random.random() < self.p(u,v):  # accept edge
                self.graph.add_edge(u,v)
                self.update_remaining(u,v)

    def phase2(self):
        # choose remaining nodes uniformly at random and use rejection sampling
        while len(self.remaining_degree) >= 2 * self.dmax:
            norm = float(max(self.remaining_degree.values()))**2
            while True:
                u,v = sorted(random.sample(self.remaining_degree.keys(), 2))
                if self.graph.has_edge(u,v):
                    continue
                if random.random() < self.q(u,v):
                    break
            if random.random() < self.p(u,v):  # accept edge
                self.graph.add_edge(u,v)
                self.update_remaining(u,v)

    def phase3(self):
        # build potential remaining edges and choose with rejection sampling
        potential_edges = combinations(self.remaining_degree, 2)
        # build auxilliary graph of potential edges not already in graph
        H = nx.Graph([(u,v) for (u,v) in potential_edges
                      if not self.graph.has_edge(u,v)])
        while self.remaining_degree:
            if not self.suitable_edge():
                raise nx.NetworkXUnfeasible('no suitable edges left')
            while True:
                u,v = sorted(random.choice(H.edges()))
                if random.random() < self.q(u,v):
                    break
            if random.random() < self.p(u,v): # accept edge
                self.graph.add_edge(u,v)
                self.update_remaining(u,v, aux_graph=H)
