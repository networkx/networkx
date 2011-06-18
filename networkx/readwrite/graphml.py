"""
*******
GraphML
*******
Read and write graphs in GraphML format.

This implementation does not support mixed graphs (directed and unidirected 
edges together), hyperedges, nested graphs, or ports. 

"GraphML is a comprehensive and easy-to-use file format for graphs. It
consists of a language core to describe the structural properties of a
graph and a flexible extension mechanism to add application-specific
data. Its main features include support of

    * directed, undirected, and mixed graphs,
    * hypergraphs,
    * hierarchical graphs,
    * graphical representations,
    * references to external data,
    * application-specific attribute data, and
    * light-weight parsers.

Unlike many other file formats for graphs, GraphML does not use a
custom syntax. Instead, it is based on XML and hence ideally suited as
a common denominator for all kinds of services generating, archiving,
or processing graphs."

http://graphml.graphdrawing.org/

Format
------
GraphML is an XML format.  See 
http://graphml.graphdrawing.org/specification.html for the specification and 
http://graphml.graphdrawing.org/primer/graphml-primer.html
for examples.
"""
__author__ = """\n""".join(['Salim Fadhley',
                            'Aric Hagberg (hagberg@lanl.gov)'
                            ])

__all__ = ['write_graphml', 'read_graphml', 'generate_graphml',
           'GraphMLWriter', 'GraphMLReader']

import networkx as nx
from networkx.utils import _get_fh, make_str
import warnings
try:
    from xml.etree.cElementTree import Element, ElementTree, tostring
except ImportError:
    try:
        from xml.etree.ElementTree import Element, ElementTree, tostring
    except ImportError:
        pass
    
def write_graphml(G, path, encoding='utf-8',prettyprint=True):
    """Write G in GraphML XML format to path

    Parameters
    ----------
    G : graph
       A networkx graph
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.
    encoding : string (optional)
       Encoding for text data.
    prettyprint : bool (optional)
       If True use line breaks and indenting in output XML.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_graphml(G, "test.graphml")

    Notes
    -----
    This implementation does not support mixed graphs (directed and unidirected 
    edges together) hyperedges, nested graphs, or ports. 
    """
    fh = _get_fh(path, mode='wb')
    writer = GraphMLWriter(encoding=encoding,prettyprint=prettyprint)
    writer.add_graph_element(G)
    writer.dump(fh)

def generate_graphml(G, encoding='utf-8',prettyprint=True):
    """Generate GraphML lines for G

    Parameters
    ----------
    G : graph
       A networkx graph
    encoding : string (optional)
       Encoding for text data.
    prettyprint : bool (optional)
       If True use line breaks and indenting in output XML.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> linefeed=chr(10) # linefeed=\n
    >>> s=linefeed.join(nx.generate_graphml(G))  # a string
    >>> for line in nx.generate_graphml(G):  # doctest: +SKIP
    ...    print(line)

    Notes
    -----
    This implementation does not support mixed graphs (directed and unidirected 
    edges together) hyperedges, nested graphs, or ports. 
    """
    writer = GraphMLWriter(encoding=encoding,prettyprint=prettyprint)
    writer.add_graph_element(G)
    for line in str(writer).splitlines():
        yield line

def read_graphml(path,node_type=str):
    """Read graph in GraphML format from path.

    Parameters
    ----------
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.

    node_type: Python type (default: str)
       Convert node ids to this type 

    Returns
    -------
    graph: NetworkX graph
        If no parallel edges are found a Graph or DiGraph is returned.
        Otherwise a MultiGraph or MultiDiGraph is returned.

    Notes
    -----
    This implementation does not support mixed graphs (directed and unidirected 
    edges together), hypergraphs, nested graphs, or ports. 
    
    For multigraphs the GraphML edge "id" will be used as the edge
    key.  If not specified then they "key" attribute will be used.  If
    there is no "key" attribute a default NetworkX multigraph edge key
    will be provided.

    Files with the yEd "yfiles" extension will can be read but the graphics
    information is discarded.

    yEd compressed files ("file.graphmlz" extension) can be read by renaming
    the file to "file.graphml.gz".

    """
    fh=_get_fh(path,mode='rb')
    reader = GraphMLReader(node_type=node_type)
    # need to check for multiple graphs
    glist=list(reader(fh))
    return glist[0]


