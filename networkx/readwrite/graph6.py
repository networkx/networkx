# Original author: D. Eppstein, UC Irvine, August 12, 2003.
# The original code at http://www.ics.uci.edu/~eppstein/PADS/ is public domain.
#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Tomas Gavenciak <gavento@ucw.cz>
#    All rights reserved.
#    BSD license.
#
# Authors: Tomas Gavenciak <gavento@ucw.cz>
#          Aric Hagberg <aric.hagberg@lanl.gov>
"""Functions for reading and writing graphs in the *graph6* format.

The *graph6* file format is suitable for small graphs or large dense
graphs. For large sparse graphs, use the *sparse6* format.

For more information, see the `graph6`_ homepage.

.. _graph6: http://users.cecs.anu.edu.au/~bdm/data/formats.html

"""
import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import open_file, not_implemented_for

__all__ = ['read_graph6', 'parse_graph6', 'generate_graph6', 'write_graph6']


def parse_graph6(string):
    """Read a simple undirected graph in graph6 format from string.

    Parameters
    ----------
    string : string
       Data in graph6 format

    Returns
    -------
    G : Graph

    Raises
    ------
    NetworkXError
        If the string is unable to be parsed in graph6 format

    Examples
    --------
    >>> G = nx.parse_graph6('A_')
    >>> sorted(G.edges())
    [(0, 1)]

    See Also
    --------
    generate_graph6, read_graph6, write_graph6

    References
    ----------
    .. [1] Graph6 specification
           <http://users.cecs.anu.edu.au/~bdm/data/formats.html>

    """
    def bits():
        """Return sequence of individual bits from 6-bit-per-value
        list of data values."""
        for d in data:
            for i in [5,4,3,2,1,0]:
                yield (d>>i)&1

    if string.startswith('>>graph6<<'):
        string = string[10:]
    data = graph6_to_data(string)
    n, data = data_to_n(data)
    nd = (n*(n-1)//2 + 5) // 6
    if len(data) != nd:
        raise NetworkXError(\
            'Expected %d bits but got %d in graph6' % (n*(n-1)//2, len(data)*6))

    G=nx.Graph()
    G.add_nodes_from(range(n))
    for (i,j),b in zip([(i,j) for j in range(1,n) for i in range(j)], bits()):
        if b:
            G.add_edge(i,j)

    return G

@open_file(0,mode='rt')
def read_graph6(path):
    """Read simple undirected graphs in graph6 format from path.

    Parameters
    ----------
    path : file or string
       File or filename to write.

    Returns
    -------
    G : Graph or list of Graphs
       If the file contains multiple lines then a list of graphs is returned

    Raises
    ------
    NetworkXError
        If the string is unable to be parsed in graph6 format

    Examples
    --------
    >>> nx.write_graph6(nx.Graph([(0,1)]), 'test.g6')
    >>> G = nx.read_graph6('test.g6')
    >>> sorted(G.edges())
    [(0, 1)]

    See Also
    --------
    generate_graph6, parse_graph6, write_graph6

    References
    ----------
    .. [1] Graph6 specification
           <http://users.cecs.anu.edu.au/~bdm/data/formats.html>

    """
    glist = []
    for line in path:
        line = line.strip()
        if not len(line):
            continue
        glist.append(parse_graph6(line))
    if len(glist) == 1:
        return glist[0]
    else:
        return glist

@not_implemented_for('directed','multigraph')
def generate_graph6(G, nodes = None, header=True):
    """Generate graph6 format string from a simple undirected graph.

    Parameters
    ----------
    G : Graph (undirected)

    nodes: list or iterable
       Nodes are labeled 0...n-1 in the order provided.  If None the ordering
       given by G.nodes() is used.

    header: bool
       If True add '>>graph6<<' string to head of data

    Returns
    -------
    s : string
       String in graph6 format

    Raises
    ------
    NetworkXError
        If the graph is directed or has parallel edges

    Examples
    --------
    >>> G = nx.Graph([(0, 1)])
    >>> nx.generate_graph6(G)
    '>>graph6<<A_'

    See Also
    --------
    read_graph6, parse_graph6, write_graph6

    Notes
    -----
    The format does not support edge or node labels, parallel edges or
    self loops.  If self loops are present they are silently ignored.

    References
    ----------
    .. [1] Graph6 specification
           <http://users.cecs.anu.edu.au/~bdm/data/formats.html>

    """
    if nodes is not None:
        G = G.subgraph(nodes)
    H = nx.convert_node_labels_to_integers(G)
    ns = sorted(H.nodes())
    def bits():
        for (i,j) in [(i,j) for j in range(1,n) for i in range(j)]:
            yield G.has_edge(ns[i],ns[j])

    n = G.order()
    data = n_to_data(n)
    d = 0
    flush = False
    for i, b in zip(range(n * n), bits()):
        d |= b << (5 - (i % 6))
        flush = True
        if i % 6 == 5:
            data.append(d)
            d = 0
            flush = False
    if flush:
        data.append(d)

    string_data =  data_to_graph6(data)
    if header:
        string_data  =  '>>graph6<<' + string_data
    return string_data


@open_file(1, mode='wt')
def write_graph6(G, path, nodes = None, header=True):
    """Write a simple undirected graph to path in graph6 format.

    Parameters
    ----------
    G : Graph (undirected)

    path : file or string
       File or filename to write.

    nodes: list or iterable
       Nodes are labeled 0...n-1 in the order provided.  If None the ordering
       given by G.nodes() is used.

    header: bool
       If True add '>>graph6<<' string to head of data

    Raises
    ------
    NetworkXError
        If the graph is directed or has parallel edges

    Examples
    --------
    >>> G = nx.Graph([(0, 1)])
    >>> nx.write_graph6(G, 'test.g6')

    See Also
    --------
    generate_graph6, parse_graph6, read_graph6

    Notes
    -----
    The format does not support edge or node labels, parallel edges or
    self loops.  If self loops are present they are silently ignored.

    References
    ----------
    .. [1] Graph6 specification
           <http://users.cecs.anu.edu.au/~bdm/data/formats.html>

    """
    path.write(generate_graph6(G, nodes=nodes, header=header))
    path.write('\n')

# helper functions

def graph6_to_data(string):
    """Convert graph6 character sequence to 6-bit integers."""
    v = [ord(c)-63 for c in string]
    if len(v) > 0 and (min(v) < 0 or max(v) > 63):
        return None
    return v

def data_to_graph6(data):
    """Convert 6-bit integer sequence to graph6 character sequence."""
    if len(data) > 0 and (min(data) < 0 or max(data) > 63):
        raise NetworkXError("graph6 data units must be within 0..63")
    return ''.join([chr(d+63) for d in data])

def data_to_n(data):
    """Read initial one-, four- or eight-unit value from graph6
    integer sequence.

    Return (value, rest of seq.)"""
    if data[0] <= 62:
        return data[0], data[1:]
    if data[1] <= 62:
        return (data[1]<<12) + (data[2]<<6) + data[3], data[4:]
    return ((data[2]<<30) + (data[3]<<24) + (data[4]<<18) +
            (data[5]<<12) + (data[6]<<6) + data[7], data[8:])

def n_to_data(n):
    """Convert an integer to one-, four- or eight-unit graph6 sequence."""
    if n < 0:
        raise NetworkXError("Numbers in graph6 format must be non-negative.")
    if n <= 62:
        return [n]
    if n <= 258047:
        return [63, (n>>12) & 0x3f, (n>>6) & 0x3f, n & 0x3f]
    if n <= 68719476735:
        return [63, 63,
            (n>>30) & 0x3f, (n>>24) & 0x3f, (n>>18) & 0x3f,
            (n>>12) & 0x3f, (n>>6) & 0x3f, n & 0x3f]
    raise NetworkXError("Numbers above 68719476735 are not supported by graph6")


def teardown_module(module):
    import os
    if os.path.isfile('test.g6'):
        os.unlink('test.g6')
