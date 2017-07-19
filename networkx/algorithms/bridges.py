import networkx as nx

__author__ = "Rohail Syed <rohailsyed@gmail.com>"

__all__ = [
    'bridges',
    'local_bridges',
    'bridges_exist',
    'local_bridges_exist'
]


def local_bridges(G):
    """ Looks through the graph object `G` for all local bridges.
    We formally define a local bridge to be any edge `(u, v)` such that the
    removal of the edge results in a distance strictly greater than 2 between
    nodes `u` and `v`. We formally define *span* as the distance between two
    nodes `u` and `v` when the edge connecting them is removed. Note that all
    bridges are local bridges with span of infinity (outputs span of
    float('inf') in this function).

    Parameters
    ----------
    G : Undirected Graph object

    Returns
    ----------
    iterable
        Yields a tuple for each local bridge found.
        Format : `(u, v, d)`
        `u, v` : edge nodes for this local bridge
        `d` : span of this local bridge

    Examples
    --------
    >>> G = nx.cycle_graph(5)
    >>> bridges_list = local_bridges(G)
    >>> list(bridges_list)
    [(0, 1, 4), (0, 4, 4), (1, 2, 4), (2, 3, 4), (3, 4, 4)]

    Notes
    ----------
    This function can be useful to determine what local bridges exist
    in a given network and what their spans are. The function finds the local
    bridges as follows. For each edge `(u, v)`, determine if its a local bridge
    by checking for no intersection in the neighbors of `u` and `v`. If the
    edge is a local bridge, determine its span by removing `(u, v)` from the
    graph, computing the new distance between `u` and `v` and then adding the
    edge back. If removal of the edge results in an impossible path, we have
    a bridge. Standard convention is to assign infinite span to bridges.
    """

    H = G.copy(with_data=False)
    for u, v in G.edges():
        if not (set(G[u]) & set(G[v])):
            # edge has a span of at least 2. this is a local bridge
            H.remove_edge(u, v)
            try:
                d = nx.shortest_path_length(H, u, v)
            except NetworkXNoPath:
                d = float('inf')
            H.add_edge(u, v)
            yield u, v, d


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
    [(1, 2), (2, 3), (3, 4), (0, 4)]

    Notes
    ----------
    This function can be useful to quickly determine what bridges exist
    in a given network. We first construct the biconnected components
    of the graph. Then, since any bridge must exist only in a two-node
    biconnected component, we simply iterate and output the two-node
    sets. This iteration is a linear time operation.
    """

    biconnects = nx.biconnected_components(G)
    for bridge_pair in biconnects:
        if len(bridge_pair) == 2:
            setiter = iter(bridge_pair)
            yield (next(setiter), next(setiter))


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

    try:
        next(local_bridges(G))
    except StopIteration:
        return False
    return True


def bridges_exist(G):
    """ Checks if any bridges exist in this network. We will simply call the
    `bridges()` function and attempt to retrieve at least one bridge.

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

    try:
        next(bridges(G))
    except StopIteration:
        return False
    return True
