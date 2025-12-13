"""Function for computing walks in a graph."""

import networkx as nx
from networkx.utils import py_random_state
from networkx.utils.random_sequence import weighted_choice

__all__ = ["number_of_walks", "unweighted_random_walk", "weighted_random_walk"]


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


@nx._dispatchable
@py_random_state("seed")
def unweighted_random_walk(G, start, walk_length, *, seed=None):
    """Generates an unweighted random walk of given length from a start node.

    Parameters
    ----------
    G : NetworkX graph

    start : node
        Starting node for the random walk.

    walk_length : int
        Length of the random walk.

    seed : integer, random_state, or None (default=None)
        Indicator of random number generation state. See :ref:`randomness`.

    Returns
    ------
    walk : list
        The nodes in the random walk sequence organized in a list in the order of the visits.

    """
    if walk_length < 0:
        raise ValueError(
            f"'walk_length' cannot be negative, currently you have passed walk_length : {walk_length}"
        )
    if start not in G:
        raise nx.NodeNotFound(start)

    walk = [start]
    current = start

    for _ in range(walk_length):
        neighbors = list(G[current])

        if not neighbors:
            break

        current = neighbors[seed.randrange(len(neighbors))]
        walk.append(current)

    return walk


@nx._dispatchable
@py_random_state("seed")
def weighted_random_walk(G, start, walk_length, *, weight="weight", seed=None):
    """Generate a weighted random walk starting at ``start``.

    Parameters
    ----------
    G : NetworkX graph
    start : node
        Starting node (must exist in ``G``).
    walk_length : int
        Number of steps to traverse. Must be nonnegative.
    weight : string or None, optional (default="weight")
        Edge attribute name to interpret as the transition weight. If ``None`` or
        the attribute is missing, the corresponding edge weight defaults to 1.
    seed : integer, random_state, or None (default=None)
        Indicator of random number generation state. See :ref:`randomness`.

    Returns
    ------
    walk : list
        The nodes visited, in order. The walk terminates early if no neighbor has
        positive weight.

    Raises
    ------
    ValueError
        If ``walk_length`` is negative or an edge weight is negative.
    """
    if walk_length < 0:
        raise ValueError(f"`walk_length` cannot be negative: {walk_length}")
    if start not in G:
        raise nx.NodeNotFound(start)

    walk = [start]
    current = start
    is_multigraph = G.is_multigraph()

    for _ in range(walk_length):
        neighbors = list(G[current])
        if not neighbors:
            break

        weight_map = {}
        for neighbor in neighbors:
            if is_multigraph:
                total = 0
                for data in G[
                    current
                ][
                    neighbor
                ].values():  # Iterate over the multiple edges having the same source and destination (neighbor)
                    val = data.get(weight, 1) if weight is not None else 1
                    if val < 0:
                        msg = f"Edge ({current}, {neighbor}) has negative weight {val}"
                        raise ValueError(msg)
                    total += val
            else:
                data = G[current][neighbor]
                val = data.get(weight, 1) if weight is not None else 1
                if val < 0:
                    msg = f"Edge ({current}, {neighbor}) has negative weight {val}"
                    raise ValueError(msg)
                total = val

            if total > 0:
                weight_map[neighbor] = total

        if not weight_map:
            break
        current = weighted_choice(weight_map, seed)
        walk.append(current)

    return walk
