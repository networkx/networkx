# -*- coding: utf-8 -*-
"""
***************
Adjacency Lists
***************

Read and write NetworkX graphs as adjacency lists.

Note that NetworkX graphs can contain any hashable Python object as
node (not just integers and strings).  So writing a NetworkX graph
as a text file may not always be what you want: see write_gpickle
and gread_gpickle for that case.

This module provides the following :

Adjacency list with single line per node:
Useful for connected or unconnected graphs without edge data.

>>> G=nx.path_graph(4)
>>> path='test.adjlist'
>>> write_adjlist(G, path)
>>> G=read_adjlist(path)

Adjacency list with multiple lines per node:
Useful for connected or unconnected graphs with or without edge data.

>>> write_multiline_adjlist(G, path)
>>> G=read_multiline_adjlist(path)

"""
__author__ = '\n'.join(['Aric Hagberg <hagberg@lanl.gov>',
                        'Dan Schult <dschult@colgate.edu>',
                        'Loïc Séguin-C. <loicseguin@gmail.com>'])
#    Copyright (C) 2004-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['generate_multiline_adjlist',
           'write_multiline_adjlist',
           'parse_multiline_adjlist',
           'read_multiline_adjlist',
           'generate_adjlist',
           'write_adjlist',
           'parse_adjlist',
           'read_adjlist']


from networkx.utils import is_string_like, make_str, _get_fh
import networkx as nx

def generate_multiline_adjlist(G, delimiter = ' '):
    """Generate a single entry of the graph G in multiline adjacency list format.

    This function is a generator.

    See read_multiline_adjlist for format details.

    Examples
    --------

    >>> G = nx.lollipop_graph(4, 3)
    >>> adjlist_str = ''
    >>> for line in nx.generate_multiline_adjlist(G):
    ...     adjlist_str += line
    ... 
    >>> print(adjlist_str[:-1])
    0 3
    1 {}
    2 {}
    3 {}
    1 2
    2 {}
    3 {}
    2 1
    3 {}
    3 1
    4 {}
    4 1
    5 {}
    5 1
    6 {}
    6 0

    """

    if G.is_directed():
        if G.is_multigraph():
            for s,nbrs in G.adjacency_iter():
                nbr_edges=[ (u,data) 
                            for u,datadict in nbrs.items() 
                            for key,data in datadict.items()]
                deg=len(nbr_edges)
                multiline = make_str(s)+delimiter+"%i\n"%(deg)
                for u,d in nbr_edges:
                    if d is None:
                        multiline += make_str(u)+'\n'
                    else:
                        multiline += make_str(u)+delimiter+make_str(d)+"\n"
                yield multiline
        else: # directed single edges
            for s,nbrs in G.adjacency_iter():
                deg=len(nbrs)
                multiline = make_str(s)+delimiter+"%i\n"%(deg)
                for u,d in nbrs.items():
                    if d is None:    
                        multiline += make_str(u)+'\n'
                    else:   
                        multiline += make_str(u)+delimiter+make_str(d)+"\n"
                yield multiline
    else: # undirected
        if G.is_multigraph():
            seen=set()  # helper dict used to avoid duplicate edges
            for s,nbrs in G.adjacency_iter():
                nbr_edges=[ (u,data) 
                            for u,datadict in nbrs.items() 
                            if u not in seen
                            for key,data in datadict.items()]
                deg=len(nbr_edges)
                multiline = make_str(s)+delimiter+"%i\n"%(deg)
                for u,d in nbr_edges:
                    if d is None:    
                        multiline += make_str(u)+'\n'
                    else:   
                        multiline += make_str(u)+delimiter+make_str(d)+"\n"
                seen.add(s)
                yield multiline
        else: # undirected single edges
            seen=set()  # helper dict used to avoid duplicate edges
            for s,nbrs in G.adjacency_iter():
                nbr_edges=[ (u,d) for u,d in nbrs.items() if u not in seen]
                deg=len(nbr_edges)
                multiline = make_str(s)+delimiter+"%i\n"%(deg)
                for u,d in nbr_edges:
                    if d is None:    
                        multiline += make_str(u)+'\n'
                    else:   
                        multiline += make_str(u)+delimiter+make_str(d)+"\n"
                seen.add(s)
                yield multiline

