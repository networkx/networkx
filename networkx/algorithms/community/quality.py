"""Functions for measuring the quality of a partition (into
communities).

"""

from itertools import combinations

import networkx as nx
from networkx.algorithms.community.community_utils import is_partition
from networkx.utils.decorators import argmap

__all__ = ["constant_potts_model", "modularity", "partition_quality"]


class NotAPartition(nx.NetworkXError):
    """Raised if a given collection is not a partition."""

    def __init__(self, G, collection):
        msg = f"{collection} is not a valid partition of the graph {G}"
        super().__init__(msg)


def _require_partition(G, partition):
    """Decorator to check that a valid partition is input to a function

    Raises :exc:`networkx.NetworkXError` if the partition is not valid.

    This decorator should be used on functions whose first two arguments
    are a graph and a partition of the nodes of that graph (in that
    order)::

        >>> @require_partition
        ... def foo(G, partition):
        ...     print("partition is valid!")
        ...
        >>> G = nx.complete_graph(5)
        >>> partition = [{0, 1}, {2, 3}, {4}]
        >>> foo(G, partition)
        partition is valid!
        >>> partition = [{0}, {2, 3}, {4}]
        >>> foo(G, partition)
        Traceback (most recent call last):
          ...
        networkx.exception.NetworkXError: `partition` is not a valid partition of the nodes of G
        >>> partition = [{0, 1}, {1, 2, 3}, {4}]
        >>> foo(G, partition)
        Traceback (most recent call last):
          ...
        networkx.exception.NetworkXError: `partition` is not a valid partition of the nodes of G

    """
    if is_partition(G, partition):
        return G, partition
    raise nx.NetworkXError("`partition` is not a valid partition of the nodes of G")


require_partition = argmap(_require_partition, (0, 1))


@nx._dispatchable
def intra_community_edges(G, partition):
    """Returns the number of intra-community edges for a partition of `G`.

    Parameters
    ----------
    G : NetworkX graph.

    partition : iterable of sets of nodes
        This must be a partition of the nodes of `G`.

    The "intra-community edges" are those edges joining a pair of nodes
    in the same block of the partition.

    """
    return sum(G.subgraph(block).size() for block in partition)


@nx._dispatchable
def inter_community_edges(G, partition):
    """Returns the number of inter-community edges for a partition of `G`.
    according to the given
    partition of the nodes of `G`.

    Parameters
    ----------
    G : NetworkX graph.

    partition : iterable of sets of nodes
        This must be a partition of the nodes of `G`.

    The *inter-community edges* are those edges joining a pair of nodes
    in different blocks of the partition.

    Implementation note: this function creates an intermediate graph
    that may require the same amount of memory as that of `G`.

    """
    # Alternate implementation that does not require constructing a new
    # graph object (but does require constructing an affiliation
    # dictionary):
    #
    #     aff = dict(chain.from_iterable(((v, block) for v in block)
    #                                    for block in partition))
    #     return sum(1 for u, v in G.edges() if aff[u] != aff[v])
    #
    MG = nx.MultiDiGraph if G.is_directed() else nx.MultiGraph
    return nx.quotient_graph(G, partition, create_using=MG).size()


@nx._dispatchable
def inter_community_non_edges(G, partition):
    """Returns the number of inter-community non-edges according to the
    given partition of the nodes of `G`.

    Parameters
    ----------
    G : NetworkX graph.

    partition : iterable of sets of nodes
        This must be a partition of the nodes of `G`.

    A *non-edge* is a pair of nodes (undirected if `G` is undirected)
    that are not adjacent in `G`. The *inter-community non-edges* are
    those non-edges on a pair of nodes in different blocks of the
    partition.

    Implementation note: this function creates two intermediate graphs,
    which may require up to twice the amount of memory as required to
    store `G`.

    """
    # Alternate implementation that does not require constructing two
    # new graph objects (but does require constructing an affiliation
    # dictionary):
    #
    #     aff = dict(chain.from_iterable(((v, block) for v in block)
    #                                    for block in partition))
    #     return sum(1 for u, v in nx.non_edges(G) if aff[u] != aff[v])
    #
    return inter_community_edges(nx.complement(G), partition)


