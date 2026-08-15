# -*- coding: ascii -*-
"""
Generators for graphs based on product operations.

"""
#    Copyright (C) 2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = "\n".join(["Aric Hagberg (hagberg@lanl.gov)",
                        "Pieter Swart (swart@lanl.gov)",
                        "Dan Schult (dschult@colgate.edu)",
                        "chebee7i (chebee7i@gmail.com)",
                        "Nikhil Desai (nikhilarundesai@gmail.com)"])

import itertools
import random
import math
import networkx as nx
from networkx.generators.classic import empty_graph

__all__ = ['kronecker_graph',
           'kronecker_random_graph',
           'kronecker2_random_graph']


def kronecker_graph(k, G):
    I = nx.adjacency_matrix(G)

    if G.is_directed():
        return kronecker_random_graph(k,I,True)
    else:
        return kronecker_random_graph(k,I,False)


def kronecker_random_graph(k, P, seed=None, directed=True):
    """Return a random graph K_k[P] (Stochastic Kronecker graph).

    Parameters
    ----------
    P : square matrix of floats
        An n-by-n square "initiator" matrix of probabilities. May be a standard 
        Python matrix or a NumPy matrix.  If the graph is undirected, 
        must be symmetric.
    k : int
        The number of times P is Kronecker-powered, creating a stochastic 
        adjacency matrix.  The generated graph has n^k nodes, 
        where n is the dimension of P as noted above.
    seed : int, optional
        Seed for random number generator (default=None).
    directed : bool, optional
        If True, return a directed graph, else return an undirected one 
        (default=True).

    Notes
    -----
    The stochastic Kronecker graph generation algorithm takes as input a 
    square matrix of probabilities, computes the iterated Kronecker power of 
    this matrix, and then uses the resulting stochastic adjacency matrix to 
    generate a graph. This algorithm is O(V^2), where V=n^k.

    See Also
    --------
    kronecker2_random_graph

    Examples
    --------
    >>> k=4
    >>> P=[[0.8,0.3],[0.3,0.2]]
    >>> G=nx.kronecker_random_graph(k,P)
    >>> P=[[0.8,0.7],[0.3,0.2]]
    >>> G=nx.kronecker_random_graph(k,P,directed=True)
 
    References
    ----------
    .. [1] Jure Leskovec, Deepayan Chakrabarti, Jon Kleinberg, Christos Faloutsos, 
           and Zoubin Ghahramani, 
       "Kronecker graphs: an approach to modeling networks",
       The Journal of Machine Learning Research, 11, 985-1042, 3/1/2010.
    """
    dim = len(P) 

    errorstring = ("The initiator matrix must be a nonempty" +
                      (", symmetric," if not directed else "") +
                      " square matrix of probabilities.")

    if dim==0: 
        raise nx.NetworkXError(errorstring)
    for i,arr in enumerate(P): 
        if len(arr)!=dim: 
            raise nx.NetworkXError(errorstring)
        for j,p in enumerate(arr):
            if p<0 or p>1:
                raise nx.NetworkXError(errorstring)
            if not directed and P[i][j] != P[j][i]:
                raise nx.NetworkXError(errorstring)

    if k<1:
        return empty_graph(1)

    n = dim**k
    G = empty_graph(n)
 
    if directed:
        G=nx.DiGraph(G)

    G.add_nodes_from(range(n))
    G.name="kronecker_random_graph(%s,%s)"%(n, P)

    if not seed is None:
        random.seed(seed)

    if G.is_directed():
        edges=itertools.product(range(n),range(n))
    else:
        edges=itertools.chain([(v,v) for v in range(n)], itertools.combinations(range(n),2))

    for e in edges:
        row,col=e
        p=1.0
        initPow = 1
        for i in range(k):
            rowVal = (row//initPow) % dim
            colVal = (col//initPow) % dim
            p = p*(P[rowVal][colVal])
            initPow = initPow*dim
        if random.random() < p:
            G.add_edge(*e)

    return G


def kronecker2_random_graph(k, P, seed=None, directed=True):
    """Return a sparse random graph K_k[P] (Stochastic Kronecker graph).

    Parameters
    ----------
    P : square matrix of floats
        An n-by-n square "initiator" matrix of probabilities. May be a standard 
        Python matrix or a NumPy matrix.  If the graph is undirected, 
        must be symmetric.
    k : int
        The number of times P is Kronecker-powered, creating a stochastic 
        adjacency matrix.  The generated graph has n^k nodes, 
        where n is the dimension of P as noted above.
    seed : int, optional
        Seed for random number generator (default=None).
    directed : bool, optional 
        If True, return a directed graph, else return an undirected one 
        (default=True).

    Notes
    -----
    The stochastic Kronecker graph generation algorithm takes as input a 
    square matrix of probabilities, computes the iterated Kronecker power of 
    this matrix, and then uses the resulting stochastic adjacency matrix to 
    generate a graph. 

    This "fast" algorithm runs in O(E) time. It thus works best when the expected
    number of edges in the graph is roughly O(V).
    The expected number of edges in the graph is given by d^k, where 
    d=\sum_{i,j} P[i,j] is the sum of all the elements in P.

    See Also
    --------
    kronecker_random_graph

    Examples
    --------
    >>> k=4
    >>> P=[[0.8,0.3],[0.3,0.2]]
    >>> G=nx.kronecker2_random_graph(k,P)
 
    References
    ----------
    .. [1] Jure Leskovec, Deepayan Chakrabarti, Jon Kleinberg, Christos Faloutsos, 
           and Zoubin Ghahramani, 
       "Kronecker graphs: an approach to modeling networks",
       The Journal of Machine Learning Research, 11, 985-1042, 3/1/2010.
    """
    dim = len(P)

    
    errorstring = ("The initiator matrix must be a nonempty" +
                      (", symmetric," if not directed else "") +
                      " square matrix of probabilities.")

    if dim==0: 
        raise nx.NetworkXError(errorstring)
    for i,arr in enumerate(P): 
        if len(arr)!=dim: 
            raise nx.NetworkXError(errorstring)
        for j,p in enumerate(arr):
            if p<0 or p>1:
                raise nx.NetworkXError(errorstring)
            if not directed and P[i][j] != P[j][i]:
                raise nx.NetworkXError(errorstring)

    if k<1:
        return empty_graph(1)

    n = dim**k
    G = empty_graph(n)
    G=nx.DiGraph(G)

    acc = 0.0
    partitions = []
    for i in range(dim):
        for j in range(dim):
            if P[i][j] != 0:
                acc = acc+P[i][j]
                partitions.append([acc,i,j])
    psum = acc

    G.add_nodes_from(range(n))
    G.name="kronecker2_random_graph(%s,%s)"%(n, P)

    if not seed is None:
        random.seed(seed)

    expected_edges=math.floor(psum**k)
    num_edges = 0
    while num_edges<expected_edges:
        multiplier = dim**k
        x = y = 0
        for i in range(k):
            multiplier = multiplier // dim
            r = c = -1
            p = random.uniform(0,psum)
            for n in range(len(partitions)):
                if partitions[n][0] >= p:
                    r = partitions[n][1]
                    c = partitions[n][2]
                    break
            x = x + r*multiplier
            y = y + c*multiplier

        if not G.has_edge(x,y):
            G.add_edge(x,y)
            num_edges = num_edges + 1

    if not directed:
        G=G.to_undirected()

    return G