def write_multiline_adjlist(G, path, delimiter=' ', comments='#',
                            encoding = 'utf-8'):
    """
    Write the graph G in multiline adjacency list format to the file or file handle path.

    See read_multiline_adjlist for file format details.

    Examples
    --------

    >>> G=nx.path_graph(4)
    >>> nx.write_multiline_adjlist(G,"test.adjlist")

    path can be a filehandle or a string with the name of the file. If a
    filehandle is provided, it has to be opened in 'wb' mode.

    >>> fh=open("test.adjlist",'wb')
    >>> nx.write_multiline_adjlist(G,fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_multiline_adjlist(G,"test.adjlist.gz")

    The file will use the utf-8 encoding by default.
    It is possible to write files in other encodings by providing the
    encoding argument to write_multiline_adjlist.

    >>> fh=open("test.adjlist",'wb')
    >>> nx.write_multiline_adjlist(G,fh,encoding='utf-8')
    
    The same result can be obtained with the following call.
    >>> nx.write_multiline_adjlist(G, 'test-utf8.adjlist', encoding = 'utf-8')

    """
    import sys
    import time

    fh=_get_fh(path,mode='wb')        
    pargs=comments+" ".join(sys.argv)
    header = ("%s\n" % (pargs)
             + comments + " GMT %s\n" % (time.asctime(time.gmtime()))
             + comments + " %s\n" % (G.name))
    fh.write(header.encode(encoding))

    for multiline in generate_multiline_adjlist(G, delimiter):
        fh.write(multiline.encode(encoding))

def parse_multiline_adjlist(lines, comments = '#', delimiter = ' ',
                            create_using = None, nodetype = None,
                            edgetype = None):
    """Parse lines of a multiline adjacency list representation of a graph.

    See read_multiline_adjlist for file format details.

    Returns
    -------
    G: NetworkX Graph
        The graph corresponding to lines

    Examples
    --------
    >>> lines = ['1 2',
    ...          "2 {'weight':3, 'name': 'Frodo'}",
    ...          "3 {}",
    ...          "2 1",
    ...          "5 {'weigth':6, 'name': 'Saruman'}"]
    >>> G = nx.parse_multiline_adjlist(iter(lines), nodetype = int)
    >>> G.nodes()
    [1, 2, 3, 5]
    >>> G.edges(data = True)
    [(1, 2, {'name': 'Frodo', 'weight': 3}), (1, 3, {}), (2, 5, {'name': 'Saruman', 'weigth': 6})]
    
       
    """
    if create_using is None:
        G=nx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    for line in lines:
        p=line.find(comments)
        if p>=0:
            line = line[:p]
        if not line: continue
        try:
            (u,deg)=line.strip().split(delimiter)
            deg=int(deg)
        except:
            raise TypeError("Failed to read node and degree on line (%s)"%line)
        if nodetype is not None:
            try:
                u=nodetype(u)
            except:
                raise TypeError("Failed to convert node (%s) to type %s"\
                      %(u,nodetype))
        G.add_node(u)
        for i in range(deg):
            while True:
                try:
                    line = next(lines)
                except StopIteration:
                    msg = "Failed to find neighbor for node (%s)" % (u,)
                    raise TypeError(msg)
                p=line.find(comments)
                if p>=0:
                    line = line[:p]
                if line: break
            vlist=line.strip().split(delimiter)
            numb=len(vlist)
            if numb<1:
                continue # isolated node
            v=vlist.pop(0)
            data=''.join(vlist)
            if nodetype is not None:
                try:
                    v=nodetype(v)
                except:
                    raise TypeError(
                            "Failed to convert node (%s) to type %s"\
                                       %(v,nodetype))
            if edgetype is not None:
                try:
                    edgedata={'weight':edgetype(data)}
                except:
                    raise TypeError(
                            "Failed to convert edge data (%s) to type %s"\
                                    %(data, edgetype))
            else:
                try:
                    from ast import literal_eval
                except:
                    literal_eval=eval # use potentially unsafe built-in eval
                try: # try to evaluate 
                    edgedata=literal_eval(data)
                except:
                    edgedata={}
            G.add_edge(u,v,attr_dict=edgedata)

    return G


