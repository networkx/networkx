"""
**************
Graph6
**************
Read graphs in graph6 format.

Format
------

"graph6 and sparse6 are formats for storing undirected graphs in a
compact manner, using only printable ASCII characters. Files in these
formats have text type and contain one line per graph."
http://cs.anu.edu.au/~bdm/data/formats.html

See http://cs.anu.edu.au/~bdm/data/formats.txt for details.
"""
# Original author: D. Eppstein, UC Irvine, August 12, 2003.
# The original code at http://www.ics.uci.edu/~eppstein/PADS/ is public domain.
#    Copyright (C) 2004-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Tomas Gavenciak <gavento@ucw.cz>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Tomas Gavenciak <gavento@ucw.cz>',
                            'Aric Hagberg <aric.hagberg@lanl.gov'
                            ])
__all__ = ['read_graph6', 'parse_graph6',
           'generate_graph6', 'write_graph6']
import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import open_file, not_implemented_for

def parse_graph6(str):
    """Read a simple undirected graph in graph6 format from string.

    Returns a single Graph.
    """
    def bits():
        """Return sequence of individual bits from 6-bit-per-value
        list of data values."""
        for d in data:
            for i in [5,4,3,2,1,0]:
                yield (d>>i)&1

    if str.startswith('>>graph6<<'):
        str = str[10:]
    data = graph6_to_data(str)
    n, data = data_to_n(data)
    nd = (n*(n-1)//2 + 5) // 6
    if len(data) != nd:
        raise NetworkXError(\
            'Expected %d bits but got %d in graph6' % (n*(n-1)//2, len(data)*6))

    G=nx.Graph()
    G.add_nodes_from(range(n))
    for (i,j),b in zip([(i,j) for j in range(1,n) for i in range(j)], bits()):
        if b: G.add_edge(i,j)
    return G

@open_file(0,mode='rt')
def read_graph6(path):
    """Read simple undirected graphs in graph6 format from path.

    Returns a list of Graphs, one for each non-empty line of the file.
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

@not_implemented_for('directed')
def generate_graph6(G, nodes = None, header=True):
    """Generate graph6 format description of a simple undirected graph.

    The format does not support edge or vetrtex labels and multiedges.
    Optional graph6 format prefix is controlled by ``header``.
    Returns an ascii string.
    """
    if nodes is not None:
        ns = list(nodes)
    else:
        ns = list(G)

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
def write_graph6(G, path, header=True):
    """Write simple undirected graphs to given path in graph6 format,
    one per line.

    Writes graph6 header with every graph by default.
    See ``generate_graph6`` for details.
    """
    path.write(generate_graph6(G, header=header))

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
