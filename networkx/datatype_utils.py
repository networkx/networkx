"""
*********
Utilities
*********

Helpers for NetworkX.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import random

### some cookbook stuff

# used in deciding whether something is a bunch of nodes, edges, etc.
# see G.add_nodes and others in Graph Class in networkx/base.py
def is_singleton(obj):
    """Is string_like or not iterable."""
    return hasattr(obj,"capitalize") or not hasattr(obj,"__iter__")

def is_string_like(obj): # from John Hunter, types-free version
    """Check if obj is string."""
#    if hasattr(obj, 'shape'): return False # this is a workaround
                                       # for a bug in numeric<23.1
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True

 
def iterable(obj):
    """ Return True if obj is iterable with a well-defined len()"""
    if hasattr(obj,"__iter__"): return True
    try:
        len(obj)
    except:
        return False
    return True

def flatten(obj, result=None):
    """ Return flattened version of (possibly nested) iterable object. """
    if not iterable(obj) or is_string_like(obj):
        return obj
    if result is None:
        result = []
    for item in obj:
        if not iterable(item) or is_string_like(item):
            result.append(item)
        else:
            flatten(item, result)
    return obj.__class__(result)

def is_list_of_ints( intlist ):
    """ Return True if list is a list of ints. """
    if not isinstance(intlist,list): return False
    for i in intlist:
        if not isinstance(i,int): return False
    return True

def _get_fh(path, mode='r'):
    """ Return a file handle for given path.

    Path can be a string or a file handle.

    Attempt to uncompress/compress files ending in '.gz' and '.bz2'.

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
    elif hasattr(path, 'read'):
        fh = path
    else:
        raise ValueError('path must be a string or file handle')
    return fh


