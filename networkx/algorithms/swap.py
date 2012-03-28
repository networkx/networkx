# -*- coding: utf-8 -*-
"""Swap edges in a graph.
"""
#    Copyright (C) 2004-2012 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import math
import random
import networkx as nx
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult (dschult@colgate.edu)'
                        'Joel Miller (joel.c.miller.research@gmail.com)'
                        'Ben Edwards'])

__all__ = ['double_edge_swap',
           'connected_double_edge_swap']


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
       An undirected graph

    nswap : integer (optional, default=1)
       Number of double-edge swaps to perform

    max_tries : integer (optional)
       Maximum number of attempts to swap edges

    Returns
    -------
    G : graph
       The graph after double edge swaps.

    Notes
    -----
    Does not enforce any connectivity constraints.

    The graph G is modified in place.
    """
    if G.is_directed():
        raise nx.NetworkXError(\
            "double_edge_swap() not defined for directed graphs.")
    if nswap>max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G) < 4:
        raise nx.NetworkXError("Graph has less than four nodes.")
    # Instead of choosing uniformly at random from a generated edge list,
    # this algorithm chooses nonuniformly from the set of nodes with
    # probability weighted by degree.
    n=0
    swapcount=0
    keys,degrees=zip(*G.degree().items()) # keys, degree
    cdf=nx.utils.cumulative_distribution(degrees)  # cdf of degree
    while swapcount < nswap:
#        if random.random() < 0.5: continue # trick to avoid periodicities?
        # pick two random edges without creating edge list
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
        if n >= max_tries:
            e=('Maximum number of swap attempts (%s) exceeded '%n +
            'before desired swaps achieved (%s).'%nswap)
            raise nx.NetworkXAlgorithmError(e)
        n+=1
    return G

def connected_double_edge_swap(G, nswap=1):
    """Attempt nswap double-edge swaps in the graph G.

    A double-edge swap removes two randomly chosen edges u-v and x-y
    and creates the new edges u-x and v-y::

     u--v            u  v
            becomes  |  |
     x--y            x  y

    If either the edge u-x or v-y already exist no swap is performed so
    the actual count of swapped edges is always <= nswap

    Parameters
    ----------
    G : graph
       An undirected graph

    nswap : integer (optional, default=1)
       Number of double-edge swaps to perform

    Returns
    -------
    G : int
       The number of successful swaps

    Notes
    -----
    The initial graph G must be connected, and the resulting graph is connected.
    The graph G is modified in place.

    References
    ----------
    .. [1] C. Gkantsidis and M. Mihail and E. Zegura,
           The Markov chain simulation method for generating connected
           power law random graphs, 2003.
           http://citeseer.ist.psu.edu/gkantsidis03markov.html
    """
    import math
    if not nx.is_connected(G):
       raise nx.NetworkXError("Graph not connected")
    if len(G) < 4:
        raise nx.NetworkXError("Graph has less than four nodes.")
    n=0
    swapcount=0
    deg=G.degree()
    dk=list(deg.keys()) # Label key for nodes
    cdf=nx.utils.cumulative_distribution(list(G.degree().values()))
    window=1
    while n < nswap:
        wcount=0
        swapped=[]
        while wcount < window and n < nswap:
            # Pick two random edges without creating edge list
            # Choose source nodes from discrete degree distribution
            (ui,xi)=nx.utils.discrete_sequence(2,cdistribution=cdf)
            if ui==xi:
                continue # same source, skip
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

