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
#    Copyright (C) 2006-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import warnings
import networkx as nx

__all__ = ['to_networkx_graph',
           'from_dict_of_dicts', 'to_dict_of_dicts',
           'from_dict_of_lists', 'to_dict_of_lists',
           'from_edgelist', 'to_edgelist',
           'from_numpy_matrix', 'to_numpy_matrix',
           'to_numpy_recarray',
           'from_scipy_sparse_matrix', 'to_scipy_sparse_matrix']

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
                result.node=dict( (n,dd.copy()) for n,dd in data.node.items() )
            return result
        except:
            raise nx.NetworkXError("Input is not a correct NetworkX graph.")

    # pygraphviz  agraph
    if hasattr(data,"is_strict"):
        try:
            return nx.from_agraph(data,create_using=create_using)
        except:
            raise nx.NetworkXError("Input is not a correct pygraphviz graph.")

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
    if (isinstance(data,list)
        or hasattr(data,'next')
        or hasattr(data, '__next__')): 
        try:
            return from_edgelist(data,create_using=create_using)
        except:
            raise nx.NetworkXError("Input is not a valid edge list")

    # numpy matrix or ndarray 
    try:
        import numpy
        if isinstance(data,numpy.matrix) or \
               isinstance(data,numpy.ndarray):
            try:
                return from_numpy_matrix(data,create_using=create_using)
            except:
                raise nx.NetworkXError(\
                  "Input is not a correct numpy matrix or array.")
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
                raise nx.NetworkXError(\
                      "Input is not a correct scipy sparse matrix type.")
    except ImportError:
        warnings.warn('scipy not found, skipping conversion test.',
                      ImportWarning)


    raise nx.NetworkXError(\
          "Input is not a known data type for conversion.")

    return 


def convert_to_undirected(G):
    """Return a new undirected representation of the graph G.

    """
    return G.to_undirected()


def convert_to_directed(G):
    """Return a new directed representation of the graph G.

    """
    return G.to_directed()


def to_dict_of_lists(G,nodelist=None):
    """Return adjacency representation of graph as a dictionary of lists.

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
        for node,nbrlist in d.items():
            for nbr in nbrlist:
                if nbr not in seen:
                    G.add_edge(node,nbr)
            seen[node]=1  # don't allow reverse edge to show up 
    else:
        G.add_edges_from( ((node,nbr) for node,nbrlist in d.items() 
                           for nbr in nbrlist) )
    return G                         


def to_dict_of_dicts(G,nodelist=None,edge_data=None):
    """Return adjacency representation of graph as a dictionary of dictionaries.

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
                for v,data in ((v,data) for v,data in G[u].items() if v in nodelist):
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
                                  for u,nbrs in d.items() 
                                  for v,datadict in nbrs.items() 
                                  for key,data in datadict.items()
                                )
            else:
                G.add_edges_from( (u,v,data)
                                  for u,nbrs in d.items() 
                                  for v,datadict in nbrs.items() 
                                  for key,data in datadict.items()
                                )
        else: # Undirected
            if G.is_multigraph():
                seen=set()   # don't add both directions of undirected graph
                for u,nbrs in d.items():
                    for v,datadict in nbrs.items():
                        if (u,v) not in seen:
                            G.add_edges_from( (u,v,key,data) 
                                               for key,data in datadict.items()
                                              )
                            seen.add((v,u)) 
            else:
                seen=set()   # don't add both directions of undirected graph
                for u,nbrs in d.items():
                    for v,datadict in nbrs.items():
                        if (u,v) not in seen:
                            G.add_edges_from( (u,v,data)
                                        for key,data in datadict.items() )
                            seen.add((v,u)) 

    else: # not a multigraph to multigraph transfer
        if G.is_multigraph() and not G.is_directed():
            # d can have both representations u-v, v-u in dict.  Only add one.
            # We don't need this check for digraphs since we add both directions,
            # or for Graph() since it is done implicitly (parallel edges not allowed)
            seen=set()
            for u,nbrs in d.items():
                for v,data in nbrs.items():
                    if (u,v) not in seen:
                        G.add_edge(u,v,attr_dict=data)
                    seen.add((v,u))
        else:
            G.add_edges_from( ( (u,v,data) 
                                for u,nbrs in d.items() 
                                for v,data in nbrs.items()) )
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

