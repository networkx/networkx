"""Functions to convert NetworkX graphs to and from other formats.

The preferred way of converting data to a NetworkX graph is through the
graph constuctor.  The constructor calls the to_networkx_graph() function
which attempts to guess the input type and convert it automatically.

Examples


Create a 10 node random graph from a numpy matrix

>>> import numpy
>>> a=numpy.reshape(numpy.random.random_integers(0,1,size=100),(10,10))
>>> D=nx.DiGraph(a)

or equivalently

>>> D=nx.to_networkx_graph(a,create_using=nx.DiGraph())

See Also
--------
nx_pygraphviz, nx_pydot
"""
#    Copyright (C) 2006-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import warnings
import networkx as nx
from networkx.convert import _prep_create_using
from networkx.utils import not_implemented_for
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult(dschult@colgate.edu)'])
__all__ = ['from_numpy_matrix', 'to_numpy_matrix',
           'to_numpy_recarray',
           'from_scipy_sparse_matrix', 'to_scipy_sparse_matrix']

def to_numpy_matrix(G, nodelist=None, dtype=None, order=None,
                    multigraph_weight=sum, weight='weight', nonedge=0.0):
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
        the edge weight.  If an edge does not have that attribute, then the
        value 1 is used instead.

    nonedge : float (default=0.0)
        The matrix values corresponding to nonedges are typically set to zero.
        However, this could be undesirable if there are matrix values
        corresponding to actual edges that also have the value zero. If so,
        one might prefer nonedges to have some other value, such as nan.

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
    import numpy as np
    if nodelist is None:
        nodelist = G.nodes()
    nodeset = set(nodelist)
    if len(nodelist) != len(nodeset):
        msg = "Ambiguous ordering: `nodelist` contained duplicates."
        raise nx.NetworkXError(msg)

    nlen=len(nodelist)
    undirected = not G.is_directed()
    index=dict(zip(nodelist,range(nlen)))

    # Initially, we start with an array of nans.  Then we populate the matrix
    # using data from the graph.  Afterwards, any leftover nans will be
    # converted to the value of `nonedge`.  Note, we use nans initially,
    # instead of zero, for two reasons:
    #
    #   1) It can be important to distinguish a real edge with the value 0
    #      from a nonedge with the value 0.
    #
    #   2) When working with multi(di)graphs, we must combine the values of all
    #      edges between any two nodes in some manner.  This often takes the
    #      form of a sum, min, or max.  Using the value 0 for a nonedge would
    #      have undesirable effects with min and max, but using nanmin and
    #      nanmax with initially nan values is not problematic at all.
    #
    # That said, there are still some drawbacks to this approach. Namely, if
    # a real edge is nan, then that value is a) not distinguishable from
    # nonedges and b) is ignored by the default combinator (nansum, nanmin,
    # nanmax) functions used for multi(di)graphs. If this becomes an issue,
    # an alternative approach is to use masked arrays.  Initially, every
    # element is masked and set to some `initial` value. As we populate the
    # graph, elements are unmasked (automatically) when we combine the initial
    # value with the values given by real edges.  At the end, we convert all
    # masked values to `nonedge`. Using masked arrays fully addresses reason 1,
    # but for reason 2, we would still have the issue with min and max if the
    # initial values were 0.0.  Note: an initial value of +inf is appropriate
    # for min, while an initial value of -inf is appropriate for max. When
    # working with sum, an initial value of zero is appropriate. Ideally then,
    # we'd want to allow users to specify both a value for nonedges and also
    # an initial value.  For multi(di)graphs, the choice of the initial value
    # will, in general, depend on the combinator function---sensible defaults
    # can be provided.

    if G.is_multigraph():
        # Handle MultiGraphs and MultiDiGraphs
        M = np.zeros((nlen, nlen), dtype=dtype, order=order) + np.nan
        # use numpy nan-aware operations
        operator={sum:np.nansum, min:np.nanmin, max:np.nanmax}
        try:
            op=operator[multigraph_weight]
        except:
            raise ValueError('multigraph_weight must be sum, min, or max')

        for u,v,attrs in G.edges_iter(data=True):
            if (u in nodeset) and (v in nodeset):
                i, j = index[u], index[v]
                e_weight = attrs.get(weight, 1)
                M[i,j] = op([e_weight, M[i,j]])
                if undirected:
                    M[j,i] = M[i,j]
    else:
        # Graph or DiGraph, this is much faster than above
        M = np.zeros((nlen,nlen), dtype=dtype, order=order) + np.nan
        for u,nbrdict in G.adjacency_iter():
            for v,d in nbrdict.items():
                try:
                    M[index[u],index[v]] = d.get(weight,1)
                except KeyError:
                    # This occurs when there are fewer desired nodes than
                    # there are nodes in the graph: len(nodelist) < len(G)
                    pass

    M[np.isnan(M)] = nonedge
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
    >>> G.edges()
    [(0, 0)]
    >>> G[0][0]['cost']
    2
    >>> G[0][0]['weight']
    1.0
    """
    # This should never fail if you have created a numpy matrix with numpy...
    import numpy as np
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


@not_implemented_for('multigraph')
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
    import numpy as np
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

    Uses coo_matrix format. To convert to other formats specify the
    format= keyword.

    Examples
    --------
    >>> G = nx.MultiDiGraph()
    >>> G.add_edge(0,1,weight=2)
    >>> G.add_edge(1,0)
    >>> G.add_edge(2,2,weight=3)
    >>> G.add_edge(2,2)
    >>> S = nx.to_scipy_sparse_matrix(G, nodelist=[0,1,2])
    >>> print(S.todense())
    [[0 2 0]
     [1 0 0]
     [0 0 4]]

    References
    ----------
    .. [1] Scipy Dev. References, "Sparse Matrices",
       http://docs.scipy.org/doc/scipy/reference/sparse.html
    """
    from scipy import sparse
    if nodelist is None:
        nodelist = G
    nlen = len(nodelist)
    if nlen == 0:
        raise nx.NetworkXError("Graph has no nodes or edges")

    if len(nodelist) != len(set(nodelist)):
        msg = "Ambiguous ordering: `nodelist` contained duplicates."
        raise nx.NetworkXError(msg)

    index = dict(zip(nodelist,range(nlen)))
    if G.number_of_edges() == 0:
        row,col,data=[],[],[]
    else:
        row,col,data = zip(*((index[u],index[v],d.get(weight,1))
                             for u,v,d in G.edges_iter(nodelist, data=True)
                             if u in index and v in index))
    if G.is_directed():
        M = sparse.coo_matrix((data,(row,col)),
                              shape=(nlen,nlen), dtype=dtype)
    else:
        # symmetrize matrix
        M = sparse.coo_matrix((data+data, (row+col,col+row)),
                              shape=(nlen,nlen), dtype=dtype)
    try:
        return M.asformat(format)
    except AttributeError:
        raise nx.NetworkXError("Unknown sparse matrix format: %s"%format)

