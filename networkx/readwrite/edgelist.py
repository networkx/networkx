"""
Read and write NetworkX graphs.

Note that NetworkX graphs can contain any hashable Python object as
node (not just integers and strings).  So writing a NetworkX graph
as a text file may not always be what you want: see write_gpickle
and gread_gpickle for that case.

This module provides the following :

Edgelist format:
Useful for connected graphs with or without edge data.

   write_edgelist(G, path)
   G=read_edgelist(path)


"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
__date__ = """"""
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2004-2007 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import codecs
import locale
import string
import sys
import time

from networkx.utils import is_string_like,_get_fh
import networkx


def write_edgelist(G, path, comments="#", delimiter=' '):
    """Write graph G in edgelist format on file path.

    See read_edgelist for file format details.

    >>> write_edgelist(G, "file.edgelist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("file.edgelist")
    >>> write_edgelist(G,fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> write_edgelist(G, "file.edgelist.gz")

    The file will use the default text encoding on your system.
    It is possible to write files in other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> import codecs
    >>> fh=codecs.open("file.edgelist",encoding='utf=8') # use utf-8 encoding
    >>> write_edgelist(G,fh)


    """
    fh=_get_fh(path,mode='w')

    pargs=comments+" "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write(comments+" GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write(comments+" %s\n" % (G.name))
    for e in G.edges():
        for n in e:  # handle Graph or XGraph, two- or three-tuple
            if n is None: continue # don't write data for XGraph None 
            if is_string_like(n):
                fh.write(n+delimiter)
            else:
                fh.write(str(n)+delimiter)                         
        fh.write("\n")                     

def read_edgelist(path, comments="#", delimiter=' ',
                  create_using=None, nodetype=None, edgetype=None):
    """Read graph in edgelist format from path.

    >>> G=read_edgelist("file.edgelist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("file.edgelist")
    >>> G=read_edgelist(fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> G=read_edgelist("file.edgelist.gz")

    nodetype is an optional function to convert node strings to nodetype

    For example

    >>> G=read_edgelist("file.edgelist", nodetype=int)

    will attempt to convert all nodes to integer type

    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.) 

    create_using is an optional networkx graph type, the default is
    Graph(), a simple undirected graph 

    >>> G=read_edgelist("file.edgelist",create_using=DiGraph())


    The comments character (default='#') at the beginning of a
    line indicates a comment line.

    The entries are separated by delimiter (default=' ').
    If whitespace is significant in node or edge labels you should use
    some other delimiter such as a tab or other symbol.  

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

    fh=_get_fh(path)

    for line in fh.readlines():
        line = line[:line.find(comments)].strip()
        if not len(line): continue
#        if line.startswith("#") or line.startswith("\n"):
#            continue
#        line=line.strip() #remove trailing \n 
        # split line, should have 2 or three items
        s=line.split(delimiter)
        if len(s)==2:
            (u,v)=s
            d=None
        elif len(s)==3:
            (u,v,d)=s
        else:
            raise TypeError("Failed to read line: %s"%line)

        # convert types
        try:
            (u,v)=map(nodetype,(u,v))
        except:
            raise TypeError("Failed to convert edge (%s, %s) to type %s"\
                  %(u,v,nodetype))
        if d is not None and edgetype is not None:

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



def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/readwrite/edgelist.txt',package='networkx')
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
    
