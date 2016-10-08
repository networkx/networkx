import networkx as nx

__author__ = "Rohail Syed <rohailsyed@gmail.com>"

__all__ = [
    'bridges',
    'local_bridges',
    'bridges_exist',
    'local_bridges_exist'
]


def local_bridges(G, first_match=False):
    """ Looks through the graph object `G` for all local bridges.
    We formally define a local bridge to be any edge `AB` such that the removal
    of the edge results in a distance strictly greater than 2 between
    nodes `A` and `B`. We formally define *span* as the distance between two
    nodes `A` and `B` when the edge connecting them is removed. Note that all
    bridges are local bridges with span of infinity (outputs span of -1
    in this function).

    Parameters
    ----------
    G : Undirected Graph object
    first_match : boolean
        Tells us if we should only look for at least one instance of a local
        bridge (True) or look for all (False).

    Returns
    ----------
    dict
        key : (tuple) edge that is a local bridge
        value : (int) span of corresponding local bridge

    Examples
    --------
    >>> G = nx.cycle_graph(5)
    >>> bridges_dict = local_bridges(G)
    >>> list(bridges_dict.keys())
    [(0, 1), (1, 2), (3, 4), (2, 3), (0, 4)]
    >>> list(bridges_dict.values())
    [4, 4, 4, 4, 4]

    Notes
    ----------
    This function can be useful to quickly determine what local bridges exist
    in a given network and what their spans are. The function finds the local
    bridges as follows. For each edge E in graph G, determine the start and
    end nodes (A and B) and delete the edge. Attempt to find the new shortest
    path between A and B. If none exists, we have a bridge(which we represent
    as having span=-1). Otherwise, if the span is strictly greater than 2,
    that edge is a local bridge. Add edge E back in the graph and repeat this
    process for all edges.
    """

    # Arya's suggestion
    bridges = {}
    for e in G.edges():
        G.remove_edge(*e)
        try:
            (u, v) = e
            path_length = nx.shortest_path_length(G, u, v)
        except nx.NetworkXNoPath:
            bridges[e] = -1  # found a bridge
            if first_match:
                return bridges
        else:
            if path_length > 2:  # found a local bridge
                bridges[e] = path_length
                if first_match:
                    return bridges
        finally:
            G.add_edge(*e)
    return bridges


def bridges(G):
    """ Looks through the graph object `G` for all bridges.

    We formally define a bridge to be any edge `(u, v)` such that the removal
    of the edge increases the total number of connected components.

    Parameters
    ----------
    G : Undirected Graph object

    Returns
    ----------
    iterable
        Edges that are bridges

    Examples
    --------
    >>> G = nx.cycle_graph(5)
    >>> bridges_list = bridges(G)
    >>> list(bridges_list)
    []
    >>> G.remove_edge(0,1)
    >>> list(bridges(G))
    [(2, 1), (3, 2), (4, 3), (0, 4)]

    Notes
    ----------
    This function can be useful to quickly determine what bridges exist
    in a given network. We use an implemenation of Tarjan's Bridge-finding
    algorithm to do this.

    The algorithm is described in [1]_.

    References
    ----------
    .. [1] R. Endre Tarjan,
        "A note on finding the bridges of a graph", *Information Processing
        Letters*, **2** (6): 160--161

    """

    visited = set()
    depths = {}
    low = {}
    parent = {node: None for node in G}

    def bridge_util(u, depth):
        visited.add(u)
        depth += 1
        depths[u] = low[u] = depth
        for v in G[u]:
            if v not in visited:
                parent[v] = u
                for e in bridge_util(v, depth):
                    yield e
                # Check if subtree rooted at v has connection
                # to an ancestor of u.
                low[u] = min(low[u], low[v])
                # If the lowest vertex reachable from the subtree under v
                # is below u in the DFS tree, then `u-v` is a bridge.
                if low[v] > depths[u]:
                    yield (u, v)
            elif v != parent[u]:
                low[u] = min(low[u], depths[v])

    for u in G:
        if u not in visited:
            for e in bridge_util(u, depth=0):
                yield e


def local_bridges_exist(G):
    """ Checks if any local bridges exist in this network. We will simply call
    the `local_bridges()` function with the first_match stop parameter.
    Since the search for local bridges will terminate after finding one
    instance, this function is faster if we just want to know if at least
    one local bridge exists in the network.

    Parameters
    ----------
    G : Undirected Graph object

    Returns
    ----------
    boolean
        True if we found at least one bridge.
        False otherwise.

    Examples
    --------
    >>> G = nx.cycle_graph(5)
    >>> local_bridges_exist(G)
    True
    >>> G = nx.complete_graph(5)
    >>> local_bridges_exist(G)
    False

    Notes
    ----------
    This function can be useful to quickly determine whether or not local
    bridges exist in a given network.
    """

    results = local_bridges(G, first_match=True)
    if len(results) > 0:
        return True
    else:
        return False


def bridges_exist(G):
    """ Checks if any bridges exist in this network. We will simply call the
    `bridges()` function and look for non-zero list length.

    Parameters
    ----------
    G : Undirected Graph object

    Returns
    ----------
    boolean
        True if we found at least one bridge.
        False otherwise.

    Examples
    --------
    >>> G = nx.cycle_graph(5)
    >>> bridges_exist(G)
    False
    >>> G.remove_edge(1,2)
    >>> bridges_exist(G)
    True

    Notes
    ----------
    This function can be useful to quickly determine whether or not bridges
    exist in a given network.
    """

    results = bridges(G)
    if len(list(results)) > 0:
        return True
    else:
        return False
