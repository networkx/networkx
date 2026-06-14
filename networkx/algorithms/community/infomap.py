"""Functions for detecting communities based on the Infomap algorithm
(the map equation).

These functions do not have NetworkX implementations.
They may only be run with an installable :doc:`backend </backends>`
that supports them.
"""

import networkx as nx

__all__ = ["infomap_communities"]


@nx._dispatchable(edge_attrs="weight", implemented_by_nx=False)
def infomap_communities(G, weight="weight", seed=None, num_trials=1):
    r"""Find communities in `G` using the Infomap algorithm (backend required)

    Infomap detects community structure by minimizing the *map equation*, the
    expected per-step description length of a random walk on the network. Unlike
    the modularity-based methods :any:`louvain_communities` and
    :any:`leiden_communities`, Infomap is a *flow-based* method: it detects
    communities by compressing the description of a random walk rather than by
    optimizing modularity. This makes it a natural fit for networks where
    community structure is carried by the direction and volume of flow. [1]_ [2]_

    This function has no NetworkX implementation; it dispatches to a backend
    such as ``infomap`` that registers an implementation.

    Parameters
    ----------
    G : NetworkX graph
        An undirected or directed graph. Edge weights are interpreted as flow.
    weight : string or None, optional (default="weight")
        The name of an edge attribute holding the numerical weight. If None,
        every edge has weight 1.
    seed : integer or None, optional (default=None)
        Seed for the backend's random number generator, for reproducible runs.
    num_trials : int, optional (default=1)
        Number of outer-most loop replications to run before picking the best
        solution (the one with the lowest codelength).

    Returns
    -------
    list
        A list of disjoint sets (a partition of `G`). Each set is one community
        and together they contain every node in `G`, with original node labels.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.karate_club_graph()
    >>> nx.community.infomap_communities(G, backend="infomap")  # doctest: +SKIP
    [{0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21}, {8, 9, 14, 15, 18, 20, 22, ...}, ...]

    References
    ----------
    .. [1] Rosvall, M. & Bergstrom, C.T. Maps of random walks on complex
       networks reveal community structure. PNAS 105, 1118-1123 (2008).
       https://doi.org/10.1073/pnas.0706851105
    .. [2] Edler, D., Holmgren, A. & Rosvall, M. The MapEquation software
       package. https://www.mapequation.org

    See Also
    --------
    :any:`louvain_communities`
    :any:`leiden_communities`
    """
    raise NotImplementedError(
        "'infomap_communities' is not implemented by networkx. "
        "Please try a different backend."
    )
