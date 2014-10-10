# encoding: utf-8
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
from __future__ import unicode_literals

__author__ = """\n""".join([
    'Aric Hagberg (hagberg@lanl.gov)',
    'Luca Pandini (luca1.pandini@gmail.com)'
])
#    Copyright (C) 2008-2010 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_gml', 'parse_gml', 'generate_gml', 'write_gml']

from cgi import escape
from collections import deque
from functools import partial

import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import open_file

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text (as a unicode object)
# @return The plain text, as a Unicode string, if necessary.
#
# Source: http://effbot.org/zone/re-sub.htm#unescape-html
#
import re
try:
    import htmlentitydefs
except ImportError:
    # Python 3.x
    import html.entities as htmlentitydefs

try:
    chr = unichr
except NameError:
    pass

try:
    str = unicode
except NameError:
    pass

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                else:
                    return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

@open_file(0, mode='rb')
def read_gml(path, relabel=False):
    """Read graph in GML format from path.

    Parameters
    ----------
    path : filename or filehandle
       The filename or filehandle to read from.

    relabel : bool, optional
       If True use the GML node label attribute for node names otherwise use
       the node id.

    Returns
    -------
    G : Graph, DiGraph, MultiGraph or MultiDiGraph depending on whether the
        graph is indirect, direct, has edges with same source and target.

    NetworkXError
        If relabel is True and there are nodes with the same label.

    SyntaxError
        If a syntax error is encountered while parsing. 

    See Also
    --------
    write_gml, parse_gml

    Notes
    -----
    The GML specification says that files should be ASCII encoded, with any
    extended ASCII characters (iso8859-1) appearing as HTML character entities.

    References
    ----------
    GML specification:
    http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.write_gml(G,'test.gml')
    >>> H = nx.read_gml('test.gml')
    """

    lines = map(lambda line: line.decode('utf-8'), path.readlines())
    G = parse_gml(lines, relabel=relabel)
    return G

@open_file(1, mode='wb')
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
    attributes must be either dictionaries, lists with at least two elements,
    single stings or numbers.  If they are not an attempt is made to represent 
    them as strings.  For example, a tuple as edge data will be represented in 
    the GML file as::

       edge [
         source 1
         target 2
         somedata "(1, 2)"
       ]


    Examples
    ---------
    >>> G=nx.path_graph(4)
    >>> nx.write_gml(G,"test.gml")

    Filenames ending in .gz or .bz2 will be compressed.

    >>> nx.write_gml(G,"test.gml.gz")
    """
    path.write(generate_gml(G).encode('ascii', 'xmlcharrefreplace'))


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
    G : Graph, DiGraph, MultiGraph or MultiDiGraph depending on whether the
        graph is indirect, direct, has edges with same source and target.

    Raises
    ------
    NetworkXError
        If relabel is True and there are nodes with the same label.

    SyntaxError
        If a syntax error is encountered while parsing. 

    See Also
    --------
    write_gml, read_gml

    Notes
    -----
    This stores nested GML attributes as dictionaries in the
    NetworkX graph, node, and edge attribute structures.

    References
    ----------
    GML specification:
    http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html
    """

    if isinstance(lines, str):
        lines = lines.split('\n')
    elms = parse(lines)
    G = nx.MultiGraph()

    edge_elms = filter(partial(filter_and_build_elm, G), elms)
    # remaining entries should be only edges
    for k, v in edge_elms:
        add_edge(G, v)

    G = convert_graph_type(G)

    if relabel and len(G):
        # relabel, but check for duplicate labels first
        mapping = [ (n, d['label']) for n, d in G.node.items() ]
        nodes, labels = zip(*mapping)
        if len(set(labels)) != len(G):
            raise NetworkXError('Failed to relabel nodes: '
                              'duplicate node labels found. '
                  'Use relabel=False.')
        nx.relabel_nodes(G, dict(mapping), copy = False)
    return G


