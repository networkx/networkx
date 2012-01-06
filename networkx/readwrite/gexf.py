"""
****
GEXF
****
Read and write graphs in GEXF format.

GEXF (Graph Exchange XML Format) is a language for describing complex
network structures, their associated data and dynamics.

This implementation does not support mixed graphs (directed and
unidirected edges together).

Format
------
GEXF is an XML format.  See http://gexf.net/format/schema.html for the
specification and http://gexf.net/format/basic.html for examples.
"""
# Based on GraphML NetworkX GraphML reader
import itertools
import networkx as nx
from networkx.utils import open_file, make_str
try:
    from xml.etree.cElementTree import Element, ElementTree, tostring
except ImportError:
    try:
        from xml.etree.ElementTree import Element, ElementTree, tostring
    except ImportError:
        pass
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)'])
__all__ = ['write_gexf', 'read_gexf', 'relabel_gexf_graph', 'generate_gexf']


@open_file(1,mode='wb')
def write_gexf(G, path, encoding='utf-8',prettyprint=True,version='1.1draft'):
    """Write G in GEXF format to path.

    "GEXF (Graph Exchange XML Format) is a language for describing
    complex networks structures, their associated data and dynamics" [1]_.

    Parameters
    ----------
    G : graph
       A NetworkX graph
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
    >>> nx.write_gexf(G, "test.gexf")

    Notes
    -----
    This implementation does not support mixed graphs (directed and unidirected
    edges together).

    The node id attribute is set to be the string of the node label.
    If you want to specify an id use set it as node data, e.g.
    node['a']['id']=1 to set the id of node 'a' to 1.

    References
    ----------
    .. [1] GEXF graph format, http://gexf.net/format/
    """
    writer = GEXFWriter(encoding=encoding,prettyprint=prettyprint,
                        version=version)
    writer.add_graph(G)
    writer.write(path)

def generate_gexf(G, encoding='utf-8',prettyprint=True,version='1.1draft'):
    """Generate lines of GEXF format representation of G"

    "GEXF (Graph Exchange XML Format) is a language for describing
    complex networks structures, their associated data and dynamics" [1]_.

    Parameters
    ----------
    G : graph
       A NetworkX graph
    encoding : string (optional)
       Encoding for text data.
    prettyprint : bool (optional)
       If True use line breaks and indenting in output XML.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> linefeed=chr(10) # linefeed=\n
    >>> s=linefeed.join(nx.generate_gexf(G))  # doctest: +SKIP
    >>> for line in nx.generate_gexf(G):  # doctest: +SKIP
    ...    print line

    Notes
    -----
    This implementation does not support mixed graphs (directed and unidirected
    edges together).

    The node id attribute is set to be the string of the node label.
    If you want to specify an id use set it as node data, e.g.
    node['a']['id']=1 to set the id of node 'a' to 1.

    References
    ----------
    .. [1] GEXF graph format, http://gexf.net/format/
    """
    writer = GEXFWriter(encoding=encoding,prettyprint=prettyprint,
                        version=version)
    writer.add_graph(G)
    for line in str(writer).splitlines():
        yield line

@open_file(0,mode='rb')
def read_gexf(path,node_type=str,relabel=False,version='1.1draft'):
    """Read graph in GEXF format from path.

    "GEXF (Graph Exchange XML Format) is a language for describing
    complex networks structures, their associated data and dynamics" [1]_.

    Parameters
    ----------
    path : file or string
       File or filename to write.
       Filenames ending in .gz or .bz2 will be compressed.

    node_type: Python type (default: str)
       Convert node ids to this type

    relabel : bool (default: False)
       If True relabel the nodes to use the GEXF node "label" attribute
       instead of the node "id" attribute as the NetworkX node label.

    Returns
    -------
    graph: NetworkX graph
        If no parallel edges are found a Graph or DiGraph is returned.
        Otherwise a MultiGraph or MultiDiGraph is returned.

    Notes
    -----
    This implementation does not support mixed graphs (directed and unidirected
    edges together).

    References
    ----------
    .. [1] GEXF graph format, http://gexf.net/format/
    """
    reader = GEXFReader(node_type=node_type,version=version)
    if relabel:
        G=relabel_gexf_graph(reader(path))
    else:
        G=reader(path)
    return G

