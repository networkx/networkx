"""
*******
GraphML
*******

Read and write graphs in GraphML format.
http://graphml.graphdrawing.org/

The module currently supports multi graphs with data
but not nested graphs or hypergraphs.
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

    Returns a MultiGraph or MultiDiGraph.

    Nested graphs and multiple graphs are ignored.

    Node, edge and graph data are stored as attributes.
    The key element can specify the type for each
    attribute (string, double, etc) and defaults.
    Data using a key value that matches a key element
    is given the attribute name attr.name.
    Data whose key value doesn't match a key element
    uses key value itself as the attribute name.
    """
    fh=_get_fh(path,mode='r')
    G=parse_graphml(fh.readlines())
    return G

def parse_graphml(lines):
    """Read graph in GraphML format from string.

    Returns a MultiGraph or MultiDiGraph.

    Nested graphs and multiple graphs are ignored.

    Node, edge and graph data are stored as attributes.
    The key element can specify the type for each
    attribute (string, double, etc) and defaults.
    Data using a key value that matches a key element
    is given the attribute name attr.name.
    Data whose key value doesn't match a key element
    uses key value itself as the attribute name.
    """
    import xml.parsers.expat
    G=nx.MultiDiGraph()
    defaultDirected=[True]
    context=[]
    storage=[{}]   # Store attributes until end of element

    # default and key->name lookup dicts
    node_attr_names={}
    node_defaults={}
    edge_attr_names={}
    edge_defaults={}
    graph_attr_names={}
    graph_defaults={}

    def start_element(name, attrs):
        context.append(name)
        context_len=len(context)
        if context_len==1:
            if name != 'graphml':
                raise GraphFormatError, \
                  'Unrecognized outer tag "%s" in GraphML' % name
            storage[-1].update(attrs)
        elif context_len==2:
            if name=='graph':
                if 'edgedefault' not in attrs:
                    raise GraphFormatError, \
                          'Required attribute edgedefault missing in GraphML'
                if attrs['edgedefault'] == 'undirected':
                    defaultDirected[0] = False
                storage[-1].update(attrs)
            elif name=='key':
                storage.append(attrs)
        elif context_len==3 and context[1]=='key':
            if name=='default':
                storage.append(attrs)
        elif context_len==3 and context[1]=='graph':
            if name=='node':
                if 'id' not in attrs:
                    raise GraphFormatError, 'Anonymous node in GraphML'
                attrs.update(node_defaults)
                storage.append(attrs)
            elif name=='edge':
                if 'source' not in attrs:
                    raise GraphFormatError, 'Edge without source in GraphML'
                if 'target' not in attrs:
                    raise GraphFormatError, 'Edge without target in GraphML'
                attrs.update(edge_defaults)
                storage.append(attrs)
            elif name=='data':
                storage.append(attrs)
        elif context_len==4 and context[1]=='graph' and context[2] in ['node','edge']:
                if name=='data':
                    storage.append(attrs)

    def end_element(name):
        context_len=len(context)
        if context_len==2 and name=='key':
            assert context.pop()==name
            attrs=storage.pop()
            attr_id=attrs['id']
            attr_name=attrs['attr.name']
            attr_for=attrs['for']
            attr_type=attrs.get('attr.type','string')
            # store attribute names by id and prepare to set defaults
            if attr_for=='node':
                attr_dict=node_defaults
                node_attr_names[attr_id]=(attr_name,attr_type)
            elif attr_for=='edge':
                attr_dict=edge_defaults
                edge_attr_names[attr_id]=(attr_name,attr_type)
            elif attr_for=='graph':
                attr_dict=graph_defaults
                graph_attr_names[attr_id]=(attr_name,attr_type)
            # convert defaults values by type
            if 'default' in attrs:
                if attr_type == 'string':
                    value=attrs['default']
                elif attr_type in ['float','double']:
                    value=float(attrs['default'])
                elif attr_type in ['int','long','boolean']:
                    value=int(attrs['default'])
                attr_dict[attr_name]=value
        elif context_len==2 and name=='graph':
            assert context.pop()==name
            G.graph.update(storage[-1])
        elif context_len==3 and context[1]=='key' and name=='default':
            assert context.pop()==name
            attrs=storage.pop()
            storage[-1]['default']=attrs['chars']
        elif context_len==3 and context[1]=='graph' and name=='node':
            assert context.pop()==name
            attrs=storage.pop()
            G.add_node(attrs['id'],attrs)
        elif context_len==3 and context[1]=='graph' and name=='edge':
            assert context.pop()==name
            attrs=storage.pop()
            G.add_edge(attrs['source'],attrs['target'],\
                    key=attrs.get('id'),attr_dict=attrs)
            if defaultDirected[0] and (attrs.get('directed')=="false"):
                #Handle undirected edges in a directed graph by adding both directions
                G.add_edge(attrs['target'],attrs['source'],\
                        key=attrs.get('id'),attr_dict=attrs)
        elif context_len==3 and context[1]=='graph' and name=='data':
            assert context.pop()==name
            attrs=storage.pop()
            key=attrs['key']
            attr_name,attr_type=graph_attr_names.get(key,(key,'string'))
            if attr_type == 'string':
                value=attrs['chars']
            elif attr_type in ['float','double']:
                value=float(attrs['chars'])
            elif attr_type in ['int','long','boolean']:
                value=int(attrs['chars'])
            storage[-1][attr_name]=value
        elif context_len==4 and context[1]=='graph' and name=='data':
            assert context.pop()==name
            attrs=storage.pop()
            key=attrs['key']
            if context[2]=='node':
                attr_name,attr_type=node_attr_names.get(key,(key,'string'))
            elif context[2]=='edge':
                attr_name,attr_type=edge_attr_names.get(key,(key,'string'))
            if attr_type == 'string':
                value=attrs['chars']
            elif attr_type in ['float','double']:
                value=float(attrs['chars'])
            elif attr_type in ['int','long','boolean']:
                value=int(attrs['chars'])
            storage[-1][attr_name]=value


    def char_element(data):
        context_len=len(context)
        if (context_len==3 and context[1]=='graph' and context[2]=='data') or\
           (context_len==3 and context[1]=='key' and context[2]=='default') or\
           (context_len==4 and context[1]=='graph' and \
               context[2] in ['node','edge'] and context[3]=='data'):
            storage[-1]['chars']=data
            #print context[-1],data

    p = xml.parsers.expat.ParserCreate()
    p.returns_unicode=True
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_element

    for line in lines:
        p.Parse(line)
    p.Parse("", 1)

    if defaultDirected[0]:
        return G
    else:
        return nx.MultiGraph(G)


if __name__ == "__main__":
    fh=open("test2.graphml")
    g=parse_graphml(fh.readlines())
    print "Nodes: ",g.nodes(data=True)
    print "Edges: ",g.edges(keys=True,data=True)
    print "Nodes: ",g.nodes()
    print "Edges: ",g.edges(keys=True)
