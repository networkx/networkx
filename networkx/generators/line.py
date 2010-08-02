"""
Line graphs.

"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

__all__ = ['line_graph']

import networkx as nx

def line_graph(G):
    """Return the line graph of the graph or digraph G.

    The line graph of a graph G has a node for each edge 
    in G and an edge between those nodes if the two edges
    in G share a common node.

    For DiGraphs an edge an edge represents a directed path of length 2.

    The original node labels are kept as two-tuple node labels
    in the line graph.  

    Parameters
    ----------
    G : graph
       A NetworkX Graph or DiGraph

    Examples
    --------    
    >>> G=nx.star_graph(3)
    >>> L=nx.line_graph(G)
    >>> print(sorted(L.edges())) # makes a clique, K3
    [((0, 1), (0, 2)), ((0, 1), (0, 3)), ((0, 3), (0, 2))]

    Notes
    -----
    Not implemented for MultiGraph or MultiDiGraph classes.

    Graph, node, and edge data are not propagated to the new graph.

    """
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise Exception("Line graph not implemented for Multi(Di)Graphs")
    L=G.__class__()
    if G.is_directed():
        for u,nlist in G.adjacency_iter():  # same as successors for digraph
            # look for directed path of length two
            for n in nlist:
                nbrs=G[n] # successors 
                for nbr in nbrs:
                    if nbr!=u:
                        L.add_edge((u,n),(n,nbr))
    else:
        for u,nlist in G.adjacency_iter():
            # label nodes as tuple of edge endpoints in original graph
            # "node tuple" must be in lexigraphical order
            nodes=[tuple(sorted(n)) for n in zip([u]*len(nlist),nlist)]
            # add clique of nodes to graph
            while nodes:
                u=nodes.pop()
                L.add_edges_from((u,v) for v in nodes)
    return L

