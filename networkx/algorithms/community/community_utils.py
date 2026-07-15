"""Helper functions for community-finding algorithms."""

import networkx as nx

__all__ = ["is_cover", "is_partition"]


@nx._dispatchable
def is_partition(G, communities):
    """Returns *True* if `communities` is a partition of the nodes of `G`.

    A partition of a universe set is a family of pairwise disjoint sets
    whose union is the entire universe set.

    Parameters
    ----------
    G : NetworkX graph.

    communities : list or iterable of sets of nodes
        If not a list, the iterable is converted internally to a list.
        If it is an iterator it is exhausted.

    """
    # Alternate implementation:
    # return all(sum(1 if v in c else 0 for c in communities) == 1 for v in G)
    if not isinstance(communities, list):
        communities = list(communities)
    nodes = {n for c in communities for n in c if n in G}

    return len(G) == len(nodes) == sum(len(c) for c in communities)


@nx._dispatchable
def is_cover(G, communities):
    """Returns *True* if `communities` is a cover of the nodes of `G`.

    A *cover* of a graph is a collection of sets of nodes such that every
    node in the graph belongs to at least one set. Unlike a partition,
    sets in a cover may overlap.

    Parameters
    ----------
    G : NetworkX graph.

    communities : list or iterable of sets of nodes
        If not a list, the iterable is converted internally to a list.
        If it is an iterator it is exhausted. Nodes appearing in
        `communities` but not in `G` are ignored, mirroring the
        behavior of :func:`is_partition`.

    See Also
    --------
    is_partition

    References
    ----------
    .. [1] Lancichinetti, A., Fortunato, S., & Kertesz, J. (2009).
       "Detecting the overlapping and hierarchical community structure
       in complex networks." New J. Phys. 11, 033015.
    """
    if not isinstance(communities, list):
        communities = list(communities)
    nodes = {n for c in communities for n in c if n in G}
    return len(nodes) == len(G)
