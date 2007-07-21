"""
Read and write NetworkX graphs.

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
__date__ = """"""
__credits__ = """"""
__revision__ = "$$"
#    Copyright (C) 2004-2007 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import cPickle 
import codecs
import locale
import string
import sys
import time

from networkx.utils import is_string_like,_get_fh
import networkx

def write_gpickle(G, path):
    """
    Write graph object in Python pickle format.

    This will preserve Python objects used as nodes or edges.

    >>> write_gpickle(G,"file.gpickle")

    See cPickle.
    
    """
    fh=_get_fh(path,mode='wb')        
    cPickle.dump(G,fh,cPickle.HIGHEST_PROTOCOL)

def read_gpickle(path):
    """
    Read graph object in Python pickle format

    >>> G=read_gpickle("file.gpickle")

    See cPickle.
    
    """
    fh=_get_fh(path,'rb')
    return cPickle.load(fh)

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/readwrite/gpickle.txt',
                                 package='networkx')
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
    
