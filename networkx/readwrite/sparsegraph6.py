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
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_graph6', 'parse_graph6', 'read_graph6_list',
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
    data = graph6data(str)
    n, data = graph6n(data)
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
    n, data = graph6n(graph6data(string[1:]))
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
        if b: v += 1
        if x >= n: break # padding with ones can cause overlarge number here
        elif x > v: v = x
        else:
            G.add_edge(x,v)

    return G

# helper functions

def graph6data(str):
    """Convert graph6 character sequence to 6-bit integers."""
    v = [ord(c)-63 for c in str]
    if min(v) < 0 or max(v) > 63:
        return None
    return v
	
def graph6n(data):
    """Read initial one or four-unit value from graph6 sequence.  
    Return value, rest of seq."""
    if data[0] <= 62:
        return data[0], data[1:]
    return (data[1]<<12) + (data[2]<<6) + data[3], data[4:]
