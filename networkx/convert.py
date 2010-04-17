"""
This module provides functions to convert 
NetworkX graphs to and from other formats.

The preferred way of converting data to a NetworkX graph 
is through the graph constuctor.  The constructor calls
the to_networkx_graph() function which attempts to guess the
input type and convert it automatically.

Examples
--------

Create a 10 node random graph from a numpy matrix

>>> import numpy
>>> a=numpy.reshape(numpy.random.random_integers(0,1,size=100),(10,10))
>>> D=nx.DiGraph(a) 

or equivalently

>>> D=nx.to_networkx_graph(a,create_using=nx.DiGraph()) 

Create a graph with a single edge from a dictionary of dictionaries

>>> d={0: {1: 1}} # dict-of-dicts single edge (0,1)
>>> G=nx.Graph(d)


See Also
--------
nx_pygraphviz, nx_pydot

"""
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult(dschult@colgate.edu)'])
#    Copyright (C) 2006-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.


__all__ = ['to_networkx_graph','from_whatever', 
           'convert_node_labels_to_integers', 'relabel_nodes',
           'from_dict_of_dicts', 'to_dict_of_dicts',
           'from_dict_of_lists', 'to_dict_of_lists',
           'from_edgelist', 'to_edgelist',
           'from_numpy_matrix', 'to_numpy_matrix',
           'from_scipy_sparse_matrix', 'to_scipy_sparse_matrix']

import warnings
import networkx as nx


def _prep_create_using(create_using):
    """Return a graph object ready to be populated.

    If create_using is None return the default (just networkx.Graph())
    If create_using.clear() works, assume it returns a graph object.
    Otherwise raise an exception because create_using is not a networkx graph.

    """
    if create_using is None:
        G=nx.Graph()
    else:
        G=create_using
        try:
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")
    return G

def to_networkx_graph(data,create_using=None,multigraph_input=False):
    """Make a NetworkX graph from a known data structure.

    The preferred way to call this is automatically
    from the class constructor

    >>> d={0: {1: {'weight':1}}} # dict-of-dicts single edge (0,1)
    >>> G=nx.Graph(d)
    
    instead of the equivalent

    >>> G=nx.from_dict_of_dicts(d)

    Parameters
    ----------
    data : a object to be converted
       Current known types are:
         any NetworkX graph
         dict-of-dicts
         dist-of-lists
         list of edges
         numpy matrix
         numpy ndarray
         scipy sparse matrix
         pygraphviz agraph

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created.

    multigraph_input : bool (default False)
      If True and  data is a dict_of_dicts,
      try to create a multigraph assuming dict_of_dict_of_lists.
      If data and create_using are both multigraphs then create
      a multigraph from a multigraph.

    """
    # NX graph
    if hasattr(data,"adj"):
        try:
            result= from_dict_of_dicts(data.adj,\
                    create_using=create_using,\
                    multigraph_input=data.is_multigraph())
            if hasattr(data,'graph') and isinstance(data.graph,dict):
                result.graph=data.graph.copy()
            if hasattr(data,'node') and isinstance(data.node,dict):
                result.node=dict( (n,dd.copy()) for n,dd in data.node.iteritems() )
            return result
        except:
            raise nx.NetworkXError,\
                "Input is not a correct NetworkX graph."

    # pygraphviz  agraph
    if hasattr(data,"is_strict"):
        try:
            return nx.from_agraph(data,create_using=create_using)
        except:
            raise nx.NetworkXError,\
                  "Input is not a correct pygraphviz graph."

    # dict of dicts/lists
    if isinstance(data,dict):
        try:
            return from_dict_of_dicts(data,create_using=create_using,\
                    multigraph_input=multigraph_input)
        except:
            try:
                return from_dict_of_lists(data,create_using=create_using)
            except:
                raise TypeError("Input is not known type.")

    # list or generator of edges
    if isinstance(data,list) or hasattr(data,'next'): 
        try:
            return from_edgelist(data,create_using=create_using)
        except:
            raise nx.NetworkXError,\
                  "Input is not a valid edge list"

    # numpy matrix or ndarray 
    try:
        import numpy
        if isinstance(data,numpy.matrix) or \
               isinstance(data,numpy.ndarray):
            try:
                return from_numpy_matrix(data,create_using=create_using)
            except:
                raise nx.NetworkXError,\
                  "Input is not a correct numpy matrix or array."
    except ImportError:
        warnings.warn('numpy not found, skipping conversion test.',
                      ImportWarning)

    # scipy sparse matrix - any format
    try:
        import scipy
        if hasattr(data,"format"):
            try:
                return from_scipy_sparse_matrix(data,create_using=create_using)
            except:
                raise nx.NetworkXError, \
                      "Input is not a correct scipy sparse matrix type."
    except ImportError:
        warnings.warn('scipy not found, skipping conversion test.',
                      ImportWarning)


    raise nx.NetworkXError, \
          "Input is not a known data type for conversion."

    return 

    

