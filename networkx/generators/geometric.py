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
           'waxman_graph',
           'geographical_threshold_graph',
           'navigable_small_world_graph']

from bisect import bisect_left
from functools import reduce
from itertools import product
import math, random, sys
import networkx as nx

#---------------------------------------------------------------------------
#  Random Geometric Graphs
#---------------------------------------------------------------------------
        
def random_geometric_graph(n, radius, dim=2, pos=None):
    r"""Return the random geometric graph in the unit cube.

    The random geometric graph model places n nodes uniformly at random 
    in the unit cube  Two nodes `u,v` are connected with an edge if
    `d(u,v)<=r` where `d` is the Euclidean distance and `r` is a radius 
    threshold.

    Parameters
    ----------
    n : int
        Number of nodes
    radius: float
        Distance threshold value  
    dim : int, optional
        Dimension of graph
    pos : dict, optional
        A dictionary keyed by node with node positions as values.

    Returns
    -------
    Graph
      
    Examples
    --------
    >>> G = nx.random_geometric_graph(20,0.1)

    Notes
    -----
    This uses an `n^2` algorithm to build the graph.  A faster algorithm
    is possible using k-d trees.

    The pos keyword can be used to specify node positions so you can create
    an arbitrary distribution and domain for positions.  If you need a distance
    function other than Euclidean you'll have to hack the algorithm.

    E.g to use a 2d Gaussian distribution of node positions with mean (0,0)
    and std. dev. 2

    >>> import random
    >>> n=20
    >>> p=dict((i,(random.gauss(0,2),random.gauss(0,2))) for i in range(n))
    >>> G = nx.random_geometric_graph(n,0.2,pos=p)

    References
    ----------
    .. [1] Penrose, Mathew, Random Geometric Graphs, 
       Oxford Studies in Probability, 5, 2003.
    """
    G=nx.Graph()
    G.name="Random Geometric Graph"
    G.add_nodes_from(range(n)) 
    if pos is None:
        # random positions 
        for n in G:
            G.node[n]['pos']=[random.random() for i in range(0,dim)]
    else:
        nx.set_node_attributes(G,'pos',pos)
    # connect nodes within "radius" of each other
    # n^2 algorithm, could use a k-d tree implementation
    nodes = G.nodes(data=True)
    while nodes:
        u,du = nodes.pop()
        pu = du['pos']
        for v,dv in nodes:
            pv = dv['pos']
            d = sum(((a-b)**2 for a,b in zip(pu,pv)))
            if d <= radius**2:
                G.add_edge(u,v)
    return G

def geographical_threshold_graph(n, theta, alpha=2, dim=2, 
                                 pos=None, weight=None):
    r"""Return a geographical threshold graph.

    The geographical threshold graph model places n nodes uniformly at random
    in a rectangular domain.  Each node `u` is assigned a weight `w_u`. 
    Two nodes `u,v` are connected with an edge if

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

    The Waxman random graph models place n nodes uniformly at random
    in a rectangular domain. Two nodes u,v are connected with an edge
    with probability

    .. math::
            p = \alpha*exp(-d/(\beta*L)).

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


def navigable_small_world_graph(n, p=1, q=1, r=2, dim=2, seed=None):
    r"""Return a navigable small-world graph.

    A navigable small-world graph is a directed grid with additional
    long-range connections that are chosen randomly.  From [1]_:

    Begin with a set of nodes that are identified with the set of lattice
    points in an `n \times n` square, `{(i,j): i\in {1,2,\ldots,n}, j\in {1,2,\ldots,n}}`
    and define the lattice distance between two nodes `(i,j)` and `(k,l)` 
    to be the number of "lattice steps" separating them: `d((i,j),(k,l)) = |k-i|+|l-j|`.  

    For a universal constant `p`, the node `u` has a directed edge to every other 
    node within lattice distance `p` (local contacts) .

    For universal constants `q\ge 0` and `r\ge 0` construct directed edges from `u` to `q`
    other nodes (long-range contacts) using independent random trials;  the i'th 
    directed edge from `u` has endpoint `v` with probability proportional to `d(u,v)^{-r}`.

    Parameters
    ----------
    n : int
        The number of nodes.
    p : int
        The diameter of short range connections. Each node is connected
        to every other node within lattice distance p.
    q : int
        The number of long-range connections for each node.
    r : float
        Exponent for decaying probability of connections.  The probability of 
        connecting to a node at lattice distance d is 1/d^r.
    dim : int
        Dimension of grid
    seed : int, optional
        Seed for random number generator (default=None). 
      
    References
    ----------
    .. [1] J. Kleinberg. The small-world phenomenon: An algorithmic 
       perspective. Proc. 32nd ACM Symposium on Theory of Computing, 2000. 
    """
    if (p < 1):
        raise nx.NetworkXException("p must be >= 1")
    if (q < 0):
        raise nx.NetworkXException("q must be >= 0")
    if (r < 0):
        raise nx.NetworkXException("r must be >= 1")
    if not seed is None:
        random.seed(seed)
    G = nx.DiGraph()
    nodes = list(product(range(n),repeat=dim))
    for p1 in nodes:
        probs = [0]
        for p2 in nodes:
            if p1==p2:
                continue
            d = sum((abs(b-a) for a,b in zip(p1,p2)))
            if d <= p:
                G.add_edge(p1,p2)
            probs.append(d**-r)
        cdf = list(nx.utils.cumulative_sum(probs))
        for _ in range(q):
            target = nodes[bisect_left(cdf,random.uniform(0, cdf[-1]))]
            G.add_edge(p1,target)
    return G
  
