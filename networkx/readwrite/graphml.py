"""
*******
GraphML
*******

Read and write graphs in GraphML format.
http://graphml.graphdrawing.org/

The module currently supports simple graphs and not nested graphs or
hypergraphs.


"""
# Original author: D. Eppstein, UC Irvine, August 12, 2003.
# The original code at http://www.ics.uci.edu/~eppstein/PADS/ is public domain.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['write_graphml', 'read_graphml', 'parse_graphml']

import networkx as nx
from networkx.exception import NetworkXException, NetworkXError
from networkx.utils import _get_fh, is_string_like

def write_graphml(G, path, encoding='utf-8'):
    """Write graph G in GraphML format to path.

    This implementation supports attributes for nodes and edges,
    with the limitation that it is assumed that all nodes (or all
    edges) have the same attributes and types.

    Parameters
    ----------
    G : graph
       A networkx graph
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_graphml(G, "test.graphml")
    """
    from xml.dom.minidom import Document

    def make_str(t):
        if is_string_like(t): return t
        return str(t)

    def new_element(name, parent):
        el = doc.createElement(name)
        parent.appendChild(el)
        return el

    def graphml_datatype(val):
        if val is None:
            return "string"
        if is_string_like(val):
            return "string"
        if type(val) == type(1):
            return "int"
        if type(val) == type(1.0):
            return "double"
        if type(val) == type(True):
            return "boolean"
        if type(val) == type(1L):
            return "long"


    def new_key(id, type, whatfor, parent):
        key = new_element("key", parent)
        key.setAttribute("id", id)
        key.setAttribute("for", whatfor)
        key.setAttribute("attr.name", id)
        key.setAttribute("attr.type", type)
        return key

    fh = _get_fh(path, mode='w')

    doc = Document()
    root = doc.createElement("graphml")
    doc.appendChild(root)
    root.setAttribute("xmlns", "http://graphml.graphdrawing.org/xmlns")

    # Create `key` elements for all node and edge attributes.
    # We assume that the first node/edge has all the available attributes:
    # it would probably be too expensive to loop over all nodes/edges.
    nodekeys = {}
    try:
        for k, v in G.node[G.nodes()[0]].items():
            nodekeys[k] = graphml_datatype(v)
    except:
        pass
    for k, v in nodekeys.items():
        new_key(k, v, "node", root)

    # set up edge key elements
    # use dictionary keys if edge data is a dictionary
    # else use "data" as the key and the edge data as value        
    edgekeys = {}
    d = G.edges(data=True)[0][2] # data of first edge
    if type(d) == type({}):
        for k,v in d.items():
            edgekeys[k] = graphml_datatype(v)
    else:
        edgekeys['data'] = graphml_datatype(d)
    for k,v in edgekeys.items():
        new_key(k, v, "edge", root)

    # Create actual network description
    graph = new_element("graph", root)
    graph.setAttribute("id", G.name)
    if G.is_directed():
        graph.setAttribute("edgedefault", "directed")
    else:
        graph.setAttribute("edgedefault", "undirected")
    for n in G:
        node = new_element("node", graph)
        node.setAttribute("id", make_str(n))
        for key in nodekeys:
            data = new_element("data", node)
            data.setAttribute("key", key)
            data.appendChild(doc.createTextNode(make_str(G.node[n][key])))
    for (u,v,d) in G.edges(data=True):
        edge = new_element("edge", graph)
        edge.setAttribute("source", make_str(u))
        edge.setAttribute("target", make_str(v))
        for k, v in d.items():
            data = new_element("data", edge)
            data.setAttribute("key", k)
            data.appendChild(doc.createTextNode(make_str(v)))
    
    fh.write(doc.toprettyxml(encoding=encoding))
    fh.close()

def read_graphml(path):
    """Read graph in GraphML format from path.

    Returns a Graph or DiGraph.

    Does not implement full GraphML specification.


    """
    fh=_get_fh(path,mode='r')        
    G=parse_graphml(fh)
    return G
	
def parse_graphml(lines):
    """Read graph in GraphML format from string.

    Returns a Graph or DiGraph.

    Does not implement full GraphML specification.
    """
	
    import xml.parsers.expat

    context = []
    G=nx.MultiDiGraph()
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
            G.add_edge(attrs['source'], attrs['target'],key=attrs.get('id'))
            # no mixed graphs in NetworkX
            # handle mixed graphs by adding two directed
            # edges for an undirected edge in a directed graph 
            if attrs.get('directed')=='false':
                if defaultDirected[0]:
                    G.add_edge(attrs['target'], attrs['source'],key=attrs.get('id'))
		
    def end_element(name):
        context.pop()

    p = xml.parsers.expat.ParserCreate()
    p.returns_unicode=True
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    for line in lines:
        p.Parse(line)
    p.Parse("", 1)

    if defaultDirected[0]:
        return G
    else:
        return nx.MultiGraph(G)

