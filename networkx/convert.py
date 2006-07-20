"""
Convert NetworkX graphs to and from other formats.

from_whatever attemps to guess the input format

Create a 10 node random digraph

>>> from networkx import *
>>> import numpy
>>> a=numpy.reshape(numpy.random.random_integers(0,1,size=100),(10,10))
>>> D=from_whatever(D,create_using=DiGraph()) # or D=DiGraph(a) 


For graphviz formats see networkx.drawing.nx_pygraphviz
or networkx.drawing.nx_pydot.

$Id$
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx

def from_whatever(thing,create_using=None):
    """Attempt to make a NetworkX graph from an known type.

    Current known types are:

       any NetworkX graph
       dict-of-dicts
       dist-of-lists
       numpy matrix
       numpy ndarray
       scipy sparse matrix

    """
    if create_using is None:
        G=networkx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a NetworkX graph type.")
        
    # NX graph
    if hasattr(thing,"add_node"):
        try:
            return from_dict_of_dicts(thing.adj,create_using=create_using)
        except:
            raise networkx.NetworkXError,\
                  "Input is not a correct NetworkX graph."

    # dict of dicts/lists
    if isinstance(thing,dict):
        try:
            return from_dict_of_dicts(thing,create_using=create_using)
        except:
            try:
                return from_dict_of_lists(thing,create_using=create_using)
            except:
                raise TypeError("Input is not known type.")

    # numpy matrix or ndarray 

    try:
        import numpy
        if isinstance(thing,numpy.core.defmatrix.matrix) or \
               isinstance(thing,numpy.ndarray):
            try:
                return from_numpy_matrix(thing,create_using=create_using)
            except:
                raise networkx.NetworkXError,\
                      "Input is not a correct numpy matrix or array."
    except ImportError:
        pass # fail silently

    # scipy sparse matrix - any format
    try:
        import scipy
        if hasattr(thing,"format"):
            try:
                return from_scipy_sparse_matrix(thing,create_using=create_using)
            except:
                raise networkx.NetworkXError, \
                      "Input is not a correct scipy sparse matrix type."
    except ImportError:
        pass # fail silently


    raise networkx.NetworkXError, \
          "Input is not a known data type for conversion."

    return 


def to_dict_of_lists(G,nodelist=None):
    """Return graph G as a Python dict of lists.

    If nodelist is defined return a dict of lists with only those nodes.

    Completely ignores edge data for XGraph and XDiGraph.

    """
    if nodelist is None:
        nodelist=G.nodes()

    # is this a XGraph or XDiGraph?
    if hasattr(G,'allow_multiedges')==True:
        xgraph=True
    else:
        xgraph=False

    d = {}

    for n in nodelist:
        d[n]=G.neighbors(n)
    return d            

def from_dict_of_lists(d,create_using=None):
    """Return a NetworkX graph G from a Python dict of lists.

    """
    if create_using is None:
        G=networkx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    G.add_nodes_from(d.keys())        
    for node in d:
        for nbr in d[node]:
            G.add_edge(node,nbr)
    return G                         


def to_dict_of_dicts(G,nodelist=None):
    """Return graph G as a Python dictionary of dictionaries.

    If nodelist is defined return a dict of dicts with only those nodes.

    """
    if nodelist is None:
        nodelist=G.nodes()

    # is this a XGraph or XDiGraph?
    if hasattr(G,'allow_multiedges')==True:
        xgraph=True
    else:
        xgraph=False

    d = {}
    for u in nodelist:
        d[u]={}
        for v in G.neighbors(u):
            if xgraph:
                data=G.get_edge(u,v)
            else:
                data=None
            d[u][v]=data
    return d            

def from_dict_of_dicts(d,create_using=None):
    """Return a NetworkX graph G from a Python dictionary of dictionaries.

    """
    if create_using is None:
        G=networkx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    # is this a XGraph or XDiGraph?
    if hasattr(G,'allow_multiedges')==True:
        xgraph=True
    else:
        xgraph=False

    G.add_nodes_from(d.keys())        
    for u in d:
        for v in d[u]:
            if xgraph:
                G.add_edge((u,v,d[u][v]))
            else:
                G.add_edge(u,v)

    return G                         



def to_numpy_matrix(G,nodelist=None):
    """Return adjacency matrix of graph as a numpy matrix.

    If nodelist is defined return adjacency matrix with nodes in nodelist
    in the order specified.  If not the ordering is whatever order
    the method G.nodes() produces.

    For Graph/DiGraph types which have no edge data 
    The value of the entry A[u,v] is one if there is an edge u-v
    and zero otherwise.

    For XGraph/XDiGraph the edge data is assumed to be a weight and be
    able to be converted to a valid numpy type (e.g. an int or a
    float).  The value of the entry A[u,v] is the weight given by
    get_edge(u,v) one if there is an edge u-v and zero otherwise.

    Graphs with multi-edges are not handled.

    """
    try:
        import numpy
    except ImportError:
        raise ImportError, \
              "Import Error: not able to import numpy: http://numpy.scipy.org "

    if hasattr(G,"multiedges"):
        if G.multiedges==True:
            raise ImportError, \
                  "Not allowed with for graphs with multiedges."

    if nodelist is None:
        nodelist=G.nodes()
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    A = numpy.asmatrix(numpy.zeros((nlen,nlen)))
    for e in G.edges_iter(nodelist):
        u=e[0]
        v=e[1]
        if len(e)==2:
            d=1
        else:
            d=e[2]
        A[index[u],index[v]]=d
        if not G.is_directed():
            A[index[v],index[u]]=d
    return A            

def from_numpy_matrix(A,create_using=None):
    """Return networkx graph G from numpy matrix adjacency list. 

    >>> G=from_numpy_matrix(A)

    """
    # This should never fail if you have created a numpy matrix with numpy...  
    try:
        import numpy
    except ImportError:
        raise ImportError, \
              "Import Error: not able to import numpy: http://numpy.scipy.org "

    if create_using is None:
        G=networkx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    # is this a XGraph or XDiGraph?
    if hasattr(G,'allow_multiedges')==True:
        xgraph=True
    else:
        xgraph=False

    nx,ny=A.shape

    try:
        nx==ny
    except:
        raise networkx.NetworkXError, \
              "Adjacency matrix is not square. nx,ny=%s",A.shape

    G.add_nodes_from(range(nx)) # make sure we get isolated nodes

    x,y=numpy.asarray(A).nonzero()         
    for (u,v) in zip(x,y):        
        if xgraph:
            G.add_edge(u,v,A[u,v])
        else:
            G.add_edge(u,v)                
    return G


def to_scipy_sparse_matrix(G,nodelist=None):
    """Return adjacency matrix of graph as a scipy sparse matrix.

    Uses lil_matrix format.  To convert to other formats see
    scipy.sparse documentation.

    If nodelist is defined return adjacency matrix with nodes in nodelist
    in the order specified.  If not the ordering is whatever order
    the method G.nodes() produces.

    For Graph/DiGraph types which have no edge data 
    The value of the entry A[u,v] is one if there is an edge u-v
    and zero otherwise.

    For XGraph/XDiGraph the edge data is assumed to be a weight and be
    able to be converted to a valid numpy type (e.g. an int or a
    float).  The value of the entry A[u,v] is the weight given by
    get_edge(u,v) one if there is an edge u-v and zero otherwise.

    Graphs with multi-edges are not handled.

    >>> A=scipy_sparse_matrix(G)
    >>> A.tocsr() # convert to compressed row storage

    """
    try:
        from scipy import sparse
    except ImportError:
        raise ImportError, \
              """Import Error: not able to import scipy sparse:
              see http://scipy.org""" 

    if hasattr(G,"multiedges"):
        if G.multiedges==True:
            raise ImportError, \
                  "Not allowed with for graphs with multiedges."

    if nodelist is None:
        nodelist=G.nodes()
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    A = sparse.lil_matrix((nlen,nlen))
    for e in G.edges_iter(nodelist):
        u=e[0]
        v=e[1]
        if len(e)==2:
            d=1
        else:
            d=e[2]
        A[index[u],index[v]]=d
        if not G.is_directed():
            A[index[v],index[u]]=d
    return A            


