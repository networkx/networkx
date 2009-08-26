"""
**************
Pickled Graphs
**************

Read and write NetworkX graphs as Python pickles.

Note that NetworkX graphs can contain any hashable Python object as
node (not just integers and strings).  So writing a NetworkX graph
as a text file may not always be what you want: see write_gpickle
and gread_gpickle for that case.

This module provides the following :

Python pickled format:
Useful for graphs with non text representable data.

    write_gpickle(G, path)
    read_gpickle(path)

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_gpickle', 'write_gpickle']


import codecs
import locale
import string
import sys
import time

from networkx.utils import is_string_like,_get_fh

import cPickle as pickle

def write_gpickle(G, path):
    """
    Write graph object in Python pickle format.

    This will preserve Python objects used as nodes or edges.

    G=nx.path_graph(4)
    nx.write_gpickle(G,"test.gpickle")

    See cPickle.
    
    """
    fh=_get_fh(path,mode='wb')        
    pickle.dump(G,fh,pickle.HIGHEST_PROTOCOL)
    fh.close()

def read_gpickle(path):
    """
    Read graph object in Python pickle format


    G=nx.path_graph(4)
    nx.write_gpickle(G,"test.gpickle")
    G=nx.read_gpickle("test.gpickle")

    See cPickle.
    
    """
    fh=_get_fh(path,'rb')
    return pickle.load(fh)
