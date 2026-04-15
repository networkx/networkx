"""Community detection and quality functions for bipartite graphs."""

import networkx as nx
from networkx.algorithms.community.community_utils import is_partition
from networkx.algorithms.community.quality import NotAPartition
from networkx.utils.decorators import not_implemented_for

__all__ = ["modularity"]


@not_implemented_for("directed")
@nx._dispatchable(name="bipartite_modularity", edge_attrs="weight")
def modularity(G, communities, nodes, weight="weight", resolution=1):
    r"""Returns Barber's bipartite modularity of the given partition.

    Bipartite modularity [1]_ adapts Newman's modularity to bipartite
    networks by replacing the configuration-model null model with one
    that respects the bipartite structure: expected edges only occur
    between the two node sets. For a bipartite graph with "red" nodes
    (one set) and "blue" nodes (the other), it is defined as

    .. math::

        Q_B = \frac{1}{m} \sum_{v=1}^{r} \sum_{w=1}^{c}
              \left( \tilde{A}_{vw} - \gamma\frac{k_v d_w}{m} \right)
              \delta(c_v, c_w)

    where $m$ is the (weighted) number of edges, $\tilde{A}$ is the
    bipartite incidence matrix, $k_v$ is the (weighted) degree of red
    node $v$, $d_w$ is the (weighted) degree of blue node $w$, $\gamma$
    is the resolution parameter, and $\delta(c_v, c_w)$ is 1 if $v$ and
    $w$ are in the same community, else 0.

    Following Clauset, Newman and Moore [2]_, this can be rewritten as a
    sum over communities:

    .. math::

        Q_B = \sum_{c=1}^{n}
              \left[ \frac{L_c}{m} - \gamma\,\frac{k_c d_c}{m^2} \right]

    where $L_c$ is the (weighted) number of intra-community edges for
    community $c$, $k_c$ is the sum of degrees of the red nodes in $c$,
    and $d_c$ is the sum of degrees of the blue nodes in $c$. This is
    the form used in the implementation.

    Note the structural analogy with the standard (unipartite) sum
    formulation `L_c/m - gamma * (k_c / 2m)^2`: the null-model term is
    a product of two degree sums, and in the undirected unipartite case
    those two sums coincide so the product becomes a square. In the
    bipartite case the sums differ (red vs. blue), so the null model
    term remains a product of two distinct terms.

    Communities in a bipartite modularity partition may contain nodes
    from both bipartite sets; the bipartite structure enters only
    through the null model.

    Parameters
    ----------
    G : NetworkX Graph
        An undirected bipartite graph.

    communities : list or iterable of sets of nodes
        These node sets must represent a partition of `G`'s nodes.
        Communities may contain nodes from both bipartite sets.

    nodes : container of nodes
        A container with all nodes in **one** bipartite node set (the
        "red" nodes). The other set is inferred as ``set(G) - set(nodes)``.
        This follows the convention used throughout the bipartite
        subpackage.

    weight : string or None, optional (default="weight")
        The edge attribute that holds the numerical value used as the
        edge weight. If None or if an edge does not have the attribute,
        that edge is treated as having weight 1.

    resolution : float (default=1)
        Resolution parameter $\gamma$. Values smaller than 1 favor
        larger communities; values greater than 1 favor smaller
        communities. Not part of Barber's original definition, but a
        standard extension consistent with
        :func:`networkx.community.modularity`.

    Returns
    -------
    Q_B : float
        The bipartite modularity of the partition.

    Raises
    ------
    NotAPartition
        If `communities` is not a valid partition of the nodes of `G`.

    NetworkXNotImplemented
        If `G` is directed. Barber's formulation is for undirected
        bipartite graphs.

    Examples
    --------
    Two disconnected :math:`K_{2,2}` components form a strong bipartite
    community structure:

    >>> from networkx.algorithms import bipartite
    >>> G = nx.Graph([(0, 2), (1, 3)])
    >>> red = {0, 1}
    >>> bipartite.modularity(G, [{0, 2}, {1, 3}], red)
    0.5

    Notes
    -----
    The functions in the bipartite package do not check that `nodes` is
    actually one side of a bipartition of `G`. It is the caller's
    responsibility to provide a valid bipartite graph and a valid
    bipartite node set.

    See Also
    --------
    networkx.algorithms.community.quality.modularity

    References
    ----------
    .. [1] Barber, M. J. (2007). "Modularity and community detection in
       bipartite networks." Physical Review E, 76(6), 066102.
       https://doi.org/10.1103/PhysRevE.76.066102
    .. [2] Clauset, A., Newman, M. E. J., and Moore, C. (2004).
       "Finding community structure in very large networks."
       Physical Review E, 70(6), 066111.
    """
    if not isinstance(communities, list):
        communities = list(communities)
    if not is_partition(G, communities):
        raise NotAPartition(G, communities)

    red = set(nodes)
    blue = set(G) - red

    degree = dict(G.degree(weight=weight))
    # Every edge has exactly one red and one blue endpoint, so the sum of
    # red degrees equals the total (weighted) number of edges m.
    m = sum(degree[v] for v in red)

    if m == 0:
        return 0.0

    norm = 1 / m**2

    def community_contribution(community):
        comm = set(community)

        # L_c: (weighted) internal edges. In a bipartite graph edges only
        # exist between the two node sets, so iterating over all edges
        # with both endpoints in comm counts each bipartite edge exactly
        # once.
        L_c = sum(wt for _, v, wt in G.edges(comm, data=weight, default=1) if v in comm)

        k_c = sum(degree[u] for u in comm & red)
        d_c = sum(degree[u] for u in comm & blue)

        return L_c / m - resolution * k_c * d_c * norm

    return sum(community_contribution(c) for c in communities)


