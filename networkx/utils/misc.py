"""
Miscellaneous Helpers for NetworkX.

These are not imported into the base networkx namespace but
can be accessed, for example, as

>>> import networkx
>>> networkx.utils.is_string_like('spam')
True
"""
#    Copyright (C) 2004-2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import sys
import subprocess
import uuid

import networkx as nx
from networkx.external.decorator import decorator

__author__ = '\n'.join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Dan Schult(dschult@colgate.edu)',
                        'Ben Edwards(bedwards@cs.unm.edu)'])
### some cookbook stuff
# used in deciding whether something is a bunch of nodes, edges, etc.
# see G.add_nodes and others in Graph Class in networkx/base.py

def is_string_like(obj): # from John Hunter, types-free version
    """Check if obj is string."""
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True

def iterable(obj):
    """ Return True if obj is iterable with a well-defined len()."""
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

def make_str(t):
    """Return the string representation of t."""
    if is_string_like(t): return t
    return str(t)

def cumulative_sum(numbers):
    """Yield cumulative sum of numbers.

    >>> import networkx.utils as utils
    >>> list(utils.cumulative_sum([1,2,3,4]))
    [1, 3, 6, 10]
    """
    csum = 0
    for n in numbers:
        csum += n
        yield csum

def generate_unique_node():
    """ Generate a unique node label."""
    return str(uuid.uuid1())

def default_opener(filename):
    """Opens `filename` using system's default program.

    Parameters
    ----------
    filename : str
        The path of the file to be opened.

    """
    cmds = {'darwin': ['open'],
            'linux2': ['xdg-open'],
            'win32': ['cmd.exe', '/C', 'start', '']}
    cmd = cmds[sys.platform] + [filename]
    subprocess.call(cmd)


def dict_to_numpy_array(d,mapping=None):
    """Convert a dictionary of dictionaries to a 2d numpy array 
    with optional mapping."""
    try:
        import numpy 
    except ImportError:
        raise ImportError(
          "dict_to_numpy_array requires numpy : http://scipy.org/ ")
    if mapping is None:
        s=set(d.keys())
        for k,v in d.items():
            s.update(v.keys())
        mapping=dict(zip(s,range(len(s))))
    n=len(mapping)
    a = numpy.zeros((n, n))
    for k1, row in d.items():
        for k2, value in row.items():
            i=mapping[k1]
            j=mapping[k2]
            a[i,j] = value 
    return a

