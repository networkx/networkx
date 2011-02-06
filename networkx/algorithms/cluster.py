# -*- coding: utf-8 -*-
"""
Algorithms to characterize the number of triangles in a graph.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__= ['triangles', 'average_clustering', 'clustering', 'transitivity']

import networkx as nx
from networkx import NetworkXError

def triangles(G,nodes=None):
    """Compute the number of triangles.

    Finds the number of triangles that include a node as one of the vertices.

    Parameters
    ----------
    G : graph
       A networkx graph
    nodes : container of nodes, optional
       Compute triangles for nodes. The default is all nodes in G.

    Returns
    -------
    out : dictionary
       Number of trianges keyed by node label.
    
    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print(nx.triangles(G,0))
    6
    >>> print(nx.triangles(G))
    {0: 6, 1: 6, 2: 6, 3: 6, 4: 6}
    >>> print(list(nx.triangles(G,(0,1)).values()))
    [6, 6]

    Notes
    -----
    When computing triangles for the entire graph each triangle is counted 
    three times, once at each node.  Self loops are ignored.

    """
    if G.is_directed():
        raise NetworkXError("triangles() is not defined for directed graphs.")
    if nodes in G: 
        # return single value
        return next(_triangles_and_degree_iter(G,nodes))[2] // 2
    return dict( (v,t // 2) for v,d,t in _triangles_and_degree_iter(G,nodes))

def _triangles_and_degree_iter(G,nodes=None):
    """ Return an iterator of (node, degree, triangles).  

    This double counts triangles so you may want to divide by 2.
    See degree() and triangles() for definitions and details.

    """
    if G.is_multigraph():
        raise NetworkXError("Not defined for multigraphs.")

    if nodes is None:
        nodes_nbrs = iter(G.adj.items())
    else:
        nodes_nbrs= ( (n,G[n]) for n in G.nbunch_iter(nodes) )

    for v,v_nbrs in nodes_nbrs:
        vs=set(v_nbrs)-set([v])
        ntriangles=0
        for w in vs:
            ws=set(G[w])-set([w])
            ntriangles+=len(vs.intersection(ws))
        yield (v,len(vs),ntriangles)


def _weighted_triangles_and_degree_iter(G,nodes=None):
    """ Return an iterator of (node, degree, weighted_triangles).  
    
    Used for weighted clustering.

    """
    if G.is_multigraph():
        raise NetworkXError("Not defined for multigraphs.")

    if G.edges()==[]:
        max_weight=1.0
    else:
        max_weight=float(max(d.get('weight',1.0) 
                             for u,v,d in G.edges(data=True)))
    if nodes is None:
        nodes_nbrs = iter(G.adj.items())
    else:
        nodes_nbrs= ( (n,G[n]) for n in G.nbunch_iter(nodes) )

    for i,nbrs in nodes_nbrs:
        inbrs=set(nbrs)-set([i])
        weighted_triangles=0.0
        seen=set()
        for j in inbrs:
            wij=G[i][j].get('weight',1.0)/max_weight
            seen.add(j)
            jnbrs=set(G[j])-seen # this keeps from double counting
            for k in inbrs&jnbrs:
                wjk=G[j][k].get('weight',1.0)/max_weight
                wki=G[i][k].get('weight',1.0)/max_weight
                weighted_triangles+=(wij*wjk*wki)**(1.0/3.0)
        yield (i,len(inbrs),weighted_triangles*2)


def average_clustering(G,weighted=False):
    """Compute average clustering coefficient.

    A clustering coefficient for the whole graph is the average, 

    .. math::

       C = \\frac{1}{n}\\sum_{v \in G} c_v,
       
    where :math:`n` is the number of nodes in :math:`G`.

    Parameters
    ----------
    G : graph
       A networkx graph
    weighted : bool, optional
       If True use weights on edges in computing clustering coefficients.

    Returns
    -------
    out : float
       Average clustering
    
    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print(nx.average_clustering(G))
    1.0

    Notes
    -----
    This is a space saving routine; it might be faster
    to use clustering to get a list and then take the average.

    Self loops are ignored.

    References
    ----------
    .. [1] Generalizations of the clustering coefficient to weighted 
       complex networks by J. Saramäki, M. Kivelä, J.-P. Onnela, 
       K. Kaski, and J. Kertész, Physical Review E, 75 027105 (2007).  
       http://jponnela.com/web_documents/a9.pdf
    """
    order=G.order()
    s=sum(clustering(G,weighted=weighted).values())
    return s/float(order)

def clustering(G,nodes=None,weighted=False):
    """ Compute the clustering coefficient for nodes.

    For each node find the fraction of possible triangles that exist,

    .. math::

      c_v = \\frac{2 T(v)}{deg(v)(deg(v)-1)}

    where :math:`T(v)` is the number of triangles through node :math:`v`.       

    Parameters
    ----------
    G : graph
       A networkx graph
    nodes : container of nodes, optional
       Limit to specified nodes. Default is entire graph.
    weighted : bool, optional
       If True use weights on edges in computing clustering coefficients.
        
    Returns
    -------
    out : float, dictionary or tuple of dictionaries
       Clustering coefficient at specified nodes

    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print(nx.clustering(G,0))
    1.0
    >>> print(nx.clustering(G))
    {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}


    Notes
    -----
    Self loops are ignored.

    References
    ----------
    .. [1] Generalizations of the clustering coefficient to weighted 
       complex networks by J. Saramäki, M. Kivelä, J.-P. Onnela, 
       K. Kaski, and J. Kertész, Physical Review E, 75 027105 (2007).  
       http://jponnela.com/web_documents/a9.pdf
    """
    if G.is_directed():
        raise NetworkXError('Clustering algorithms are not defined',
                            'for directed graphs.')
    if weighted:
        td_iter=_weighted_triangles_and_degree_iter
    else:
        td_iter=_triangles_and_degree_iter

    clusterc={}

    for v,d,t in td_iter(G,nodes):
        if t==0:
            clusterc[v]=0.0
        else:
            clusterc[v]=t/float(d*(d-1))

    if nodes in G: 
        return list(clusterc.values())[0] # return single value
    return clusterc

def transitivity(G):
    """Compute transitivity.

    Finds the fraction of all possible triangles which are in fact triangles.
    Possible triangles are identified by the number of "triads" (two edges
    with a shared vertex).

    T = 3*triangles/triads


    Parameters
    ----------
    G : graph
       A networkx graph

    Returns
    -------
    out : float
       Transitivity

    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print(nx.transitivity(G))
    1.0

"""
    triangles=0 # 6 times number of triangles
    contri=0  # 2 times number of connected triples
    for v,d,t in _triangles_and_degree_iter(G):
        contri += d*(d-1)
        triangles += t
    if triangles==0: # we had no triangles or possible triangles
        return 0.0
    else:
        return triangles/float(contri)

