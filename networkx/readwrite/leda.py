"""
Read graphs in LEDA format.
See http://www.algorithmic-solutions.info/leda_guide/graphs/leda_native_graph_fileformat.html

"""
# Original author: D. Eppstein, UC Irvine, August 12, 2003.
# The original code at http://www.ics.uci.edu/~eppstein/PADS/ is public domain.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_leda', 'parse_leda']


import networkx
from networkx.exception import NetworkXError
from networkx.utils import _get_fh, is_string_like
	
def read_leda(path,encoding='UTF-8'):
    """Read graph in GraphML format from path.

    Returns an XGraph or XDiGraph."""
    fh=_get_fh(path,mode='rb')        
    lines=(line.decode(encoding) for line in fh)
    G=parse_leda(lines)
    fh.close()
    return G


def parse_leda(lines):
    """Parse LEDA.GRAPH format from string or iterable.

    Returns an Graph or DiGraph."""
    if is_string_like(lines): lines=iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines \
            if not (line.startswith('#') or line.startswith('\n') or line=='')])
    for i in range(3):
        next(lines)
    # Graph
    du = int(next(lines))	# -1 directed, -2 undirected
    if du==-1:
        G = networkx.DiGraph()
    else:
        G = networkx.Graph()
        
    # Nodes
    n =int(next(lines))	# number of vertices
    node={}
    for i in range(1,n+1):  # LEDA counts from 1 to n
        symbol=next(lines).rstrip().strip('|{}|  ')
        if symbol=="": symbol=str(i) # use int if no label - could be trouble
        node[i]=symbol

    G.add_nodes_from([s for i,s in node.items()])
	
    # Edges
    m = int(next(lines))	# number of edges
    for i in range(m):
        try:
            s,t,reversal,label=next(lines).split()
        except:
            raise NetworkXError(\
                  'Too few fields in LEDA.GRAPH edge %d' % (i+1))
        # BEWARE: no handling of reversal edges
        G.add_edge(node[int(s)],node[int(t)],label=label[2:-2])
    return G

