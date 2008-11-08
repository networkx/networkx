"""
*******
GraphML
*******

Read graphs in GraphML format.
http://graphml.graphdrawing.org/

"""
# Original author: D. Eppstein, UC Irvine, August 12, 2003.
# The original code at http://www.ics.uci.edu/~eppstein/PADS/ is public domain.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2007 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

__all__ = ['read_graphml', 'parse_graphml']



import networkx
from networkx.exception import NetworkXException, NetworkXError
from networkx.utils import _get_fh
	
def read_graphml(path):
    """Read graph in GraphML format from path.
    Returns an Graph or DiGraph."""
    fh=_get_fh(path,mode='r')        
    G=parse_graphml(fh)
    return G
	
def parse_graphml(lines):
    """Read graph in GraphML format from string.
    Returns an Graph or DiGraph."""
    context = []
    G=networkx.DiGraph()
    defaultDirected = [True]
	
    def start_element(name,attrs):
        context.append(name)
        if len(context) == 1:
            if name != 'graphml':
                raise GraphFormatError, \
                      'Unrecognized outer tag "%s" in GraphML' % name
        elif len(context) == 2 and name == 'graph':
            if 'edgedefault' not in attrs:
                raise GraphFormatError, \
                      'Required attribute edgedefault missing in GraphML'
            if attrs['edgedefault'] == 'undirected':
                print "undirected"
                defaultDirected[0] = False
        elif len(context) == 3 and context[1] == 'graph' and name == 'node':
            if 'id' not in attrs:
                raise GraphFormatError, 'Anonymous node in GraphML'
            G.add_node(attrs['id'])
        elif len(context) == 3 and context[1] == 'graph' and name == 'edge':
            if 'source' not in attrs:
                raise GraphFormatError, 'Edge without source in GraphML'
            if 'target' not in attrs:
                raise GraphFormatError, 'Edge without target in GraphML'
            G.add_edge(attrs['source'], attrs['target'],attrs.get('id'))  
            # no mixed graphs in NetworkX
            # handle mixed graphs by adding two directed
            # edges for an undirected edge in a directed graph 
            if attrs.get('directed')=='false':
                if defaultDirected[0]:
                    G.add_edge(attrs['target'], attrs['source'],attrs.get('id'))
		
    def end_element(name):
        context.pop()
	
    import xml.parsers.expat
    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    for line in lines:
        p.Parse(line)
    p.Parse("", 1)

    if defaultDirected[0]:
        return G
    else:
        return networkx.Graph(G)

