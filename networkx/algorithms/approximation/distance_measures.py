"""Distance measures approximated metrics."""

import networkx as nx
from networkx.utils.decorators import py_random_state

__all__ = ["diameter"]


@py_random_state(1)
def diameter(G, seed=None):
    """Returns a lower bound on the diameter of the graph G.

    The function computes a lower bound on the diameter (i.e., the maximum eccentricity)
    of a directed or undirected graph G. The procedure used varies depending on the graph
    being directed or not.

    If G is an `undirected` graph, then the `2-sweep` procedure is being used [1]_.
    The main idea is to pick the farthest node from a random node and return its eccentricity.

    Otherwise, if G is a `directed` graph, then the directed version of the 2-sweep
    algorithm is used, referred to as `2-dSweep` [2]_. The procedure starts by selecting
    a random source node $s$ from which it performs a forward and a backward BFS.
    Let $a_1$ and $a_2$ be the farthest nodes in the forward and backward cases, respectively.
    Then, it computes the backward eccentricity of $a_1$ using a backward BFS and the
    forward eccentricity of $a_2$ using a forward BFS. Finally, it returns the best
    bound between the two.

    In both cases, the time complexity is linear with respect to the size of G.

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
        If the graph is empty or
        If the graph is undirected and not connected or
        If the graph is directed and not strongly connected.

    See Also
    --------
    networkx.algorithms.distance_measures.diameter

    References
    ----------
    .. [1] Magnien, Clémence, Matthieu Latapy, and Michel Habib.
       *Fast computation of empirically tight bounds for the diameter of massive graphs.*
       Journal of Experimental Algorithmics (JEA), 2009.
       https://arxiv.org/pdf/0904.2728.pdf
    .. [2] Crescenzi, Pierluigi, Roberto Grossi, Leonardo Lanzi, and Andrea Marino.
       *On computing the diameter of real-world directed (weighted) graphs.*
       International Symposium on Experimental Algorithms. Springer, Berlin, Heidelberg, 2012.
       https://courses.cs.ut.ee/MTAT.03.238/2014_fall/uploads/Main/diameter.pdf
    """
    # if G is empty
    if not G:
        raise nx.NetworkXError("Expected non-empty NetworkX graph!")
    # if there's only a node
    if G.number_of_nodes() == 1:
        return 0
    # if G is directed
    if G.is_directed():
        if not nx.is_strongly_connected(G):
            raise nx.NetworkXError("DiGraph not strongly connected.")
        return _two_sweep_directed(G, seed)
    # else if G is undirected
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
    # pick a random source node
    source = seed.sample(G.nodes(), 1)[0]
    # get a node v that is (one of) the farthest nodes from the source
    *_, (_, v) = nx.bfs_edges(G, source)
    # compute the distances from v to the other nodes
    distances = nx.single_source_shortest_path_length(G, v)
    # return the eccentricity of v
    return max(distances.values())


def _two_sweep_directed(G, seed=None):
    """Helper function for finding a lower bound on the diameter
        for directed Graphs.

        It is based on the directed version of the 2-sweep algorithm.
        The algorithm is based on the following steps.
        1. Select a source node $s$ at random.
        2. Perform a forward BFS from $s$ to select a node $a_1$ at the maximum
        distance from the source, and compute $LB_1$, the backward eccentricity of $a_1$.
        3. Perform a backward BFS from $s$ to select a node $a_2$ at the maximum
        distance from the source, and compute $LB_2$, the forward eccentricity of $a_2$.
        4. Return the maximum between $LB_1$ and $LB_2$.

        ``G`` is a NetworkX directed graph.

    .. note::

        ``seed`` is a random.Random or numpy.random.RandomState instance
    """
    # get a new digraph G' with the edges reversed in the opposite direction
    G_reversed = G.reverse()
    # pick a random source node
    source = seed.sample(G.nodes(), 1)[0]
    # get a node a_1 at the maximum distance from the source in G
    *_, (_, a_1) = nx.bfs_edges(G, source)
    # compute the distances from a_1 to the other nodes in G reversed
    distances_1 = nx.single_source_shortest_path_length(G_reversed, a_1)
    # get a node a_2 at the maximum distance from the source in G_reversed
    *_, (_, a_2) = nx.bfs_edges(G, source, reverse=True)
    # compute the distances from a_2 to the other nodes in G
    distances_2 = nx.single_source_shortest_path_length(G, a_2)
    # compute the two bounds
    lb_1, lb_2 = max(distances_1.values()), max(distances_2.values())
    # return the best bound
    return max(lb_1, lb_2)
