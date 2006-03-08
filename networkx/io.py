"""
Read and write networkx graphs.

This module provides the following simple functions to read and write
networkx graphs:

Edgelist format:

   write_edgelist(G,path)
   read_edgelist(path, create_using=networkx.Graph(), 
                 nodetype=str, edgetype=str)

Useful for connected graphs with or without edge data.

Adjacency list with single line per node:

    write_adjlist(G,path)
    read_adjlist(path, create_using=networkx.Graph(), nodetype=str)

Useful for connected or unconnected graphs without edge data.

Adjacency list with multiple lines per node:

    write_multiline_adjlist(G,path)
    read_multiline_adjlist(path, create_using=networkx.Graph(), 
                           nodetype=str, edgetype=str)

Useful for connected or unconnected graphs with or without edge data.

Python pickled format:

    write_gpickle(G,path)
    read_gpickle(path)

Useful for graphs with non ASCII representable data.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
__date__ = "$Date: 2005-07-06 07:58:26 -0600 (Wed, 06 Jul 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1063 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import cPickle 
import string
import sys
import time

from networkx.utils import is_string_like
import networkx

def write_multiline_adjlist(G,path):
    """
    Write graph in multiline adjacency list format to path.

    path can be a filehandle or a string with the name of the file.
    Filenames ending in .gz or .bz2 will be compressed.

    Se read_multiline_adjlist for file format details.

    """
    fh=_get_fh(path,mode='w')        
    pargs="# "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write("# GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write("# %s\n" % (G.name))
    e={}  # helper dict used to avoid duplicate edges

    # is this a XGraph or XDiGraph?
    if hasattr(G,'allow_multiedges')==True:
        multiedges=G.multiedges
    else:
        multiedges=False
        
    # directed
    directed=G.is_directed()

    for s in G.nodes():
        neighbors=[(t,d) for (t,d) in G.neighbors(s,with_labels=True) \
                   if (t,s) not in e]
        # seen these edges
        if not directed:
            e.update(dict.fromkeys([(s,t) for (t,d) in neighbors],1)) 
        nlist=[]
        for (t,d) in neighbors:
            if d is None:
                nlist.append("%s\n" %(t))
            else:
                nlist.append("%s %s\n" %(t,d))
        fh.write("%s %i\n" %(s,len(nlist)))
        for n in nlist:
            fh.write(n)
            
def read_multiline_adjlist(path, create_using=networkx.Graph(), nodetype=str, edgetype=str):
    """Read graph in multi-line adjacency list format from path.

    path can be a filehandle or a string with the name of the file.
    Filenames ending in .gz or .bz2 will be uncompressed.

    nodetype is an optional function to map node strings to an alternate type.
    e.g., use nodemap=int to create node IDs as integers
    Since nodes must be hashable, the function nodetype
    must return hashable types (e.g. int, float, str, frozenset -
    or tuples of those, etc.) 

    edgetype is an optional function to map edge data strings to an alternate
    type. e.g. use edgetype=float to create edge data as floating point numbers

    create_using is an optional networkx graph type 

    A '# ' character at the beginning of a line indicates a comment line

    >>> import networkx as NX
    >>> G=NX.read_multiline_adjlist("file.adjlist")

    >>> fh=open("file.edgelist")
    >>> G=NX.read_multiline_adjlist(fh)

    >>> G=NX.read_multiline_edgelist("file.adjlist",create_using=NX.DiGraph())

    Example multiline adjlist file format:: 

     # source target for Graph or DiGraph
     a 2
     b
     c
     d 1
     e

    or

     # source target for XGraph or XDiGraph with edge data
     a 2
     b edge-ab-data
     c edge-ac-data
     d 1
     e edge-de-data

    """
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

    inp=_get_fh(path)        

    for line in inp:
        if line.startswith("#") or line.startswith("\n"):
            continue
        try:
            (u,deg)=string.split(line)
            deg=int(deg)
        except:
            raise "Failed to read node and degree on line (%s)"%line
        try:
            u=nodetype(u)
        except:
            raise TypeError("Failed to convert node (%s) to type %s"\
                  %(u,nodetype))
        G.add_node(nodetype(u))
        for i in range(deg):
            vlist=string.split(inp.next())
            if len(vlist)==1:
                v=vlist[0]
                d=None
            elif len(vlist)==2:
                (v,d)=vlist
            else:
                raise "Failed to read line: %s"%vlist
            try:
                v=nodetype(v)
            except:
                raise TypeError("Failed to convert node (%s) to type %s"\
                                %(v,nodetype))
            if xgraph:
                if d is not None:
                    try:
                        d=edgetype(d)
                    except:
                        raise TypeError\
                              ("Failed to convert edge data (%s) to type %s"\
                                %(d, edgetype))
                G.add_edge(u,v,d)
            else:
                G.add_edge(u,v)
                
    return G


def write_adjlist(G,path):
    """Write graph in single line adjacency list format to path.

    path can be a filehandle or a string with the name of the file.
    Filenames ending in .gz or .bz2 will be compressed.

    Does not handle data in XGraph or XDiGraph, use 'write_edgelist'
    or 'write_multiline_adjlist'

    See read_adjlist for file format details.

    """
    fh=_get_fh(path,mode='w')        
    pargs="# "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write("# GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write("# %s\n" % (G.name))
    e={}  # helper dict used to avoid duplicate edges
    try:
        multiedges=G.multiedges
    except:
        multiedges=False

    # directed
    directed=G.is_directed()

    for s in G.nodes():
        fh.write("%s " %(s))
        for t in G.neighbors(s):
            if not directed:
                if e.has_key((t,s)):
                    continue
                e.setdefault((s,t),1)
            if multiedges:
                for d in G.get_edge(s,t):
                    fh.write("%s " %(t))
            else:
                fh.write("%s " %(t))                
        fh.write("\n")            


def read_adjlist(path,create_using=networkx.Graph(),nodetype=str):
    """Read graph in single line adjacency list format from path.

    path can be a filehandle or a string with the name of the file.
    Filenames ending in .gz or .bz2 will be uncompressed.

    The default is to create a simple graph from the adjacency list.
    Does not handle edge data: use 'read_edgelist' or 'read_multiline_adjlist'

    nodetype is an optional function to map node strings to an alternate type.
    e.g., use nodemap=int to create node IDs as integers
    Since nodes must be hashable, the function nodetype
    must return hashable types (e.g. int, float, str, frozenset -
    or tuples of those, etc.) 

    edgetype is an optional function to map edge data strings to an alternate
    type. e.g. use edgetype=float to create edge data as floating point numbers

    create_using is an optional networkx graph type 

    A '# ' character at the beginning of a line indicates a comment line

    >>> import networkx as NX
    >>> G=NX.read_adjlist("file.adjlist")

    >>> fh=open("file.edgelist")
    >>> G=NX.read_adjlist(fh)

    >>> G=NX.read_edgelist("file.adjlist",create_using=NX.DiGraph())

    Example adjlist file format:: 

     # source target
     a b c
     d e

    """
    try:
        G=create_using
        G.clear()
    except:
        raise TypeError("Input graph is not a networkx graph type")

    fh=_get_fh(path)        

    for line in fh.readlines():
        if line.startswith("#") or line.startswith("\n"):
            continue
        vlist=string.split(line)
        u=vlist.pop(0)
        # convert types
        try:
            u=nodetype(u)
        except:
            raise TypeError("Failed to convert node (%s) to type %s"\
                  %(u,nodetype))
        G.add_node(u)
        try:
            vlist=map(nodetype,vlist)
        except:
            raise TypeError("Failed to convert nodes (%s) to type %s"\
                            %(','.join(vlist),nodetype))
        for v in vlist:
            G.add_edge(u,v)
    return G


def write_edgelist(G,path):
    """Write graph G in edgelist format on file path.

    path can be a filehandle or a string with the name of the file.
    Filenames ending in .gz or .bz2 will be compressed.

    See read_edgelist for file format details.

    """
    fh=_get_fh(path,mode='w')        

    pargs="# "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write("# GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write("# %s\n" % (G.name))
    for e in G.edges():
        for n in e:  # handle Graph or XGraph, two- or three-tuple
            if n is None: continue # don't write data for XGraph None 
            fh.write("%s "%n) 
        fh.write("\n")                     

def read_edgelist(path, create_using=networkx.Graph(), nodetype=str, edgetype=str):
    """Read graph in edgelist format from path

    path can be a filehandle or a string with the name of the file.
    Filenames ending in .gz or .bz2 will be uncompressed.

    nodetype is an optional function to map node strings
    to an alternate type.
    e.g., use nodemap=int to create node IDs as integers

    Since nodes must be hashable, the function nodetype
    must return hashable types (e.g. int, float, str, frozenset -
    or tuples of those, etc.) 

    edgetype is an optional function to map edge data strings
    to an alternate type. e.g. use edgetype=float to create edge
    data as floating point numbers

    create_using is an optional networkx graph type 

    A '# ' character at the line beginning indicates a comment line

    >>> import networkx as NX
    >>> G=NX.read_edgelist("file.edgelist")

    >>> fh=open("file.edgelist")
    >>> G=NX.read_edgelist(fh)

    >>> G=NX.read_edgelist("file.edgelist",create_using=NX.DiGraph())

    Example edgelist file format:: 

     # source target
     a b
     a c
     d e

    or for an XGraph() with edge data 

     # source target data
     a b 1
     a c 3.14159
     d e apple

    """
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

    fh=_get_fh(path)        


    for line in fh.readlines():
        if line.startswith("#") or line.startswith("\n"):
            continue
        # split line, should have 2 or three items
        s=string.split(line)
        if len(s)==2:
            (u,v)=s
            d=None
        elif len(s)==3:
            (u,v,d)=s
        else:
            raise "Failed to read line: %s"%line

        # convert types
        try:
            (u,v)=map(nodetype,(u,v))
        except:
            raise TypeError("Failed to convert edge (%s, %s) to type %s"\
                  %(u,v,nodetype))
        if d is not None:
            try:
               d=edgetype(d)
            except:
                raise TypeError("Failed to convert edge data (%s) to type %s"\
                                %(d, edgetype))
            
        if xgraph:
            G.add_edge(u,v,d)  # XGraph or XDiGraph
        else:
            G.add_edge(u,v)    # Graph or DiGraph
            
    return G

def write_gpickle(G,path):
    """
    Write graph object in python pickle format
    See cPickle.
    
    """
    fh=_get_fh(path,mode='w')        
    cPickle.dump(G,fh,cPickle.HIGHEST_PROTOCOL)

def read_gpickle(path):
    """
    Read graph object in python pickle format
    See cPickle.
    
    """
    fh=_get_fh(path)
    return cPickle.load(fh)

def _get_fh(path,mode='r'):
    """ Return a file handle for given path.

    Path can be a string or a file handle.

    An attempt is made to uncompress files ending in '.gz' and '.bz2'.

    """
    if is_string_like(path):
        if path.endswith('.gz'):
            import gzip
            fh = gzip.open(path,mode=mode)
        elif path.endswith('.bz2'):
            import bz2
            fh = bz2.BZ2File(path,mode=mode)
        else:
            fh = file(path,mode=mode)
    elif hasattr(path, 'seek'):
        fh = path
    else:
        raise ValueError('path must be a string or file handle')
    return fh

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/io.txt',package='networkx')
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
    