def to_numpy_matrix(G, nodelist=None, dtype=None, order=None,
                    multigraph_weight=sum, weight='weight'):
    """Return the graph adjacency matrix as a NumPy matrix.

    Parameters
    ----------
    G : graph
        The NetworkX graph used to construct the NumPy matrix.

    nodelist : list, optional       
       The rows and columns are ordered according to the nodes in `nodelist`.
       If `nodelist` is None, then the ordering is produced by G.nodes().

    dtype : NumPy data type, optional
        A valid single NumPy data type used to initialize the array. 
        This must be a simple type such as int or numpy.float64 and
        not a compound data type (see to_numpy_recarray)
        If None, then the NumPy default is used.

    order : {'C', 'F'}, optional
        Whether to store multidimensional data in C- or Fortran-contiguous
        (row- or column-wise) order in memory. If None, then the NumPy default 
        is used.

    multigraph_weight : {sum, min, max}, optional        
        An operator that determines how weights in multigraphs are handled.
        The default is to sum the weights of the multiple edges.

    weight : string or None   optional (default='weight')
        The edge attribute that holds the numerical value used for 
        the edge weight.  If None then all edge weights are 1.


    Returns
    -------
    M : NumPy matrix
       Graph adjacency matrix.

    See Also
    --------
    to_numpy_recarray, from_numpy_matrix

    Notes
    -----
    The matrix entries are assigned with weight edge attribute. When
    an edge does not have the weight attribute, the value of the entry is 1.
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
        raise ImportError(\
          "to_numpy_matrix() requires numpy: http://scipy.org/ ")

    if nodelist is None:
        nodelist = G.nodes()

    nodeset = set(nodelist)
    if len(nodelist) != len(nodeset):
        msg = "Ambiguous ordering: `nodelist` contained duplicates."
        raise nx.NetworkXError(msg)

    nlen=len(nodelist)
    undirected = not G.is_directed()
    index=dict(zip(nodelist,range(nlen)))

    if G.is_multigraph():
        # Handle MultiGraphs and MultiDiGraphs
        # array of nan' to start with, any leftover nans will be converted to 0
        # nans are used so we can use sum, min, max for multigraphs
        M = np.zeros((nlen,nlen), dtype=dtype, order=order)+np.nan
        # use numpy nan-aware operations
        operator={sum:np.nansum, min:np.nanmin, max:np.nanmax}
        try:
            op=operator[multigraph_weight]
        except:
            raise ValueError('multigraph_weight must be sum, min, or max')

        for u,v,attrs in G.edges_iter(data=True):
            if (u in nodeset) and (v in nodeset):
                i,j = index[u],index[v]
                e_weight = attrs.get(weight, 1)
                M[i,j] = op([e_weight,M[i,j]]) 
                if undirected:
                    M[j,i] = M[i,j]
        # convert any nans to zeros
        M = np.asmatrix(np.nan_to_num(M))
    else:
        # Graph or DiGraph, this is much faster than above 
        M = np.zeros((nlen,nlen), dtype=dtype, order=order)
        for u,nbrdict in G.adjacency_iter():
            for v,d in nbrdict.items():
                try:
                    M[index[u],index[v]]=d.get(weight,1)
                except KeyError:
                    pass
        M = np.asmatrix(M)
    return M


def from_numpy_matrix(A,create_using=None):
    """Return a graph from numpy matrix.

    The numpy matrix is interpreted as an adjacency matrix for the graph.

    Parameters
    ----------
    A : numpy matrix
      An adjacency matrix representation of a graph

    create_using : NetworkX graph
       Use specified graph for result.  The default is Graph()

    Notes
    -----
    If the numpy matrix has a single data type for each matrix entry it 
    will be converted to an appropriate Python data type.  

    If the numpy matrix has a user-specified compound data type the names
    of the data fields will be used as attribute keys in the resulting 
    NetworkX graph.

    See Also
    --------
    to_numpy_matrix, to_numpy_recarray

    Examples
    --------
    Simple integer weights on edges:

    >>> import numpy
    >>> A=numpy.matrix([[1,1],[2,1]])
    >>> G=nx.from_numpy_matrix(A)

    User defined compound data type on edges:

    >>> import numpy
    >>> dt=[('weight',float),('cost',int)]
    >>> A=numpy.matrix([[(1.0,2)]],dtype=dt)                      
    >>> G=nx.from_numpy_matrix(A)
    >>> G.edges(data=True)
    [(0, 0, {'cost': 2, 'weight': 1.0})]
    """
    kind_to_python_type={'f':float,
                         'i':int,
                         'u':int,
                         'b':bool,
                         'c':complex,
                         'S':str,
                         'V':'void'}

    try: # Python 3.x
        blurb = chr(1245) # just to trigger the exception
        kind_to_python_type['U']=str
    except ValueError: # Python 2.6+
        kind_to_python_type['U']=unicode

    # This should never fail if you have created a numpy matrix with numpy...  
    try:
        import numpy as np
    except ImportError:
        raise ImportError(\
          "from_numpy_matrix() requires numpy: http://scipy.org/ ")

    G=_prep_create_using(create_using)
    n,m=A.shape
    if n!=m:
        raise nx.NetworkXError("Adjacency matrix is not square.",
                               "nx,ny=%s"%(A.shape,))
    dt=A.dtype
    try:
        python_type=kind_to_python_type[dt.kind]
    except:
        raise TypeError("Unknown numpy data type: %s"%dt)

    # make sure we get isolated nodes
    G.add_nodes_from(range(n)) 
    # get a list of edges
    x,y=np.asarray(A).nonzero()         

    # handle numpy constructed data type
    if python_type is 'void':
        fields=sorted([(offset,dtype,name) for name,(dtype,offset) in
                       A.dtype.fields.items()])
        for (u,v) in zip(x,y):         
            attr={}
            for (offset,dtype,name),val in zip(fields,A[u,v]):
                attr[name]=kind_to_python_type[dtype.kind](val)
            G.add_edge(u,v,attr)
    else: # basic data type
        G.add_edges_from( ((u,v,{'weight':python_type(A[u,v])}) 
                           for (u,v) in zip(x,y)) )
    return G


def to_numpy_recarray(G,nodelist=None,
                      dtype=[('weight',float)],
                      order=None):
    """Return the graph adjacency matrix as a NumPy recarray.

    Parameters
    ----------
    G : graph
        The NetworkX graph used to construct the NumPy matrix.

    nodelist : list, optional       
       The rows and columns are ordered according to the nodes in `nodelist`.
       If `nodelist` is None, then the ordering is produced by G.nodes().

    dtype : NumPy data-type, optional
        A valid NumPy named dtype used to initialize the NumPy recarray. 
        The data type names are assumed to be keys in the graph edge attribute 
        dictionary.

    order : {'C', 'F'}, optional
        Whether to store multidimensional data in C- or Fortran-contiguous
        (row- or column-wise) order in memory. If None, then the NumPy default 
        is used.

    Returns
    -------
    M : NumPy recarray
       The graph with specified edge data as a Numpy recarray 

    Notes
    -----
    When `nodelist` does not contain every node in `G`, the matrix is built 
    from the subgraph of `G` that is induced by the nodes in `nodelist`.
    
    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_edge(1,2,weight=7.0,cost=5)
    >>> A=nx.to_numpy_recarray(G,dtype=[('weight',float),('cost',int)])
    >>> print(A.weight)
    [[ 0.  7.]
     [ 7.  0.]]
    >>> print(A.cost)
    [[0 5]
     [5 0]]
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(\
          "to_numpy_matrix() requires numpy: http://scipy.org/ ")

    if G.is_multigraph():
        raise nx.NetworkXError("Not implemented for multigraphs.")

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

    names=M.dtype.names
    for u,v,attrs in G.edges_iter(data=True):
        if (u in nodeset) and (v in nodeset):
            i,j = index[u],index[v]
            values=tuple([attrs[n] for n in names])
            M[i,j] = values
            if undirected:
                M[j,i] = M[i,j]

    return M.view(np.recarray)