class GEXF(object):
#    global register_namespace

    versions={}
    d={'NS_GEXF':"http://www.gexf.net/1.1draft",
       'NS_VIZ':"http://www.gexf.net/1.1draft/viz",
       'NS_XSI':"http://www.w3.org/2001/XMLSchema-instance",
       'SCHEMALOCATION':' '.join(['http://www.gexf.net/1.1draft',
                                'http://www.gexf.net/1.1draft/gexf.xsd'
                                ]),
       'VERSION':'1.1'
       }
    versions['1.1draft']=d
    d={'NS_GEXF':"http://www.gexf.net/1.2draft",
       'NS_VIZ':"http://www.gexf.net/1.2draft/viz",
       'NS_XSI':"http://www.w3.org/2001/XMLSchema-instance",
       'SCHEMALOCATION':' '.join(['http://www.gexf.net/1.2draft',
                                'http://www.gexf.net/1.2draft/gexf.xsd'
                                ]),
       'VERSION':'1.2'
       }
    versions['1.2draft']=d


    types=[(int,"integer"),
           (float,"float"),
           (float,"double"),
           (bool,"boolean"),
           (list,"string"),
           (dict,"string"),
           ]

    try: # Python 3.x
        blurb = chr(1245) # just to trigger the exception
        types.extend([
           (str,"liststring"),
           (str,"anyURI"),
           (str,"string")])
    except ValueError: # Python 2.6+
        types.extend([
           (str,"liststring"),
           (str,"anyURI"),
           (str,"string"),
           (unicode,"liststring"),
           (unicode,"anyURI"),
           (unicode,"string")])

    xml_type = dict(types)
    python_type = dict(reversed(a) for a in types)
    convert_bool={'true':True,'false':False}

#    try:
#        register_namespace = ET.register_namespace
#    except AttributeError:
#        def register_namespace(prefix, uri):
#            ET._namespace_map[uri] = prefix


    def set_version(self,version):
        d=self.versions.get(version)
        if d is None:
            raise nx.NetworkXError('Unknown GEXF version %s'%version)
        self.NS_GEXF = d['NS_GEXF']
        self.NS_VIZ = d['NS_VIZ']
        self.NS_XSI = d['NS_XSI']
        self.SCHEMALOCATION = d['NS_XSI']
        self.VERSION=d['VERSION']
        self.version=version

#        register_namespace('viz', d['NS_VIZ'])


