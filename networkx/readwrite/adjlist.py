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

    write_adjlist(G, path)
    G=read_adjlist(path)

Adjacency list with multiple lines per node:
Useful for connected or unconnected graphs with or without edge data.

    write_multiline_adjlist(G, path)
    read_multiline_adjlist(path)

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_multiline_adjlist', 'write_multiline_adjlist',
           'read_adjlist', 'write_adjlist']


from networkx.utils import is_string_like,_get_fh
import networkx as nx

def write_multiline_adjlist(G, path, delimiter=' ', comments='#'):
    """
    Write the graph G in multiline adjacency list format to the file
    or file handle path.

    See read_multiline_adjlist for file format details.

    Examples
    --------

    >>> G=nx.path_graph(4)
    >>> nx.write_multiline_adjlist(G,"test.adjlist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("test.adjlist",'w')
    >>> nx.write_multiline_adjlist(G,fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_multiline_adjlist(G,"test.adjlist.gz")

    The file will use the default text encoding on your system.
    It is possible to write files in other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> import codecs
    >>> fh=codecs.open("test.adjlist",'w',encoding='utf=8') # utf-8 encoding
    >>> nx.write_multiline_adjlist(G,fh)

    """
    import sys
    import time

    fh=_get_fh(path,mode='w')        
    pargs=comments+" ".join(sys.argv)
    fh.write("%s\n" % (pargs))
    fh.write(comments+" GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write(comments+" %s\n" % (G.name))

    def make_str(t):
        if is_string_like(t): return t
        return str(t)

    if G.is_directed():
        if G.is_multigraph():
            for s,nbrs in G.adjacency_iter():
                nbr_edges=[ (u,data) 
                            for u,datadict in nbrs.iteritems() 
                            for key,data in datadict.items()]
                deg=len(nbr_edges)
                fh.write(make_str(s)+delimiter+"%i\n"%(deg))
                for u,d in nbr_edges:
                    if d is None:    
                        fh.write(make_str(u)+'\n')
                    else:   
                        fh.write(make_str(u)+delimiter+make_str(d)+"\n")
        else: # directed single edges
            for s,nbrs in G.adjacency_iter():
                deg=len(nbrs)
                fh.write(make_str(s)+delimiter+"%i\n"%(deg))
                for u,d in nbrs.iteritems():
                    if d is None:    
                        fh.write(make_str(u)+'\n')
                    else:   
                        fh.write(make_str(u)+delimiter+make_str(d)+"\n")
    else: # undirected
        if G.is_multigraph():
            seen=set()  # helper dict used to avoid duplicate edges
            for s,nbrs in G.adjacency_iter():
                nbr_edges=[ (u,data) 
                            for u,datadict in nbrs.iteritems() 
                            if u not in seen
                            for key,data in datadict.items()]
                deg=len(nbr_edges)
                fh.write(make_str(s)+delimiter+"%i\n"%(deg))
                for u,d in nbr_edges:
                    if d is None:    
                        fh.write(make_str(u)+'\n')
                    else:   
                        fh.write(make_str(u)+delimiter+make_str(d)+"\n")
                seen.add(s)
        else: # undirected single edges
            seen=set()  # helper dict used to avoid duplicate edges
            for s,nbrs in G.adjacency_iter():
                nbr_edges=[ (u,d) for u,d in nbrs.iteritems() if u not in seen]
                deg=len(nbr_edges)
                fh.write(make_str(s)+delimiter+"%i\n"%(deg))
                for u,d in nbr_edges:
                    if d is None:    
                        fh.write(make_str(u)+'\n')
                    else:   
                        fh.write(make_str(u)+delimiter+make_str(d)+"\n")
                seen.add(s)
            
def read_multiline_adjlist(path, comments="#", delimiter=' ',
                           create_using=None,
                           nodetype=None, edgetype=None):
    """Read graph in multi-line adjacency list format from path.

    Examples
    --------

    >>> G=nx.path_graph(4)
    >>> nx.write_multiline_adjlist(G,"test.adjlist")
    >>> G=nx.read_multiline_adjlist("test.adjlist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("test.adjlist")
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

    Reading the file will use the default text encoding on your system.
    It is possible to read files with other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> import codecs
    >>> fh=codecs.open("test.adjlist",'r',encoding='utf=8') # utf-8 encoding
    >>> G=nx.read_multiline_adjlist(fh)
    """
    try:
        from ast import literal_eval 
    except:
        literal_eval=eval
        pass # use potentially unsafe built-in eval 

    if create_using is None:
        G=nx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    inp=_get_fh(path)        

    for line in inp:
        p=line.find(comments)
        if p>=0:
            line = line[:line.find(comments)]
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
                    line = inp.next()
                except StopIteration:
                    msg = "Failed to find neighbor for node (%s)" % (u,)
                    raise TypeError(msg)
                p=line.find(comments)
                if p>=0:
                    line = line[:line.find(comments)]
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
                    raise \
                        TypeError("Failed to convert node (%s) to type %s"\
                                       %(v,nodetype))
            if edgetype is not None:
                try:
                    edgedata={'weight':edgetype(data)}
                except:
                    raise TypeError("Failed to convert edge data (%s) to type %s"\
                                    %(data, edgetype))
            else:
                try: # try to evaluate 
                    edgedata=literal_eval(data)
                except:
                    edgedata={}
            G.add_edge(u,v,**edgedata)  

    return G


def write_adjlist(G, path, comments="#", delimiter=' '):
    """Write graph G in single-line adjacency-list format to path.

    See read_adjlist for file format details.

    Examples
    --------

    >>> G=nx.path_graph(4)
    >>> nx.write_adjlist(G,"test.adjlist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("test.adjlist",'w')
    >>> nx.write_adjlist(G, fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_adjlist(G, "test.adjlist.gz")

    The file will use the default text encoding on your system.
    It is possible to write files in other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> import codecs

    fh=codecs.open("test.adjlist",encoding='utf=8') # use utf-8 encoding
    nx.write_adjlist(G,fh)

    Does not handle edge data. 
    Use 'write_edgelist' or 'write_multiline_adjlist'
    """
    import sys
    import time
    fh=_get_fh(path,mode='w')        
    pargs=comments+" ".join(sys.argv)
    fh.write("%s\n" % (pargs))
    fh.write(comments+" GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write(comments+" %s\n" % (G.name))

    def make_str(t):
        if is_string_like(t): return t
        return str(t)
    directed=G.is_directed()

    seen=set()
    for s,nbrs in G.adjacency_iter():
        fh.write(make_str(s)+delimiter)
        for t,data in nbrs.iteritems():
            if not directed and t in seen: 
                continue
            if G.is_multigraph():
                for d in data.values():
                    fh.write(make_str(t)+delimiter)
            else:
                fh.write(make_str(t)+delimiter)
        fh.write("\n")            
        if not directed: 
            seen.add(s)


def read_adjlist(path, comments="#", delimiter=' ',
                 create_using=None, nodetype=None):
    """Read graph in single line adjacency list format from path.

    Examples
    --------

    >>> G=nx.path_graph(4)
    >>> nx.write_adjlist(G, "test.adjlist")
    >>> G=nx.read_adjlist("test.adjlist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("test.adjlist")
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
    if create_using is None:
        G=nx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    fh=_get_fh(path)        

    for line in fh.readlines():
        p=line.find(comments)
        if p>=0:
            line = line[:line.find(comments)]
        if not len(line): continue
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
        for v in vlist:
            G.add_edge(u,v)
    return G


