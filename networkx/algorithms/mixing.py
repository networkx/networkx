#-*- coding: utf-8 -*-
"""
Mixing matrices and assortativity coefficients.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

__all__ = ['degree_assortativity',
           'attribute_assortativity',
           'numeric_assortativity',
           'attribute_mixing_matrix',
           'degree_mixing_matrix',
           'degree_pearsonr',
           'degree_mixing_dict',
           'attribute_mixing_dict',
           ]

import networkx as nx

def degree_assortativity(G,nodes=None):
    """Compute degree assortativity of graph.

    Assortativity measures the similarity of connections
    in the graph with respect to the node degree.

    Parameters
    ----------
    G : NetworkX graph

    nodes: list or iterable (optional)
        Compute degree assortativity only for nodes in container. 
        The default is all nodes.

    Returns
    -------
    r : float
       Assortativity of graph by degree.
    
    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> r=nx.degree_assortativity(G)
    >>> print("%3.1f"%r)
    -0.5

    See Also
    --------
    attribute_assortativity
    numeric_assortativity
    neighbor_connectivity
    degree_mixing_dict
    degree_mixing_matrix

    Notes
    -----
    This computes Eq. (21) in Ref. [1]_ , where e is the joint
    probability distribution (mixing matrix) of the degrees.  If G is
    directed than the matrix e is the joint probability of out-degree
    and in-degree.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks,
       Physical Review E, 67 026126, 2003

    """
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    return numeric_assortativity_coefficient(degree_mixing_matrix(G, node_iter))


def degree_pearsonr(G,nodes=None):
    """Compute degree assortativity of graph. 

    Assortativity measures the similarity of connections
    in the graph with respect to the node degree.

    Parameters
    ----------
    G : NetworkX graph

    nodes: list or iterable (optional)
        Compute pearson correlation of degrees only for nodes in container.
        The default is all nodes.

    Returns
    -------
    r : float
       Assortativity of graph by degree.
    
    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> r=nx.degree_pearsonr(G) 
    >>> r 
    -0.5

    Notes
    -----
    This calls scipy.stats.pearsonr().

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks
           Physical Review E, 67 026126, 2003
    """
    try:
        import scipy.stats as stats
    except ImportError:
        raise ImportError(
          "Assortativity requires SciPy: http://scipy.org/ ")
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    xy=node_degree_xy(G,node_iter)
    x,y=zip(*xy)
    return stats.pearsonr(x,y)[0]

def attribute_mixing_dict(G,attribute,nodes=None,normalized=False):
    """Return dictionary representation of mixing matrix for attribute.

    Parameters
    ----------
    G : graph 
       NetworkX graph object.

    attribute : string 
       Node attribute key.

    nodes: list or iterable (optional)
        Unse nodes in container to build the dict. The default is all nodes.

    normalized : bool (default=False)
       Return counts if False or probabilities if True.

    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_nodes_from([0,1],color='red')
    >>> G.add_nodes_from([2,3],color='blue')
    >>> G.add_edge(1,3)
    >>> d=nx.attribute_mixing_dict(G,'color')
    >>> print(d['red']['blue'])
    1
    >>> print(d['blue']['red']) # d symmetric for undirected graphs
    1

    Returns
    -------
    d : dictionary
       Counts or joint probability of occurrence of attribute pairs.
    """
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    xy_iter=node_attribute_xy(G,attribute,node_iter)
    return mixing_dict(xy_iter,normalized=normalized)


def attribute_mixing_matrix(G,attribute,nodes=None,mapping=None,normalized=True):
    """Return mixing matrix for attribute.

    Parameters
    ----------
    G : graph 
       NetworkX graph object.

    attribute : string 
       Node attribute key.

    nodes: list or iterable (optional)
        Use only nodes in container to build the matrix. The default is 
        all nodes.

    mapping : dictionary, optional        
       Mapping from node attribute to integer index in matrix.  
       If not specified, an arbitrary ordering will be used. 
    
    normalized : bool (default=False)
       Return counts if False or probabilities if True.

    Returns
    -------
    m: numpy array
       Counts or joint probability of occurrence of attribute pairs.
    """
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    d=attribute_mixing_dict(G,attribute,node_iter)
    a=dict_to_numpy_array(d,mapping=mapping)
    if normalized:
        a=a/a.sum()
    return a


def attribute_assortativity(G,attribute,nodes=None):
    """Compute assortativity for node attributes.

    Assortativity measures the similarity of connections
    in the graph with respect to the given attribute.
    
    Parameters
    ----------
    G : NetworkX graph

    attribute : string 
        Node attribute key

    nodes: list or iterable (optional)
        Compute attribute assortativity for nodes in container. 
        The default is all nodes. 

    Returns
    -------
    a: float
       Assortativity of given attribute
    
    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_nodes_from([0,1],color='red')
    >>> G.add_nodes_from([2,3],color='blue')
    >>> G.add_edges_from([(0,1),(2,3)])
    >>> print(nx.attribute_assortativity(G,'color'))
    1.0

    Notes
    -----
    This computes Eq. (2) in Ref. [1]_ , (trace(e)-sum(e))/(1-sum(e)),
    where e is the joint probability distribution (mixing matrix)
    of the specified attribute.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks,
       Physical Review E, 67 026126, 2003
    """
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    a=attribute_mixing_matrix(G,attribute,node_iter)
    return attribute_assortativity_coefficient(a)


def numeric_assortativity(G,attribute,nodes=None):
    """Compute assortativity for numerical node attributes.

    Assortativity measures the similarity of connections
    in the graph with respect to the given numeric attribute.
    
    Parameters
    ----------
    G : NetworkX graph

    attribute : string 
        Node attribute key

    nodes: list or iterable (optional)
        Compute numeric assortativity only for attributes of nodes in 
        container. The default is all nodes.

    Returns
    -------
    a: float
       Assortativity of given attribute
    
    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_nodes_from([0,1],size=2)
    >>> G.add_nodes_from([2,3],size=3)
    >>> G.add_edges_from([(0,1),(2,3)])
    >>> print(nx.numeric_assortativity(G,'size'))
    1.0

    Notes
    -----
    This computes Eq. (21) in Ref. [1]_ ,
    where e is the joint probability distribution (mixing matrix)
    of the specified attribute.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks
           Physical Review E, 67 026126, 2003
    """
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    a=numeric_mixing_matrix(G,attribute,node_iter)
    return numeric_assortativity_coefficient(a)


def attribute_assortativity_coefficient(e):
    """Compute assortativity for attribute matrix e.

    Parameters
    ----------
    e : numpy array or matrix
        Attribute mixing matrix.

    Notes
    -----
    This computes Eq. (2) in Ref. [1]_ , (trace(e)-sum(e))/(1-sum(e)),
    where e is the joint probability distribution (mixing matrix)
    of the specified attribute.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks,
       Physical Review E, 67 026126, 2003
    """
    try:
        import numpy
    except ImportError:
        raise ImportError(
          "attribute_assortativity requires NumPy: http://scipy.org/ ")
    if e.sum() != 1.0:
        e=e/float(e.sum())
    e=numpy.asmatrix(e)
    s=(e*e).sum()
    t=e.trace()
    r=(t-s)/(1-s)
    return float(r)


def degree_mixing_dict(G,nodes=None,normalized=False):
    """Return dictionary representation of mixing matrix for degree.

    Parameters
    ----------
    G : graph 
        NetworkX graph object.

    normalized : bool (default=False)
        Return counts if False or probabilities if True.

    Returns
    -------
    d: dictionary
       Counts or joint probability of occurrence of degree pairs.
    """
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    xy_iter=node_degree_xy(G,node_iter)
    return mixing_dict(xy_iter,normalized=normalized)


def numeric_mixing_matrix(G,attribute,nodes=None,normalized=True):
    """Return numeric mixing matrix for attribute.

    Parameters
    ----------
    G : graph 
       NetworkX graph object.

    attribute : string 
       Node attribute key.

    nodes: list or iterable (optional)
        Build the matrix only with nodes in container. The default is all nodes.
    
    normalized : bool (default=False)
       Return counts if False or probabilities if True.

    Returns
    -------
    m: numpy array
       Counts, or joint, probability of occurrence of node attribute pairs.
    """
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    d=attribute_mixing_dict(G,attribute,node_iter)
    s=set(d.keys())
    for k,v in d.items():
        s.update(v.keys())
    m=max(s)            
    mapping=dict(zip(range(m+1),range(m+1)))
    a=dict_to_numpy_array(d,mapping=mapping)
    if normalized:
        a=a/a.sum()
    return a

def degree_mixing_matrix(G,nodes=None,normalized=True):
    """Return mixing matrix for attribute.

    Parameters
    ----------
    G : graph 
       NetworkX graph object.

    nodes: list or iterable (optional)
        Build the matrix using only nodes in container. 
        The default is all nodes.

    normalized : bool (default=False)
       Return counts if False or probabilities if True.

    Returns
    -------
    m: numpy array
       Counts, or joint probability, of occurrence of node degree.
    """
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    d=degree_mixing_dict(G,node_iter)
    s=set(d.keys())
    for k,v in d.items():
        s.update(v.keys())
    m=max(s)            
    mapping=dict(zip(range(m+1),range(m+1)))
    a=dict_to_numpy_array(d,mapping=mapping)
    if normalized:
        a=a/a.sum()
    return a

def numeric_assortativity_coefficient(e):
    try:
        import numpy
    except ImportError:
        raise ImportError(
          "numeric_assortativity_coefficient requires NumPy: http://scipy.org/ ")
    if e.sum() != 1.0:
        e=e/float(e.sum())
    nx,ny=e.shape # nx=ny
    x=numpy.arange(nx)
    y=numpy.arange(ny)
    a=e.sum(axis=0)
    b=e.sum(axis=1)
    vara=(a*x**2).sum()-((a*x).sum())**2
    varb=(b*x**2).sum()-((b*x).sum())**2
    xy=numpy.outer(x,y)
    ab=numpy.outer(a,b)
    return (xy*(e-ab)).sum()/numpy.sqrt(vara*varb)

def mixing_dict(xy,normalized=False):
    """Return a dictionary representation of mixing matrix.

    Parameters
    ----------
    xy : list or container of two-tuples
       Pairs of (x,y) items. 

    attribute : string 
       Node attribute key 

    normalized : bool (default=False)
       Return counts if False or probabilities if True.

    Returns
    -------
    d: dictionary
       Counts or Joint probability of occurrence of values in xy.
    """

    d={}
    psum=0.0
    for x,y in xy:
        if x not in d:
            d[x]={}
        if y not in d:
            d[y]={}
        v=d[x].setdefault(y,0)
        d[x][y]=v+1
        psum+=1

    if normalized:
        for k,jdict in d.items():
            for j in jdict:
                jdict[j]/=psum
    return d


def dict_to_numpy_array(d,mapping=None):
    """Convert a dictionary to numpy array with optional mapping."""
    try:
        import numpy 
    except ImportError:
        raise ImportError(
          "dict_to_numpy_array requires numpy : http://scipy.org/ ")
    if mapping is None:
        s=set(d.keys())
        for k,v in d.items():
            s.update(v.keys())
        mapping=dict(zip(s,range(len(s))))
    n=len(mapping)
    a = numpy.zeros((n, n))
    for k1, row in d.items():
        for k2, value in row.items():
            i=mapping[k1]
            j=mapping[k2]
            a[i,j] = value 
    return a


def node_attribute_xy(G,attribute,nodes=None):
    """Return iterator of node attribute pairs for all edges in G.

    For undirected graphs each edge is produced twice, once for each
    representation u-v and v-u, with the exception of self loop edges
    that only appear once.
    """
    if nodes is None:
        node_set = G
    else:
        node_set = G.subgraph(nodes)
    node=G.node
    for u,nbrsdict in G.adjacency_iter():
        if u not in node_set:
            continue
        uattr=node[u].get(attribute,None)
        if G.is_multigraph():
            for v,keys in nbrsdict.items():
                vattr=node[v].get(attribute,None)                
                for k,d in keys.items():
                    yield (uattr,vattr)
        else:
            for v,eattr in nbrsdict.items():
                vattr=node[v].get(attribute,None)
                yield (uattr,vattr)


def node_degree_xy(G,nodes=None):
    """Return iterator of degree-degree pairs for edges in G.

    Parameters
    ----------
    G : NetworkX graph

    nodes: list or iterable (optional)
        Use only edges that start or end in nodes in this container. 
        The default is all nodes.

    Notes
    -----
    For undirected graphs each edge is produced twice, once for each 
    representation u-v and v-u, with the exception of self loop edges 
    that only appear once.

    For directed graphs this produces out-degree,in-degree pairs
    """
    if nodes is None:
        node_set = G
    else:
        node_set = G.subgraph(nodes)
    if G.is_directed():
        in_degree=G.in_degree
        out_degree=G.out_degree
    else:
        in_degree=G.degree
        out_degree=G.degree
    for u,nbrsdict in G.adjacency_iter():
        if u not in node_set:
            continue
        degu=out_degree(u)
        if G.is_multigraph():
            for v,keys in nbrsdict.items():
                degv=in_degree(v)
                for k,d in keys.items():
                    yield degu,degv
        else:
            for v,eattr in nbrsdict.items():
                degv=in_degree(v)
                yield degu,degv

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
    try:
        import scipy
    except:
        raise SkipTest("SciPy not available")