class GEXFWriter(GEXF):
    # class for writing GEXF format files
    # use write_gexf() function
    def __init__(self, graph=None, encoding="utf-8",
                 mode='static',prettyprint=True,
                 version='1.1draft'):
        try:
            import xml.etree.ElementTree
        except ImportError:
             raise ImportError('GEXF writer requires '
                               'xml.elementtree.ElementTree')
        self.prettyprint=prettyprint
        self.mode=mode
        self.encoding = encoding
        self.set_version(version)
        self.xml = Element("gexf",
                           {'xmlns':self.NS_GEXF,
                            'xmlns:xsi':self.NS_XSI,
                            'xmlns:viz':self.NS_VIZ,
                            'xsi:schemaLocation':self.SCHEMALOCATION,
                            'version':self.VERSION})

        # counters for edge and attribute identifiers
        self.edge_id=itertools.count()
        self.attr_id=itertools.count()
        # default attributes are stored in dictionaries
        self.attr={}
        self.attr['node']={}
        self.attr['edge']={}
        self.attr['node']['dynamic']={}
        self.attr['node']['static']={}
        self.attr['edge']['dynamic']={}
        self.attr['edge']['static']={}

        if graph is not None:
            self.add_graph(graph)

    def __str__(self):
        if self.prettyprint:
            self.indent(self.xml)
        s=tostring(self.xml).decode(self.encoding)
        return s

    def add_graph(self, G):
        # Add a graph element to the XML
        if G.is_directed():
            default='directed'
        else:
            default='undirected'
        graph_element = Element("graph",defaultedgetype=default,mode=self.mode)
        self.graph_element=graph_element
        self.add_nodes(G,graph_element)
        self.add_edges(G,graph_element)
        self.xml.append(graph_element)


    def add_nodes(self, G, graph_element):
        nodes_element = Element('nodes')
        for node,data in G.nodes_iter(data=True):
            node_data=data.copy()
            node_id = make_str(node_data.pop('id', node))
            kw={'id':node_id}
            label = make_str(node_data.pop('label', node))
            kw['label']=label
            try:
                pid=node_data.pop('pid')
                kw['pid'] = make_str(pid)
            except KeyError:
                pass

            # add node element with attributes
            node_element = Element("node", **kw)

            # add node element and attr subelements
            default=G.graph.get('node_default',{})
            node_data=self.add_parents(node_element, node_data)
            if self.version=='1.1':
                node_data=self.add_slices(node_element, node_data)
            else:
                node_data=self.add_spells(node_element, node_data)
            node_data=self.add_viz(node_element,node_data)
            node_data=self.add_attributes("node", node_element,
                                          node_data, default)
            nodes_element.append(node_element)
        graph_element.append(nodes_element)


    def add_edges(self, G, graph_element):
        def edge_key_data(G):
            # helper function to unify multigraph and graph edge iterator
            if G.is_multigraph():
                for u,v,key,data in G.edges_iter(data=True,keys=True):
                    edge_data=data.copy()
                    edge_data.update(key=key)
                    edge_id=edge_data.pop('id',None)
                    if edge_id is None:
                        edge_id=next(self.edge_id)
                    yield u,v,edge_id,edge_data
            else:
                for u,v,data in G.edges_iter(data=True):
                    edge_data=data.copy()
                    edge_id=edge_data.pop('id',None)
                    if edge_id is None:
                        edge_id=next(self.edge_id)
                    yield u,v,edge_id,edge_data

        edges_element = Element('edges')
        for u,v,key,edge_data in edge_key_data(G):
            kw={'id':make_str(key)}
            try:
                edge_weight=edge_data.pop('weight')
                kw['weight']=make_str(edge_weight)
            except KeyError:
                pass
            try:
                edge_type=edge_data.pop('type')
                kw['type']=make_str(edge_type)
            except KeyError:
                pass
            edge_element = Element("edge",
                                   source=make_str(u),target=make_str(v),
                                   **kw)
            default=G.graph.get('edge_default',{})
            edge_data=self.add_viz(edge_element,edge_data)
            edge_data=self.add_attributes("edge", edge_element,
                                          edge_data, default)
            edges_element.append(edge_element)
        graph_element.append(edges_element)


    def add_attributes(self, node_or_edge, xml_obj, data, default):
        # Add attrvalues to node or edge
        attvalues=Element('attvalues')
        if len(data)==0:
            return data
        if 'start' in data or 'end' in data:
            mode='dynamic'
        else:
            mode='static'
        for k,v in data.items():
            # rename generic multigraph key to avoid any name conflict
            if k == 'key':
                k='networkx_key'
            attr_id = self.get_attr_id(make_str(k), self.xml_type[type(v)],
                                       node_or_edge, default, mode)
            if type(v)==list:
                # dynamic data
                for val,start,end in v:
                    e=Element("attvalue")
                    e.attrib['for']=attr_id
                    e.attrib['value']=make_str(val)
                    e.attrib['start']=make_str(start)
                    e.attrib['end']=make_str(end)
                    attvalues.append(e)
            else:
                # static data
                e=Element("attvalue")
                e.attrib['for']=attr_id
                e.attrib['value']=make_str(v)
                attvalues.append(e)
        xml_obj.append(attvalues)
        return data

    def get_attr_id(self, title, attr_type, edge_or_node, default, mode):
        # find the id of the attribute or generate a new id
        try:
            return self.attr[edge_or_node][mode][title]
        except KeyError:
            # generate new id
            new_id=str(next(self.attr_id))
            self.attr[edge_or_node][mode][title] = new_id
            attr_kwargs = {"id":new_id, "title":title, "type":attr_type}
            attribute=Element("attribute",**attr_kwargs)
            # add subelement for data default value if present
            default_title=default.get(title)
            if default_title is not None:
                default_element=Element("default")
                default_element.text=make_str(default_title)
                attribute.append(default_element)
            # new insert it into the XML
            attributes_element=None
            for a in self.graph_element.findall("attributes"):
                # find existing attributes element by class and mode
                a_class=a.get('class')
                a_mode=a.get('mode','static') # default mode is static
                if a_class==edge_or_node and a_mode==mode:
                    attributes_element=a
            if attributes_element is None:
                # create new attributes element
                attr_kwargs = {"mode":mode,"class":edge_or_node}
                attributes_element=Element('attributes', **attr_kwargs)
                self.graph_element.insert(0,attributes_element)
            attributes_element.append(attribute)
        return new_id


    def add_viz(self,element,node_data):
        viz=node_data.pop('viz',False)
        if viz:
            color=viz.get('color')
            if color is not None:
                if self.VERSION=='1.1':
                    e=Element("{%s}color"%self.NS_VIZ,
                              r=str(color.get('r')),
                              g=str(color.get('g')),
                              b=str(color.get('b')),
                              )
                else:
                    e=Element("{%s}color"%self.NS_VIZ,
                              r=str(color.get('r')),
                              g=str(color.get('g')),
                              b=str(color.get('b')),
                              a=str(color.get('a')),
                              )
                element.append(e)

            size=viz.get('size')
            if size is not None:
                e=Element("{%s}size"%self.NS_VIZ,value=str(size))
                element.append(e)

            thickness=viz.get('thickness')
            if thickness is not None:
                e=Element("{%s}thickness"%self.NS_VIZ,value=str(thickness))
                element.append(e)

            shape=viz.get('shape')
            if shape is not None:
                if shape.startswith('http'):
                    e=Element("{%s}shape"%self.NS_VIZ,
                              value='image',uri=str(shape))
                else:
                    e=Element("{%s}shape"%self.NS_VIZ,value=str(shape.get))
                element.append(e)

            position=viz.get('position')
            if position is not None:
                e=Element("{%s}position"%self.NS_VIZ,
                          x=str(position.get('x')),
                          y=str(position.get('y')),
                          z=str(position.get('z')),
                          )
                element.append(e)
        return node_data

    def add_parents(self,node_element,node_data):
        parents=node_data.pop('parents',False)
        if parents:
            parents_element=Element('parents')
            for p in parents:
                e=Element('parent')
                e.attrib['for']=str(p)
                parents_element.append(e)
            node_element.append(parents_element)
        return node_data

    def add_slices(self,node_element,node_data):
        slices=node_data.pop('slices',False)
        if slices:
            slices_element=Element('slices')
            for start,end in slices:
                e=Element('slice',start=str(start),end=str(end))
                slices_element.append(e)
            node_element.append(slices_element)
        return node_data


    def add_spells(self,node_element,node_data):
        spells=node_data.pop('spells',False)
        if spells:
            spells_element=Element('spells')
            for start,end in spells:
                e=Element('spell',start=str(start),end=str(end))
                spells_element.append(e)
            node_element.append(spells_element)
        return node_data


    def write(self, fh):
        # Serialize graph G in GEXF to the open fh
        if self.prettyprint:
            self.indent(self.xml)
        document = ElementTree(self.xml)
        header='<?xml version="1.0" encoding="%s"?>'%self.encoding
        fh.write(header.encode(self.encoding))
        document.write(fh, encoding=self.encoding)


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


