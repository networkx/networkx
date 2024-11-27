"""Function for detecting communities based on Leiden Community Detection
Algorithm"""

import itertools
from collections import defaultdict, deque

import networkx as nx
from networkx.algorithms.community import modularity
from networkx.utils import not_implemented_for, py_random_state

__all__ = ["leiden_communities", "leiden_partitions"]


@not_implemented_for("directed")
@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def leiden_communities(G, weight="weight", resolution=1, max_level=None, seed=None):
    """Find the best partition of a graph using the Leiden Community Detection
    Algorithm.

    TODO: more documentation.
    TODO: admonish that this is a backend-only function.
    TODO: add Examples section (that calls a backend?)

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    resolution : float, optional (default=1)
        If resolution is less than 1, the algorithm favors larger communities.
        Greater than 1 favors smaller communities.
    max_level : int or None, optional (default=None)
        The maximum number of levels (steps of the algorithm) to compute.
        Must be a positive integer or None. If None, then there is no max
        level and the algorithm will run until converged.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    list
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.

    References
    ----------
    .. [1] Traag, V.A., Waltman, L. & van Eck, N.J. From Leiden to Leiden: guaranteeing
       well-connected communities. Sci Rep 9, 5233 (2019). https://doi.org/10.1038/s41598-019-41695-z

    See Also
    --------
    leiden_partitions
    louvain_communities
    """
    partitions = leiden_partitions(G, weight, resolution, seed)
    if max_level is not None:
        if max_level <= 0:
            raise ValueError("max_level argument must be a positive integer or None")
        partitions = itertools.islice(partitions, max_level)
    final_partition = deque(partitions, maxlen=1)
    return final_partition.pop()


@not_implemented_for("directed")
@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def leiden_partitions(G, weight="weight", resolution=1, seed=None):
    """Yields partitions for each level of the Leiden Community Detection Algorithm

    TODO: more documentation.
    TODO: admonish that this is a backend-only function.
    TODO: add Examples section (that calls a backend?)

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    resolution : float, optional (default=1)
        If resolution is less than 1, the algorithm favors larger communities.
        Greater than 1 favors smaller communities.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Yields
    ------
    list
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.

    References
    ----------
    .. [1] Traag, V.A., Waltman, L. & van Eck, N.J. From Leiden to Leiden: guaranteeing
       well-connected communities. Sci Rep 9, 5233 (2019). https://doi.org/10.1038/s41598-019-41695-z

    See Also
    --------
    leiden_communities
    louvain_partitions
    """
    raise NotImplementedError(
        "'leiden_partitions' is not implemented by networkx. "
        "Please try a different backend."
    )