class GraphML(object):
    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
    #xmlns:y="http://www.yworks.com/xml/graphml"
    NS_Y = "http://www.yworks.com/xml/graphml"
    SCHEMALOCATION = \
        ' '.join(['http://graphml.graphdrawing.org/xmlns',
                  'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd'])
    
    try:
        chr(12345)     # Fails on Py!=3.
        unicode = str  # Py3k's str is our unicode type
    except ValueError:
        pass

    types=((str,"yfiles"),(str,"string"), (unicode,"string"),
           (int,"int"), (int,"integer"), (float,"float"), (float,"double"),
           (bool, "boolean"))
    xml_type = dict(types)
    python_type = dict(reversed(a) for a in types)

    
class GraphMLWriter(GraphML):
    def __init__(self, graph=None, encoding="utf-8",prettyprint=True):
        try:
            import xml.etree.ElementTree
        except ImportError:
             raise ImportError('GraphML writer requires '
                               'xml.elementtree.ElementTree')
        self.prettyprint=prettyprint
        self.encoding = encoding
        self.xml = Element("graphml",
                           {'xmlns':self.NS_GRAPHML,
                            'xmlns:xsi':self.NS_XSI,
                            'xsi:schemaLocation':self.SCHEMALOCATION}
                           )
        self.keys={}

        if graph is not None:
            self.add_graph_element(graph)

    
    def __str__(self):
        if self.prettyprint:
            self.indent(self.xml)
        s=tostring(self.xml).decode(self.encoding)
        return s

    def get_key(self, name, attr_type, scope, default):
        keys_key = (name, attr_type, scope)
        try:
            return self.keys[keys_key]
        except KeyError:
            new_id = "d%i" % len(list(self.keys))
            self.keys[keys_key] = new_id
            key_kwargs = {"id":new_id,
                          "for":scope,
                          "attr.name":name, 
                          "attr.type":attr_type}
            key_element=Element("key",**key_kwargs)
            # add subelement for data default value if present
            if default is not None:
                default_element=Element("default")
                default_element.text=make_str(default)
                key_element.append(default_element)
            self.xml.insert(0,key_element)
        return new_id
    

    def add_data(self, name, element_type, value, 
                 scope="all",
                 default=None):
        """
        Make a data element for an edge or a node. Keep a log of the
        type in the keys table.
        """
        if element_type not in self.xml_type:
            raise nx.NetworkXError('GraphML writer does not support '
                                   'dict types as data values.')
        key_id = self.get_key(name, self.xml_type[element_type], scope, default)
        data_element = Element("data", key=key_id)
        data_element.text = make_str(value)
        return data_element
    
    def add_attributes(self, scope, xml_obj, data, default):
        """Appends attributes to edges or nodes.
        """
        for k,v in data.items():
            default_value=default.get(k)
            obj=self.add_data(make_str(k), type(v), make_str(v), 
                              scope=scope, default=default_value)
            xml_obj.append(obj)
            
    def add_nodes(self, G, graph_element):
        for node,data in G.nodes_iter(data=True):
            node_element = Element("node", id = make_str(node))
            default=G.graph.get('node_default',{})
            self.add_attributes("node", node_element, data, default)
            graph_element.append(node_element)

    def add_edges(self, G, graph_element):        
        if G.is_multigraph():
            for u,v,key,data in G.edges_iter(data=True,keys=True):            
                edge_element = Element("edge",source=make_str(u),
                                       target=make_str(v)) 
                default=G.graph.get('edge_default',{})
                self.add_attributes("edge", edge_element, data, default)
                self.add_attributes("edge", edge_element, 
                                    {'key':key}, default)
                graph_element.append(edge_element)                
        else:
            for u,v,data in G.edges_iter(data=True):
                edge_element = Element("edge",source=make_str(u),
                                       target=make_str(v))
                default=G.graph.get('edge_default',{})
                self.add_attributes("edge", edge_element, data, default)
                graph_element.append(edge_element)                

    def add_graph_element(self, G):
        """
        Serialize graph G in GraphML to the stream.
        """
        if G.is_directed():
            default_edge_type='directed'
        else:
            default_edge_type='undirected'
        
        graphid=G.graph.pop('id',None)
        if graphid is None:
            graph_element = Element("graph",
                                edgedefault = default_edge_type)
        else:
            graph_element = Element("graph",
                                edgedefault = default_edge_type, 
                                id=graphid)

        default={}
        data=dict((k,v) for (k,v) in  G.graph.items() 
                  if k not in ['node_default','edge_default'])
        self.add_attributes("graph", graph_element, data, default)
        self.add_nodes(G,graph_element)
        self.add_edges(G,graph_element)
        self.xml.append(graph_element)

    def add_graphs(self, graph_list):
        """
        Add many graphs to this GraphML document.
        """
        for G in graph_list:
            self.add_graph_element(G)

    def dump(self, stream):
        if self.prettyprint:
            self.indent(self.xml)
        document = ElementTree(self.xml)
        header='<?xml version="1.0" encoding="%s"?>'%self.encoding
        stream.write(header.encode(self.encoding))
        document.write(stream, encoding=self.encoding)

    def indent(self, elem, level=0):
        # in-place prettyprint formatter
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