class GEXFReader(GEXF):
    # Class to read GEXF format files
    # use read_gexf() function
    def __init__(self, node_type=None,version='1.1draft'):
        try:
            import xml.etree.ElementTree
        except ImportError:
             raise ImportError('GEXF reader requires '
                               'xml.elementtree.ElementTree')
        self.node_type=node_type
        # assume simple graph and test for multigraph on read
        self.simple_graph=True
        self.set_version(version)

    def __call__(self, stream):
        self.xml = ElementTree(file=stream)
        g=self.xml.find("{%s}graph" % self.NS_GEXF)
        if g is not None:
            return self.make_graph(g)
        # try all the versions
        for version in self.versions:
            self.set_version(version)
            g=self.xml.find("{%s}graph" % self.NS_GEXF)
            if g is not None:
                return self.make_graph(g)
        raise nx.NetworkXError("No <graph> element in GEXF file")


    def make_graph(self, graph_xml):
        # mode is "static" or "dynamic"
        graph_mode = graph_xml.get("mode", "")
        self.dynamic=(graph_mode=='dynamic')

        # start with empty DiGraph or MultiDiGraph
        edgedefault = graph_xml.get("defaultedgetype", None)
        if edgedefault=='directed':
            G=nx.MultiDiGraph()
        else:
            G=nx.MultiGraph()

        # graph attributes
        graph_start=graph_xml.get('start')
        if graph_start is not None:
            G.graph['start']=graph_start
        graph_end=graph_xml.get('end')
        if graph_end is not None:
            G.graph['end']=graph_end

        # node and edge attributes
        attributes_elements=graph_xml.findall("{%s}attributes"%self.NS_GEXF)
        # dictionaries to hold attributes and attribute defaults
        node_attr={}
        node_default={}
        edge_attr={}
        edge_default={}
        for a in attributes_elements:
            attr_class = a.get("class")
            if attr_class=='node':
                na,nd = self.find_gexf_attributes(a)
                node_attr.update(na)
                node_default.update(nd)
                G.graph['node_default']=node_default
            elif attr_class=='edge':
                ea,ed = self.find_gexf_attributes(a)
                edge_attr.update(ea)
                edge_default.update(ed)
                G.graph['edge_default']=edge_default
            else:
                raise # unknown attribute class

        # Hack to handle Gephi0.7beta bug
        # add weight attribute
        ea={'weight':{'type': 'double', 'mode': 'static', 'title': 'weight'}}
        ed={}
        edge_attr.update(ea)
        edge_default.update(ed)
        G.graph['edge_default']=edge_default

        # add nodes
        nodes_element=graph_xml.find("{%s}nodes" % self.NS_GEXF)
        if nodes_element is not None:
            for node_xml in nodes_element.findall("{%s}node" % self.NS_GEXF):
                self.add_node(G, node_xml, node_attr)

        # add edges
        edges_element=graph_xml.find("{%s}edges" % self.NS_GEXF)
        if edges_element is not None:
            for edge_xml in edges_element.findall("{%s}edge" % self.NS_GEXF):
                self.add_edge(G, edge_xml, edge_attr)

        # switch to Graph or DiGraph if no parallel edges were found.
        if self.simple_graph:
            if G.is_directed():
                G=nx.DiGraph(G)
            else:
                G=nx.Graph(G)
        return G

    def add_node(self, G, node_xml, node_attr, node_pid=None):
        # add a single node with attributes to the graph

        # get attributes and subattributues for node
        data = self.decode_attr_elements(node_attr, node_xml)
        data = self.add_parents(data, node_xml) # add any parents
        if self.version=='1.1':
            data = self.add_slices(data, node_xml)  # add slices
        else:
            data = self.add_spells(data, node_xml)  # add spells
        data = self.add_viz(data, node_xml) # add viz
        data = self.add_start_end(data, node_xml) # add start/end

        # find the node id and cast it to the appropriate type
        node_id = node_xml.get("id")
        if self.node_type is not None:
            node_id=self.node_type(node_id)

        # every node should have a label
        node_label = node_xml.get("label")
        data['label']=node_label

        # parent node id
        node_pid = node_xml.get("pid", node_pid)
        if node_pid is not None:
            data['pid']=node_pid

        # check for subnodes, recursive
        subnodes=node_xml.find("{%s}nodes" % self.NS_GEXF)
        if subnodes is not None:
            for node_xml in subnodes.findall("{%s}node" % self.NS_GEXF):
                self.add_node(G, node_xml, node_attr, node_pid=node_id)

        G.add_node(node_id, data)

    def add_start_end(self, data, xml):
        # start and end times
        node_start = xml.get("start")
        if node_start is not None:
            data['start']=node_start
        node_end = xml.get("end")
        if node_end is not None:
            data['end']=node_end
        return data


    def add_viz(self, data, node_xml):
        # add viz element for node
        viz={}
        color=node_xml.find("{%s}color"%self.NS_VIZ)
        if color is not None:
            if self.VERSION=='1.1':
                viz['color']={'r':int(color.get('r')),
                              'g':int(color.get('g')),
                              'b':int(color.get('b'))}
            else:
                viz['color']={'r':int(color.get('r')),
                              'g':int(color.get('g')),
                              'b':int(color.get('b')),
                              'a':float(color.get('a')),
                              }

        size=node_xml.find("{%s}size"%self.NS_VIZ)
        if size is not None:
            viz['size']=float(size.get('value'))

        thickness=node_xml.find("{%s}thickness"%self.NS_VIZ)
        if thickness is not None:
            viz['thickness']=float(thickness.get('value'))

        shape=node_xml.find("{%s}shape"%self.NS_VIZ)
        if shape is not None:
            viz['shape']=shape.get('shape')
            if viz['shape']=='image':
                viz['shape']=shape.get('uri')

        position=node_xml.find("{%s}position"%self.NS_VIZ)
        if position is not None:
            viz['position']={'x':float(position.get('x',0)),
                             'y':float(position.get('y',0)),
                             'z':float(position.get('z',0))}

        if len(viz)>0:
            data['viz']=viz
        return data

    def add_parents(self, data, node_xml):
        parents_element=node_xml.find("{%s}parents"%self.NS_GEXF)
        if parents_element is not None:
            data['parents']=[]
            for p in parents_element.findall("{%s}parent"%self.NS_GEXF):
                parent=p.get('for')
                data['parents'].append(parent)
        return data

    def add_slices(self, data,  node_xml):
        slices_element=node_xml.find("{%s}slices"%self.NS_GEXF)
        if slices_element is not None:
            data['slices']=[]
            for s in slices_element.findall("{%s}slice"%self.NS_GEXF):
                start=s.get('start')
                end=s.get('end')
                data['slices'].append((start,end))
        return data

    def add_spells(self, data,  node_xml):
        spells_element=node_xml.find("{%s}spells"%self.NS_GEXF)
        if spells_element is not None:
            data['spells']=[]
            for s in spells_element.findall("{%s}spell"%self.NS_GEXF):
                start=s.get('start')
                end=s.get('end')
                data['spells'].append((start,end))
        return data


    def add_edge(self, G, edge_element, edge_attr):
        # add an edge to the graph

        # raise error if we find mixed directed and undirected edges
        edge_direction = edge_element.get("type")
        if G.is_directed() and edge_direction=='undirected':
            raise nx.NetworkXError(\
                "Undirected edge found in directed graph.")
        if (not G.is_directed()) and edge_direction=='directed':
            raise nx.NetworkXError(\
                "Directed edge found in undirected graph.")

        # Get source and target and recast type if required
        source = edge_element.get("source")
        target = edge_element.get("target")
        if self.node_type is not None:
            source=self.node_type(source)
            target=self.node_type(target)

        data = self.decode_attr_elements(edge_attr, edge_element)
        data = self.add_start_end(data,edge_element)

        # GEXF stores edge ids as an attribute
        # NetworkX uses them as keys in multigraphs
        # if networkx_key is not specified as an attribute
        edge_id = edge_element.get("id")
        if edge_id is not None:
            data["id"] = edge_id

        # check if there is a 'multigraph_key' and use that as edge_id
        multigraph_key = data.pop('networkx_key',None)
        if multigraph_key is not None:
            edge_id=multigraph_key

        weight = edge_element.get('weight')
        if weight is not None:
            data['weight']=float(weight)

        edge_label = edge_element.get("label")
        if edge_label is not None:
            data['label']=edge_label



        if G.has_edge(source,target):
            # seen this edge before - this is a multigraph
            self.simple_graph=False
        G.add_edge(source, target, key=edge_id, **data)
        if edge_direction=='mutual':
            G.add_edge(target, source, key=edge_id, **data)

    def decode_attr_elements(self, gexf_keys, obj_xml):
        # Use the key information to decode the attr XML
        attr = {}
        # look for outer "<attvalues>" element
        attr_element=obj_xml.find("{%s}attvalues" % self.NS_GEXF)
        if attr_element is not None:
            # loop over <attvalue> elements
            for a in attr_element.findall("{%s}attvalue" % self.NS_GEXF):
                key = a.get('for') # for is required
                try: # should be in our gexf_keys dictionary
                    title=gexf_keys[key]['title']
                except KeyError:
                    raise nx.NetworkXError("No attribute defined for=%s"%key)
                atype=gexf_keys[key]['type']
                value=a.get('value')
                if atype=='boolean':
                    value=self.convert_bool[value]
                else:
                    value=self.python_type[atype](value)
                if gexf_keys[key]['mode']=='dynamic':
                    # for dynamic graphs use list of three-tuples
                    # [(value1,start1,end1), (value2,start2,end2), etc]
                    start=a.get('start')
                    end=a.get('end')
                    if title in attr:
                        attr[title].append((value,start,end))
                    else:
                        attr[title]=[(value,start,end)]
                else:
                    # for static graphs just assign the value
                    attr[title] = value
        return attr

    def find_gexf_attributes(self, attributes_element):
        # Extract all the attributes and defaults
        attrs = {}
        defaults = {}
        mode=attributes_element.get('mode')
        for k in attributes_element.findall("{%s}attribute" % self.NS_GEXF):
            attr_id = k.get("id")
            title=k.get('title')
            atype=k.get('type')
            attrs[attr_id]={'title':title,'type':atype,'mode':mode}
            # check for the "default" subelement of key element and add
            default=k.find("{%s}default" % self.NS_GEXF)
            if default is not None:
                if atype=='boolean':
                    value=self.convert_bool[default.text]
                else:
                    value=self.python_type[atype](default.text)
                defaults[title]=value
        return attrs,defaults


