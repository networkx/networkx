# -*- coding: utf-8 -*-
"""
Connected components.
"""
__authors__ = "\n".join(['Eben Kenah',
                         'Aric Hagberg (hagberg@lanl.gov)'
                         'Christopher Ellison'])
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['number_connected_components', 
           'connected_components',
           'connected_component_subgraphs',
           'is_connected',
           'node_connected_component',
           ]

import networkx as nx

def connected_components(G):
    """Return nodes in connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    comp : list of lists
       A list of nodes for each component of G.

    See Also       
    --------
    strongly_connected_components

    Notes
    -----
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 
    """
    if G.is_directed():
        raise nx.NetworkXError("""Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph.""")
    seen={}
    components=[]
    for v in G:      
        if v not in seen:
            c=nx.single_source_shortest_path_length(G,v)
            components.append(list(c.keys()))
            seen.update(c)
    components.sort(key=len,reverse=True)            
    return components            


def number_connected_components(G):
    """Return number of connected components in graph.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    n : integer
       Number of connected components

    See Also       
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    return len(connected_components(G))


def is_connected(G):
    """Test graph connectivity.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    connected : bool
      True if the graph is connected, false otherwise.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> print(nx.is_connected(G))
    True

    See Also
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    if G.is_directed():
        raise nx.NetworkXError(\
            """Not allowed for directed graph G.
Use UG=G.to_undirected() to create an undirected graph.""")

    if len(G)==0:
        raise nx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(nx.single_source_shortest_path_length(G,
                                              next(G.nodes_iter())))==len(G)


def connected_component_subgraphs(G):
    """Return connected components as subgraphs.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    glist : list
      A list of graphs, one for each connected component of G.

    Examples
    --------
    Get largest connected component as subgraph

    >>> G=nx.path_graph(4)
    >>> G.add_edge(5,6)
    >>> H=nx.connected_component_subgraphs(G)[0]

    See Also
    --------
    connected_components

    Notes
    -----
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 

    Graph, node, and edge attributes are copied to the subgraphs.
    """
    cc=connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c).copy())
    return graph_list


def node_connected_component(G,n):
    """Return nodes in connected components of graph containing node n.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    n : node label       
       A node in G

    Returns
    -------
    comp : lists
       A list of nodes in component of G containing node n.

    See Also       
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    if G.is_directed():
        raise nx.NetworkXError("""Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph.""")
    return list(nx.single_source_shortest_path_length(G,n).keys())

        
