"""
Miscellaneous Helpers for NetworkX.

These are not imported into the base networkx namespace but
can be accessed, for example, as

>>> import networkx
>>> networkx.utils.is_string_like('spam')
True
"""
#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import sys
import uuid
# itertools.accumulate is only available on Python 3.2 or later.
#
# Once support for Python versions less than 3.2 is dropped, this code should
# be removed.
try:
    from itertools import accumulate
except ImportError:
    import operator

    # The code for this function is from the Python 3.5 documentation,
    # distributed under the PSF license:
    # <https://docs.python.org/3.5/library/itertools.html#itertools.accumulate>
    def accumulate(iterable, func=operator.add):
        it = iter(iterable)
        try:
            total = next(it)
        except StopIteration:
            return
        yield total
        for element in it:
            total = func(total, element)
            yield total

import networkx as nx

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

PY2 = sys.version_info[0] == 2
if PY2:
    def make_str(x):
        """Return the string representation of t."""
        if isinstance(x, unicode):
            return x
        else:
            # Note, this will not work unless x is ascii-encoded.
            # That is good, since we should be working with unicode anyway.
            # Essentially, unless we are reading a file, we demand that users
            # convert any encoded strings to unicode before using the library.
            #
            # Also, the str() is necessary to convert integers, etc.
            # unicode(3) works, but unicode(3, 'unicode-escape') wants a buffer.
            #
            return unicode(str(x), 'unicode-escape')
else:
    def make_str(x):
        """Return the string representation of t."""
        return str(x)


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
    from subprocess import call

    cmds = {'darwin': ['open'],
            'linux2': ['xdg-open'],
            'win32': ['cmd.exe', '/C', 'start', '']}
    cmd = cmds[sys.platform] + [filename]
    call(cmd)


def dict_to_numpy_array(d,mapping=None):
    """Convert a dictionary of dictionaries to a numpy array
    with optional mapping."""
    try:
        return dict_to_numpy_array2(d, mapping)
    except (AttributeError, TypeError):
        # AttributeError is when no mapping was provided and v.keys() fails.
        # TypeError is when a mapping was provided and d[k1][k2] fails.
        return dict_to_numpy_array1(d,mapping)

def dict_to_numpy_array2(d,mapping=None):
    """Convert a dictionary of dictionaries to a 2d numpy array
    with optional mapping.

    """
    import numpy
    if mapping is None:
        s=set(d.keys())
        for k,v in d.items():
            s.update(v.keys())
        mapping=dict(zip(s,range(len(s))))
    n=len(mapping)
    a = numpy.zeros((n, n))
    for k1, i in mapping.items():
        for k2, j in mapping.items():
            try:
                a[i,j]=d[k1][k2]
            except KeyError:
                pass
    return a

def dict_to_numpy_array1(d,mapping=None):
    """Convert a dictionary of numbers to a 1d numpy array
    with optional mapping.

    """
    import numpy
    if mapping is None:
        s = set(d.keys())
        mapping = dict(zip(s,range(len(s))))
    n = len(mapping)
    a = numpy.zeros(n)
    for k1,i in mapping.items():
        i = mapping[k1]
        a[i] = d[k1]
    return a