def from_whatever(data,create_using=None,multigraph_input=False):
    """Deprecated. Use to_networkx_graph.

    See Also
    --------
    to_networkx_graph()
    """

    return to_networkx_graph(data,
                             create_using=create_using,
                             multigraph_input=multigraph_input)

def convert_to_undirected(G):
    """Return a new undirected representation of the graph G.

    """
    return G.to_undirected()


def convert_to_directed(G):
    """Return a new directed representation of the graph G.

    """
    return G.to_directed()


def relabel_nodes(G,mapping):
    """Return a copy of G with node labels transformed by mapping.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    mapping : dictionary or function
       Either a dictionary with the old labels as keys and new labels as values
       or a function transforming an old label with a new label.
       In either case, the new labels must be hashable Python objects.

    Examples
    --------
    mapping as dictionary

    >>> G=nx.path_graph(3)  # nodes 0-1-2
    >>> mapping={0:'a',1:'b',2:'c'}
    >>> H=nx.relabel_nodes(G,mapping)
    >>> print H.nodes()
    ['a', 'c', 'b']

    >>> G=nx.path_graph(26) # nodes 0..25
    >>> mapping=dict(zip(G.nodes(),"abcdefghijklmnopqrstuvwxyz"))
    >>> H=nx.relabel_nodes(G,mapping) # nodes a..z
    >>> mapping=dict(zip(G.nodes(),xrange(1,27)))
    >>> G1=nx.relabel_nodes(G,mapping) # nodes 1..26

    mapping as function

    >>> G=nx.path_graph(3)
    >>> def mapping(x):
    ...    return x**2
    >>> H=nx.relabel_nodes(G,mapping)
    >>> print H.nodes()
    [0, 1, 4]

    See Also
    --------
    convert_node_labels_to_integers()

    """
    H=G.__class__()
    H.name="(%s)" % G.name

    if hasattr(mapping,"__getitem__"):   # if we are a dict
        map_func=mapping.__getitem__   # call as a function
    else:
        map_func=mapping

    for node in G:
        try:
            H.add_node(map_func(node))
        except:
            raise nx.NetworkXError,\
                  "relabeling function cannot be applied to node %s" % node

    #for n1,n2,d in G.edges_iter(data=True):
    #    u=map_func(n1)
    #    v=map_func(n2)
    #    H.add_edge(u,v,d)
    if G.is_multigraph():
        H.add_edges_from( (map_func(n1),map_func(n2),k,d) 
                          for (n1,n2,k,d) in G.edges_iter(keys=True,data=True)) 
    else:
        H.add_edges_from( (map_func(n1),map_func(n2),d) 
                          for (n1,n2,d) in G.edges_iter(data=True)) 

    H.node.update(dict((map_func(n),d) for n,d in G.node.iteritems()))
    H.graph.update(G.graph)

    return H        
    

