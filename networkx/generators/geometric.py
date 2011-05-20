# -*- coding: utf-8 -*-
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
           'geographical_threshold_graph',
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

def geographical_threshold_graph(n, theta, alpha=2, dim=2, 
                                 pos=None, weight=None):
    r"""Return a geographical threshold graph.

    The geographical threshold graph model places n nodes uniformly at random
    in a rectangular domain.  Each node `u` is assigned a weight `w_u`. 
    Two nodes u,v are connected with an edge if

    .. math::

       w_u + w_v \ge \theta r^{\alpha}

    where `r` is the Euclidean distance between `u` and `v`, 
    and `\theta`, `\alpha` are parameters.

    Parameters
    ----------
    n : int
        Number of nodes
    theta: float
        Threshold value
    alpha: float, optional
        Exponent of distance function
    dim : int, optional
        Dimension of graph
    pos : dict
        Node positions as a dictionary of tuples keyed by node.
    weight : dict
        Node weights as a dictionary of numbers keyed by node.

    Returns
    -------
    Graph
      
    Examples
    --------
    >>> G = nx.geographical_threshold_graph(20,50)

    Notes
    -----
    If weights are not specified they are assigned to nodes by drawing randomly
    from an the exponential distribution with rate parameter `\lambda=1`.
    To specify a weights from a different distribution assign them to a 
    dictionary and pass it as the weight= keyword

    >>> import random
    >>> n = 20
    >>> w=dict((i,random.expovariate(5.0)) for i in range(n))
    >>> G = nx.geographical_threshold_graph(20,50,weight=w)
    
    If node positions are not specified they are randomly assigned from the
    uniform distribution.

    References
    ----------
    .. [1] Masuda, N., Miwa, H., Konno, N.: 
       Geographical threshold graphs with small-world and scale-free properties.
       Physical Review E 71, 036108 (2005)
    .. [2]  Milan Bradonjić, Aric Hagberg and Allon G. Percus, 
       Giant component and connectivity in geographical threshold graphs, 
       in Algorithms and Models for the Web-Graph (WAW 2007), 
       Antony Bonato and Fan Chung (Eds), pp. 209--216, 2007
    """
    G=nx.Graph()
    # add n nodes
    G.add_nodes_from([v for v in range(n)])  
    if weight is None:
        # choose weights from exponential distribution 
        for n in G:
            G.node[n]['weight'] = random.expovariate(1.0)
    else:
        nx.set_node_attributes(G,'weight',weight)
    if pos is None:
        # random positions 
        for n in G:
            G.node[n]['pos']=[random.random() for i in range(0,dim)]
    else:
        nx.set_node_attributes(G,'pos',pos)
    G.add_edges_from(geographical_threshold_edges(G, theta, alpha))
    return G

def geographical_threshold_edges(G, theta, alpha=2):
    # generate edges for a geographical threshold graph given a graph 
    # with positions and weights assigned as node attributes 'pos' and 'weight'.
    nodes = G.nodes(data=True)
    while nodes:
        u,du = nodes.pop()
        wu = du['weight']
        pu = du['pos']
        for v,dv in nodes:
            wv = dv['weight']
            pv = dv['pos']
            r = math.sqrt(sum(((a-b)**2 for a,b in zip(pu,pv))))
            if wu+wv >= theta*r**alpha:
                yield(u,v)

def waxman_graph(n, alpha=0.4, beta=0.1, L=None, domain=(0,0,1,1)):
    r"""Return a Waxman random graph.

    The Waxman random graph model places n nodes uniformly at random
    in a rectangular domain. Two nodes u,v are connected with an edge
    with probability

    .. math::
            p = \alpha*exp(d/(\beta*L)).

    This function implements both Waxman models.            

    Waxman-1:  `L` not specified
       The distance `d` is the Euclidean distance between the nodes u and v.
       `L` is the maximum distance between all nodes in the graph.

    Waxman-2: `L` specified
       The distance `d` is chosen randomly in `[0,L]`.

    Parameters
    ----------
    n : int
        Number of nodes
    alpha: float
        Model parameter
    beta: float
        Model parameter
    L : float, optional
        Maximum distance between nodes.  If not specified the actual distance
        is calculated.
    domain : tuple of numbers, optional
         Domain size (xmin, ymin, xmax, ymax)

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
    (xmin,ymin,xmax,ymax)=domain
    for n in G:
        G.node[n]['pos']=((xmin + (xmax-xmin))*random.random(),
                          (ymin + (ymax-ymin))*random.random())
    if L is None:
        # find maximum distance L between two nodes
        l = 0
        pos = list(nx.get_node_attributes(G,'pos').values())
        while pos:
            x1,y1 = pos.pop()
            for x2,y2 in pos:
                r2 = (x1-x2)**2 + (y1-y2)**2
                if r2 > l:
                    l = r2
        l=math.sqrt(l)
    else: 
        # user specified maximum distance
        l = L

    nodes=G.nodes()
    if L is None:
        # Waxman-1 model
        # try all pairs, connect randomly based on euclidean distance
        while nodes:
            u = nodes.pop()
            x1,y1 = G.node[u]['pos']
            for v in nodes:
                x2,y2 = G.node[v]['pos']
                r = math.sqrt((x1-x2)**2 + (y1-y2)**2)
                if random.random() < alpha*math.exp(-r/(beta*l)):
                    G.add_edge(u,v)
    else:
        # Waxman-2 model
        # try all pairs, connect randomly based on randomly chosen l
        while nodes:
            u = nodes.pop()
            for v in nodes:
                r = random.random()*l
                if random.random() < alpha*math.exp(-r/(beta*l)):
                    G.add_edge(u,v)
    return G