@nx._dispatchable(edge_attrs="weight")
def modularity(G, communities, weight="weight", resolution=1):
    r"""Returns the modularity of the given partition of the graph.

    Modularity is defined in [1]_ as

    .. math::
        Q = \frac{1}{2m} \sum_{ij} \left( A_{ij} - \gamma\frac{k_ik_j}{2m}\right)
            \delta(c_i,c_j)

    where $m$ is the number of edges (or sum of all edge weights as in [5]_),
    $A$ is the adjacency matrix of `G`, $k_i$ is the (weighted) degree of $i$,
    $\gamma$ is the resolution parameter, and $\delta(c_i, c_j)$ is 1 if $i$ and
    $j$ are in the same community else 0.

    According to [2]_ (and verified by some algebra) this can be reduced to

    .. math::
       Q = \sum_{c=1}^{n}
       \left[ \frac{L_c}{m} - \gamma\left( \frac{k_c}{2m} \right) ^2 \right]

    where the sum iterates over all communities $c$, $m$ is the number of edges,
    $L_c$ is the number of intra-community links for community $c$,
    $k_c$ is the sum of degrees of the nodes in community $c$,
    and $\gamma$ is the resolution parameter.

    The resolution parameter sets an arbitrary tradeoff between intra-group
    edges and inter-group edges. More complex grouping patterns can be
    discovered by analyzing the same network with multiple values of gamma
    and then combining the results [3]_. That said, it is very common to
    simply use gamma=1. More on the choice of gamma is in [4]_.

    The second formula is the one actually used in calculation of the modularity.
    For directed graphs the second formula replaces $k_c$ with $k^{in}_c k^{out}_c$.

    Parameters
    ----------
    G : NetworkX Graph

    communities : list or iterable of set of nodes
        These node sets must represent a partition of G's nodes.

    weight : string or None, optional (default="weight")
        The edge attribute that holds the numerical value used
        as a weight. If None or an edge does not have that attribute,
        then that edge has weight 1.

    resolution : float (default=1)
        If resolution is less than 1, modularity favors larger communities.
        Greater than 1 favors smaller communities.

    Returns
    -------
    Q : float
        The modularity of the partition.

    Raises
    ------
    NotAPartition
        If `communities` is not a partition of the nodes of `G`.

    Examples
    --------
    >>> G = nx.barbell_graph(3, 0)
    >>> nx.community.modularity(G, [{0, 1, 2}, {3, 4, 5}])
    0.35714285714285715
    >>> nx.community.modularity(G, nx.community.label_propagation_communities(G))
    0.35714285714285715

    References
    ----------
    .. [1] M. E. J. Newman "Networks: An Introduction", page 224.
       Oxford University Press, 2011.
    .. [2] Clauset, Aaron, Mark EJ Newman, and Cristopher Moore.
       "Finding community structure in very large networks."
       Phys. Rev. E 70.6 (2004). <https://arxiv.org/abs/cond-mat/0408187>
    .. [3] Reichardt and Bornholdt "Statistical Mechanics of Community Detection"
       Phys. Rev. E 74, 016110, 2006. https://doi.org/10.1103/PhysRevE.74.016110
    .. [4] M. E. J. Newman, "Equivalence between modularity optimization and
       maximum likelihood methods for community detection"
       Phys. Rev. E 94, 052315, 2016. https://doi.org/10.1103/PhysRevE.94.052315
    .. [5] Blondel, V.D. et al. "Fast unfolding of communities in large
       networks" J. Stat. Mech 10008, 1-12 (2008).
       https://doi.org/10.1088/1742-5468/2008/10/P10008
    """
    if not isinstance(communities, list):
        communities = list(communities)
    if not is_partition(G, communities):
        raise NotAPartition(G, communities)

    directed = G.is_directed()
    if directed:
        out_degree = dict(G.out_degree(weight=weight))
        in_degree = dict(G.in_degree(weight=weight))
        m = sum(out_degree.values())
        norm = 1 / m**2
    else:
        out_degree = in_degree = dict(G.degree(weight=weight))
        deg_sum = sum(out_degree.values())
        m = deg_sum / 2
        norm = 1 / deg_sum**2

    def community_contribution(community):
        comm = set(community)
        L_c = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm)

        out_degree_sum = sum(out_degree[u] for u in comm)
        in_degree_sum = sum(in_degree[u] for u in comm) if directed else out_degree_sum

        return L_c / m - resolution * out_degree_sum * in_degree_sum * norm

    return sum(map(community_contribution, communities))