def convert_node_labels_to_integers(G,first_label=0,
                                    ordering="default",
                                    discard_old_labels=True):
    """ Return a copy of G node labels replaced with integers.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    first_label : int, optional (default=0)       
       An integer specifying the offset in numbering nodes.
       The n new integer labels are numbered first_label, ..., n+first_label.

    ordering : string
        "default" : inherit node ordering from G.nodes() 
        "sorted"  : inherit node ordering from sorted(G.nodes())
        "increasing degree" : nodes are sorted by increasing degree
        "decreasing degree" : nodes are sorted by decreasing degree

    discard_old_labels : bool, optional (default=True)
       if True (default) discard old labels
       if False, create a dict self.node_labels that maps new
       labels to old labels
    """
#    This function strips information attached to the nodes and/or
#    edges of a graph, and returns a graph with appropriate integer
#    labels. One can view this as a re-labeling of the nodes. Be
#    warned that the term "labeled graph" has a loaded meaning
#    in graph theory. The fundamental issue is whether the names
#    (labels) of the nodes (and edges) matter in deciding when two
#    graphs are the same. For example, in problems of graph enumeration
#    there is a distinct difference in techniques required when
#    counting labeled vs. unlabeled graphs.

#    When implementing graph
#    algorithms it is often convenient to strip off the original node
#    and edge information and appropriately relabel the n nodes with
#    the integer values 1,..,n. This is the purpose of this function,
#    and it provides the option (see discard_old_labels variable) to either
#    preserve the original labels in separate dicts (these are not
#    returned but made an attribute of the new graph.

    N=G.number_of_nodes()+first_label
    if ordering=="default":
        mapping=dict(zip(G.nodes(),range(first_label,N)))
    elif ordering=="sorted":
        nlist=G.nodes()
        nlist.sort()
        mapping=dict(zip(nlist,range(first_label,N)))
    elif ordering=="increasing degree":
        dv_pairs=[(d,n) for (n,d) in G.degree_iter()]
        dv_pairs.sort() # in-place sort from lowest to highest degree
        mapping=dict(zip([n for d,n in dv_pairs],range(first_label,N)))
    elif ordering=="decreasing degree":
        dv_pairs=[(d,n) for (n,d) in G.degree_iter()]
        dv_pairs.sort() # in-place sort from lowest to highest degree
        dv_pairs.reverse()
        mapping=dict(zip([n for d,n in dv_pairs],range(first_label,N)))
    else:
        raise nx.NetworkXError,\
              "unknown value of node ordering variable: ordering"

    H=relabel_nodes(G,mapping)

    H.name="("+G.name+")_with_int_labels"
    if not discard_old_labels:
        H.node_labels=mapping
    return H



def to_dict_of_lists(G,nodelist=None):
    """Return adjacency representation of graph as a dictionary of lists

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list       
       Use only nodes specified in nodelist

    Notes
    -----
    Completely ignores edge data for MultiGraph and MultiDiGraph.

    """
    if nodelist is None:
        nodelist=G

    d = {}
    for n in nodelist:
        d[n]=[nbr for nbr in G.neighbors(n) if nbr in nodelist]
    return d            

def from_dict_of_lists(d,create_using=None):
    """Return a graph from a dictionary of lists.

    Parameters
    ----------
    d : dictionary of lists
      A dictionary of lists adjacency representation.

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created.

    Examples
    --------
    >>> dol= {0:[1]} # single edge (0,1)
    >>> G=nx.from_dict_of_lists(dol)

    or
    >>> G=nx.Graph(dol) # use Graph constructor

    """
    G=_prep_create_using(create_using)
    G.add_nodes_from(d)        

    if G.is_multigraph() and not G.is_directed():
        # a dict_of_lists can't show multiedges.  BUT for undirected graphs,
        # each edge shows up twice in the dict_of_lists.  
        # So we need to treat this case separately.
        seen={}
        for node,nbrlist in d.iteritems():
            for nbr in nbrlist:
                if nbr not in seen:
                    G.add_edge(node,nbr)
            seen[node]=1  # don't allow reverse edge to show up 
    else:
        G.add_edges_from( ((node,nbr) for node,nbrlist in d.iteritems() 
                           for nbr in nbrlist) )
    return G                         


