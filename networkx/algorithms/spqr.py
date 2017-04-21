"""
Find SPQR tree of a biconnected graph
"""
import networkx as nx
from operator import itemgetter

__authors__ = "\n".join(['James Clough <james.clough91@gmail.com>'])
#    Copyright (C) 2017 by
#    James Clough <james.clough91@gmail.com>
#    All rights reserved.
#    BSD license.

__all__ = ['palm_tree']

def palm_tree(G, root):
    """ Returns a Palm Tree of undirected simple graph G

    P has the same vertex set as G, and the same edges although they are now
    directed.
    A palm tree consists of a directed spanning tree of G where all tree arcs
    go from nodes with a lower number to a higher one, and `fronds' which are
    edges from higher numbered nodes to lower numbered ones.
    The tree arcs and fronds together make up all of the edges of the original
    graph G.

    Edges in P have the attribute 'edge_type' which is either 'tree_arc' or
    'frond'.
    Nodes in P have the attribute 'number' as described above.
    They also have attributes 'lowpt1', 'lowpt2', 'ND', 'father' and 'flag'
    which are used in the algorithm for the SPQR tree.

    Parameters
    ----------
    G - NetworkX undirected simple graph
    root - vertex in G to be used as the root of the palm tree

    Returns
    -------
    P - NetworkX directed simple graph

    Notes
    -----
    For a description of what a palm tree is, and this algorithm, see
    Hopcroft & Tarjan ``Dividing a Graph into Triconnected Components'', 1973
    """
    P = nx.DiGraph()
    P.add_nodes_from(G.nodes())
    nx.set_node_attributes(P, 'number', 0)
    nx.set_node_attributes(P, 'flag', True)
    P.graph['n'] = 0
    palm_tree_dfs(G, P, root, None)
    return P

def palm_tree_dfs(G, P, v, u):
    """ Using notation of Hopcroft and Tarjan when referring to u and v

    u is the father of v in the spanning tree being constructed
    """
    P.graph['n'] += 1
    P.node[v]['number'] = P.graph['n']
    P.node[v]['lowpt1'] = P.node[v]['number']
    P.node[v]['lowpt2'] = P.node[v]['number']
    P.node[v]['ND'] = 1

    for w in G.neighbors(v):
        if P.node[w]['number'] == 0:
            # then w is a new vertex
            P.add_edge(v, w, edge_type='tree_arc')
            palm_tree_dfs(G, P, w, v)
            if P.node[w]['lowpt1'] < P.node[v]['lowpt1']:
                P.node[v]['lowpt2'] = min(P.node[v]['lowpt1'], P.node[w]['lowpt2'])
                P.node[v]['lowpt1'] = P.node[w]['lowpt1']
            elif P.node[w]['lowpt1'] == P.node[v]['lowpt1']:
                P.node[v]['lowpt2'] = min(P.node[v]['lowpt2'], P.node[w]['lowpt2'])
            else:
                P.node[v]['lowpt2'] = min(P.node[v]['lowpt2'], P.node[w]['lowpt1'])
            P.node[v]['ND'] = P.node[v]['ND'] + P.node[w]['ND']
            P.node[w]['father'] = v

        elif ((P.node[w]['number'] < P.node[v]['number']) and
              ((w != u) or (not P.node[v]['flag']))):
            # this test makes us avoid exploring an edge in both directions
            # flag(v) becomes false when (u,v) is examined
            P.add_edge(v, w, edge_type='frond')
            if P.node[w]['number'] < P.node[v]['lowpt1']:
                P.node[v]['lowpt2'] = P.node[v]['lowpt1']
                P.node[v]['lowpt1'] = P.node[w]['number']
            elif P.node[w]['number'] > P.node[v]['lowpt1']:
                P.node[v]['lowpt2'] = min(P.node[v]['lowpt2'], P.node[w]['number'])

        if w == u:
            P.node[v]['flag'] = False
