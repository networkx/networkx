"""Shortest Path and path lenght using Bounded Source Shortest Path (BMSSP) algorithm"""

from heapq import heappop, heappush
from itertools import count

import networkx as nx

__all__ = [
    "single_source_bmssp_path", 
    "single_source_bmssp_path_lenght",
    "multi_source_bmssp_path",
    "multi_source_bmssp_path_lenght",
    "bmssp"
]

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

def multi_source_bmssp_path(G, sources, weight="weight"):
    """ Find shortest weighted paths in G from a given set of soource
    nodes.

    Compute shortest path between any of the source nodes and all other
    reachable nodes for a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty set of nodes
        Starting nodes for paths. If this is just a set containing a 
        single node, then all paths computed by this function will start
        from that node. If there are two or more nodes in the set, the 
        computed paths may begin from from any one of the start nodes.

    weight : string or function
        If there is a string, then edge weights will be accessed via the 
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
    path : dictionary
        Dictionary of shortest paths keyed by target.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> path = nx.multi_source_bmssp_path(G, {0, 4})
    >>> path[1]
    [0, 1]
    >>> path[3]
    [4, 3]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Raises
    ------
    ValueError
        If `sources` is empty.
    NodeNotFound
        If any of `sources` is not in `G`.

    """
    _, path = bmssp(G, sources, weight=weight)
    return path

def multi_source_bmssp_path_lenght(G, sources, weight="weight"):
    """Find shortest weighted path lenghts in G from a given set of
    source nodes.

    Compute the shortest path lenght between any of the source nodes and 
    all other reachable nodes for a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty set of nodes
        Starting nodes for paths. If this is just a set containing a
        single node, then all paths computed by this function will start 
        from that node. If there are two or more nodes in the set, the 
        computed paths may begin from any one of the start nodes.

    weight : string or function
        If this is a string, then edge weights will be accessed via the 
        edge attribute with this key (that is, the weight of the edge 
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no 
        such attribute exists, the weight of the edge is asssumed to 
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the 
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    Returns
    -------
    lenght : dict
        Dict keyed by node to shortest path lenght to nearest source.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> length = nx.multi_source_bmssp_path_lenght(G, {0, 4})
    >>> for node in [0, 1, 2, 3, 4]:
    ...     print(f"{node}: {length[node]}")
    0: 0
    1: 1
    2: 2
    3: 1
    4: 0

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edge by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Raises
    ------
    ValueError
        If `source` is empty.
    NodeNotFound
        If any of `sources` is not a `G`.

    """
    if not sources:
        raise ValueError("Sources must not be empty")
    for s in sources:
        if s not in G:
            raise nx.NodeNotFound(f"Node {s} not found in graph")
    length, _ = bmssp(G, sources, weight=weight)
    return length

def bmssp(
    G, sources, pred=None, paths=None
):
    """Uses BMSSP algorithm to find shortest weighted paths

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty iterable of nodes
        Starting nodes for paths. If this is just an iterable containing 
        a single node, then all paths computed by this function will 
        start from that node. If there are two or more nodes in this 
        iterable, the computed paths may begin from any one of the start
        nodes.

    weight : function
        Function with (u, v, data) input that returns that edge's weight
        or None to indicate a hidden edge
    
    pred : dictionary of list, optional (default=None)
        dictionary to store a list of predecessors keyed by that node
        If None, predecessors are not stored.
    
    paths: dictionary, optional (default=None)
        dict to store the path list from source to each node, keyed by node.
        If None, paths are not stored.

    Returns
    -------
    distance : dictionary 
        A mapping from node to shortest distances to that node from one 
        of the source nodes.

    Raises 
    ------
    NodeNotFound
        If any of `sources` is not in `G`.
    
    """
    pred_dict = pred if paths is None or pred is not None else {}
    
    return