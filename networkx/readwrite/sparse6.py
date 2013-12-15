"""
**************
Sparse6
**************
Read graphs in sparse6 format.

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
__all__ = ['read_sparse6', 'parse_sparse6',
           'generate_sparse6', 'write_sparse6']
import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import open_file, not_implemented_for
from networkx.readwrite.graph6 import data_to_graph6, graph6_to_data,\
    data_to_n, n_to_data

@not_implemented_for('directed')
def generate_sparse6(G, header=True):
    """Generate sparse6 format description of a simple undirected (multi)graph.

    The format does not support edge or vetrtex labels,
    but supports loops and multiedges.
    Optional sparse6 format prefix is controlled by ``header``.
    Returns an ascii string.
    """
    n = G.order()
    k = 1
    while 1<<k < n:
        k += 1

    def enc(x):
        """Big endian k-bit encoding of x"""
        return [1 if (x & 1 << (k-1-i)) else 0 for i in range(k)]

    ns = sorted(G.nodes()) # number -> node
    ndict = dict(((ns[i], i) for i in range(len(ns)))) # node -> number
    edges = [(ndict[u], ndict[v]) for (u, v) in G.edges()]
    edges = [(max(u,v), min(u,v)) for (u, v) in edges]
    edges.sort()

    bits = []
    curv = 0
    for (v, u) in edges:
        if v == curv: # current vertex edge
            bits.append(0)
            bits.extend(enc(u))
        elif v == curv + 1: # next vertex edge
            curv += 1
            bits.append(1)
            bits.extend(enc(u))
        else: # skip to vertex v and then add edge to u
            curv = v
            bits.append(1)
            bits.extend(enc(v))
            bits.append(0)
            bits.extend(enc(u))
    if k < 6 and n == (1 << k) and ((-len(bits)) % 6) >= k and curv < (n - 1):
        # Padding special case: small k, n=2^k,
        # more than k bits of padding needed,
        # current vertex is not (n-1) --
        # appending 1111... would add a loop on (n-1)
        bits.append(0)
        bits.extend([1] * ((-len(bits)) % 6))
    else:
        bits.extend([1] * ((-len(bits)) % 6))

    data = [(bits[i+0]<<5) + (bits[i+1]<<4) + (bits[i+2]<<3) + (bits[i+3]<<2) +
            (bits[i+4]<<1) + (bits[i+5]<<0) for i in range(0, len(bits), 6)]

    res = (':' + data_to_graph6(n_to_data(n)) +
                data_to_graph6(data))
    if header:
        return '>>sparse6<<' + res
    else:
        return res

@open_file(1, mode='wt')
def write_sparse6(G, path, header=True):
    """Write undirected (multi)graphs to given path in sparse6 format,
    one per line.

    Writes sparse6 header with every graph by default.
    See ``generate_sparse6`` for details.
    """
    path.write(generate_sparse6(G, header=header))

@open_file(0,mode='rt')
def read_sparse6(path):
    """Read undirected graphs in sparse6 format from path.

    Returns a list of MultiGraphs, one for each non-empty line of the file."""
    glist=[]
    for line in path:
        line = line.strip()
        if not len(line): continue
        glist.append(parse_sparse6(line))
    if len(glist) == 1:
        return glist[0]
    else:
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
