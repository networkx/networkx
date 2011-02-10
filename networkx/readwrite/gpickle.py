"""
**************
Pickled Graphs
**************
Read and write NetworkX graphs as Python pickles.

"The pickle module implements a fundamental, but powerful algorithm
for serializing and de-serializing a Python object
structure. "Pickling" is the process whereby a Python object hierarchy
is converted into a byte stream, and "unpickling" is the inverse
operation, whereby a byte stream is converted back into an object
hierarchy." 

Note that NetworkX graphs can contain any hashable Python object as
node (not just integers and strings).  For arbitrary data types it may
be difficult to represent the data as text.  In that case using Python
pickles to store the graph data can be used.

Format
------
See http://docs.python.org/library/pickle.html
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_gpickle', 'write_gpickle']

import networkx as nx
from networkx.utils import _get_fh

try:
    import cPickle as pickle
except ImportError:
    import pickle

def write_gpickle(G, path):
    """Write graph in Python pickle format.

    Pickles are a serialized byte stream of a Python object [1]_.
    This format will preserve Python objects used as nodes or edges.

    Parameters
    ----------
    G : graph
       A NetworkX graph
    path : file or string
       File or filename to write. 
       Filenames ending in .gz or .bz2 will be compressed.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_gpickle(G,"test.gpickle")

    References
    ----------
    .. [1] http://docs.python.org/library/pickle.html
    """
    fh=_get_fh(path,mode='wb')        
    pickle.dump(G,fh,pickle.HIGHEST_PROTOCOL)
    fh.close()

def read_gpickle(path):
    """Read graph object in Python pickle format.

    Pickles are a serialized byte stream of a Python object [1]_.
    This format will preserve Python objects used as nodes or edges.

    Parameters
    ----------
    path : file or string
       File or filename to write. 
       Filenames ending in .gz or .bz2 will be uncompressed.

    Returns
    -------
    G : graph
       A NetworkX graph

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_gpickle(G,"test.gpickle")
    >>> G=nx.read_gpickle("test.gpickle")

    References
    ----------
    .. [1] http://docs.python.org/library/pickle.html
    """
    fh=_get_fh(path,'rb')
    return pickle.load(fh)

# fixture for nose tests
def teardown_module(module):
    import os
    os.unlink('test.gpickle')