def read_multiline_adjlist(path, comments="#", delimiter=' ',
                           create_using=None,
                           nodetype=None, edgetype=None,
                           encoding = 'utf-8'):
    """Read graph in multi-line adjacency list format from path.

    Examples
    --------

    >>> G=nx.path_graph(4)
    >>> nx.write_multiline_adjlist(G,"test.adjlist")
    >>> G=nx.read_multiline_adjlist("test.adjlist")

    path can be a filehandle or a string with the name of the file. If a
    filehandle is provided, it has to be opened in 'rb' mode.

    >>> fh=open("test.adjlist", 'rb')
    >>> G=nx.read_multiline_adjlist(fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_multiline_adjlist(G,"test.adjlist.gz")
    >>> G=nx.read_multiline_adjlist("test.adjlist.gz")

    nodetype is an optional function to convert node strings to nodetype

    For example

    >>> G=nx.read_multiline_adjlist("test.adjlist", nodetype=int)

    will attempt to convert all nodes to integer type

    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.) 

    edgetype is a function to convert edge data strings to edgetype

    >>> G=nx.read_multiline_adjlist("test.adjlist")

    create_using is an optional networkx graph type, the default is
    Graph(), a simple undirected graph 

    >>> G=nx.read_multiline_adjlist("test.adjlist", create_using=nx.DiGraph())

    The comments character (default='#') at the beginning of a
    line indicates a comment line.

    The entries are separated by delimiter (default=' ').
    If whitespace is significant in node or edge labels you should use
    some other delimiter such as a tab or other symbol.  
    

    Example multiline adjlist file format

    No edge data::

     # source target for Graph or DiGraph
     a 2
     b
     c
     d 1
     e

     With edge data::

     # source target for XGraph or XDiGraph with edge data
     a 2
     b edge-ab-data
     c edge-ac-data
     d 1
     e edge-de-data

    Reading the file will use the utf-8 text encoding by default.
    It is possible to read files with other encodings by providing the
    encoding arguement to read_multiline_adjlist.

    >>> fh=open("test.adjlist",'rb')
    >>> G=nx.read_multiline_adjlist(fh, encoding = 'iso-8859-1')
    """
    inp=_get_fh(path, 'rb')
    lines = (line.decode(encoding) for line in inp)
    return parse_multiline_adjlist(lines, 
                                   comments = comments,
                                   delimiter = delimiter,
                                   create_using = create_using,
                                   nodetype = nodetype,
                                   edgetype = edgetype)


def generate_adjlist(G, delimiter = ' '):
    """Generate a single line of the graph G in adjacency list format.

    This function is a generator.

    See read_adjlist for line format details.

    Examples
    --------

    >>> G = nx.lollipop_graph(4, 3)
    >>> adjlist_str = ''
    >>> for line in nx.generate_adjlist(G):
    ...     adjlist_str += line
    ... 
    >>> print(adjlist_str[:-1])
    0 1 2 3 
    1 2 3 
    2 3 
    3 4 
    4 5 
    5 6 
    6 

    """
    directed=G.is_directed()
    seen=set()
    for s,nbrs in G.adjacency_iter():
        line = make_str(s)+delimiter
        for t,data in nbrs.items():
            if not directed and t in seen:
                continue
            if G.is_multigraph():
                for d in data.values():
                    line += make_str(t) + delimiter
            else:
                line += make_str(t) + delimiter
        line += '\n'
        if not directed:
            seen.add(s)
        yield line