def _bipartite_modularity_delta_partial_eval_remove(
    G, node, community, resolution, weight="weight", *, nodes, m
):
    r"""Change in bipartite modularity from removing *node* from *community*.

    One of a pair of partial-evaluation helpers following the pattern
    established in PR #8507 for CPM (``_cpm_delta_partial_eval_remove``).

    Let P = [A, B, C, ...] be a partition with *node* in A, and let
    P' = [A\{node}, B U {node}, C, ...] be the partition after moving
    *node* from A into B. The overall quality change is:

        q_delta = bipartite.modularity(G, P', nodes)
                - bipartite.modularity(G, P, nodes)

    and can be decomposed as q_delta = q_rem + q_add where:

        q_rem = _bipartite_modularity_delta_partial_eval_remove(
            G, node, A, resolution, weight, nodes=nodes, m=m)
        q_add = _bipartite_modularity_delta_partial_eval_add(
            G, node, B, resolution, weight, nodes=nodes, m=m)

    This avoids recomputing Q_B over the whole partition on every candidate
    move in a Louvain/Leiden-style optimization loop.

    The composition property also holds:
        q_rem == -q_add(G, node, A\{node}, ...)

    Unlike the CPM helpers (which return unnormalized values since CPM has
    no 1/m factor), these helpers return m-normalized values matching the
    bipartite modularity definition Q_B = sum_c [L_c/m - gamma k_c d_c/m^2].

    Parameters
    ----------
    G : NetworkX Graph
    node : node
        The node being removed from *community*.
    community : set
        The community that *node* currently belongs to (including *node*).
    resolution : float
        Resolution parameter gamma.
    weight : str or None
        Edge weight attribute.
    nodes : set
        Keyword-only. One bipartite node set ("red" nodes). Must be a set
        or frozenset for efficient membership testing.
    m : float
        Keyword-only. Total (weighted) edge count, computed as
        ``sum(G.degree(v, weight=weight) for v in nodes)``.
    """
    node_is_red = node in nodes

    # Opposite-side degree sum of the community. Since *node* contributes
    # to its own side only, opp_deg_sum is the same whether we include or
    # exclude *node* from the community.
    if node_is_red:
        opp_deg_sum = sum(
            G.degree(v, weight=weight) for v in community if v not in nodes
        )
    else:
        opp_deg_sum = sum(G.degree(v, weight=weight) for v in community if v in nodes)

    deg_u = G.degree(node, weight=weight)

    E_A = sum(
        wt
        for _, v, wt in G.edges(node, data=weight, default=1)
        if v in community and v != node
    )

    return resolution * deg_u * opp_deg_sum / m**2 - E_A / m


def _bipartite_modularity_delta_partial_eval_add(
    G, node, community, resolution, weight="weight", *, nodes, m
):
    r"""Change in bipartite modularity from inserting *node* into *community*.

    One of a pair of partial-evaluation helpers following the pattern
    established in PR #8507 for CPM (``_cpm_delta_partial_eval_add``).

    Let P = [A, B, C, ...] be a partition with *node* in A, and let
    P' = [A\{node}, B U {node}, C, ...] be the partition after moving
    *node* from A into B. The overall quality change is:

        q_delta = bipartite.modularity(G, P', nodes)
                - bipartite.modularity(G, P, nodes)

    and can be decomposed as q_delta = q_rem + q_add where:

        q_rem = _bipartite_modularity_delta_partial_eval_remove(
            G, node, A, resolution, weight, nodes=nodes, m=m)
        q_add = _bipartite_modularity_delta_partial_eval_add(
            G, node, B, resolution, weight, nodes=nodes, m=m)

    This avoids recomputing Q_B over the whole partition on every candidate
    move in a Louvain/Leiden-style optimization loop.

    The composition property also holds:
        q_rem == -q_add(G, node, A\{node}, ...)

    Unlike the CPM helpers (which return unnormalized values since CPM has
    no 1/m factor), these helpers return m-normalized values matching the
    bipartite modularity definition Q_B = sum_c [L_c/m - gamma k_c d_c/m^2].

    Parameters
    ----------
    G : NetworkX Graph
    node : node
        The node being inserted into *community*.
    community : set
        The target community (*node* is not yet a member).
    resolution : float
        Resolution parameter gamma.
    weight : str or None
        Edge weight attribute.
    nodes : set
        Keyword-only. One bipartite node set ("red" nodes). Must be a set
        or frozenset for efficient membership testing.
    m : float
        Keyword-only. Total (weighted) edge count, computed as
        ``sum(G.degree(v, weight=weight) for v in nodes)``.
    """
    node_is_red = node in nodes

    if node_is_red:
        opp_deg_sum = sum(
            G.degree(v, weight=weight) for v in community if v not in nodes
        )
    else:
        opp_deg_sum = sum(G.degree(v, weight=weight) for v in community if v in nodes)

    deg_u = G.degree(node, weight=weight)

    E_B = sum(
        wt for _, v, wt in G.edges(node, data=weight, default=1) if v in community
    )

    return E_B / m - resolution * deg_u * opp_deg_sum / m**2