def relabel_gexf_graph(G):
    """Relabel graph using "label" node keyword for node label.

    Parameters
    ----------
    G : graph
       A NetworkX graph read from GEXF data

    Returns
    -------
    H : graph
      A NetworkX graph with relabed nodes

    Notes
    -----
    This function relabels the nodes in a NetworkX graph with the
    "label" attribute.  It also handles relabeling the specific GEXF
    node attributes "parents", and "pid".
    """
    # build mapping of node labels, do some error checking
    try:
        mapping=[(u,G.node[u]['label']) for u in G]
    except KeyError:
        raise nx.NetworkXError('Failed to relabel nodes: '
                               'missing node labels found. '
                               'Use relabel=False.')
    x,y=zip(*mapping)
    if len(set(y))!=len(G):
        raise nx.NetworkXError('Failed to relabel nodes: '
                               'duplicate node labels found. '
                               'Use relabel=False.')
    mapping=dict(mapping)
    H=nx.relabel_nodes(G,mapping)
    # relabel attributes
    for n in G:
        m=mapping[n]
        H.node[m]['id']=n
        if 'pid' in H.node[m]:
            H.node[m]['pid']=mapping[G.node[n]['pid']]
        if 'parents' in H.node[m]:
            H.node[m]['parents']=[mapping[p] for p in G.node[n]['parents']]
    return H

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import xml.etree.cElementTree
    except:
        raise SkipTest("xml.etree.cElementTree not available")

# fixture for nose tests
def teardown_module(module):
    import os
    try:
        os.unlink('test.gexf')
    except:
        pass