def write_adjlist(G, path, comments="#", delimiter=' ', encoding = 'utf-8'):
    """Write graph G in single-line adjacency-list format to path.

    See read_adjlist for file format details.

    Examples
    --------

    >>> G=nx.path_graph(4)
    >>> nx.write_adjlist(G,"test.adjlist")

    path can be a filehandle or a string with the name of the file. If a
    filehandle is provided, it has to be opened in 'wb' mode.

    >>> fh=open("test.adjlist",'wb')
    >>> nx.write_adjlist(G, fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_adjlist(G, "test.adjlist.gz")

    The file will use the utf-8 encoding by default.
    It is possible to write files in other encodings by providing the
    encoding argument to write_adjlist.

    >>> fh=open("test.adjlist", 'wb') 
    >>> nx.write_adjlist(G,fh, encoding='iso-8859-1')

    Does not handle edge data. 
    Use 'write_edgelist' or 'write_multiline_adjlist'
    """
    import sys
    import time
    fh=_get_fh(path,mode='wb')        
    pargs=comments + " ".join(sys.argv) + '\n'
    header = (pargs
             + comments + " GMT %s\n" % (time.asctime(time.gmtime()))
             + comments + " %s\n" % (G.name))
    fh.write(header.encode(encoding))

    for line in generate_adjlist(G, delimiter):
        fh.write(line.encode(encoding))


def parse_adjlist(lines, comments = '#', delimiter = ' ',
                  create_using = None, nodetype = None):
    """Parse lines of an adjacency list representation of a graph.

    See read_adjlist for file format details.

    Returns
    -------
    G: NetworkX Graph
        The graph corresponding to the lines in adjacency list format.

    Examples
    --------
    >>> lines = ['1 2 5',
    ...          '2 3 4',
    ...          '3 5',
    ...          '4',
    ...          '5']
    >>> G = nx.parse_adjlist(iter(lines), nodetype = int)
    >>> G.nodes()
    [1, 2, 3, 4, 5]
    >>> G.edges()
    [(1, 2), (1, 5), (2, 3), (2, 4), (3, 5)]
    
    """
    if create_using is None:
        G=nx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    for line in lines:
        p=line.find(comments)
        if p>=0:
            line = line[:p]
        if not len(line):
            continue
        vlist=line.strip().split(delimiter)
        u=vlist.pop(0)
        # convert types
        if nodetype is not None:
            try:
                u=nodetype(u)
            except:
                raise TypeError("Failed to convert node (%s) to type %s"\
                                %(u,nodetype))
        G.add_node(u)
        if nodetype is not None:
            try:
                vlist=map(nodetype,vlist)
            except:
                raise TypeError("Failed to convert nodes (%s) to type %s"\
                                    %(','.join(vlist),nodetype))
        G.add_edges_from([(u, v) for v in vlist])
    return G

def read_adjlist(path, comments="#", delimiter=' ',
                 create_using=None, nodetype=None,
                 encoding = 'utf-8'):
    """Read graph in single line adjacency list format from path.

    Examples
    --------

    >>> G=nx.path_graph(4)
    >>> nx.write_adjlist(G, "test.adjlist")
    >>> G=nx.read_adjlist("test.adjlist")

    path can be a filehandle or a string with the name of the file. If a
    filehandle is provided, it has to be opened in 'rb' mode.

    >>> fh=open("test.adjlist", 'rb')
    >>> G=nx.read_adjlist(fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_adjlist(G, "test.adjlist.gz")
    >>> G=nx.read_adjlist("test.adjlist.gz")

    nodetype is an optional function to convert node strings to nodetype

    For example

    >>> G=nx.read_adjlist("test.adjlist", nodetype=int)

    will attempt to convert all nodes to integer type

    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.) 

    create_using is an optional networkx graph type, the default is
    Graph(), an undirected graph. 

    >>> G=nx.read_adjlist("test.adjlist", create_using=nx.DiGraph())

    Does not handle edge data: use 'read_edgelist' or 'read_multiline_adjlist'

    The comments character (default='#') at the beginning of a
    line indicates a comment line.

    The entries are separated by delimiter (default=' ').
    If whitespace is significant in node or edge labels you should use
    some other delimiter such as a tab or other symbol.  

    Sample format::

     # source target
     a b c
     d e

    """
    fh=_get_fh(path, 'rb')
    lines = (line.decode(encoding) for line in fh)
    return parse_adjlist(lines,
                         comments = comments,
                         delimiter = delimiter,
                         create_using = create_using,
                         nodetype = nodetype)

