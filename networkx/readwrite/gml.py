"""
Read graphs in GML format.
See http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html
for format specification.

Example graphs in GML format:
http://www-personal.umich.edu/~mejn/netdata/

Requires pyparsing: http://pyparsing.wikispaces.com/


"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2008-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_gml', 'parse_gml', 'write_gml']

import networkx as nx
from networkx.exception import NetworkXException, NetworkXError
from networkx.utils import _get_fh, is_string_like

	
def read_gml(path):
    """Read graph in GML format from path.

    Parameters
    ----------
    path : filename or filehandle
       The filename or filehandle to read from.

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
    This doesn't implement the complete GML specification for
    nested attributes for graphs, edges, and nodes. 

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
    fh=_get_fh(path,mode='r')        
    G=parse_gml(fh)
    return G


def parse_gml(lines):
    """Parse GML graph from a string or iterable.

    Parameters
    ----------
    lines : string or iterable
       Data in GML format.

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
    This stores nested GML attributes as dicts in the 
    NetworkX Graph attribute structures.

    Requires pyparsing: http://pyparsing.wikispaces.com/

    References
    ----------
    GML specification:
    http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_gml(G,'test.gml')
    >>> fh=open('test.gml')
    >>> H=nx.read_gml(fh)
    """
    try:
        from pyparsing import ParseException
    except ImportError:
        raise ImportError, \
          "Import Error: not able to import pyparsing: http://pyparsing.wikispaces.com/"

    try:
        data = "".join(lines)
        gml = pyparse_gml()
        tokens =gml.parseString(data)
    except ParseException, err:
        print err.line
        print " "*(err.column-1) + "^"
        print err
        raise

    # function to recursively make dicts of key/value pairs
    def wrap(tok):
        listtype=type(tok)
        result={}
        for k,v in tok:
            if type(v)==listtype:
                result[k]=wrap(v)
            else:
                result[k]=v
        return result
    # storage areas
    node_labels={}
    graphs=[]
    nodes=[]
    edges=[]
    directed=False
    # process parsed info
    tokenlist=tokens.asList()
    for k,v in tokenlist:
        if k=="node":
            vdict=wrap(v)
            id=vdict['id']
            label=vdict['label']
            node_labels[id]=label
            nodes.append((label,vdict))
        elif k=="edge":
            vdict=wrap(v)
            edges.append((vdict.pop('source'), vdict.pop('target'), vdict))
        else:
            if type(v)==type(tokenlist):
                graphs.append((k,wrap(v)))
            else:
                graphs.append((k,v))
            if k=="directed" and v==1:
                directed=True
    # Now create the Graph
    if directed:
        G=nx.MultiDiGraph()
    else:
        G=nx.MultiGraph()
    G.graph.update(graphs)
    G.add_nodes_from(nodes)
    G.add_edges_from( (node_labels[s],node_labels[t],d) for s,t,d in edges)
    return G 
            
