"""
Convert NetworkX graphs to and from other formats.

from_whatever attempts to guess the input format

Example: Create a 10 node random digraph

>>> import numpy
>>> a=numpy.reshape(numpy.random.random_integers(0,1,size=100),(10,10))
>>> D=nx.from_whatever(a,create_using=nx.DiGraph()) 

or

>>> D=nx.DiGraph(a) 

For graphviz formats see networkx.drawing.nx_pygraphviz
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
           'from_numpy_matrix', 'to_numpy_matrix',
           'from_scipy_sparse_matrix', 'to_scipy_sparse_matrix']

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
        G=create_using
        try:
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")
    return G


def from_whatever(thing,create_using=None,multigraph_input=False):
    """Attempt to make a NetworkX graph from an known type.

    Current known types are:

       any NetworkX graph
       dict-of-dicts
       dist-of-lists
       numpy matrix
       numpy ndarray
       scipy sparse matrix
       pygraphviz agraph

    If multigraph_input is True and thing is a dict_of_dicts,
    try to create a multigraph assuming dict_of_dict_of_lists.
    If thing and create_using are both multigraphs then create
    a multigraph from a multigraph.

    """
    # NX graph
    if hasattr(thing,"adj"):
        try:
            result= from_dict_of_dicts(thing.adj,\
                    create_using=create_using,\
                    multigraph_input=thing.multigraph)
            result.weighted=thing.weighted
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

    Completely ignores edge data for MultiGraph and MultiDiGraph.

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

    if G.multigraph and not G.directed:
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
    """Return graph G as a Python dictionary of dictionaries.

    If nodelist is defined return a dict of dicts with only those nodes.

    If edge_data is given, the value of the dictionary will be
    set to edge_data for all edges.  This is useful to make
    an adjacency matrix type representation with 1 as the edge data.
    If edgedata is None, the edgedata in G is used to fill the values.
    If G is a multigraph, the edgedata is a list for each pair (u,v).
    
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
    """Return a NetworkX graph G from a Python dictionary of dictionaries.

    The value of the inner dict becomes the edge_data for the NetworkX graph.

    When multigraph_input is True, the values of the inner dict are assumed 
    to be containers of edge data for multiple edges.
    Otherwise this routine assumes the edgedata are singletons.

    """
    G=_prep_create_using(create_using)
    G.add_nodes_from(d)

    # is dict a MultiGraph or MultiDiGraph?
    if multigraph_input:
        # make a copy of the list of edge data (but not the edge data)
        if G.directed:   # copy edge list
            G.add_edges_from( ((u,v,data) for u,nbrs in d.iteritems() \
                    for v,dl in nbrs.iteritems() for data in dl) )
        else: # Undirected
            seen={}   # don't add both directions of undirected graph
            for u,nbrs in d.iteritems():
                for v,datalist in nbrs.iteritems():
                    if v not in seen:
                        G.add_edges_from( ((u,v,data) for data in datalist) )
                seen[u]=1  # don't allow reverse edge to show up 
    else: # not a multigraph to multigraph transfer
        if G.directed:
            G.add_edges_from( ((u,v,data) for u,nbrs in d.iteritems() \
                    for v,data in nbrs.iteritems()) )
        else:    # need this if G is multigraph and slightly faster if not multigraph
            seen={}  
            for u,nbrs in d.iteritems():
                for v,data in nbrs.iteritems():
                    if v not in seen:
                        G.add_edge(u,v,data)
                seen[u]=1
    return G                         


def to_numpy_matrix(G,nodelist=None):
    """Return the adjacency matrix of graph G as a numpy matrix.

    If nodelist is defined return adjacency matrix with nodes in nodelist
    in the order specified.  All nodes must appear in nodelist or a KeyError
    is raised.
    If nodelist is None, the ordering is produced by G.nodes()

    When G.weighted==False the value of the entry A[u,v] is one 
    if there is an edge u-v and zero otherwise.

    Multiple edges and edge data are both ignored for MultiGraph/MultiDiGraph.

    """
    try:
        import numpy
    except ImportError:
        raise ImportError, \
              "Import Error: not able to import numpy: http://numpy.scipy.org "


    if nodelist is None:
        nodelist=G.nodes()
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    A = numpy.asmatrix(numpy.zeros((nlen,nlen)))
    if G.weighted and not G.multigraph:
        for n,nbrdict in G.adjacency_iter():
            if n in index:
                for nbr,data in nbrdict.iteritems():
                    if nbr in index:
                        A[index[n],index[nbr]]=data
    else: # ignore edge data
        for n,nbrdict in G.adjacency_iter():
            if n in index:
                for nbr in nbrdict:
                    if nbr in index:
                        A[index[n],index[nbr]]=1
    return A            

def from_numpy_matrix(A,create_using=None):
    """Return networkx graph G from numpy matrix adjacency list. 

    >>> import numpy
    >>> A=numpy.matrix([[1,1],[2,1]])
    >>> G=nx.from_numpy_matrix(A)

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
    G.add_edges_from( ((u,v,A[u,v]) for (u,v) in zip(x,y)) )
    return G


def to_scipy_sparse_matrix(G,nodelist=None):
    """Return adjacency matrix of graph as a scipy sparse matrix.

    Uses lil_matrix format.  To convert to other formats see
    scipy.sparse documentation.

    If nodelist is defined return adjacency matrix with nodes 
    in the order specified by nodelist.  Otherwise the order
    is produced by G.nodes().

    If G.weighted is True and G is not a multigraph, the edgedata
    is assumed to be numeric and becomes the value of A[u.v].
    Otherwise A[u,v] is one if an edge u-v exists and zero otherwise.

    >>> G=nx.path_graph(4)
    >>> A=nx.to_scipy_sparse_matrix(G)
    >>> C=A.tocsr() # convert to compressed row storage

    """
    try:
        from scipy import sparse
    except ImportError:
        raise ImportError, \
              """Import Error: not able to import scipy sparse:
              see http://scipy.org""" 


    if nodelist is None:
        nodelist=G.nodes()
    nlen=len(nodelist)    
    index=dict(zip(nodelist,range(nlen)))# dict mapping vertex name to position
    A = sparse.lil_matrix((nlen,nlen))
    if G.weighted and not G.multigraph:
        for n,nbrdict in G.adjacency_iter():
            if n in index:
                for nbr,data in nbrdict.iteritems():
                    if nbr in index:
                        A[index[n],index[nbr]]=data
    else: # ignore edge data
        for n,nbrdict in G.adjacency_iter():
            if n in index:
                for nbr in nbrdict:
                    if nbr in index:
                        A[index[n],index[nbr]]=1
    return A            


def from_scipy_sparse_matrix(A,create_using=None):
    """Return networkx graph G from scipy scipy sparse matrix
    adjacency list. 

    >>> import scipy.sparse
    >>> A=scipy.sparse.eye(2,2,1)
    >>> G=nx.from_scipy_sparse_matrix(A)

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
