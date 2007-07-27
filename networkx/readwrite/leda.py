"""
Read graphs in LEDA format.
See http://www.algorithmic-solutions.info/leda_guide/graphs/leda_native_graph_fileformat.html

"""
# Original author: D. Eppstein, UC Irvine, August 12, 2003.
# The original code at http://www.ics.uci.edu/~eppstein/PADS/ is public domain.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = """"""
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2004-2007 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx
from networkx.exception import NetworkXException, NetworkXError
from networkx.utils import _get_fh, is_string_like
	
def read_leda(path):
    """Read graph in GraphML format from path.
    Returns an XGraph or XDiGraph."""
    fh=_get_fh(path,mode='r')        
    G=parse_leda(fh)
    return G
	
def parse_leda(lines):
    """Parse LEDA.GRAPH format from string or iterable.
    Returns an XGraph or XDiGraph."""
    if is_string_like(lines): lines=iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines \
            if not (line.startswith('#') or line.startswith('\n') or line=='')])
    for i in range(3):
        lines.next()
    # Graph
    du = int(lines.next())	# -1 directed, -2 undirected
    if du==-1:
        G = networkx.XDiGraph()
    else:
        G = networkx.XGraph()
        
    # Nodes
    n =int(lines.next())	# number of vertices
    node={}
    for i in range(1,n+1):  # LEDA counts from 1 to n
        symbol=lines.next()[2:-3]  # strip out data from |{data}|
        if symbol=="": symbol=str(i) # use int if no label - could be trouble
        node[i]=symbol

    G.add_nodes_from([s for i,s in node.items()])
	
    # Edges
    m = int(lines.next())	# number of edges
    for i in range(m):
        try:
            s,t,reversal,label=lines.next().split()
        except:
            raise NetworkXError,\
                  'Too few fields in LEDA.GRAPH edge %d' % (i+1)
        # BEWARE: no handling of reversal edges
        G.add_edge(node[int(s)],node[int(t)],label[2:-2])
    return G


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/readwrite/leda.txt',
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
