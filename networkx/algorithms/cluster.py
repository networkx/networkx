"""
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__= ['triangles', 'average_clustering', 'clustering', 'transitivity']

from networkx import NetworkXError

def triangles(G,nbunch=None,with_labels=False):
    """Compute the number of triangles.

    Finds the number of triangles that include a node as one of the vertices.

    Parameters
    ----------
    G : graph
       A networkx graph
    nbunch : container of nodes, optional
       Compute triangles for nodes in nbunch. The default is all nodes in G.
    with_labels: bool, optional
        If True return a dictionary keyed by node label.

    Returns
    -------
    out : list or dictionary
       Number of trianges
    
    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print nx.triangles(G,0)
    6
    >>> print nx.triangles(G,with_labels=True)
    {0: 6, 1: 6, 2: 6, 3: 6, 4: 6}
    >>> print nx.triangles(G,(0,1))
    [6, 6]

    Notes
    -----
    When computing triangles for the entire graph 
    each triangle is counted three times, once at each node.

    Self loops are ignored.

    """
    if G.is_directed():
        raise NetworkXError("triangles() is not defined for directed graphs.")
    if with_labels:
        return dict( (v,t/2) for v,d,t in _triangles_and_degree_iter(G,nbunch))
    elif nbunch in G: 
        return _triangles_and_degree_iter(G,nbunch).next()[2]/2 # return single value
    return [t/2 for n,d,t in _triangles_and_degree_iter(G,nbunch)]

def _triangles_and_degree_iter(G,nbunch=None):
    """ Return an iterator of (node, degree, triangles).  

    This double counts triangles so you may want to divide by 2.
    See degree() and triangles() for definitions and details.

    """
    if G.is_multigraph():
        raise NetworkXError("Not defined for multigraphs.")

    if nbunch is None:
        nodes_nbrs = G.adj.iteritems()
    else:
        nodes_nbrs= ( (n,G[n]) for n in G.nbunch_iter(nbunch) )

    for v,v_nbrs in nodes_nbrs:
        vs=set(v_nbrs)
        if v in vs:
            vs.remove(v)
        ntriangles=0
        for w in vs:
            ws=set(G[w])
            if w in ws:
                ws.remove(w)
            ntriangles+=len(vs.intersection(ws))
        yield (v,len(vs),ntriangles)


def average_clustering(G):
    """Compute average clustering coefficient.

    A clustering coefficient for the whole graph is the average, 

    .. math::

       C = \\frac{1}{n}\\sum_{v \in G} c_v,
       
    where :math:`n` is the number of nodes in :math:`G`.

    Parameters
    ----------
    G : graph
       A networkx graph

    Returns
    -------
    out : float
       Average clustering
    
    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print nx.average_clustering(G)
    1.0

    Notes
    -----
    This is a space saving routine; it might be faster
    to use clustering to get a list and then take the average.

    Self loops are ignored.

    """
    order=G.order()
    s=sum(clustering(G))
    return s/float(order)

def clustering(G,nbunch=None,with_labels=False,weights=False):
    """ Compute the clustering coefficient for nodes.

    For each node find the fraction of possible triangles that exist,

    .. math::

      c_v = \\frac{2 T(v)}{deg(v)(deg(v)-1)}

    where :math:`T(v)` is the number of triangles through node :math:`v`.       

    Parameters
    ----------
    G : graph
       A networkx graph
    nbunch : container of nodes, optional
       Limit to specified nodes. Default is entire graph.
    with_labels: bool, optional
        If True return a dictionary keyed by node label.
    weights : bool, optional
        If True return fraction of connected triples as dictionary
        
    Returns
    -------
    out : float, list, dictionary or tuple of dictionaries
       Clustering coefficient at specified nodes

    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print nx.clustering(G,0)
    1.0
    >>> print nx.clustering(G,with_labels=True)
    {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}


    Notes
    -----
    The weights are the fraction of connected triples in the graph
    which include the keyed node.  Ths is useful for computing
    transitivity.

    Self loops are ignored.

    """
    if G.is_directed():
        raise NetworkXError("Clustering algorithms are not defined for directed graphs.")
    if with_labels and weights:
        clusterc={}
        weights={}
        for v,d,t in _triangles_and_degree_iter(G,nbunch):
            weights[v]=float(d*(d-1))
            if t==0:
                clusterc[v]=0.0
            else:
                clusterc[v]=t/float(d*(d-1))
        scale=1./sum(weights.itervalues())
        for v,w in weights.iteritems():
            weights[v]=w*scale
        return clusterc,weights

    clusterc={}
    for v,d,t in _triangles_and_degree_iter(G,nbunch):
        if t==0:
            clusterc[v]=0.0
        else:
            clusterc[v]=t/float(d*(d-1))

    if with_labels:
        return clusterc
    elif nbunch in G: 
        return clusterc.values()[0] # return single value
    return clusterc.values()

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
    >>> print nx.transitivity(G)
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