def to_dict_of_dicts(G,nodelist=None,edge_data=None):
    """Return adjacency representation of graph as a dictionary of dictionaries

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list       
       Use only nodes specified in nodelist

    edge_data : list, optional       
       If provided,  the value of the dictionary will be
       set to edge_data for all edges.  This is useful to make
       an adjacency matrix type representation with 1 as the edge data.
       If edgedata is None, the edgedata in G is used to fill the values.
       If G is a multigraph, the edgedata is a dict for each pair (u,v).
    
    """
    dod={}
    if nodelist is None:
        if edge_data is None:
            for u,nbrdict in G.adjacency_iter():
                dod[u]=nbrdict.copy()
        else: # edge_data is not None
            for u,nbrdict in G.adjacency_iter():
                dod[u]=dod.fromkeys(nbrdict, edge_data)
    else: # nodelist is not None
        if edge_data is None:
            for u in nodelist:
                dod[u]={}
                for v,data in ((v,data) for v,data in G[u].iteritems() if v in nodelist):
                    dod[u][v]=data
        else: # nodelist and edge_data are not None
            for u in nodelist:
                dod[u]={}
                for v in ( v for v in G[u] if v in nodelist):
                    dod[u][v]=edge_data
    return dod

def from_dict_of_dicts(d,create_using=None,multigraph_input=False):
    """Return a graph from a dictionary of dictionaries.

    Parameters
    ----------
    d : dictionary of dictionaries
      A dictionary of dictionaries adjacency representation.

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created.

    multigraph_input : bool (default False)
       When True, the values of the inner dict are assumed 
       to be containers of edge data for multiple edges.
       Otherwise this routine assumes the edge data are singletons.

    Examples
    --------
    >>> dod= {0: {1:{'weight':1}}} # single edge (0,1)
    >>> G=nx.from_dict_of_dicts(dod)

    or
    >>> G=nx.Graph(dod) # use Graph constructor

    """
    G=_prep_create_using(create_using)
    G.add_nodes_from(d)

    # is dict a MultiGraph or MultiDiGraph?
    if multigraph_input:
        # make a copy of the list of edge data (but not the edge data)
        if G.is_directed():  
            if G.is_multigraph():
                G.add_edges_from( (u,v,key,data)
                                  for u,nbrs in d.iteritems() 
                                  for v,datadict in nbrs.iteritems() 
                                  for key,data in datadict.items()
                                )
            else:
                G.add_edges_from( (u,v,data)
                                  for u,nbrs in d.iteritems() 
                                  for v,datadict in nbrs.iteritems() 
                                  for key,data in datadict.items()
                                )
        else: # Undirected
            if G.is_multigraph():
                seen=set()   # don't add both directions of undirected graph
                for u,nbrs in d.iteritems():
                    for v,datadict in nbrs.iteritems():
                        if v not in seen:
                            G.add_edges_from( (u,v,key,data) 
                                               for key,data in datadict.items()
                                          )
                    seen.add(u) 
            else:
                seen=set()   # don't add both directions of undirected graph
                for u,nbrs in d.iteritems():
                    for v,datadict in nbrs.iteritems():
                        if v not in seen:
                            G.add_edges_from( (u,v,data)
                                        for key,data in datadict.items() )
                    seen.add(u) 

    else: # not a multigraph to multigraph transfer
        if G.is_directed():
            G.add_edges_from( ( (u,v,data) 
                                for u,nbrs in d.iteritems() 
                                for v,data in nbrs.iteritems()) )
        # need this if G is multigraph and slightly faster if not multigraph
        else:
            seen=set()
            for u,nbrs in d.iteritems():
                for v,data in nbrs.iteritems():
                    if v not in seen:
                        G.add_edge(u,v,attr_dict=data)
                seen.add(u)
    return G                         

