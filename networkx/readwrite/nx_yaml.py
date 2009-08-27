"""
****
YAML
****

Read and write NetworkX graphs in YAML format.
See http://www.yaml.org for documentation.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_yaml', 'write_yaml']

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
          "write_yaml() requires PyYAML: http://pyyaml.org/ "
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
          "read_yaml() requires PyYAML: http://pyyaml.org/ "

    fh=_get_fh(path,mode='r')        
    return yaml.load(fh)


