"""Current-flow closeness centrality measures."""

import networkx as nx
from networkx.algorithms.centrality.flow_matrix import (
    CGInverseLaplacian,
    FullInverseLaplacian,
    SuperLUInverseLaplacian,
)
from networkx.utils import not_implemented_for, reverse_cuthill_mckee_ordering

__all__ = ["current_flow_closeness_centrality", "information_centrality"]


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight")
def current_flow_closeness_centrality(G, weight=None, dtype=float, solver="lu"):
    """Compute current-flow closeness centrality for nodes.

    Current-flow closeness centrality is variant of closeness
    centrality based on effective resistance between nodes in
    a network. This metric is also known as information centrality.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    weight : None or string, optional (default=None)
        If ``None``, all edge weights are considered equal.
        Otherwise holds the name of the edge attribute used as weight.
        The weight reflects the capacity or the strength of the edge.

    dtype : data type (default=float)
        Default data type for internal matrices.
        Set to ``np.float32`` for lower memory consumption.

    solver : string (default="lu")
        Type of linear solver to use for computing the flow matrix.
        Options are ``"full"`` (uses most memory), ``"lu"`` (recommended), and
        ``"cg"`` (uses least memory).

    Returns
    -------
    nodes : dictionary
        Dictionary keyed by node with current-flow closeness centrality as value.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is directed.

    NetworkXError
        If `G` is not connected.

    See Also
    --------
    closeness_centrality

    Notes
    -----
    The algorithm is based on Brandes and Fleischer [1]_
    and is only implemented for undirected graphs.
    Our implementation differs from the original in the following ways:

    - for the null graph, it outputs an empty dictionary;
    - for a graph with one node, it defines the centrality to be ``1.0``;
    - it allows multigraphs, handling multiedges by summing their weights.

    See also [2]_ for the original definition of information centrality.

    References
    ----------
    .. [1] Ulrik Brandes and Daniel Fleischer,
       Centrality Measures Based on Current Flow.
       Proc. 22nd Symp. Theoretical Aspects of Computer Science (STACS '05).
       LNCS 3404, pp. 533--544. Springer-Verlag, 2005.
       https://doi.org/10.1007/978-3-540-31856-9_44

    .. [2] Karen Stephenson and Marvin Zelen:
       Rethinking centrality: Methods and examples.
       Social Networks 11(1):1--37, 1989.
       https://doi.org/10.1016/0378-8733(89)90016-6
    """
    if (N := len(G)) <= 1:
        return {n: 1.0 for n in G}

    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")

    solvername = {
        "full": FullInverseLaplacian,
        "lu": SuperLUInverseLaplacian,
        "cg": CGInverseLaplacian,
    }
    ordering = list(reverse_cuthill_mckee_ordering(G))
    # make a copy with integer labels according to rcm ordering
    # this could be done without a copy if we really wanted to
    H = nx.relabel_nodes(G, dict(zip(ordering, range(N))))
    betweenness = dict.fromkeys(H, 0.0)  # b[n]=0 for n in H
    L = nx.laplacian_matrix(H, nodelist=range(N), weight=weight).asformat("csc")
    L = L.astype(dtype)
    C2 = solvername[solver](L, width=1, dtype=dtype)  # initialize solver
    for v in H:
        col = C2.get_row(v)
        for w in H:
            betweenness[v] += col.item(v) - 2 * col.item(w)
            betweenness[w] += col.item(v)
    return {ordering[node]: 1 / value for node, value in betweenness.items()}


information_centrality = current_flow_closeness_centrality