graph = None
def pyparse_gml():
    """A pyparsing tokenizer for GML graph format.

    This is not intended to be called directly.

    See Also
    --------
    write_gml, read_gml, parse_gml

    Notes
    -----
    This doesn't implement the complete GML specification for
    nested attributes for graphs, edges, and nodes. 

    """  
    global graph
    
    try:
        from pyparsing import \
             Literal, CaselessLiteral, Word, Forward,\
             ZeroOrMore, Group, Dict, Optional, Combine,\
             ParseException, restOfLine, White, alphas, alphanums, nums,\
             OneOrMore,quotedString,removeQuotes,dblQuotedString
    except ImportError:
        raise ImportError, \
          "Import Error: not able to import pyparsing: http://pyparsing.wikispaces.com/"

    if not graph:
        lbrack = Literal("[").suppress()
        rbrack = Literal("]").suppress()
        pound = ("#")
        comment = pound + Optional( restOfLine )
        white = White(" \t\n")
        point = Literal(".")
        e = CaselessLiteral("E")
        integer = Word(nums).setParseAction(lambda s,l,t:[ int(t[0])])
        real = Combine( Word("+-"+nums, nums )+ 
                        Optional(point+Optional(Word(nums)))+
                        Optional(e+Word("+-"+nums, nums))).setParseAction(
                                        lambda s,l,t:[ float(t[0]) ])
        key = Word(alphas,alphanums+'_')
        value_atom = integer^real^Word(alphanums)^quotedString.setParseAction(removeQuotes)

        value = Forward()   # to be defined later with << operator
        keyvalue = Group(key+value)
        value << (value_atom | Group( lbrack + ZeroOrMore(keyvalue) + rbrack ))
        node = Group(Literal("node") + lbrack + Group(OneOrMore(keyvalue)) + rbrack)
        edge = Group(Literal("edge") + lbrack + Group(OneOrMore(keyvalue)) + rbrack)

        creator = Group(Literal("Creator")+ Optional( restOfLine ))
        version = Group(Literal("Version")+ Optional( restOfLine ))
        graphkey = Literal("graph").suppress()

        graph = Optional(creator)+Optional(version)+\
            graphkey + lbrack + ZeroOrMore( (node|edge|keyvalue) ) + rbrack
        graph.ignore(comment)
        
    return graph

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
    The output file will use the default text encoding on your system.
    It is possible to write files in other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> G=nx.path_graph(4)
    >>> import codecs
    >>> fh=codecs.open('test.gml','w',encoding='iso8859-1')# use iso8859-1
    >>> nx.write_gml(G,fh)

    GML specifications indicate that the file should only use
    7bit ASCII text encoding.iso8859-1 (latin-1). 

    For nested attributes for graphs, nodes, and edges you should
    use dicts for the value of the attribute.  

    Examples
    ---------
    >>> G=nx.path_graph(4)
    >>> nx.write_gml(G,"test.gml")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("test.gml",'w')
    >>> nx.write_gml(G,fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_gml(G,"test.gml.gz")
    """
    fh=_get_fh(path,mode='w')        

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
    count=iter(range(G.number_of_nodes()))
    node_id={}
    dicttype=type({})

    # recursively make dicts into gml brackets
    def listify(d,indent,indentlevel):
        result='[ \n'
        dicttype=type({})
        for k,v in d.iteritems():
            if type(v)==dicttype:
                v=listify(v,indent,indentlevel+1)
            result += indentlevel*indent+"%s %s\n"%(k,v)
        return result+indentlevel*indent+"]"

    fh.write("graph [\n")
    if G.is_directed():
        fh.write(indent+"directed 1\n")
    # write graph attributes 
    for k,v in G.graph.items():
        if is_string_like(v):
            v='"'+v+'"'
        elif type(v)==dicttype:
            v=listify(v,indent,1)
        fh.write(indent+"%s %s\n"%(k,v))
    # write nodes        
    for n in G:
        fh.write(indent+"node [\n")
        # get id or assign number
        nid=G.node[n].get('id',count.next())
        node_id[n]=nid
        fh.write(2*indent+"id %s\n"%nid)
        fh.write(2*indent+"label \"%s\"\n"%n)
        if n in G:
          for k,v in G.node[n].items():
              if is_string_like(v): v='"'+v+'"'
              if type(v)==dicttype: v=listify(v,indent,2)
              if k=='id': continue
              fh.write(2*indent+"%s %s\n"%(k,v))
        fh.write(indent+"]\n")
    # write edges
    for u,v,edgedata in G.edges_iter(data=True):
        # try to guess what is on the edge and do something reasonable
        fh.write(indent+"edge [\n")
        fh.write(2*indent+"source %s\n"%node_id[u])
        fh.write(2*indent+"target %s\n"%node_id[v])
        for k,v in edgedata.items():
            if k=='source': continue
            if k=='target': continue
            if is_string_like(v): v='"'+v+'"'
            if type(v)==dicttype: v=listify(v,indent,2)
            fh.write(2*indent+"%s %s\n"%(k,v))
        fh.write(indent+"]\n")
    fh.write("]")
