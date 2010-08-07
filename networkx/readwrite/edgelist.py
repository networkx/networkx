"""
**********
Edge Lists
**********

Read and write NetworkX graphs as edge lists.

You can read or write three formats of edge lists with these functions.

Node pairs::

 1 2 # no data

Dictionary as data::

 1 2 {'weight':7, 'color':'green'} 

Arbitrary data::

 1 2 7 green

See the read_edgelist() function for details and examples.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['generate_edgelist',
           'write_edgelist',
           'parse_edgelist',
           'read_edgelist',
           'read_weighted_edgelist',
           'write_weighted_edgelist']

from networkx.utils import is_string_like, _get_fh, make_str
import networkx as nx

def generate_edgelist(G, delimiter = ' ', data = True):
    """Generate a single entry of the graph G in edge list format.

    This function is a generator.

    See read_edgelist for format details.

    Examples
    --------

    >>> G = nx.lollipop_graph(4, 3)
    >>> G[1][2]['weight'] = 3
    >>> G[3][4]['capacity'] = 12
    >>> adjlist_str = ''
    >>> for line in nx.generate_edgelist(G):
    ...     adjlist_str += line
    ... 
    >>> print(adjlist_str[:-1])
    0 1 {}
    0 2 {}
    0 3 {}
    1 2 {'weight': 3}
    1 3 {}
    2 3 {}
    3 4 {'capacity': 12}
    4 5 {}
    5 6 {}
    """
    if data is True or data is False:
        for e in G.edges(data=data):
            yield delimiter.join(map(make_str,e))+"\n"
    else:
        for u,v,d in G.edges(data=True):
            e=[u,v]
            e.extend(d[k] for k in data)
            yield delimiter.join(map(make_str,e))+"\n"


def write_edgelist(G, path, comments="#", delimiter=' ', data=True,
                   encoding = 'utf-8'):
    """Write graph as a list of edges.

    Parameters
    ----------
    G : graph
       A NetworkX graph
    path : file or string
       File or filename to write. If a file is provided, it must be
       opened in 'wb' mode.
       Filenames ending in .gz or .bz2 will be compressed.
    comments : string, optional
       The character used to indicate the start of a comment 
    delimiter : string, optional
       The string used to separate values.  The default is whitespace.
    data : bool or list, optional
       If False write no edge data.
       If True write a string representation of the edge data dictionary..  
       If a list (or other iterable) is provided, write the  keys specified 
       in the list.
    encoding: string, optional
       Specify which encoding to use when writing file.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_edgelist(G, "test.edgelist")
    >>> G=nx.path_graph(4)
    >>> fh=open("test.edgelist",'wb')
    >>> nx.write_edgelist(G, fh)
    >>> nx.write_edgelist(G, "test.edgelist.gz")
    >>> nx.write_edgelist(G, "test.edgelist.gz", data=False)

    >>> G=nx.Graph()
    >>> G.add_edge(1,2,weight=7,color='red')
    >>> nx.write_edgelist(G,'test.edgelist',data=False)
    >>> nx.write_edgelist(G,'test.edgelist',data=['color'])
    >>> nx.write_edgelist(G,'test.edgelist',data=['color','weight'])
    
    Notes
    -----
    The file will use the utf-8 encoding by default.
    It is possible to write files in other encodings by providing the
    encoding argument to write_edgelist.
    
    
    See Also
    --------
    write_edgelist()
    write_weighted_edgelist()
    """
    fh=_get_fh(path, 'wb')

    for line in generate_edgelist(G, delimiter, data):
        fh.write(line.encode(encoding))

def parse_edgelist(lines, comments = '#', delimiter = ' ',
                   create_using = None, nodetype = None, data = True):
    """Parse lines of an edge list representation of a graph.

    See read_edgelist for file format details.

    Returns
    -------
    G: NetworkX Graph
        The graph corresponding to lines

    Examples
    --------
    >>> lines = ["1 2 {}",
    ...          "2 3 {'weight':3, 'name': 'Frodo'}",
    ...          "3 4 {}",
    ...          "2 4 {}",
    ...          "5 2 {'weigth':6, 'name': 'Saruman'}"]
    >>> G = nx.parse_edgelist(iter(lines), nodetype = int)
    >>> G.nodes()
    [1, 2, 3, 4, 5]
    >>> G.edges(data = True)
    [(1, 2, {}), (2, 3, {'name': 'Frodo', 'weight': 3}), (2, 4, {}), (2, 5, {'name': 'Saruman', 'weigth': 6}), (3, 4, {})]
        
    """
    if create_using is None:
        G=nx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a NetworkX graph type")

    for line in lines:
        p=line.find(comments)
        if p>=0:
            line = line[:p]
        if not len(line):
            continue
        # split line, should have 2 or more
        s=line.strip().split(delimiter)
        if len(s)<2:
            continue
        u=s.pop(0)
        v=s.pop(0)
        d=s
        if nodetype is not None:
            try:
                u=nodetype(u)
                v=nodetype(v)
            except:
                raise TypeError("Failed to convert nodes %s,%s to type %s."\
                          %(u,v,nodetype))

        if len(d)==0 or data is False:
            # no data or data type specified
            edgedata={}
        elif data is True:
            try:
                from ast import literal_eval
            except:
                literal_eval=eval # use potentially unsafe built-in eval
            # no edge types specified
            try: # try to evaluate as dictionary
                edgedata=dict(literal_eval(' '.join(d)))
            except:
                raise TypeError(
                        "Failed to convert edge data (%s) to dictionary."%(d))
        else:
            # convert edge data to dictionary with specified keys and type
            if len(d)!=len(data):
                raise IndexError(
                        "Edge data %s and data_keys %s are not the same length"%
                                 (d, data))
            edgedata={}
            for (edge_key,edge_type),edge_value in zip(data,d):
                try:
                    edge_value=edge_type(edge_value)
                except:
                    raise TypeError("Failed to convert edge data (%s) to type %s."%
                                    (edge_key, edge_type))
                edgedata.update({edge_key:edge_value})
        G.add_edge(u, v, **edgedata)
    return G


def read_edgelist(path, 
                  comments="#", 
                  delimiter=' ',
                  create_using=None, 
                  nodetype=None, 
                  data=True,
                  edgetype = None,
                  encoding = 'utf-8'
                  ):
    """Read a graph from a list of edges.

    Parameters
    ----------
    path : file or string
       File or filename to write. If a file is provided, it must be
       opened in 'rb' mode.
       Filenames ending in .gz or .bz2 will be uncompressed.
    comments : string, optional
       The character used to indicate the start of a comment. 
    delimiter : string, optional
       The string used to separate values.  The default is whitespace.
    create_using : Graph container, optional, 
       Use specified container to build graph.  The default is networkx.Graph,
       an undirected graph.
    nodetype : int, float, str, Python type, optional
       Convert node data from strings to specified type
    data : list of (label,type) tuples
       Tuples specifying dictionary key names and types for edge data
    edgetype : int, float, str, Python type, optional OBSOLETE
       Convert edge data from strings to specified type and use as 'weight'
    encoding: string, optional
       Specify which encoding to use when reading file.

    Returns
    -------
    G : graph
       A networkx Graph or other type specified with create_using

    Examples
    --------
    >>> nx.write_edgelist(nx.path_graph(4), "test.edgelist")
    >>> G=nx.read_edgelist("test.edgelist")

    >>> fh=open("test.edgelist", 'rb')
    >>> G=nx.read_edgelist(fh)

    >>> G=nx.read_edgelist("test.edgelist", nodetype=int)
    >>> G=nx.read_edgelist("test.edgelist",create_using=nx.DiGraph())

    Notes
    -----
    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.) 

    Example edgelist file formats.

    Without edge data::

     # read with 
     # >>> G=nx.read_edgelist(fh,data=False)
     # source target
     a b
     a c
     d e

    With edge data as dictionary:: 

     # read with 
     # >>> G=nx.read_edgelist(fh,data=True)
     # source target data  
     a b {'weight': 1}
     a c {'weight': 3.14159}
     d e {'fruit': 'apple'}

    With arbitrary edge data:: 

     # read with 
     # >>> G=nx.read_edgelist(fh,data=[('weight',float')])
     # or
     # >>> G=nx.read_weighted_edgelist(fh)
     # source target data  
     a b 1
     a c 3.14159
     d e 42
    """
    fh=_get_fh(path, 'rb')
    lines = (line.decode(encoding) for line in fh)
    return parse_edgelist(lines,
                          comments = comments,
                          delimiter = delimiter,
                          create_using = create_using,
                          nodetype = nodetype,
                          data = data)


def write_weighted_edgelist(G, path, 
                            comments="#", 
                            delimiter=' ',
                            encoding = 'utf-8'):
    """Write graph G as a list of edges with numeric weights.

    Parameters
    ----------
    G : graph
       A NetworkX graph
    path : file or string
       File or filename to write. If a file is provided, it must be
       opened in 'wb' mode.
       Filenames ending in .gz or .bz2 will be compressed.
    comments : string, optional
       The character used to indicate the start of a comment 
    delimiter : string, optional
       The string used to separate values.  The default is whitespace.
    encoding: string, optional
       Specify which encoding to use when writing file.

    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_edge(1,2,weight=7)
    >>> nx.write_weighted_edgelist(G, 'weighted.edgelist')

    See Also
    --------
    read_edgelist()
    write_edgelist()
    write_weighted_edgelist()