def from_scipy_sparse_matrix(A, create_using=None, edge_attribute='weight'):
    """Return a graph from scipy sparse matrix adjacency list.

    Parameters
    ----------
    A: scipy sparse matrix
      An adjacency matrix representation of a graph

    create_using: NetworkX graph
       Use specified graph for result.  The default is Graph()

    edge_attribute: string
       Name of edge attrbute to store matrix numeric value. The data will
       have the same type as the matrix entry (int, float, (real,imag)).

    Examples
    --------
    >>> import scipy.sparse
    >>> A = scipy.sparse.eye(2,2,1)
    >>> G = nx.from_scipy_sparse_matrix(A)
    """
    G = _prep_create_using(create_using)
    n,m = A.shape
    if n != m:
        raise nx.NetworkXError(\
              "Adjacency matrix is not square. nx,ny=%s"%(A.shape,))
    G.add_nodes_from(range(n)) # make sure we get isolated nodes

    if A.format == 'coo':
        for i,j,d in zip(A.row, A.col, A.data):
            G.add_edge(i,j,**{edge_attribute:d})
    elif A.format == 'dia':
        # make a copy - could be done more efficiently
        B = A.tocoo()
        for i,j,d in zip(B.row, B.col, B.data):
            G.add_edge(i,j,**{edge_attribute:d})
    else:
        for i,j in zip(*A.nonzero()):
            G.add_edge(i,j,**{edge_attribute:A[i,j]})
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
