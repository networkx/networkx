"""
**************
SparseGraph 6
**************
Read graphs in graph6 and sparse6 format.

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
__author__ = """Aric Hagberg <aric.hagberg@lanl.gov>"""
#    Copyright (C) 2004-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_graph6', 'parse_graph6', 'read_graph6_list',
	   'generate_graph6', 'write_graph6', 'write_graph6_list',
           'read_sparse6', 'parse_sparse6', 'read_sparse6_list']

import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import open_file

# graph6

def read_graph6(path):
    """Read simple undirected graphs in graph6 format from path.

    Returns a single Graph.
    """
    return read_graph6_list(path)[0]

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
def read_graph6_list(path):
    """Read simple undirected graphs in graph6 format from path.

    Returns a list of Graphs, one for each line in file.
    """
    glist=[]
    for line in path:
        line = line.strip()
        if not len(line): continue
        glist.append(parse_graph6(line))
    return glist


def generate_graph6(G, header=True):
    """Generate graph6 format description of a simple undirected graph.
    
    The format does not support edge or vetrtex labels and multiedges,
    the vertices are converted to numbers 0..(n-1) by sorting them.
    Optional graph6 format prefix is controlled by `header`.
    Returns a single line string.
    """

    if G.is_directed():
	raise NetworkXError('graph6 format does not support directed graphs')
    ns = sorted(G.nodes())

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

    if header:
        return '>>graph6<<' + data_to_graph6(data)
    else:
	return data_to_graph6(data)

@open_file(1, mode='wt')
def write_graph6_list(Gs, path, header=True):
    """Write simple undirected graphs to given path in graph6 format, one per line.

    Writes graph6 header with every graph by default.
    See `generate_graph6` for details.
    """
    for G in Gs:
	path.write(generate_graph6(G, header=header))
	path.write('\n')

def write_graph6(G, path, header=True):
    """Write a simple undirected graph to given path in graph6 format.

    Writes a graph6 header by default.
    See `generate_graph6` for details.
    """
    return write_graph6_list([G], path, header=header)

# sparse6

def read_sparse6(path):
    """Read simple undirected graphs in sparse6 format from path.

    Returns a single MultiGraph."""
    return read_sparse6_list(path)[0]

@open_file(0,mode='rt')
def read_sparse6_list(path):
    """Read undirected graphs in sparse6 format from path.

    Returns a list of MultiGraphs, one for each line in file."""
    glist=[]
    for line in path:
        line = line.strip()
        if not len(line): continue
        glist.append(parse_sparse6(line))
    return glist

def parse_sparse6(string):
    """Read undirected graph in sparse6 format from string.

    Returns a MultiGraph.
    """
    if string.startswith('>>sparse6<<'):
        string = str[10:]
    if not string.startswith(':'):
        raise NetworkXError('Expected colon in sparse6')
    n, data = data_to_n(graph6_to_data(string[1:]))
    k = 1
    while 1<<k < n:
        k += 1

    def parseData():
        """Return stream of pairs b[i], x[i] for sparse6 format."""
        chunks = iter(data)
        d = None # partial data word
        dLen = 0 # how many unparsed bits are left in d

        while 1:
            if dLen < 1:
                d = next(chunks)
                dLen = 6
            dLen -= 1
            b = (d>>dLen) & 1 # grab top remaining bit

            x = d & ((1<<dLen)-1) # partially built up value of x
            xLen = dLen		# how many bits included so far in x
            while xLen < k:	# now grab full chunks until we have enough
                d = next(chunks)
                dLen = 6
                x = (x<<6) + d
                xLen += 6
            x = (x >> (xLen - k)) # shift back the extra bits
            dLen = xLen - k
            yield b,x

    v = 0

    G=nx.MultiGraph()
    G.add_nodes_from(range(n))

    for b,x in parseData():
        if b == 1:
            v += 1
        # padding with ones can cause overlarge number here
        if x >= n or v >= n:
            break
        elif x > v:
            v = x
        else:
            G.add_edge(x,v)
    return G

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
    """Read initial one-, four- or eight-unit value from graph6 integer sequence.

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

