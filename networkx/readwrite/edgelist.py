"""
**********
Edge Lists
**********

Read and write NetworkX graphs as edge lists.


"""

__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

__all__ = ['read_edgelist', 'write_edgelist']

import codecs
import locale
import string
import sys
import time

from networkx.utils import is_string_like,_get_fh
import networkx


def write_edgelist(G, path, comments="#", delimiter=' '):
    """Write graph as a list of edges.

    Parameters
    ----------
    G : graph
       A networkx graph
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.
    comments : string, optional
       The character used to indicate the start of a comment 
    delimiter : string, optional
       The string uses to separate values.  The default is whitespace.


    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_edgelist(G, "test.edgelist")

    >>> fh=open("test.edgelist",'w')
    >>> nx.write_edgelist(G,fh)

    >>> nx.write_edgelist(G, "test.edgelist.gz")

    Notes
    -----
    The file will use the default text encoding on your system.
    It is possible to write files in other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> import codecs
    >>> fh=codecs.open("test.edgelist",'w',encoding='utf=8') # utf-8 encoding
    >>> nx.write_edgelist(G,fh)

    See Also
    --------
    networkx.write_edgelist


    """
    fh=_get_fh(path,mode='w')

    pargs=comments+" "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write(comments+" GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write(comments+" %s\n" % (G.name))

    def make_str(t):
        if is_string_like(t): return t
        return str(t)

    for e in G.edges(data=True):
        fh.write(delimiter.join(map(make_str,e))+"\n")
        #if G.multigraph:
        #    u,v,datalist=e
        #    for d in datalist:
        #        fh.write(delimiter.join(map(make_str,(u,v,d)))+"\n")
        #else:

def read_edgelist(path, comments="#", delimiter=' ',
                  create_using=None, nodetype=None, edgetype=None):
    """Read a graph from a list of edges.

    Parameters
    ----------
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be uncompressed.
    comments : string, optional
       The character used to indicate the start of a comment 
    delimiter : string, optional
       The string uses to separate values.  The default is whitespace.
    create_using : Graph container, optional       
       Use specified Graph container to build graph.  The default is
       nx.Graph().
    nodetype : int, float, str, Python type, optional
       Convert node data from strings to specified type
    edgetype : int, float, str, Python type, optional
       Convert edge data from strings to specified type

    Returns
    ----------
    out : graph
       A networkx Graph or other type specified with create_using

    Examples
    --------
    >>> nx.write_edgelist(nx.path_graph(4), "test.edgelist")
    >>> G=nx.read_edgelist("test.edgelist")

    >>> fh=open("test.edgelist")
    >>> G=nx.read_edgelist(fh)

    >>> G=nx.read_edgelist("test.edgelist", nodetype=int)

    >>> G=nx.read_edgelist("test.edgelist",create_using=nx.DiGraph())

    Notes
    -----
    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.) 


    Example edgelist file formats

    Without edge data::

     # source target
     a b
     a c
     d e

    With edge data::: 

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
            if nodetype is not None:
                try:
                    (u,v)=map(nodetype,s)
                except:
                    raise TypeError("Failed to convert edge %s to type %s"\
                          %(s,nodetype))
            else:
                (u,v)=s
            G.add_edge(u,v) 
        elif len(s)==3:
            (u,v,d)=s
            if nodetype is not None:
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
            G.add_edge(u,v,d)  # XGraph or XDiGraph
        else:
            raise TypeError("Failed to read line: %s"%line)
    return G