def convert_graph_type(G):
    """ G is assumed to be a MultiGraph """
    directed   = G.graph.pop('directed', 0)
    multigraph = G.graph.pop('multigraph', False)
    if directed == 1:
        G = nx.MultiDiGraph(G) if multigraph else nx.DiGraph(G)
    elif not multigraph:
        G = nx.Graph(G)
    return G


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
    attributes must be either dictionaries, lists with at least two elements,
    single stings or numbers.  If they are not an attempt is made to represent 
    them as strings.  For example, a tuple as edge data will be represented in 
    the GML file as::

       edge [
         source 1
         target 2
         somedata "(1, 2)"
       ]
    """

    ensure_correct_ids(G)
    indent, lines = '  ', ['graph [']
    if G.is_directed(): G.graph['directed'] = True
    for k, v in G.graph.items():
        lines.append(format_attribute(k, v, indent))
    for node_num, (n, d) in enumerate(G.nodes_iter(data=True)):
        lines.append('  node [')
        lines.append(format_attribute('id', n, indent * 2))
        for k, v in d.items():
            lines.append(format_attribute(k, v, indent * 2))
        lines.append('  ]')
    for u, v, d in G.edges_iter(data=True):
        lines.append('  edge [')
        lines.append(format_attribute('source', u, indent * 2))
        lines.append(format_attribute('target', v, indent * 2))
        for k, v in d.items():
            lines.append(format_attribute(k, v, indent * 2))
        lines.append('  ]')
    lines.append(']')
    return '\n'.join(lines)


def filterfalse(predicate, iterable):
    fn = lambda *args: not predicate(*args)
    return filter(fn, iterable)


def is_int(v):
    try:
        int(v)
        return True
    except TypeError:
        return False


def ignore_line(line):
    return not len(line) or line.strip().startswith('#')


def remove_ignored_lines(lines):
    return filterfalse(ignore_line, lines)


def tokenize(lines):
    s = ('\n'.join(remove_ignored_lines(lines))
             .replace('[', ' [ ')
             .replace(']', ' ] '))
    # This way a quoted string is a token
    return deque(re.findall('([^\s"]+|"[^"]*")', s))


def parse(lines):
    tokens = tokenize(lines)
    if not len(tokens): raise SyntaxError('unexpected EOF')
    t = tokens.popleft()
    if 'graph' != t:
        raise SyntaxError('expected {0}, found {1}'.format('graph', t))
    if '[' != tokens[0]:
        raise SyntaxError('expected {0} after graph, found {1}'.format('[', tokens[0]))
    return parse_graph(tokens)


def raise_with_context(msg, tokens):
    ctx = ' '.join(tokens)[:120] + '... '
    raise SyntaxError('{0}:\n{1}'.format(msg, ctx))


def string_item(s):
    return unescape(s.replace('"', ''))


def parse_graph(tokens):
    elms = []
    t = tokens.popleft()

    if t == '[':
        while tokens[0] != ']':
            elms.append(parse_graph(tokens))
        tokens.popleft()
    elif t == 'node' or t == 'edge':
        elms.append(t)
        elms.append(parse_graph(tokens))
    elif t == ']': raise_with_context('unexpected ]', tokens)
    else:
        if t.startswith('"'): return string_item(t)
        try:
            return int(t)
        except ValueError: pass
        try:
            return float(t)
        except ValueError: pass
        elms.append(t)
        elms.append(parse_graph(tokens))
    return elms


def filter_and_build_elm(G, elm):
    k, v = elm
    if k == "node": add_node(G, v)
    elif k == "edge": return elm
    else:
        add_attribute(G.graph, elm)


def add_node(G, attr_list):
    dattr = dict()
    for a in attr_list: add_attribute(dattr, a)
    G.add_node(dattr.pop('id', G.number_of_nodes()), attr_dict = dattr)


def add_edge(G, attr_list):
    dattr = dict()
    s = find_and_pop_attribute(attr_list, 'source')
    t = find_and_pop_attribute(attr_list, 'target')
    if G.has_edge(s, t): G.graph['multigraph'] = True
    for a in attr_list: add_attribute(dattr, a)
    G.add_edge(s, t, attr_dict = dattr)


def find_and_pop_attribute(attr_list, key):
    try:
        idx = next(idx for idx, (a, v) in enumerate(attr_list) if a == key)
        return attr_list.pop(idx)[1]
    except StopIteration:
        raise NetworkXError('missing {0} attribute for edge {1}'.format(key, attr_list))


record = list
def add_attribute(attrs, attribute):
    k, v = attribute
    # dict
    if type(v) == record:
        d = {}
        for av in v: add_attribute(d, av)
        attrs[k] = d
    # list
    elif k in attrs:
        attrs[k] = [attrs[k], v] if type(attrs[k]) != list else attrs[k].append(v)
    # dict entry
    else:
        attrs[k] = v
    return attrs


def ensure_correct_ids(G):
    for n in G.node:
        if not is_int(n):
            mapping = list(zip(G.node.keys(), range(0, len(G))))
            nx.relabel_nodes(G, dict(mapping), copy = False)
            for old, new in mapping: G.node[new]['label'] = '"{}"'.format(old)
            break

def format_attribute(k, v, indent='  '):
    if isinstance(v, list): v = format_list_attribute(k, v, indent)
    elif type(v) == dict: v = format_dict_attribute(k, v, indent)
    else:
        v = '{0}{1} {2}'.format(indent, k, format_value(v))
    return v


def format_list_attribute(k, v, indent):
    d = []
    for vv in v:
        d.append(format_attribute(k, vv, indent))
    return '\n'.join(d)


def format_dict_attribute(k, v, indent):
    d = ['{0}{1} ['.format(indent, k)]
    for kk, vv in v.items():
        d.append(format_attribute(kk, vv, indent + '  '))
    d.append('{}]'.format(indent))
    return '\n'.join(d)


def format_value(v, indent='  '):
    if isinstance(v, str) and v.startswith('"'): v = v.replace('"', '')
    if isinstance(v, bool):         return 1 if v else 0
    if isinstance(v, (int, float)): return v
    else: return '"{}"'.format(escape(str(v), quote = True))


# fixture for nose tests
def teardown_module(module):
    import os
    os.unlink('test.gml')
    os.unlink('test.gml.gz')