class GraphMLReader(GraphML):
    """Read a GraphML document.  Produces NetworkX graph objects.
    """
    def __init__(self, node_type=str):
        try:
            import xml.etree.ElementTree
        except ImportError:
             raise ImportError('GraphML reader requires '
                               'xml.elementtree.ElementTree')
        self.node_type=node_type
        self.multigraph=False # assume multigraph and test for parallel edges
        
    def __call__(self, stream):
        self.xml = ElementTree(file=stream)
        (keys,defaults) = self.find_graphml_keys(self.xml)
        for g in self.xml.findall("{%s}graph" % self.NS_GRAPHML):
            yield self.make_graph(g, keys, defaults)
            
    def make_graph(self, graph_xml, graphml_keys, defaults):
        # set default graph type
        edgedefault = graph_xml.get("edgedefault", None)
        if edgedefault=='directed':
            G=nx.MultiDiGraph()
        else:
            G=nx.MultiGraph()
        # set defaults for graph attributes
        for key_id,value in defaults.items():
            key_for=graphml_keys[key_id]['for']
            name=graphml_keys[key_id]['name']
            python_type=graphml_keys[key_id]['type']
            if key_for=='node':
                G.graph['node_default']={name:python_type(value)}
            if key_for=='edge':
                G.graph['edge_default']={name:python_type(value)}
        # hyperedges are not supported
        hyperedge=graph_xml.find("{%s}hyperedge" % self.NS_GRAPHML)        
        if hyperedge is not None:
            raise nx.NetworkXError("GraphML reader does not support hyperedges")
        # add nodes
        for node_xml in graph_xml.findall("{%s}node" % self.NS_GRAPHML):        
            self.add_node(G, node_xml, graphml_keys)                            
        # add edges
        for edge_xml in graph_xml.findall("{%s}edge" % self.NS_GRAPHML):        
            self.add_edge(G, edge_xml, graphml_keys)                            
        # add graph data            
        data = self.decode_data_elements(graphml_keys, graph_xml)
        G.graph.update(data)

        # switch to Graph or DiGraph if no parallel edges were found.
        if not self.multigraph: 
            if G.is_directed():
                return nx.DiGraph(G)
            else:
                return nx.Graph(G)
        else:
            return G
            
    def add_node(self, G, node_xml, graphml_keys):
        """Add a node to the graph.
        """
        # warn on finding unsupported ports tag
        ports=node_xml.find("{%s}port" % self.NS_GRAPHML)
        if ports is not None:
            warnings.warn("GraphML port tag not supported.")
        # find the node by id and cast it to the appropriate type
        node_id = self.node_type(node_xml.get("id"))
        # get data/attributes for node
        data = self.decode_data_elements(graphml_keys, node_xml)
        G.add_node(node_id, data)
        
    def add_edge(self, G, edge_element, graphml_keys):
        """Add an edge to the graph.
        """
        # warn on finding unsupported ports tag
        ports=edge_element.find("{%s}port" % self.NS_GRAPHML)
        if ports is not None:
            warnings.warn("GraphML port tag not supported.")

        # raise error if we find mixed directed and undirected edges
        directed = edge_element.get("directed")
        if G.is_directed() and directed=='false':
            raise nx.NetworkXError(\
                "directed=false edge found in directed graph.")
        if (not G.is_directed()) and directed=='true':
            raise nx.NetworkXError(\
                "directed=true edge found in undirected graph.")

        source = self.node_type(edge_element.get("source"))
        target = self.node_type(edge_element.get("target"))
        data = self.decode_data_elements(graphml_keys, edge_element)
        # GraphML stores edge ids as an attribute
        # NetworkX uses them as keys in multigraphs too if no key
        # attribute is specified
        edge_id = edge_element.get("id")
        if edge_id:
            data["id"] = edge_id
        if G.has_edge(source,target):
            # mark this as a multigraph
            self.multigraph=True
        if edge_id is None:
            # no id specified, try using 'key' attribute as id
            edge_id=data.pop('key',None)
        G.add_edge(source, target, key=edge_id, **data)
            
    def decode_data_elements(self, graphml_keys, obj_xml):
        """Use the key information to decode the data XML if present."""
        data = {}
        for data_element in obj_xml.findall("{%s}data" % self.NS_GRAPHML): 
            key = data_element.get("key")
            try:
                data_name=graphml_keys[key]['name']
                data_type=graphml_keys[key]['type']
            except KeyError:
                raise nx.NetworkXError("Bad GraphML data: no key %s"%key)
            text=data_element.text
            # assume anything with subelements is a yfiles extension
            if text is not None and len(list(data_element))==0:
                data[data_name] = data_type(text)
            elif len(list(data_element)) > 0:
                # Assume yfiles as subelements, try to extract node_label
                node_label = data_element.find("{%s}ShapeNode/{%s}NodeLabel"% 
                                               (self.NS_Y, self.NS_Y))
                if node_label is not None:
                    data['label'] = node_label.text
                edge_label = data_element.find("{%s}PolyLineEdge/{%s}EdgeLabel"%
                                               (self.NS_Y, (self.NS_Y)))
                if edge_label is not None:
                    data['label'] = edge_label.text
        return data
            
    def find_graphml_keys(self, graph_element):
        """Extracts all the keys and key defaults from the xml.
        """
        graphml_keys = {}
        graphml_key_defaults = {}
        for k in graph_element.findall("{%s}key" % self.NS_GRAPHML):
            attr_id = k.get("id")
            attr_type=k.get('attr.type')
            attr_name=k.get("attr.name")
            if attr_type is None:
                attr_name=k.get('yfiles.type')
                attr_type='yfiles'
            if attr_name is None:
                raise nx.NetworkXError("Unknown key type in file.")
            graphml_keys[attr_id] = {
                "name":attr_name,
                "type":self.python_type[attr_type],
                "for":k.get("for")}
            # check for "default" subelement of key element
            default=k.find("{%s}default" % self.NS_GRAPHML)
            if default is not None:
                graphml_key_defaults[attr_id]=default.text
        return graphml_keys,graphml_key_defaults

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import xml.etree.ElementTree
    except:
        raise SkipTest("xml.etree.ElementTree not available")

# fixture for nose tests
def teardown_module(module):
    import os
    try:
        os.unlink('test.graphml')
    except:
        pass
