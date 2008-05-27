"""
Convert NetworkX graphs to and from other formats.

from_whatever attemps to guess the input format

Create a 10 node random digraph

>>> from networkx import *
>>> import numpy
>>> a=numpy.reshape(numpy.random.random_integers(0,1,size=100),(10,10))
>>> D=from_whatever(a,create_using=DiGraph()) # or D=DiGraph(a) 

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

def _prep_create_using(create_using):
    """
    Returns a graph object ready to be populated.

    If create_using is None return the default (just networkx.Graph())
    If create_using.clear() works, assume it returns a graph object.
    Otherwise raise an exception because create_using is not a networkx graph.

    """
    if create_using is None:
        G=networkx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")
    return G


def from_whatever(thing,create_using=None):
    """Attempt to make a NetworkX graph from an known type.

    Current known types are:

       any NetworkX graph
       dict-of-dicts
       dist-of-lists
       numpy matrix
       numpy ndarray
       scipy sparse matrix
       pygraphviz agraph

    """
    # pygraphviz  agraph
    if hasattr(thing,"is_strict"):
        try:
            return networkx.from_agraph(thing,create_using=create_using)
        except:
            raise networkx.NetworkXError,\
                  "Input is not a correct pygraphviz graph."

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
        nodelist=G

    d = {}
    for n in nodelist:
        d[n]=[nbr for nbr in G.neighbors(n) if nbr in nodelist]
    return d            

def from_dict_of_lists(d,create_using=None):
    """Return a NetworkX graph G from a Python dict of lists.

    """
    G=_prep_create_using(create_using)
    G.add_nodes_from(d)        

    if hasattr(G,"allow_multiedges") and G.multiedges and not G.is_directed():
        # a dict_of_lists can't show multiedges.  BUT for undirected graphs,
        # each edge shows up twice in the dict_of_lists.  
        # So we need to treat this case separately.
        seen={}
        for node in d:
            for nbr in d[node]:
                if (node,nbr) not in seen:
                    G.add_edge(node,nbr)
                    seen[(nbr,node)]=1  # don't allow reverse edge to show up 
    else:
        for node in d:
            for nbr in d[node]:
                G.add_edge(node,nbr)
    return G                         


def to_dict_of_dicts(G,nodelist=None,edge_data=None):
    """Return graph G as a Python dictionary of dictionaries.

    If nodelist is defined return a dict of dicts with only those nodes.

    If edge_data is given, the value of the dictionary will be
    set to edge_data for all edges.  This is useful to make
    an adjacency matrix type representation with 1 as the edge data.
    
    """
    if nodelist is None:
        nodelist=G.nodes()
    if edge_data is not None:
        get_edge=lambda x,y:edge_data
    else:
        get_edge=G.get_edge

    d = {}
    for u in nodelist:
        d[u]={}
        for v in G.neighbors(u):
            if v in nodelist:
                d[u][v]=get_edge(u,v)
    return d            


def from_dict_of_dicts(d,create_using=None):
    """Return a NetworkX graph G from a Python dictionary of dictionaries.

    The value of the inner dict becomes the edge_data for the NetworkX graph
    EVEN if create_using is a NetworkX Graph which doesn't ever use this data.

    If create_using is an XGraph/XDiGraph with multiedges==True, the edge_data
    should be a list, though this routine does not check for that.

    """
    G=_prep_create_using(create_using)
    G.add_nodes_from(d)

    # is this a XGraph or XDiGraph?
    # FIXME
    # This is a bad way to check for whether edge data exists...
    # If someone ever creates a graph class with edge data and
    # without an allow_multiedges method, it won't work.
    if hasattr(G,'allow_multiedges'): # assume edge data
        if G.multiedges:
            # this is a NetworkX graph with multiedges=True
            # make a copy of the list of edge data (but not the edge data)
            if G.is_directed():
                for u,nbrs in d.iteritems():
                    for v,datalist in nbrs.iteritems():
                        if type(datalist) == type([]):
                            dl=datalist[:] # copy of the edge_data list
                        else:
                            dl=[datalist]
                        G.pred[u][v]=dl
                        G.succ[u][v]=dl
            else:
                for u,nbrs in d.iteritems():
                    for v,datalist in nbrs.iteritems():
                        if type(datalist) == type([]):
                            dl=datalist[:] # copy of the edge_data list
                        else:
                            dl=[datalist]
                        G.adj[u][v]=dl
                        G.adj[v][u]=dl
        else:
            for u,nbrs in d.iteritems():
                for v,data in nbrs.iteritems():
                    G.add_edge(u,v,data)
    else: # no edge data
        for u,nbrs in d.iteritems():
            for v in nbrs:
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
        if G.multiedges:
            raise TypeError, \
                  "Conversion to numpy_matrix not allowed with for graphs with multiedges."

    if nodelist is None:
        nodelist=G.nodes()
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    A = numpy.asmatrix(numpy.zeros((nlen,nlen)))
    directed=G.is_directed()
    for e in G.edges_iter(nodelist):
        u=e[0]
        v=e[1]
        if len(e)==2:
            d=1
        else:
            d=e[2]
            if d is None: d=1 # None would be a nan in numpy, use 1
        if u not in nodelist or v not in nodelist:
            continue
        A[index[u],index[v]]=d
        if not directed:
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

    G=_prep_create_using(create_using)

    nx,ny=A.shape

    if nx!=ny:
        raise networkx.NetworkXError, \
              "Adjacency matrix is not square. nx,ny=%s"%(A.shape,)

    G.add_nodes_from(range(nx)) # make sure we get isolated nodes

    # get a list of edges
    x,y=numpy.asarray(A).nonzero()         
    # is this a XGraph or XDiGraph?
    # FIXME
    # This is a bad way to check for whether edge data exists...
    # If someone ever creates a graph class with edge data and
    # without an allow_multiedges method, it won't work.
    if hasattr(G,'allow_multiedges'):
        for (u,v) in zip(x,y):        
            G.add_edge(u,v,A[u,v])
    else:
        for (u,v) in zip(x,y):        
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
        if G.multiedges:
            raise TypeError, \
                  "Conversion to scipy_sparse_matrix not allowed with for graphs with multiedges."

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
            if d is None: d=1 # None would be a nan, use 1 
        if u not in nodelist or v not in nodelist:
            continue
        A[index[u],index[v]]=d
        if not G.is_directed():
            A[index[v],index[u]]=d
    return A            


def from_scipy_sparse_matrix(A,create_using=None):
    """Return networkx graph G from scipy scipy sparse matrix
    adjacency list. 

    >>> G=from_scipy_sparse_matrix(A)

    """
    G=_prep_create_using(create_using)

    # is this a XGraph or XDiGraph?
    # FIXME
    # This is a bad way to check for whether edge data exists...
    # If someone ever creates a graph class with edge data and
    # without an allow_multiedges method, it won't work.
    if hasattr(G,'allow_multiedges'):
        xgraph=True
    else:
        xgraph=False

    # convert all formats to lil - not the most efficient way       
    AA=A.tolil()
    nx,ny=AA.shape

    if nx!=ny:
        raise networkx.NetworkXError, \
              "Adjacency matrix is not square. nx,ny=%s"%(A.shape,)


    G.add_nodes_from(range(nx)) # make sure we get isolated nodes

    for i,row in enumerate(AA.rows):
        for pos,j in enumerate(row):
           if xgraph:
               G.add_edge(i,j,AA.data[i][pos])
           else:
               G.add_edge(i,j)
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