"""
    write_edgelist(G,path,
                   comments=comments,
                   delimiter=delimiter,
                   data=('weight',),
                   encoding = encoding)
    
def read_weighted_edgelist(path, comments="#", delimiter=' ',
                           create_using=None, nodetype=None,
                           encoding = 'utf-8') :

    """Read list of edges with numeric weights.

    Parameters
    ----------
    path : file or string
       File or filename to write. If a file is provided, it must be
       opened in 'rb' mode.
       Filenames ending in .gz or .bz2 will be uncompressed.
    comments : string, optional
       The character used to indicate the start of a comment. 
    delimiter : string, optional
       The string used to separate values.  The default is whitespace.
    create_using : Graph container, optional, 
       Use specified container to build graph.  The default is networkx.Graph,
       an undirected graph.
    nodetype : int, float, str, Python type, optional
       Convert node data from strings to specified type
    encoding: string, optional
       Specify which encoding to use when reading file.

    Returns
    -------
    G : graph
       A networkx Graph or other type specified with create_using

    Notes
    -----
    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.) 

    Example edgelist file format.

    With numeric edge data:: 

     # read with 
     # >>> G=nx.read_weighted_edgelist(fh)
     # source target data  
     a b 1
     a c 3.14159
     d e 42
    """
    return read_edgelist(path,
                         comments=comments,
                         delimiter=delimiter,
                         create_using=create_using,
                         nodetype=nodetype,
                         data=(('weight',float),),
                         encoding = encoding
                         )