def _cpm_delta_partial_eval_remove(
    G, node, community, resolution, weight="weight", node_weight="node_weight"
):
    r"""
    Let P = [A, B, C, D,...] be a partition, and let P' = [A', B', C, D,...]
    be the partition obtained by moving the node u from community A to
    community B, that is where A' = A\{u} and B = B \union {u}

    The overall change in quality associated with this move is

        q_delta = constant_potts_mode(G, P') - constant_potts_model(G, P)

    Throughout the algorithm the quality q_delta will be computed by
    calculating two intermediate values q_rem and q_add satisfying the
    property that

        q_delta = q_rem + q_add

    The current function is one of a pair of similar functions
    that compute these values with

    q_rem = _cpm_delta_partial_eval_remove(G, u, A)
    q_add = _cpm_delta_partial_eval_add(G, u, B)

    """
    A_prime = community - {node}

    n_A_prime = sum(wt for u, wt in G.nodes(data=node_weight) if u in A_prime)

    u_wt = G.nodes[node][node_weight]

    E_diff = sum(wt for _, v, wt in G.edges({node}, data=weight) if v in A_prime)

    return resolution * 2 * n_A_prime * u_wt - E_diff


def _cpm_delta_partial_eval_add(
    G, node, community, resolution, weight="weight", node_weight="node_weight"
):
    r"""
    One of a pair of partial evaluation functions. See

        _cpm_delta_partial_eval_remove

    for more details.
    """
    n_B = sum(wt for u, wt in G.nodes(data=node_weight) if u in community)

    # could optimise by passing u_wt directly as a parameter rather than
    # making this lookup
    u_wt = G.nodes[node][node_weight]

    E_D = sum(wt for _, v, wt in G.edges({node}, data=weight) if v in community)
    return E_D - resolution * 2 * n_B * u_wt


