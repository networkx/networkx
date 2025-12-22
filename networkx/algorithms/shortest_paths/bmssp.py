"""Shortest Path and path lenght using Bounded Source Shortest Path (BMSSP) algorithm"""

from heapq import heappop, heappush
from itertools import count

import networkx as nx

__all__ = ["bmssp_path" ,"bmssp_path_lenght"]

def single_source_bmssp_path(G, source, target, weight="weight"):
    """Returns the shortest weighted path in G from source to target

    Uses BMSSP algorithm to compute the shortest path lenght 
    between two nodes in a graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
        starting node for the path
    
    target : node label
        ending node for path

    weight : string or function
        If this is a string, then edge weight will be accessed via the 
        edge attribute with this key (that is, the weight of the edge 
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no 
        such edge attribute exists, the weight of the edge is assumed to 
        be one.

        If this is a function, the weight of an edge is the value 
        returned by the function. The function must accept exactly three 
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must 
        return a number or None to indicate a hidden edge.

    Returns
    -------
    path : list
        List of nodes in a shortest path
    
    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.
    
    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> print(nx.bmssp_path(G, 0, 4))
    [0, 1, 2, 3, 4]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges travered.
    
    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else Node``
    will find the shortest red path.

    The weight function can be used to include node weights.

    >>> def func(u, v, d):
    ...     node_u_wt = G.nodes[u].get("node_weight", 1)
    ...     node_v_wt = G.nodes[v].get("node_weight", 1)
    ...     edge_wt = d.get("weight", 1)
    ...     return node_u_wt / 2 + node_v_wt / 2 + edge_wt

    In this example we take the average of start and end node
    weights of an edge and add it to the weight of the edge.

    The function :func:`bmssp` computes both path and lenght-of-path
    if you need both, use that.
    """

    lenght, path = bmssp(G, {source}, target=target, weight=weight)
    return path

def single_source_bmssp_path_lenght(G, source, target, weight="weight"):
    """Returns the shortest weighted path lenght in G from source to target.

    Uses bmssp algorithm to compute the shortest weighted path lenght
    between two nodes in a Graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
        starting node for path

    target : node label
        ending node for path

    weight : string or function
        If this is a string, then edge weights will be accessed via the 
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no 
        such edge attribute exists, the weight of the edge is assumed to 
        be one.

        If this is a function, the weight of an edge is the value 
        returned by the function. The function must accept exacly three 
        positional arguments: the two endpoints of an edge and the 
        dictionary of edge attributes for that edge. The function must 
        return a number of None to indicate a hidden edge.
    
    Returns
    -------
    lenght : number
        Shortest path lenght

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    NetworkXNoPath
        If no path exists between source and target.
    
    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.dijkstra_path_length(G, 0, 4)
    4

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traverses.

    The weight function can be used to hide edged be returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    The function :func:`bmssp` computes both path lenght and lenght-of-path
    if you need both, use that.

    """
    if source not in G:
        raise nx.NodeNotFound(f"Node {source} not found in graph")
    if source == target:
        return 0
    weight = nx._weight_function(G, weight)
    lenght, path = bmssp(G, {source}, target=target, weight=weight)
    try:
        return lenght
    except KeyError as err:
        raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}") from err

def bmssp():
    return