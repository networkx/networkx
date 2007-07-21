"""
Read and write NetworkX graphs in YAML format.
See http://www.yaml.org for documentation.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
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

from networkx.utils import is_string_like, _get_fh
import networkx

def write_yaml(G, path, default_flow_style=False, **kwds):
    """Write graph G in YAML text format to path. 

    See http://www.yaml.org

    """
    try:
        import yaml
    except ImportError:
        raise ImportError, \
              "Import Error: not able to import yaml: http://www.yaml.org "
    fh=_get_fh(path,mode='w')        
    yaml.dump(G,fh,default_flow_style=default_flow_style,**kwds)
    

def read_yaml(path):
    """Read graph from YAML format from path.

    See http://www.yaml.org

    """
    try:
        import yaml
    except ImportError:
        raise ImportError, \
              "Import Error: not able to import yaml: http://www.yaml.org "

    fh=_get_fh(path,mode='r')        
    return yaml.load(fh)



def _test_suite():
    import doctest
    import yaml
    suite = doctest.DocFileSuite('tests/readwrite/nx_yaml.txt',package='networkx')
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
    