def constant_potts_model(
    G,
    communities,
    weight,
    node_weight,
    resolution,
):
    r"""
    Computes the Constant Potts Model, which is a measure of quality of a
    partition. This is defined in [1]_ as

    .. math::
        Q = \sum_{C \in P} E(C,C) - \gamma n_C^2

    Where

    E(C,C) is the sum of all edge weights within the community C,
    n_C is the sum of the weights of the nodes in C.
    \gamma is the resolution parameter. See Notes below for more
    more detail on resolution parameter.

    The Constant Potts Model is similar to modularity, but overcomes the
    so-called resolution limit problem when used in community detection
    algorithms like leiden and louvain.

    The Constant Potts Model is used by default in the leiden community
    detection algorithm

    Parameters
    ----------
    G : NetworkX Graph

    communities : list or iterable of sets of nodes
        These node sets must represent a partition of G's nodes.

    weight : string or None, optional
        The edge attribute that holds the numerical value used
        as a weight. If None or an edge does not have that attribute,
        then that edge has weight 1.

    node_weight : string or None, optional
        The node attribute that holds the numerical value used as
        a weight. If None or an edge does not have tha attribute,
        then the node is treated as having weight 1

    resolution : float
        For smaller resolution values, the constant_potts_model will be
        maximised by a partition consisting of larger communities; for
        larger resolution values constant_potts_model will be maximised
        for smaller communities.

    Returns
    -------
    Q : float
        The Constant Potts Model value of the partition.

    Notes
    -----

    The interpretation of the resolution parameter \gamma is explained as
    follows in page 3 of [1]_:

        [The Constant Potts Model] tries to maximize the number of
        internal edges while at the same time keeping relatively small
        communities.

        [The resolution, \gamma] balances these two imperatives. In fact,
        the parameter \gamma acts as the inner and outer edge density
        threshold. That is, suppose there is a community [C] with [E(C, C)]
        edges and [n_C] nodes. Then it is better to split it into two
        communities r and s whenever

        .. math::
            \frac{[E(r,s)]}{2 n_r n_s} < \gamma

        where [E(r,s)] is the number [or weighted sum] of links between
        community r and s. This ratio is exactly the density of links between
        community r and s. So, the link density between communities should be
        lower than \gamma, while the link density within communities should
        be higher than \gamma.

    References
    ----------
    .. [1] V.A. Traag, P. Van Dooren, Y. Nesterov "Narrow scope for
       resolution-limit-free community detection"
       <https://arxiv.org/abs/1104.3083>
    """

    def community_contribution(community):
        comm = set(community)
        E_c = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm)

        n_c = sum(G.nodes[node].get(node_weight, 1) for node in community)

        return E_c - resolution * (n_c**2)

    return sum(community_contribution(c) for c in communities)


@require_partition
@nx._dispatchable
def partition_quality(G, partition):
    """Returns the coverage and performance of a partition of G.

    The *coverage* of a partition is the ratio of the number of
    intra-community edges to the total number of edges in the graph.

    The *performance* of a partition is the number of
    intra-community edges plus inter-community non-edges divided by the total
    number of potential edges.

    This algorithm has complexity $O(C^2 + L)$ where C is the number of
    communities and L is the number of links.

    Parameters
    ----------
    G : NetworkX graph

    partition : sequence
        Partition of the nodes of `G`, represented as a sequence of
        sets of nodes (blocks). Each block of the partition represents a
        community.

    Returns
    -------
    (float, float)
        The (coverage, performance) tuple of the partition, as defined above.

    Raises
    ------
    NetworkXError
        If `partition` is not a valid partition of the nodes of `G`.

    Notes
    -----
    If `G` is a multigraph;
        - for coverage, the multiplicity of edges is counted
        - for performance, the result is -1 (total number of possible edges is not defined)

    References
    ----------
    .. [1] Santo Fortunato.
           "Community Detection in Graphs".
           *Physical Reports*, Volume 486, Issue 3--5 pp. 75--174
           <https://arxiv.org/abs/0906.0612>
    """

    node_community = {}
    for i, community in enumerate(partition):
        for node in community:
            node_community[node] = i

    # `performance` is not defined for multigraphs
    if not G.is_multigraph():
        # Iterate over the communities, quadratic, to calculate `possible_inter_community_edges`
        possible_inter_community_edges = sum(
            len(p1) * len(p2) for p1, p2 in combinations(partition, 2)
        )

        if G.is_directed():
            possible_inter_community_edges *= 2
    else:
        possible_inter_community_edges = 0

    # Compute the number of edges in the complete graph -- `n` nodes,
    # directed or undirected, depending on `G`
    n = len(G)
    total_pairs = n * (n - 1)
    if not G.is_directed():
        total_pairs //= 2

    intra_community_edges = 0
    inter_community_non_edges = possible_inter_community_edges

    # Iterate over the links to count `intra_community_edges` and `inter_community_non_edges`
    for e in G.edges():
        if node_community[e[0]] == node_community[e[1]]:
            intra_community_edges += 1
        else:
            inter_community_non_edges -= 1

    coverage = intra_community_edges / len(G.edges)

    if G.is_multigraph():
        performance = -1.0
    else:
        performance = (intra_community_edges + inter_community_non_edges) / total_pairs

    return coverage, performance
