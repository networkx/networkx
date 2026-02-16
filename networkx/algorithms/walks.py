"""Function for computing walks in a graph."""

import networkx as nx
from networkx.utils import not_implemented_for, py_random_state

__all__ = ["number_of_walks", "random_walk"]


@nx._dispatchable
def number_of_walks(G, walk_length):
    """Returns the number of walks connecting each pair of nodes in `G`

    A *walk* is a sequence of nodes in which each adjacent pair of nodes
    in the sequence is adjacent in the graph. A walk can repeat the same
    edge and go in the opposite direction just as people can walk on a
    set of paths, but standing still is not counted as part of the walk.

    This function only counts the walks with `walk_length` edges. Note that
    the number of nodes in the walk sequence is one more than `walk_length`.
    The number of walks can grow very quickly on a larger graph
    and with a larger walk length.

    Parameters
    ----------
    G : NetworkX graph

    walk_length : int
        A nonnegative integer representing the length of a walk.

    Returns
    -------
    dict
        A dictionary of dictionaries in which outer keys are source
        nodes, inner keys are target nodes, and inner values are the
        number of walks of length `walk_length` connecting those nodes.

    Raises
    ------
    ValueError
        If `walk_length` is negative

    Examples
    --------

    >>> G = nx.Graph([(0, 1), (1, 2)])
    >>> walks = nx.number_of_walks(G, 2)
    >>> walks
    {0: {0: 1, 1: 0, 2: 1}, 1: {0: 0, 1: 2, 2: 0}, 2: {0: 1, 1: 0, 2: 1}}
    >>> total_walks = sum(sum(tgts.values()) for _, tgts in walks.items())

    You can also get the number of walks from a specific source node using the
    returned dictionary. For example, number of walks of length 1 from node 0
    can be found as follows:

    >>> walks = nx.number_of_walks(G, 1)
    >>> walks[0]
    {0: 0, 1: 1, 2: 0}
    >>> sum(walks[0].values())  # walks from 0 of length 1
    1

    Similarly, a target node can also be specified:

    >>> walks[0][1]
    1

    """
    import scipy as sp

    if walk_length < 0:
        raise ValueError(f"`walk_length` cannot be negative: {walk_length}")

    A = nx.adjacency_matrix(G, weight=None)
    power = sp.sparse.linalg.matrix_power(A, walk_length).tocsr()
    result = {
        u: {v: power[u_idx, v_idx].item() for v_idx, v in enumerate(G)}
        for u_idx, u in enumerate(G)
    }
    return result


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
@py_random_state("seed")
def random_walk(G, *, start, weight=None, seed=None):
    """Yields nodes visited by a random walk starting at `start`.

    The generator yields nodes in walk order, including `start` as the first
    yielded node, and terminates when there is no valid outgoing transition.

    If `weight` is None, transitions are uniform over neighbors. If `weight` is
    a string, transitions are proportional to that edge attribute, defaulting to
    1 if missing.

    Parameters
    ----------
    G : NetworkX graph
        The input graph.
    start : node
        Starting node for the random walk.
    weight : string or None, optional (default=None)
        Edge attribute name to interpret as the transition weight. If None, each edge has
        weight 1.
    seed : integer, random_state, or None (default=None)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    iterator
        An iterator yielding visited nodes in walk order.
    """
    if start not in G:
        raise nx.NodeNotFound(start)

    adj = G._adj
    node = start
    while True:
        yield node
        nbrs = adj[node]
        if not nbrs:
            return

        if weight is None:
            node = seed.choice(list(nbrs))
            continue

        positive_nbrs = []
        positive_weights = []
        for nbr, edge_data in nbrs.items():
            edge_weight = edge_data.get(weight, 1)
            if edge_weight < 0:
                raise ValueError(
                    f"Edge ({node}, {nbr}) has negative weight {edge_weight}"
                )
            if edge_weight > 0:
                positive_nbrs.append(nbr)
                positive_weights.append(edge_weight)

        if not positive_nbrs:
            return

        node = seed.choices(positive_nbrs, weights=positive_weights, k=1)[0]
