"""Functions for generating inverse line graphs."""
#    Copyright (C) 2016 by
#    James Clough <james.clough91@gmail.com>
#    All rights reserved.
#    BSD license.

__author__ = "\n".join(["James Clough (james.clough91@gmail.com)"])

__all__ = ['inverse_line_graph']

from itertools import combinations
from collections import defaultdict

import networkx as nx
from networkx.utils import arbitrary_element
from networkx.utils.decorators import *


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def inverse_line_graph(G):
    """ Returns the inverse line graph of graph G.
    
    If H is a graph, and G is the line graph of H, such that H = L(G).
    Then H is the inverse line graph of G.
    
    Not all graphs are line graphs and these do not have an inverse line graph.
    In these cases this generator returns a NetworkXError.
    
    Parameters
    ----------
    G : graph
        A NetworkX Graph
        
    Returns
    -------
    H : graph
        The inverse line graph of G.
    
    Raises
    ------
    NetworkXNotImplemented
        If G is directed or a multigraph
        
    NetworkXError
        If G is not a line graph
    
    Notes
    -----
    This is an implementation of the Roussopoulos algorithm.
    
    References
    ----------
    * Roussopolous, N, "A max {m,n} algorithm for determining the graph H from its line graph G",
      Information Processing Letters 2, (1973), 108--112. 
    
    """
    if G.number_of_edges() == 0 or G.number_of_nodes() == 0:
        raise nx.NetworkXError("G is not a line graph (has zero vertices or edges)")
    
    starting_cell = _select_starting_cell(G)
    P = _find_partition(G, starting_cell)
    # count how many times each vertex appears in the partition set
    P_count = {u:0 for u in G.nodes()}
    for p in P:
        for u in p:
            P_count[u] += 1
    
    if max(P_count.values()) > 2:
        raise nx.NetworkXError("G is not a line graph (vertex found in more than two partition cells)")
    W = tuple([(u,) for u in P_count if P_count[u]==1])
    H = nx.Graph()
    H.add_nodes_from(P)
    H.add_nodes_from(W)
    for a,b in combinations(H.nodes(), 2):
        if len(set(a).intersection(set(b))) > 0:
            H.add_edge(a,b)
    return H   
            
def _triangles(G, e):
    """ Return list of all triangles containing edge e"""
    u, v = e
    if v not in G.neighbors(u):
        raise nx.NetworkXError("Edge %s not in graph" % e)
    triangle_list = []
    for x in G.neighbors(u):
        if x in G.neighbors(v):
            triangle_list.append((u,v,x))
    return triangle_list           
    
def _odd_triangle(G, T):
    """ Test whether T is an odd triangle in G
    
    Parameters
    ----------
    G : NetworkX Graph
    T : 3-tuple of vertices forming triangle in G
    
    Returns
    -------
    True is T is an odd triangle
    False otherwise
    
    Raises
    ------
    NetworkXError
        T is not a triangle in G
        
    Notes
    -----
    An odd triangle is one in which there exists another vertex in G which is adjacent
    to either exactly one or exactly all three of the vertices in the triangle"""
    for u in T:
        if u not in G.nodes():
            raise nx.NetworkXError("Vertex %s not in graph" % u)
    for e in list(combinations(T, 2)):
        if e[0] not in G.neighbors(e[1]):
            raise nx.NetworkXError("Edge (%s, %s) not in graph" % (e[0], e[1]))
            
    T_neighbors = defaultdict(int)
    for t in T:
        for v in G.neighbors(t):
            if v not in T:       
                T_neighbors[v] += 1
    for v in T_neighbors:
        if T_neighbors[v] in [1,3]:
            return True
    return False  
                
def _find_partition(G, starting_cell):
    G_partition = G.copy()
    P = [starting_cell] # partition set
    G_partition.remove_edges_from(list(combinations(starting_cell, 2)))
    
    while G_partition.number_of_edges() > 0:
        for u in G_partition.nodes(): # TODO don't need to search them all every time
            deg_u = len(G_partition[u])
            if deg_u > 0:
                # u has some incident edges left in the graph
                # we now want to find the one other cell u is in (as it can be in 2 max)
                new_cell = [u] + list(G_partition.neighbors(u))
                # check that new_cell is a complete subgraph in G
                for u in new_cell:
                    for v in new_cell:
                        if (u!=v) and (v not in G.neighbors(u)):
                            raise nx.NetworkXError("G is not a line graph (partition cell was not a complete subgraph)")
                P.append(tuple(new_cell))
                G_partition.remove_edges_from(list(combinations(new_cell, 2)))
    return P
    
def _select_starting_cell(G, starting_edge=None):
    # If starting edge not specified pick an arbitrary edge - doesn't matter which
    # However, this function may call itself requiring a specific starting edge
    if starting_edge == None:
        e = arbitrary_element(list(G.edges()))
    else:
        e = starting_edge
        if e[0] not in G.neighbors(e[1]):
            raise nx.NetworkXError('starting_edge %s is not in the Graph' % e) 
    e_triangles = _triangles(G, e)
    r = len(e_triangles)
    if r == 0:
        starting_cell = e
    elif r == 1:
        # if other 2 edges of this triangle belong only to T then T is starting cell
        T = e_triangles[0]
        a,b,c = T
        # ab was original edge so check the other 2 edges
        ac_edges = [x for x in _triangles(G, (a,c))]
        bc_edges = [x for x in _triangles(G, (b,c))]
        if len(ac_edges) == 1:
            if len(bc_edges) == 1:
                starting_cell = T
            else:
                return _select_starting_cell(G, starting_edge=(b,c))
        else:
            return _select_starting_cell(G, starting_edge=(a,c))
    else:
        s = 0
        odd_triangles = []
        for T in e_triangles:
            if _odd_triangle(G, T):
                s += 1
                odd_triangles.append(T)
                
        if r==2 and s==0:
            # in this case it doesn't matter which of our two triangles we choose, so just use T
            starting_cell = T 
        elif r-1 <= s <= r:
            # check if odd triangles containing e form complete subgraph
            # there must be exactly s+2 of them
            # and they must all be connected
            triangle_nodes = set([])
            for T in odd_triangles:
                for x in T:
                    triangle_nodes.add(x)
            if len(triangle_nodes) == s+2:
                for u in triangle_nodes:
                    for v in triangle_nodes:
                        if u!=v and (v not in G.neighbors(u)):
                            raise nx.NetworkXError("G is not a line graph (odd triangles do not form complete subgraph)")
                # otherwise then we can use this as the starting cell
                starting_cell = tuple(triangle_nodes)  
            else:
                raise nx.NetworkXError("G is not a line graph (odd triangles do not form complete subgraph)")
        else:
            raise nx.NetworkXError("G is not a line graph (incorrect number of odd triangles around starting edge)")
            # TODO JC - are these recursive calls OK or should we do something else?
    return starting_cell    
    
