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

    Yields
    ------
    node
        The next node in the random walk

    Raises
    ------
    nx.NodeNotFound
        If `start` is not in `G`
    ValueError
        If `weight` is not None and a negative weight is encountered.

    Examples
    --------
    The `random_walk` generator is designed to be very flexible, thus there is
    no default condition for terminating a walk.

    .. warning::
       Calling ``list(nx.random_walk(G, start=n))`` will result in an infinite
       loop if `G` is undirected (or strongly connected if directed).

    >>> G = nx.cycle_graph(10)

    To generate a walk with a given length:

    >>> walk_length = 4
    >>> rw = nx.random_walk(G, start=0, seed=99)
    >>> [next(rw) for _ in range(walk_length)]
    [0, 9, 0, 1]

    or with `itertools.islice`:

    >>> import itertools

    >>> rw = nx.random_walk(G, start=0, seed=99)
    >>> list(itertools.islice(rw, walk_length))
    [0, 9, 0, 1]

    One may want to terminate a walk when a specific node (or set of nodes) is
    reached; for example, transitioning from one "barbell" to the other:

    >>> G = nx.barbell_graph(5, 0)
    >>> terminal_nodes = set(range(5, 10))
    >>> rwg = nx.random_walk(G, start=0, seed=999999)
    >>> list(itertools.takewhile(lambda n: n not in terminal_nodes, rwg))
    [0, 2, 1, 2, 4]

    Or perform a walk with a termination probability for each step:

    >>> import random
    >>> random.seed(5040)
    >>> termination_probability = 0.25

    >>> G = nx.complete_graph(10)
    >>> list(
    ...     itertools.takewhile(
    ...         lambda _: random.random() > termination_probability,
    ...         nx.random_walk(G, start=0, seed=999),
    ...     )
    ... )
    [0, 2, 9, 7]

    `random_walk` can be combined with distance constraints to sample local
    regions in a graph:

    >>> G = nx.balanced_tree(2, 3)
    >>> distance = nx.single_source_shortest_path_length(G, source=0)
    >>> distance_limit = 3

    >>> list(
    ...     itertools.takewhile(
    ...         lambda n: distance[n] < distance_limit,
    ...         nx.random_walk(G, start=0, seed=99),
    ...     )
    ... )
    [0, 2, 5, 2, 6, 2, 0, 1, 0, 1, 3]

    The `weight` keyword can be used to indicate an edge attribute to use for
    weighted sampling:

    >>> G = nx.path_graph(3)
    >>> nx.set_edge_attributes(G, {(0, 1): 2, (1, 2): 10}, name="weight")
    >>> rw = nx.random_walk(G, start=1, weight="weight", seed=2048)
    >>> list(itertools.islice(rw, 10))
    [1, 2, 1, 2, 1, 2, 1, 2, 1, 0]

    When performing a weighted walk, edges with 0 weight are ignored:

    >>> G = nx.star_graph(5)
    >>> nx.set_edge_attributes(G, {(0, n): 0 for n in range(2, len(G))}, name="weight")
    >>> rw = nx.random_walk(G, start=0, weight="weight")
    >>> list(itertools.islice(rw, 4))
    [0, 1, 0, 1]

    For directed graphs, if a node with 0 outdegree is reached, the walk will
    terminate:

    >>> G = nx.path_graph(5, create_using=nx.DiGraph)
    >>> list(nx.random_walk(G, start=3))
    [3, 4]

    Self-loop edges are included in the neighbor sampling:

    >>> G = nx.Graph([(0, 0)])
    >>> list(itertools.islice(nx.random_walk(G, start=0), 5))
    [0, 0, 0, 0, 0]
    """
    if start not in G:
        raise nx.NodeNotFound(start)

    node = start
    yield node
    while nbrs := G._adj[node]:
        if weight is None:
            node = seed.choice(list(nbrs))
        else:
            wts = [nbr.get(weight, 1) for nbr in nbrs.values()]
            if any(w < 0 for w in wts):
                raise ValueError("random_walk doesn't support negative weights")
            if sum(wts) == 0:
                return
            node = seed.choices(list(nbrs), weights=wts, k=1)[0]

        yield node