def to_edgelist(G,nodelist=None):
    """Return a list of edges in the graph.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list       
       Use only nodes specified in nodelist

    """
    if nodelist is None:
        return G.edges(data=True)
    else:
        return G.edges(nodelist,data=True)

def from_edgelist(edgelist,create_using=None):
    """Return a graph from a list of edges.

    Parameters
    ----------
    edgelist : list or iterator
      Edge tuples 

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created.

    Examples
    --------
    >>> edgelist= [(0,1)] # single edge (0,1)
    >>> G=nx.from_edgelist(edgelist)

    or
    >>> G=nx.Graph(edgelist) # use Graph constructor

    """
    G=_prep_create_using(create_using)
    G.add_edges_from(edgelist)
    return G                         

def to_numpy_matrix(G,nodelist=None,dtype=None,order=None):
    """Return the graph adjacency matrix as a NumPy matrix.

    Parameters
    ----------
    G : graph
        The NetworkX graph used to construct the NumPy matrix.

    nodelist : list, optional       
       The rows and columns are ordered according to the nodes in `nodelist`.
       If `nodelist` is None, then the ordering is produced by G.nodes().

    dtype : NumPy data-type, optional
        A valid NumPy dtype used to initialize the array. If None, then the
        NumPy default is used.

    order : {'C', 'F'}, optional
        Whether to store multidimensional data in C- or Fortran-contiguous
        (row- or column-wise) order in memory. If None, then the NumPy default 
        is used.

    Returns
    -------
    M : NumPy matrix
       Graph adjacency matrix.

    Notes
    -----
    The matrix entries are populated using the 'weight' edge attribute. When
    an edge does not have the 'weight' attribute, the value of the entry is 1.
    For multiple edges, the values of the entries are the sums of the edge
    attributes for each edge.

    When `nodelist` does not contain every node in `G`, the matrix is built 
    from the subgraph of `G` that is induced by the nodes in `nodelist`.
    
    Examples
    --------
    >>> G = nx.MultiDiGraph()
    >>> G.add_edge(0,1,weight=2)
    >>> G.add_edge(1,0)
    >>> G.add_edge(2,2,weight=3)
    >>> G.add_edge(2,2)
    >>> nx.to_numpy_matrix(G, nodelist=[0,1,2])
    matrix([[ 0.,  2.,  0.],
            [ 1.,  0.,  0.],
            [ 0.,  0.,  4.]])

    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "to_numpy_matrix() requires numpy: http://scipy.org/ "

    if nodelist is None:
        nodelist = G.nodes()

    nodeset = set(nodelist)
    if len(nodelist) != len(nodeset):
        msg = "Ambiguous ordering: `nodelist` contained duplicates."
        raise nx.NetworkXError(msg)

    nlen=len(nodelist)
    undirected = not G.is_directed()
    index=dict(zip(nodelist,range(nlen)))
    M = np.zeros((nlen,nlen), dtype=dtype, order=order)

    for u,v,attrs in G.edges_iter(data=True):
        if (u in nodeset) and (v in nodeset):
            i,j = index[u],index[v]
            M[i,j] += attrs.get('weight', 1)
            if undirected:
                M[j,i] = M[i,j]

    M = np.asmatrix(M)
    return M

def from_numpy_matrix(A,create_using=None):
    """Return a graph from numpy matrix adjacency list. 

    Parameters
    ----------
    A : numpy matrix
      An adjacency matrix representation of a graph

    create_using : NetworkX graph
       Use specified graph for result.  The default is Graph()

    Examples
    --------
    >>> import numpy
    >>> A=numpy.matrix([[1,1],[2,1]])
    >>> G=nx.from_numpy_matrix(A)

    """
    # This should never fail if you have created a numpy matrix with numpy...  
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "from_numpy_matrix() requires numpy: http://scipy.org/ "


    G=_prep_create_using(create_using)

    n,m=A.shape

    if n!=m:
        raise nx.NetworkXError, \
              "Adjacency matrix is not square. n,m=%s"%(A.shape,)

    G.add_nodes_from(range(n)) # make sure we get isolated nodes

    # get a list of edges
    x,y=np.asarray(A).nonzero()         
    G.add_edges_from( ((u,v,{'weight':A[u,v]}) for (u,v) in zip(x,y)) )
    return G


def to_scipy_sparse_matrix(G,nodelist=None,dtype=None):
    """Return the graph adjacency matrix as a SciPy sparse matrix.

    Parameters
    ----------
    G : graph
        The NetworkX graph used to construct the NumPy matrix.

    nodelist : list, optional       
       The rows and columns are ordered according to the nodes in `nodelist`.
       If `nodelist` is None, then the ordering is produced by G.nodes().

    dtype : NumPy data-type, optional
        A valid NumPy dtype used to initialize the array. If None, then the
        NumPy default is used.

    Returns
    -------
    M : SciPy sparse matrix
       Graph adjacency matrix.

    Notes
    -----
    The matrix entries are populated using the 'weight' edge attribute. When
    an edge does not have the 'weight' attribute, the value of the entry is 1.
    For multiple edges, the values of the entries are the sums of the edge
    attributes for each edge.

    When `nodelist` does not contain every node in `G`, the matrix is built 
    from the subgraph of `G` that is induced by the nodes in `nodelist`.
    
    Uses lil_matrix format.  To convert to other formats see the documentation
    for scipy.sparse.

    Examples
    --------
    >>> G = nx.MultiDiGraph()
    >>> G.add_edge(0,1,weight=2)
    >>> G.add_edge(1,0)
    >>> G.add_edge(2,2,weight=3)
    >>> G.add_edge(2,2)
    >>> S = nx.to_scipy_sparse_matrix(G, nodelist=[0,1,2])
    >>> S.todense()
    matrix([[ 0.,  2.,  0.],
            [ 1.,  0.,  0.],
            [ 0.,  0.,  4.]])

    """
    try:
        from scipy import sparse
    except ImportError:
        raise ImportError, \
          "to_scipy_sparse_matrix() requires scipy: http://scipy.org/ "

    if nodelist is None:
        nodelist = G.nodes()

    nodeset = set(nodelist)
    if len(nodelist) != len(nodeset):
        msg = "Ambiguous ordering: `nodelist` contained duplicates."
        raise nx.NetworkXError(msg)

    nlen=len(nodelist)
    undirected = not G.is_directed()
    index=dict(zip(nodelist,range(nlen)))
    M = sparse.lil_matrix((nlen,nlen), dtype=dtype)

    for u,v,attrs in G.edges_iter(data=True):
        if (u in nodeset) and (v in nodeset):
            i,j = index[u],index[v]
            M[i,j] += attrs.get('weight', 1)
            if undirected:
                M[j,i] = M[i,j]

    return M

def from_scipy_sparse_matrix(A,create_using=None):
    """Return a graph from scipy sparse matrix adjacency list. 

    Parameters
    ----------
    A : scipy sparse matrix
      An adjacency matrix representation of a graph

    create_using : NetworkX graph
       Use specified graph for result.  The default is Graph()

    Examples
    --------
    >>> import scipy.sparse
    >>> A=scipy.sparse.eye(2,2,1)
    >>> G=nx.from_scipy_sparse_matrix(A)

    """
    G=_prep_create_using(create_using)

    # convert all formats to lil - not the most efficient way       
    AA=A.tolil()
    n,m=AA.shape

    if n!=m:
        raise nx.NetworkXError, \
              "Adjacency matrix is not square. n,m=%s"%(A.shape,)


    G.add_nodes_from(range(n)) # make sure we get isolated nodes

    for i,row in enumerate(AA.rows):
        for pos,j in enumerate(row):
            G.add_edge(i,j,**{'weight':AA.data[i][pos]})
    return G
