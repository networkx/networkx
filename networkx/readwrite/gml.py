"""
Read graphs in GML format.

"GML, the G>raph Modelling Language, is our proposal for a portable
file format for graphs. GML's key features are portability, simple
syntax, extensibility and flexibility. A GML file consists of a
hierarchical key-value lists. Graphs can be annotated with arbitrary
data structures. The idea for a common file format was born at the
GD'95; this proposal is the outcome of many discussions. GML is the
standard file format in the Graphlet graph editor system. It has been
overtaken and adapted by several other systems for drawing graphs."

See http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html

Requires pyparsing: http://pyparsing.wikispaces.com/

Format
------
See http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html
for format specification.

Example graphs in GML format:
http://www-personal.umich.edu/~mejn/netdata/
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2008-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_gml', 'parse_gml', 'generate_gml', 'write_gml']

import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import is_string_like, open_file


@open_file(0,mode='rb')
def read_gml(path,encoding='UTF-8',relabel=False):
    """Read graph in GML format from path.

    Parameters
    ----------
    path : filename or filehandle
       The filename or filehandle to read from.

    encoding : string, optional
       Text encoding. 

    relabel : bool, optional       
       If True use the GML node label attribute for node names otherwise use
       the node id.  

    Returns
    -------
    G : MultiGraph or MultiDiGraph

    Raises
    ------
    ImportError
        If the pyparsing module is not available.

    See Also
    --------
    write_gml, parse_gml
    
    Notes
    -----
    Requires pyparsing: http://pyparsing.wikispaces.com/

    References
    ----------
    GML specification:
    http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_gml(G,'test.gml')
    >>> H=nx.read_gml('test.gml')
    """
    lines=(line.decode(encoding) for line in path)
    G=parse_gml(lines,relabel=relabel)
    return G

def parse_gml(lines, relabel=True):
    """Parse GML graph from a string or iterable.

    Parameters
    ----------
    lines : string or iterable
       Data in GML format.

    relabel : bool, optional       
       If True use the GML node label attribute for node names otherwise use
       the node id.

    Returns
    -------
    G : MultiGraph or MultiDiGraph

    Raises
    ------
    ImportError
        If the pyparsing module is not available.

    See Also
    --------
    write_gml, read_gml
    
    Notes
    -----
    This stores nested GML attributes as dictionaries in the 
    NetworkX graph, node, and edge attribute structures.

    Requires pyparsing: http://pyparsing.wikispaces.com/

    References
    ----------
    GML specification:
    http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html
    """
    try:
        from pyparsing import ParseException
    except ImportError:
        try:
            from matplotlib.pyparsing import ParseException
        except:
            raise ImportError('Import Error: not able to import pyparsing:', 
                              'http://pyparsing.wikispaces.com/')
    try:
        data = "".join(lines)
        gml = pyparse_gml()
        tokens =gml.parseString(data)
    except ParseException as err:
        print((err.line))
        print((" "*(err.column-1) + "^"))
        print(err)
        raise

    # function to recursively make dicts of key/value pairs
    def wrap(tok):
        listtype=type(tok)
        result={}
        for k,v in tok:
            if type(v)==listtype:
                result[str(k)]=wrap(v)
            else:
                result[str(k)]=v
        return result

    # Set flag
    multigraph=False
    # but assume multigraphs to start
    if tokens.directed==1:
        G=nx.MultiDiGraph()
    else:
        G=nx.MultiGraph()

    for k,v in tokens.asList():
        if k=="node":
            vdict=wrap(v)
            node=vdict['id']
            G.add_node(node,attr_dict=vdict)
        elif k=="edge":
            vdict=wrap(v)
            source=vdict.pop('source')
            target=vdict.pop('target')
            if G.has_edge(source,target):
                multigraph=True
            G.add_edge(source,target,attr_dict=vdict)
        else:
            G.graph[k]=v

    # switch to Graph or DiGraph if no parallel edges were found.
    if not multigraph: 
        if G.is_directed():
            G=nx.DiGraph(G)
        else:
            G=nx.Graph(G)

    if relabel:
        # relabel, but check for duplicate labels first
        mapping=[(n,d['label']) for n,d in G.node.items()]
        x,y=zip(*mapping)
        if len(set(y))!=len(G):
            raise NetworkXError('Failed to relabel nodes: '
                                'duplicate node labels found. '
                                'Use relabel=False.')
        G=nx.relabel_nodes(G,dict(mapping))
    return G


def pyparse_gml():
    """A pyparsing tokenizer for GML graph format.

    This is not intended to be called directly.

    See Also
    --------
    write_gml, read_gml, parse_gml
    """  
    try:
        from pyparsing import \
             Literal, CaselessLiteral, Word, Forward,\
             ZeroOrMore, Group, Dict, Optional, Combine,\
             ParseException, restOfLine, White, alphas, alphanums, nums,\
             OneOrMore,quotedString,removeQuotes,dblQuotedString, Regex
    except ImportError:
        try:
            from matplotlib.pyparsing import \
             Literal, CaselessLiteral, Word, Forward,\
             ZeroOrMore, Group, Dict, Optional, Combine,\
             ParseException, restOfLine, White, alphas, alphanums, nums,\
             OneOrMore,quotedString,removeQuotes,dblQuotedString, Regex
        except:
            raise ImportError('pyparsing not found',
                              'http://pyparsing.wikispaces.com/')

    lbrack = Literal("[").suppress()
    rbrack = Literal("]").suppress()
    pound = ("#")
    comment = pound + Optional( restOfLine )
    integer = Word(nums+'-').setParseAction(lambda s,l,t:[ int(t[0])])
    real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?").setParseAction(
        lambda s,l,t:[ float(t[0]) ])
    dblQuotedString.setParseAction( removeQuotes )
    key = Word(alphas,alphanums+'_')
    value_atom = (real | integer | Word(alphanums) | dblQuotedString) 
    value = Forward()   # to be defined later with << operator
    keyvalue = Group(key+value)
    value << (value_atom | Group( lbrack + ZeroOrMore(keyvalue) + rbrack ))
    node = Group(Literal("node") + lbrack + Group(OneOrMore(keyvalue)) + rbrack)
    edge = Group(Literal("edge") + lbrack + Group(OneOrMore(keyvalue)) + rbrack)

    creator = Group(Literal("Creator")+ Optional( restOfLine ))
    version = Group(Literal("Version")+ Optional( restOfLine ))
    graphkey = Literal("graph").suppress()

    graph = Dict (Optional(creator)+Optional(version)+\
        graphkey + lbrack + ZeroOrMore( (node|edge|keyvalue) ) + rbrack )
    graph.ignore(comment)
    
    return graph

def generate_gml(G):
    """Generate a single entry of the graph G in GML format.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    lines: string
       Lines in GML format.

    Notes
    -----
    This implementation does not support all Python data types as GML
    data.  Nodes, node attributes, edge attributes, and graph
    attributes must be either dictionaries or single stings or
    numbers.  If they are not an attempt is made to represent them as
    strings.  For example, a list as edge data
    G[1][2]['somedata']=[1,2,3], will be represented in the GML file
    as::

       edge [
         source 1
         target 2
         somedata "[1, 2, 3]"
       ]
    """
    # recursively make dicts into gml brackets
    def listify(d,indent,indentlevel):
        result='[ \n'
        for k,v in d.items():
            if type(v)==dict:
                v=listify(v,indent,indentlevel+1)
            result += (indentlevel+1)*indent + \
                string_item(k,v,indentlevel*indent)+'\n'
        return result+indentlevel*indent+"]"

    def string_item(k,v,indent):
        # try to make a string of the data
        if type(v)==dict: 
            v=listify(v,indent,2)
        elif is_string_like(v):
            v='"%s"'%v
        elif type(v)==bool:
            v=int(v)
        return "%s %s"%(k,v)

    # check for attributes or assign empty dict
    if hasattr(G,'graph_attr'):
        graph_attr=G.graph_attr
    else:
        graph_attr={}
    if hasattr(G,'node_attr'):
        node_attr=G.node_attr
    else:
        node_attr={}

    indent=2*' '
    count=iter(range(len(G)))
    node_id={}

    yield "graph ["
    if G.is_directed():
        yield indent+"directed 1"
    # write graph attributes 
    for k,v in G.graph.items():
        if k == 'directed':
            continue
        yield indent+string_item(k,v,indent)
    # write nodes
    for n in G:
        yield indent+"node ["
        # get id or assign number
        nid=G.node[n].get('id',next(count))
        node_id[n]=nid
        yield 2*indent+"id %s"%nid
        label=G.node[n].get('label',n)
        if is_string_like(label):
            label='"%s"'%label
        yield 2*indent+'label %s'%label
        if n in G:
          for k,v in G.node[n].items():
              if k=='id' or k == 'label': continue
              yield 2*indent+string_item(k,v,indent)
        yield indent+"]"
    # write edges
    for u,v,edgedata in G.edges_iter(data=True):
        yield indent+"edge ["
        yield 2*indent+"source %s"%node_id[u]
        yield 2*indent+"target %s"%node_id[v]
        for k,v in edgedata.items():
            if k=='source': continue
            if k=='target': continue
            yield 2*indent+string_item(k,v,indent)
        yield indent+"]"
    yield "]"

@open_file(1,mode='wb')
def write_gml(G, path):
    """
    Write the graph G in GML format to the file or file handle path.

    Parameters
    ----------
    path : filename or filehandle
       The filename or filehandle to write.  Filenames ending in
       .gz or .gz2 will be compressed.

    See Also
    --------
    read_gml, parse_gml

    Notes
    -----
    GML specifications indicate that the file should only use
    7bit ASCII text encoding.iso8859-1 (latin-1). 

    This implementation does not support all Python data types as GML
    data.  Nodes, node attributes, edge attributes, and graph
    attributes must be either dictionaries or single stings or
    numbers.  If they are not an attempt is made to represent them as
    strings.  For example, a list as edge data
    G[1][2]['somedata']=[1,2,3], will be represented in the GML file
    as::

       edge [
         source 1
         target 2
         somedata "[1, 2, 3]"
       ]

    
    Examples
    ---------
    >>> G=nx.path_graph(4)
    >>> nx.write_gml(G,"test.gml")

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_gml(G,"test.gml.gz")
    """
    for line in generate_gml(G):
        line+='\n'
        path.write(line.encode('latin-1'))


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import pyparsing
    except:
        try:
            import matplotlib.pyparsing
        except:
            raise SkipTest("pyparsing not available")

# fixture for nose tests
def teardown_module(module):
    import os
    os.unlink('test.gml')
    os.unlink('test.gml.gz')
