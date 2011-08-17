"""
This module provides the following: read and write of p2g format 
used in metabolic pathway studies.

See http://www.cs.purdue.edu/homes/koyuturk/pathway/ for a description.

The summary is included here:

A file that describes a uniquely labeled graph (with extension ".gr")
format looks like the following:


name
3 4
a
1 2
b

c
0 2

"name" is simply a description of what the graph corresponds to. The
second line displays the number of nodes and number of edges,
respectively. This sample graph contains three nodes labeled "a", "b",
and "c". The rest of the graph contains two lines for each node. The
first line for a node contains the node label. After the declaration
of the node label, the out-edges of that node in the graph are
provided. For instance, "a" is linked to nodes 1 and 2, which are
labeled "b" and "c", while the node labeled "b" has no outgoing
edges. Observe that node labeled "c" has an outgoing edge to
itself. Indeed, self-loops are allowed. Node index starts from 0.

"""
__author__ = """Willem Ligtenberg (w.p.a.ligtenberg@tue.nl)\n Aric Hagberg (hagberg@lanl.gov)"""
__date__ = """2008-05-27"""
#    Copyright (C) 2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx
from networkx.utils import is_string_like,open_file


@open_file(1,mode='w')
def write_p2g(G, path):
    """Write NetworkX graph in p2g format.

    This format is meant to be used with directed graphs with
    possible self loops.
    """

    path.write("%s\n"%G.name)
    path.write("%s %s\n"%(G.order(),G.size()))

    nodes = G.nodes()

    # make dictionary mapping nodes to integers
    nodenumber=dict(zip(nodes,range(len(nodes)))) 

    for n in nodes:
        path.write("%s\n"%n)
        for nbr in G.neighbors(n):
            path.write("%s "%nodenumber[nbr])
        path.write("\n")

@open_file(0,mode='r')
def read_p2g(path):
    """Read graph in p2g format from path. 

    Returns an MultiDiGraph.

    If you want a DiGraph (with no self loops allowed and no edge data)
    use D=networkx.DiGraph(read_p2g(path))
    """
    G=parse_p2g(path)
    return G

def parse_p2g(lines):
    """Parse p2g format graph from string or iterable. 

    Returns an MultiDiGraph.
    """
    if is_string_like(lines): lines=iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines])

    description = lines.next()
    # are multiedges (parallel edges) allowed?
    G=networkx.MultiDiGraph(name=description,selfloops=True)
    nnodes,nedges=map(int,lines.next().split())

    nodelabel={}
    nbrs={}
    # loop over the nodes keeping track of node labels and out neighbors
    # defer adding edges until all node labels are known
    for i in range(nnodes):
        n=lines.next()
        nodelabel[i]=n
        G.add_node(n)
        nbrs[n]=map(int,lines.next().split())

    # now we know all of the node labels so we can add the edges
    # with the correct labels        
    for n in G:
        for nbr in nbrs[n]:
            G.add_edge(n,nodelabel[nbr])
    return G
