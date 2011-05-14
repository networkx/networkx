"""
Generators for geometric graphs.
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from __future__ import print_function

__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Dan Schult (dschult@colgate.edu)',
                        'Ben Edwards (BJEdwards@gmail.com)'])

__all__ = ['random_geometric_graph',
           'waxman_graph']

import math, random, sys
from functools import reduce
import networkx as nx

#---------------------------------------------------------------------------
#  Random Geometric Graphs
#---------------------------------------------------------------------------
        
def random_geometric_graph(n, radius, create_using=None, repel=0.0, verbose=False, dim=2):
    """Random geometric graph in the unit cube.

    Returned Graph has added attribute G.pos which is a 
    dict keyed by node to the position tuple for the node.
    """
    if create_using is None:    
        G=nx.Graph()
    else:
        G=create_using
        G.clear()
    G.name="Random Geometric Graph"
    G.add_nodes_from([v for v in range(n)])  # add n nodes
    # position them randomly in the unit cube in n dimensions
    # but not any two within "repel" distance of each other
    # pick n random positions
    positions=[]
    while(len(positions)< n):
        pnew=[]
        [pnew.append(random.random()) for i in range(0,dim)]
        reject=False
        # avoid existing nodes
        if repel > 0.0 :
            for pold in positions:
                m2=map(lambda x,y: (x-y)**2, pold,pnew)
                r2=reduce(lambda x, y: x+y, m2, 0.)
                if r2 < repel**2 :
                    reject=True
                    print("rejecting", len(positions),pnew, file = sys.stderr)
                    break
            if(reject):
                reject=False
                continue
        if(verbose):
            print("accepting", len(positions),pnew, file = sys.stderr)
        positions.append(pnew)

    # add positions to nodes        
    G.pos={}
    for v in G.nodes():
        G.pos[v]=positions.pop()

    # connect nodes within "radius" of each other
    # n^2 algorithm, oh well, should work in n dimensions anyway...
    for u in G.nodes():
        p1=G.pos[u]
        for v in G.nodes():
            if u==v:  # no self loops
                continue
            p2=G.pos[v]
            m2=map(lambda x,y: (x-y)**2, p1,p2)
            r2=reduce(lambda x, y: x+y, m2, 0.)
            if r2 < radius**2 :
                G.add_edge(u,v)
    return G

def waxman_graph(n, alpha=0.4, beta=0.1):
    """Return a Waxman random graph.

    The Waxman random graph model places n nodes uniformly at random in 
    the unit square.  Two nodes u,v are connected with an edge with probability

    .. math::
            p = alpha*exp(d/(beta*L))

    where d is the Euclidean distance between the nodes u and v and   
    L is the maximum distance between all nodes in the graph.

    Parameters
    ----------
    n : int
        Number of nodes
    alpha: float
        Model parameter
    beta: float
        Model parameter

    Returns
    -------
    G: Graph

    References
    ----------
    .. [1]  B. M. Waxman, Routing of multipoint connections. 
       IEEE J. Select. Areas Commun. 6(9),(1988) 1617-1622. 
    """
    # build graph of n nodes with random positions in the unit square
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for n in G:
        G.node[n]['pos']=(random.random(),random.random())

    # find maximum distance L between two nodes
    L = 0
    pos = nx.get_node_attributes(G,'pos').values()
    while pos:
        x1,y1 = pos.pop()
        for x2,y2 in pos:
            r2 = (x1-x2)**2 + (y1-y2)**2
            if r2 > L:
                L = r2
    L=math.sqrt(L)

    # try all pairs and connect probabilistically
    nodes=G.nodes()
    while nodes:
        u = nodes.pop()
        x1,y1 = G.node[u]['pos']
        for v in nodes:
            x2,y2 = G.node[v]['pos']
            r = math.sqrt((x1-x2)**2 + (y1-y2)**2)
            if random.random() < alpha*math.exp(-r/(beta*L)):
                G.add_edge(u,v)
    return G
