"""Distance measures approximated metrics."""

import networkx as nx
from networkx.utils.decorators import py_random_state

__all__ = ["diameter"]


@py_random_state(1)
def diameter(G, seed=None):
    """Returns a lower bound on the diameter of the graph G.

    The function computes a lower bound on the diameter
    (i.e., the maximum eccentricity) of G.

    @TODO to be added the detailed description and the references.

    Parameters
    ----------
    G : NetworkX graph

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    d : integer
       Lower Bound on the Diameter of G

    Raises
    ------
    NetworkXError
        If the graph is empty or consists of multiple components

    Notes
    -----
    The algorithm was proposed in the following papers:

    See Also
    --------
    diameter
    eccentricity
    """
    if not G:
        raise ValueError("Expected non-empty NetworkX graph!")
    # if G is a directed graph
    if G.is_directed():
        if not nx.is_strongly_connected(G):
            raise nx.NetworkXError("DiGraph not strongly connected.")
        return _two_sweep_directed(G, seed)
    # else if G is an undirected graph
    else:
        if not nx.is_connected(G):
            raise nx.NetworkXError("Graph not connected.")
        return _two_sweep_undirected(G, seed)


def _two_sweep_undirected(G, seed=None):
    """Helper function for finding a lower bound on the diameter
        for undirected Graphs.

        The idea is to pick the farthest node from a random node
        and return its eccentricity.

        ``G`` is a NetworkX undirected graph.

    .. note::

        ``seed`` is a random.Random or numpy.random.RandomState instance
    """
    # pick a random node u
    u = seed.sample(G.nodes(), 1)[0]
    # compute the distances from node u
    distances = nx.single_source_shortest_path_length(G, u)
    max_distance = max(distances.values())
    farthest_nodes = [node for node, dist in distances.items() if dist == max_distance]
    # get a node v that is (one of) the farthest nodes from u
    v = seed.choice(farthest_nodes)
    # return the eccentricity of j
    distances = nx.single_source_shortest_path_length(G, v)
    return max(distances.values())


def _two_sweep_directed(G, seed=None):
    """Helper function for finding a lower bound on the diameter
        for directed Graphs.

        ``G`` is a NetworkX directed graph.

    .. note::

        ``seed`` is a random.Random or numpy.random.RandomState instance
    """
    raise NotImplementedError