def from_scipy_sparse_matrix(A,create_using=None):
    """Return networkx graph G from scipy scipy sparse matrix
    adjacency list. 

    >>> G=from_scipy_sparse_matrix(A)

    """
    if create_using is None:
        G=networkx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    # is this a XGraph or XDiGraph?
    if hasattr(G,'allow_multiedges')==True:
        xgraph=True
    else:
        xgraph=False

    # convert everythin to coo - not the most efficient        
    AA=A.tocoo()
    nx,ny=AA.shape
    try:
        nx==ny
    except:
        raise networkx.NetworkXError, \
              "Adjacency matrix is not square. nx,ny=%s",A.shape


    G.add_nodes_from(range(nx)) # make sure we get isolated nodes
    for i in range(AA.nnz):
        e=AA.rowcol(i)
        if xgraph:
            e=(e[0],e[1],AA.getdata(i))
        G.add_edge(e)
    return G


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/convert.txt',
                                 package='networkx')
    return suite

def _test_suite_numpy():
    import doctest
    suite = doctest.DocFileSuite('tests/convert_numpy.txt',
                                     package='networkx')
    return suite

def _test_suite_scipy():
    import doctest
    suite = doctest.DocFileSuite('tests/convert_scipy.txt',
                                     package='networkx')
    return suite




if __name__ == "__main__":
    import os 
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    try:
        import numpy
        unittest.TextTestRunner().run(_test_suite_numpy())
    except ImportError: 
        pass
    try:
        import scipy
        unittest.TextTestRunner().run(_test_suite_scipy())
    except ImportError: 
        pass    
