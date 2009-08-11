"""
-------
Convert
-------

This module provides functions to convert 
NetworkX graphs to and from other formats.

The preferred way of converting data to a NetworkX graph 
is through the graph constuctor.  The constructor calls
the from_whatever() function which attempts to guess the
input type and convert it automatically.

Examples
--------

Create a 10 node random graph from a numpy matrix

>>> import numpy
>>> a=numpy.reshape(numpy.random.random_integers(0,1,size=100),(10,10))
>>> D=nx.DiGraph(a) 

or equivalently

>>> D=nx.from_whatever(a,create_using=nx.DiGraph()) 

Create a graph with a single edge from a dictionary of dictionaries

>>> d={0: {1: 1}} # dict-of-dicts single edge (0,1)
>>> G=nx.Graph(d)


See Also
--------
For graphviz dot formats see networkx.drawing.nx_pygraphviz
or networkx.drawing.nx_pydot.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2006-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html


__all__ = ['from_whatever', 
           'from_dict_of_dicts', 'to_dict_of_dicts',
           'from_dict_of_lists', 'to_dict_of_lists',
           'from_edgelist', 'to_edgelist',
           'from_numpy_matrix', 'to_numpy_matrix',
           'from_scipy_sparse_matrix', 'to_scipy_sparse_matrix']

import networkx

try:
    from peak.util.imports import lazyModule
except:
    from networkx.util.imports import lazyModule

numpy=lazyModule('numpy')
scipy=lazyModule('scipy')
sparse=lazyModule('scipy.sparse')

def _prep_create_using(create_using):
    """
    Return a graph object ready to be populated.

    If create_using is None return the default (just networkx.Graph())
    If create_using.clear() works, assume it returns a graph object.
    Otherwise raise an exception because create_using is not a networkx graph.

    """
    if create_using is None:
        G=networkx.Graph()
    else:
        G=create_using
        try:
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")
    return G


def from_whatever(thing,create_using=None,multigraph_input=False):
    """Make a NetworkX graph from an known type.

    The preferred way to call this is automatically
    from the class constructor

    >>> d={0: {1: {'weight':1}}} # dict-of-dicts single edge (0,1)
    >>> G=nx.Graph(d)
    
    instead of the equivalent

    >>> G=nx.from_dict_of_dicts(d)

    Parameters
    ----------
    thing : a object to be converted
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
      If True and  thing is a dict_of_dicts,
      try to create a multigraph assuming dict_of_dict_of_lists.
      If thing and create_using are both multigraphs then create
      a multigraph from a multigraph.

    """
    # NX graph
    if hasattr(thing,"adj"):
        try:
            result= from_dict_of_dicts(thing.adj,\
                    create_using=create_using,\
                    multigraph_input=thing.is_multigraph())
            if hasattr(thing,'graph') and isinstance(thing.graph,dict):
                result.graph=thing.graph.copy()
            if hasattr(thing,'node') and isinstance(thing.node,dict):
                result.node=dict( (n,dd.copy()) for n,dd in thing.node.iteritems() )
            return result
        except:
            raise networkx.NetworkXError,\
                "Input is not a correct NetworkX graph."

    # pygraphviz  agraph
    if hasattr(thing,"is_strict"):
        try:
            return networkx.from_agraph(thing,create_using=create_using)
        except:
            raise networkx.NetworkXError,\
                  "Input is not a correct pygraphviz graph."

    # dict of dicts/lists
    if isinstance(thing,dict):
        try:
            return from_dict_of_dicts(thing,create_using=create_using,\
                    multigraph_input=multigraph_input)
        except:
            try:
                return from_dict_of_lists(thing,create_using=create_using)
            except:
                raise TypeError("Input is not known type.")

    # list or generator of edges
    if isinstance(thing,list) or hasattr(thing,'next'): 
        try:
            return from_edgelist(thing,create_using=create_using)
        except:
            raise networkx.NetworkXError,\
                  "Input is not a valid edge list"

    # numpy matrix or ndarray 
#    try:
#        import numpy
    if isinstance(thing,numpy.core.defmatrix.matrix) or \
           isinstance(thing,numpy.ndarray):
        try:
            return from_numpy_matrix(thing,create_using=create_using)
        except:
            raise networkx.NetworkXError,\
                  "Input is not a correct numpy matrix or array."
#    except ImportError:
#        pass # fail silently

    # scipy sparse matrix - any format
#    try:
#        import scipy
    if hasattr(thing,"format"):
        try:
            return from_scipy_sparse_matrix(thing,create_using=create_using)
        except:
            raise networkx.NetworkXError, \
                  "Input is not a correct scipy sparse matrix type."
#    except ImportError:
#        pass # fail silently


    raise networkx.NetworkXError, \
          "Input is not a known data type for conversion."

    return 


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


def to_numpy_matrix(G,nodelist=None,dtype=None):
    """Return the graph adjacency matrix as a numpy matrix. 

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list, optional       
       Use the order of nodes in nodelist for the rows.
       All nodes must appear in nodelist or a KeyError is raised.
       If nodelist is None, the ordering is produced by G.nodes()

    dtype : numpy type
       Data type for matrix entries.  Default is 4 byte float (single).

    Notes
    -----
    When no weights are specified the value of the entry A[u,v] is 1
    if there is an edge u-v and 0 otherwise.

    Multiple edges and edge data are both ignored for MultiGraph/MultiDiGraph.

    """
#    try:
#        import numpy
#    except ImportError:
#        raise ImportError, \
#              "Import Error: not able to import numpy: http://numpy.scipy.org "

    if dtype is None:
        dtype=numpy.float32

    if nodelist is None:
        nodelist=G.nodes()
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    A = numpy.asmatrix(numpy.zeros((nlen,nlen),dtype=dtype))
    for n,nbrdict in G.adjacency_iter():
        if n in index:
            for nbr,data in nbrdict.iteritems():
                if nbr in index:
                    A[index[n],index[nbr]]=data.get('weight',1)
    return A

#     if G.is_multigraph():
#         for n,nbrdict in G.adjacency_iter():
#             if n in index:
#                 for nbr,data in nbrdict.iteritems():
#                     if nbr in index:
#                         A[index[n],index[nbr]]=data
#     else: # ignore edge data
#         for n,nbrdict in G.adjacency_iter():
#             if n in index:
#                 for nbr in nbrdict:
#                     if nbr in index:
#                         A[index[n],index[nbr]]=1
#     return A            

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
#    try:
#        import numpy
#    except ImportError:
#        raise ImportError, \
#              "Import Error: not able to import numpy: http://numpy.scipy.org "

    G=_prep_create_using(create_using)

    nx,ny=A.shape

    if nx!=ny:
        raise networkx.NetworkXError, \
              "Adjacency matrix is not square. nx,ny=%s"%(A.shape,)

    G.add_nodes_from(range(nx)) # make sure we get isolated nodes

    # get a list of edges
    x,y=numpy.asarray(A).nonzero()         
    G.add_edges_from( ((u,v,{'weight':A[u,v]}) for (u,v) in zip(x,y)) )
    return G


def to_scipy_sparse_matrix(G,nodelist=None,dtype=None):
    """Return the graph adjacency matrix as a scipy sparse matrix.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list, optional       
       Use the order of nodes in nodelist for the rows.
       All nodes must appear in nodelist or a KeyError is raised.
       If nodelist is None, the ordering is produced by G.nodes()

    dtype : numpy type
       Data type for matrix entries.  Default is 4 byte float (single).

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> A=nx.to_scipy_sparse_matrix(G)
    >>> C=A.tocsr() # convert to compressed row storage

    Notes
    -----
    Uses lil_matrix format.  To convert to other formats see
    scipy.sparse documentation.

    If G.weighted is True and G is not a multigraph, the edgedata
    is assumed to be numeric and becomes the value of A[u.v].
    Otherwise A[u,v] is 1 if an edge u-v exists and 0 otherwise.
    """
#    try:
#        from scipy import sparse
#    except ImportError:
#        raise ImportError, \
#              """Import Error: not able to import scipy sparse:
#              see http://scipy.org""" 
    if dtype is None:
        dtype=scipy.float32

    if nodelist is None:
        nodelist=G.nodes()
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    A = sparse.lil_matrix((nlen,nlen),dtype=dtype)
    for n,nbrdict in G.adjacency_iter():
        if n in index:
            for nbr,data in nbrdict.iteritems():
                if nbr in index:
                    A[index[n],index[nbr]]=data.get('weight',1)
    return A

#     if G.weighted and not G.multigraph:
#         for n,nbrdict in G.adjacency_iter():
#             if n in index:
#                 for nbr,data in nbrdict.iteritems():
#                     if nbr in index:
#                         A[index[n],index[nbr]]=data
#     else: # ignore edge data
#         for n,nbrdict in G.adjacency_iter():
#             if n in index:
#                 for nbr in nbrdict:
#                     if nbr in index:
#                         A[index[n],index[nbr]]=1
#     return A            


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
    nx,ny=AA.shape

    if nx!=ny:
        raise networkx.NetworkXError, \
              "Adjacency matrix is not square. nx,ny=%s"%(A.shape,)


    G.add_nodes_from(range(nx)) # make sure we get isolated nodes

    for i,row in enumerate(AA.rows):
        for pos,j in enumerate(row):
            G.add_edge(i,j,**{'weight':AA.data[i][pos]})
    return G
