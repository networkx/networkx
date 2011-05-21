#-*- coding: utf-8 -*-
#    Copyright (C) 2011 by 
#    Jordi Torrents <jtorrents@milnou.net>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['Jordi Torrents <jtorrents@milnou.net>',
                            'Aric Hagberg (hagberg@lanl.gov)'])
__all__ = ['clustering','average_clustering']

# functions for computing clustering of pairs
def cc_dot(nu,nv):
    return float(len(nu & nv))/len(nu | nv)

def cc_max(nu,nv):
    return float(len(nu & nv))/max(len(nu),len(nv))

def cc_min(nu,nv):
    return float(len(nu & nv))/min(len(nu),len(nv))
    
modes={'dot':cc_dot,
       'min':cc_min,
       'max':cc_max}

def clustering(G, nodes=None, mode='dot'):
    r"""Compute a bipartite clustering coefficient for nodes.

    The bipartie clustering coefficient is a measure of local density
    of connections defined as [1]_
    
    .. math::

       c_u = \frac{\sum_{v \in N(N(v))} c_{uv} }{|N(N(u))|}

    where `N(N(u))` are the second order neighbors of `u` in `G` excluding `u`, 
    and `c_{uv}` is the pairwise clustering coefficient between nodes 
    `u` and `v`.

    The mode selects the function for `c_{uv}`
    'dot': 

    .. math::

       c_{uv}=\frac{|N(u)\cap N(v)|}{|N(u) \cup N(v)|}

    'min': 

    .. math::

       c_{uv}=\frac{|N(u)\cap N(v)|}{min(|N(u)|,|N(v)|)}

    'max': 

    .. math::

       c_{uv}=\frac{|N(u)\cap N(v)|}{max(|N(u)|,|N(v)|)}


    Parameters
    ----------
    G : graph
        A bipartite graph

    nodes : list or iterable (optional)
        Compute bipartite clustering for these nodes. The default 
        is all nodes in G.

    mode : string
        The pariwise bipartite clustering method to be used in the computation.
        It must be "dot", "max", or "min". 
    
    Returns
    -------
    clustering : dictionary
        A dictionary keyed by node with the clustering coefficient value.


    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G=nx.path_graph(4) # path is bipartite
    >>> c=bipartite.clustering(G) 
    >>> c[0]
    0.5
    >>> c=bipartite.clustering(G,mode='min') 
    >>> c[0]
    1.0

    See Also
    --------
    networkx.algorithms.bipartite.cluster.average_clustering
    
    References
    ----------
    .. [1] Latapy, Matthieu, Clémence Magnien, and Nathalie Del Vecchio (2008).
       Basic notions for the analysis of large two-mode networks. 
       Social Networks 30(1), 31--48.
    """
    if not nx.algorithms.bipartite.is_bipartite(G):
        raise nx.NetworkXError("Graph is not bipartite")
    
    try:
        cc_func = modes[mode]
    except KeyError:
        raise nx.NetworkXError(\
                "Mode for bipartite clustering must be: dot, min or max")

    if nodes is None:
        nodes = G
    ccs = {}
    for v in nodes:
        cc = 0.0
        nbrs2=set([u for nbr in G[v] for u in G[nbr]])-set([v])
        for u in nbrs2:
            cc += cc_func(set(G[u]),set(G[v]))
        if cc > 0.0: # len(nbrs2)>0
            cc /= len(nbrs2)
        ccs[v] = cc
    return ccs

def average_clustering(G, nodes=None, mode='dot'):
    r"""Compute the average bipartite clustering coefficient.

    A clustering coefficient for the whole graph is the average, 

    .. math::

       C = \frac{1}{n}\sum_{v \in G} c_v,
       
    where `n` is the number of nodes in `G`.

    Similar measures for the two bipartite sets can be defined [1]_
    
    .. math::

       C_X = \frac{1}{|X|}\sum_{v \in X} c_v,
       
    where `X` is a bipartite set of `G`.

    Parameters
    ----------
    G : graph
        A bipartite graph

    nodes : list or iterable, optional
        A container of nodes to use in computing the average.  
        The nodes should be either the entire graph (the default) or one of the 
        bipartite sets.

    mode : string
        The pariwise bipartite clustering method. 
        It must be "dot", "max", or "min" 
    
    Returns
    -------
    clustering : float
       The average bipartite clustering for the given set of nodes or the 
       entire graph if no nodes are specified.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G=nx.star_graph(3) # path is bipartite
    >>> bipartite.average_clustering(G) 
    0.75
    >>> X,Y=bipartite.sets(G)
    >>> bipartite.average_clustering(G,X) 
    0.0
    >>> bipartite.average_clustering(G,Y) 
    1.0

    See Also
    --------
    networkx.algorithms.bipartite.cluster.clustering
   
    Notes    
    -----
    The container of nodes passed to this function must contain all of the nodes
    in one of the bipartite sets ("top" or "bottom") in order to compute 
    the correct average bipartite clustering coefficients.

    References
    ----------
    .. [1] Latapy, Matthieu, Clémence Magnien, and Nathalie Del Vecchio (2008).
        Basic notions for the analysis of large two-mode networks. 
        Social Networks 30(1), 31--48.
    """
    if nodes is None:
        nodes=G
    ccs=clustering(G, nodes=nodes, mode=mode)
    return float(sum(ccs[v] for v in nodes))/len(nodes)
