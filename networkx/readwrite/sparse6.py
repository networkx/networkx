"""Sparse6

Read and write graphs in sparse6 format.

Format
------

"graph6 and sparse6 are formats for storing undirected graphs in a
compact manner, using only printable ASCII characters. Files in these
formats have text type and contain one line per graph."

See http://cs.anu.edu.au/~bdm/data/formats.txt for details.
"""
# Original author: D. Eppstein, UC Irvine, August 12, 2003.
# The original code at http://www.ics.uci.edu/~eppstein/PADS/ is public domain.
#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Tomas Gavenciak <gavento@ucw.cz>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import open_file, not_implemented_for
from networkx.readwrite.graph6 import data_to_graph6, graph6_to_data,\
    data_to_n, n_to_data
__author__ = """\n""".join(['Tomas Gavenciak <gavento@ucw.cz>',
                            'Aric Hagberg <aric.hagberg@lanl.gov'])
__all__ = ['read_sparse6', 'parse_sparse6',
           'generate_sparse6', 'write_sparse6']

def parse_sparse6(string):
    """Read an undirected graph in sparse6 format from string.

    Parameters
    ----------
    string : string
       Data in sparse6 format

    Returns
    -------
    G : Graph

    Raises
    ------
    NetworkXError
        If the string is unable to be parsed in sparse6 format

    Examples
    --------
    >>> G = nx.parse_sparse6(':A_')
    >>> sorted(G.edges())
    [(0, 1), (0, 1), (0, 1)]

    See Also
    --------
    generate_sparse6, read_sparse6, write_sparse6

    References
    ----------
    Sparse6 specification: http://cs.anu.edu.au/~bdm/data/formats.txt
    """
    if string.startswith('>>sparse6<<'):
        string = string[11:]
    if not string.startswith(':'):
        raise NetworkXError('Expected leading colon in sparse6')
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

    G = nx.MultiGraph()
    G.add_nodes_from(range(n))

    multigraph = False
    for b,x in parseData():
        if b == 1:
            v += 1
        # padding with ones can cause overlarge number here
        if x >= n or v >= n:
            break
        elif x > v:
            v = x
        else:
            if G.has_edge(x,v):
                multigraph = True
            G.add_edge(x,v)
    if not multigraph:
        G = nx.Graph(G)
    return G

@open_file(0,mode='rt')
def read_sparse6(path):
    """Read an undirected graph in sparse6 format from path.

    Parameters
    ----------
    path : file or string
       File or filename to write.

    Returns
    -------
    G : Graph/Multigraph or list of Graphs/MultiGraphs
       If the file contains multple lines then a list of graphs is returned

    Raises
    ------
    NetworkXError
        If the string is unable to be parsed in sparse6 format

    Examples
    --------
    >>> nx.write_sparse6(nx.Graph([(0,1),(0,1),(0,1)]), 'test.s6')
    >>> G = nx.read_sparse6('test.s6')
    >>> sorted(G.edges())
    [(0, 1)]

    See Also
    --------
    generate_sparse6, read_sparse6, parse_sparse6

    References
    ----------
    Sparse6 specification: http://cs.anu.edu.au/~bdm/data/formats.txt
    """
    glist = []
    for line in path:
        line = line.strip()
        if not len(line):
            continue
        glist.append(parse_sparse6(line))
    if len(glist) == 1:
        return glist[0]
    else:
        return glist

@not_implemented_for('directed')
def generate_sparse6(G, nodes=None, header=True):
    """Generate sparse6 format string from an undirected graph.

    Parameters
    ----------
    G : Graph (undirected)

    nodes: list or iterable
       Nodes are labeled 0...n-1 in the order provided.  If None the ordering
       given by G.nodes() is used.

    header: bool
       If True add '>>sparse6<<' string to head of data

    Returns
    -------
    s : string
       String in sparse6 format

    Raises
    ------
    NetworkXError
        If the graph is directed

    Examples
    --------
    >>> G = nx.MultiGraph([(0, 1), (0, 1), (0, 1)])
    >>> nx.generate_sparse6(G)
    '>>sparse6<<:A_'

    See Also
    --------
    read_sparse6, parse_sparse6, write_sparse6

    Notes
    -----
    The format does not support edge or node labels.
    References
    ----------
    Sparse6 specification:
    http://cs.anu.edu.au/~bdm/data/formats.txt for details.
    """
    n = G.order()
    k = 1
    while 1<<k < n:
        k += 1

    def enc(x):
        """Big endian k-bit encoding of x"""
        return [1 if (x & 1 << (k-1-i)) else 0 for i in range(k)]

    if nodes is None:
        ns = list(G.nodes()) # number -> node
    else:
        ns = list(nodes)
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
def write_sparse6(G, path, nodes=None, header=True):
    """Write graph G to given path in sparse6 format.
    Parameters
    ----------
    G : Graph (undirected)

    path : file or string
       File or filename to write

    nodes: list or iterable
       Nodes are labeled 0...n-1 in the order provided.  If None the ordering
       given by G.nodes() is used.

    header: bool
       If True add '>>sparse6<<' string to head of data

    Raises
    ------
    NetworkXError
        If the graph is directed

    Examples
    --------
    >>> G = nx.Graph([(0, 1), (0, 1), (0, 1)])
    >>> nx.write_sparse6(G, 'test.s6')

    See Also
    --------
    read_sparse6, parse_sparse6, generate_sparse6

    Notes
    -----
    The format does not support edge or node labels.

    References
    ----------
    Sparse6 specification:
    http://cs.anu.edu.au/~bdm/data/formats.txt for details.
    """
    path.write(generate_sparse6(G, nodes=nodes, header=header))
    path.write('\n')


def teardown_module(test):
    import os
    if os.path.isfile('test.s6'):
        os.unlink('test.s6')