def to_scipy_sparse_matrix(G, nodelist=None, dtype=None, 
                           weight='weight', format='csr'):
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

    weight : string or None   optional (default='weight')
        The edge attribute that holds the numerical value used for 
        the edge weight.  If None then all edge weights are 1.

    format : str in {'bsr', 'csr', 'csc', 'coo', 'lil', 'dia', 'dok'} 
        The type of the matrix to be returned (default 'csr').  For
        some algorithms different implementations of sparse matrices
        can perform better.  See [1]_ for details.
    
    Returns
    -------
    M : SciPy sparse matrix
       Graph adjacency matrix.

    Notes
    -----
    The matrix entries are populated using the edge attribute held in 
    parameter weight. When an edge does not have that attribute, the 
    value of the entry is 1.

    For multiple edges the matrix values are the sums of the edge weights.

    When `nodelist` does not contain every node in `G`, the matrix is built 
    from the subgraph of `G` that is induced by the nodes in `nodelist`.
    
    Uses lil_matrix format. To convert to other formats specify the 
    format= keyword.

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
    
    References
    ----------
    .. [1] Scipy Dev. References, 
       "Sparse Matrices"  
       http://docs.scipy.org/doc/scipy/reference/sparse.html
    """
    try:
        from scipy import sparse
    except ImportError:
        raise ImportError(\
          "to_scipy_sparse_matrix() requires scipy: http://scipy.org/ ")

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
            M[i,j] += attrs.get(weight, 1)
            if undirected:
                M[j,i] = M[i,j]
    try:
        return M.asformat(format)
    except AttributeError:
        raise nx.NetworkXError("Unknown sparse matrix format: %s"%format)
    

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
        raise nx.NetworkXError(\
              "Adjacency matrix is not square. nx,ny=%s"%(A.shape,))
    G.add_nodes_from(range(n)) # make sure we get isolated nodes

    for i,row in enumerate(AA.rows):
        for pos,j in enumerate(row):
            G.add_edge(i,j,**{'weight':AA.data[i][pos]})
    return G

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

