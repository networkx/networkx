"""
Read and write graphs and networks.

The example undirected graph below consists of the two edges (a,b),(a,c).

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

def write_multiline_adjlist(G,path=False):
    """
    Write graph in multiline adjacency list format.

    Example multiline adjacency list file format::

     # node degree
     a 2
     b
     c
     b 1
     a
     c 1
     a

    """
    # FIXME, this won't work with parallel edges
    if path:
        try: 
            fh=open(path,'w')
        except IOError:                     
            print "The file %s cannot be created."%path
            raise
    else:
        fh=sys.stdout  # no path, write to stdout

    pargs="# "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write("# GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write("# %s\n" % (G.name))
    for v in G.nodes():
        fh.write("%s %i " %(v,G.degree(v)))
        fh.write("\n")
        for n in G.neighbors(v):
            fh.write("%s\n" %(n))


def read_multiline_adjlist(path=False, create_using=None):
    """
    Read graph in multiline adjacency list format.

    Example multiline adjacency list file format:: 

     # node degree
     a 2
     b
     c
     b 1
     a
     c 1
     a

    """
    from NX.base import Graph

    if create_using is None:
        G=Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            print "Input graph is not in NX graph format"
            raise

    if path:
        try: 
            fh=open(path,'r')
        except IOError:                     
            print "The file %s does not exist"%path
            raise
    else:
        fh=sys.stdin  # no path, read from stdin

    for line in fh.readlines():
        if line.startswith("#"):
            continue
        vlist=string.split(line)
        if len(vlist) > 1:
            u=vlist.pop(0)
            vlist.pop(0) # throw away degree
            G.add_node(u)
            continue
        v=vlist[0]
        G.add_edge(u,v)
    return G


def write_adjlist(G,path=False):
    """
    Write graph in single line adjacency list format in file path.

    If no file is given, write to standard output. 

    Example adjacency list file format:: 

     # node degree
     a b c
     b a
     c a

    """
    # FIXME, this won't work with parallel edges hack (PseudoGraph)
    # FIXME will use strings no matter what
    if path:
        try: 
            fh=open(path,'w')
        except IOError:                     
            print "The file %s cannot be created."%path
            raise
    else:
        fh=sys.stdout  # no path, write to stdout

    pargs="# "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write("# GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write("# %s\n" % (G.name))
    for v in G.nodes():
        fh.write("%s " %(v))
        for n in G.neighbors(v):
            fh.write("%s " %(n))
        fh.write("\n")            

def read_adjlist(path=False, create_using=None):
    """
    Read graph in single line adjacency list format from path.
    The default is to create a simple graph from the adjacency list.
    The optional create_using argument allows other types of graphs.

    >>> G=DiGraph()
    >>> G=read_adjlist(file, create_using=G)

    Example adjacency list file format:: 

     # node degree
     a b c
     b a
     c a
    """
    # FIXME, this won't work with parallel edges hack (PseudoGraph)
    # FIXME will use strings no matter what
    from NX.base import Graph

    if create_using is None:
        G=Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            print "Input graph is not in NX graph format"
            raise

    if path:
        try: 
            fh=open(path,'r')
        except IOError:                     
            print "The file %s does not exist"%path
            raise
    else:
        fh=sys.stdin  # no path, read from stdin

    for line in fh.readlines():
        if line.startswith("#"):
           continue
        vlist=string.split(line)
        if len(vlist)==0:  # skip blank lines
            continue
        u=vlist.pop(0)
        G.add_node(u)
        for v in vlist:
            G.add_edge(u,v)
    return G


def write_edgelist(G,path=False):
    """
    Write graph G in edgelist format on file path.

    If no file is given write to standard output.

    Example adjacency list file format:: 
 
     # node degree
     a b
     a c

    """
    if path:
        try: 
            fh=open(path,'w')
        except IOError:                     
            print "The file %s cannot be created."%path
            raise
    else:
        fh=sys.stdout  # no path, write to stdout


    pargs="# "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write("# GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write("# %s\n" % (G.name))
    for (u,v) in G.edges():
        fh.write("%s %s\n" %(u,v))

def read_edgelist(path=False, create_using=None):
    """
    Read graph in edgelist format

    Example adjacency list file format:: 

     # node degree
     a b
     a c

    """
    from NX.base import Graph

    if create_using is None:
        G=Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            print "Input graph is not in NX graph format"
            raise

    if path:
        try: 
            fh=open(path,'r')
        except IOError:                     
            print "The file %s does not exist"%path
            raise
    else:
        fh=sys.stdin  # no path, read from stdin

    for line in fh.readlines():
        if line.startswith("#"):
            continue
        if line=="\n":  # skip blank line
            continue
        (u,v)=string.split(line)
        G.add_edge(u,v)
    return G

def write_gpickle(G,path=False):
    """
    Write graph object in python pickle format
    See cPickle.
    
    """
    if path:
        try: 
            fh=open(path,'w')
        except IOError:                     
            print "The file %s cannot be created."%path
            raise
    else:
        fh=sys.stdout  # no path, read from stdin

    cPickle.dump(G,fh,cPickle.HIGHEST_PROTOCOL)

def read_gpickle(path=False):
    """
    Read graph object in python pickle format
    See cPickle.
    
    """
    if path:
        try: 
            fh=open(path,'r')
        except IOError:                     
            print "The file %s does not exist"%path
            raise
    else:
        fh=sys.stdin  # no path, read from stdin

    return cPickle.load(fh)


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/io.txt',package='NX')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
