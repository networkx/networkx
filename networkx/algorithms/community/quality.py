"""Functions for measuring the quality of a partition (into
communities).

"""

from collections import defaultdict
from itertools import combinations
from math import isfinite, log2

import networkx as nx
from networkx.algorithms.community.community_utils import is_cover, is_partition
from networkx.utils.decorators import argmap, not_implemented_for

__all__ = [
    "constant_potts_model",
    "map_equation",
    "modularity",
    "overlapping_modularity",
    "partition_quality",
]


class NotAPartition(nx.NetworkXError):
    """Raised if a given collection is not a partition."""

    def __init__(self, G, collection):
        msg = f"{collection} is not a valid partition of the graph {G}"
        super().__init__(msg)


# ---------------------------------------------------------------------------
# The map equation
#
# Infomap pictures a random walker stepping along the (weighted, possibly
# directed) edges of the network. The map equation [Rosvall & Bergstrom 2008]
# is the average number of bits needed to describe one step of that walk when
# the walk is encoded with a *two-level* codebook:
#
#   * one **index codebook** names the modules and is used whenever the walker
#     crosses from one module into another, and
#   * one **module codebook** per module names the nodes inside it (plus an
#     "exit" symbol) and is used while the walker stays within that module.
#
# A partition that keeps the walker inside modules for long stretches makes
# module switches -- the shared index codebook -- rare, so the description is
# short. Minimizing the codelength therefore reveals community structure. Each
# codebook is an entropy-optimal (Huffman-style) code, so its per-step cost is
# the Shannon entropy of its symbol frequencies and the whole map equation
# reduces to sums of ``p * log2(p)`` terms over node and module visit/exit
# rates -- which is what the helpers below assemble.
# ---------------------------------------------------------------------------


def _plogp(p):
    """Return ``p * log2(p)``, using the convention ``0 * log2(0) = 0``.

    Shannon entropy is ``H = -sum(_plogp(p_i))``, so every codebook cost in the
    map equation is built from these terms.
    """
    return p * log2(p) if p > 0 else 0.0


def _undirected_flow(G, weight):
    r"""Random-walk flow of an undirected graph: ``(visit_rate, link_flows)``.

    On an undirected graph the walker's stationary distribution is known in
    closed form: it visits a node in proportion to the node's (weighted) degree,
    :math:`p_\alpha = k_\alpha / 2m`. A self-loop is one transition that keeps
    the walker in place, so -- as in Infomap -- it counts *once* toward the
    degree and the normalization, giving :math:`2m = 2\sum w - \sum_{self} w`
    (NetworkX's ``degree`` counts a self-loop twice, so subtract one copy). The
    per-step probability of traversing a particular edge is :math:`w / 2m`;
    ``link_flows`` emits each edge in *both* directions with that flow, so that
    summing the flow crossing a module's boundary later gives the rate at which
    the walker enters or leaves it. A self-loop never crosses a boundary, so it
    is emitted once.
    """
    self_loop = {}
    for u, v, w in G.edges(data=weight, default=1):
        if u == v:
            self_loop[u] = self_loop.get(u, 0.0) + w
    # 2m with self-loops counted once (Infomap's undirected normalization).
    total = 2 * G.size(weight=weight) - sum(self_loop.values())
    if total == 0:  # no edges (or only zero-weight edges), no flow
        return {node: 0.0 for node in G}, []
    visit_rate = {
        node: (strength - self_loop.get(node, 0.0)) / total
        for node, strength in G.degree(weight=weight)
    }

    def link_flows():
        for u, v, w in G.edges(data=weight, default=1):
            flow = w / total
            yield u, v, flow
            if u != v:
                yield v, u, flow

    return visit_rate, link_flows()


def _directed_flow(G, weight, teleportation_prob, tol=1e-13):
    r"""Random-walk flow of a directed graph: ``(visit_rate, link_flows)``.

    A directed graph has no closed-form stationary distribution, and a plain
    walk can get stuck (in sinks or cycles). Infomap uses the PageRank remedy:
    with probability ``teleportation_prob`` the walker teleports instead of
    following a link, which makes the walk ergodic. The recorded distribution
    ``pi`` is exactly :func:`~networkx.algorithms.link_analysis.pagerank_alg.pagerank`
    with damping ``1 - teleportation_prob`` and teleportation weighted by
    out-degree (so dangling nodes redistribute their flow the same way).

    Teleportation is a modelling device, not part of the structure we want to
    describe, so the rates that get *coded* come from *unrecorded* teleportation:
    one further link-following step (with no teleportation) on top of ``pi``
    yields the visit rates and link flows the codebooks are built from.
    """
    nodes = list(G)
    out_strength = dict(G.out_degree(weight=weight))
    dangling = [u for u in nodes if out_strength[u] == 0]
    sum_out = sum(out_strength.values())
    if sum_out == 0:  # no out-links anywhere: uniform visits, nothing crosses
        return {u: 1 / len(nodes) for u in nodes}, []

    # Teleport in proportion to out-degree (Infomap's default "to links"); this
    # is exactly PageRank's personalization (and dangling) vector.
    teleport = {u: out_strength[u] / sum_out for u in nodes}
    pi = nx.pagerank(
        G,
        alpha=1 - teleportation_prob,
        personalization=teleport,
        dangling=teleport,
        weight=weight,
        tol=tol,
        max_iter=1000,
    )

    # Unrecorded step: spread ``pi`` once more along links only (no teleporting),
    # renormalizing away the flow that would have teleported. The result is the
    # visit rate and per-link flow the codebooks are built from.
    sum_node_rank = 1 - sum(pi[u] for u in dangling)
    visit_rate = {u: 0.0 for u in nodes}
    link_flows = []
    for u, v, w in G.edges(data=weight, default=1):
        # A dangling source (zero out-strength) redistributes its flow purely by
        # teleportation, already captured in ``pi``; its links carry no recorded
        # flow, so skip them -- and avoid dividing by its zero out-strength.
        if out_strength[u] == 0:
            continue
        flow = pi[u] * w / out_strength[u] / sum_node_rank
        visit_rate[v] += flow
        link_flows.append((u, v, flow))
    return visit_rate, link_flows


@nx._dispatchable(edge_attrs="weight")
def map_equation(G, communities, weight="weight", teleportation_prob=0.15):
    r"""Return the two-level map equation codelength of a partition of `G`.

    The map equation [1]_ is the expected per-step description length, in bits,
    of a random walk on `G` encoded with a two-level codebook given by
    `communities`. Infomap finds communities by minimizing this quantity.

    The codelength is the map equation

    .. math::
        L = q_\curvearrowleft H(\mathcal{Q})
            + \sum_i p^i_\circlearrowright H(\mathcal{P}^i)

    the index-codebook entropy :math:`H(\mathcal{Q})`, used on every module
    switch at the total exit rate :math:`q_\curvearrowleft`, plus each module
    codebook entropy :math:`H(\mathcal{P}^i)`, used at rate
    :math:`p^i_\circlearrowright` (module :math:`i`'s total node visit rate plus
    its exit rate). A partition that keeps the walk inside modules makes
    switches rare, so the codelength is short. (Internally this is evaluated by
    the equivalent closed form in sums of :math:`x \log_2 x`.)

    For an undirected graph the visit rate of a node is proportional to its
    (weighted) degree, :math:`p_\alpha = k_\alpha / 2m`. For a directed graph
    the visit rates are the stationary distribution of a random walk with
    teleportation (as in PageRank and Infomap's default directed flow model).

    Parameters
    ----------
    G : NetworkX graph
        An undirected or directed graph. Edge weights are interpreted as flow.
    communities : list or iterable of set of nodes
        A partition of the nodes of `G`.
    weight : string or None, optional (default="weight")
        Edge attribute holding the numerical weight. If None, every edge has
        weight 1.
    teleportation_prob : float, optional (default=0.15)
        Teleportation probability for the directed-flow random walk. Ignored
        for undirected graphs.

    Returns
    -------
    float
        The codelength in bits. Lower is better.

    Raises
    ------
    NetworkXError
        If `communities` is not a partition of the nodes of `G`.

    References
    ----------
    .. [1] Rosvall, M. & Bergstrom, C.T. Maps of random walks on complex
       networks reveal community structure. PNAS 105, 1118-1123 (2008).
       https://doi.org/10.1073/pnas.0706851105
    """
    communities = [set(c) for c in communities]
    if not is_partition(G, communities):
        raise nx.NetworkXError("`communities` is not a partition of the nodes of `G`")
    module_of = {node: i for i, c in enumerate(communities) for node in c}
    visit_rate, link_flows = _flow(G, weight, teleportation_prob)
    return _codelength(visit_rate, link_flows, module_of)


def _flow(G, weight="weight", teleportation_prob=0.15):
    """Return ``(visit_rate, link_flows)`` for `G`, dispatching on direction.

    The flow depends only on the graph, not on any partition, so it is computed
    once and reused across many codelength evaluations. ``link_flows`` is a
    materialized list of ``(source, target, flow)`` triples.

    Note this is plain dict/list flow, not an annotated graph. The quantity is
    random-walk *flow* (computed once), not edge weight, and the optimizer's
    inner loop wants O(1) dict access -- it builds adjacency dicts from these,
    just as ``louvain._one_level`` builds them from ``G``. Carrying flow
    alongside ``G`` also keeps aggregation from copying/mutating graphs.
    """
    # Flow is a probability distribution, so weights must be finite and
    # non-negative; reject ill-defined inputs instead of returning a
    # clean-looking but meaningless codelength.
    for _, _, w in G.edges(data=weight, default=1):
        if not isfinite(w) or w < 0:
            raise ValueError("edge weights must be finite and non-negative")
    if G.is_directed():
        return _directed_flow(G, weight, teleportation_prob)
    visit_rate, link_flows = _undirected_flow(G, weight)
    return visit_rate, list(link_flows)


def _codelength(visit_rate, link_flows, module_of):
    r"""Assemble the two-level map equation codelength, in bits per step.

    From the random-walk flow (``visit_rate`` per node and the directed
    ``link_flows``) and a ``node -> module`` assignment, sum the three groups of
    terms, one for each codebook role:

    * **node term** -- naming nodes inside their modules costs the entropy of
      the node visit rates, :math:`-\sum_\alpha plogp(p_\alpha)`.
    * **index term** -- the index codebook is used on every module switch. Its
      symbols are the modules, with frequencies equal to the module *enter*
      rates :math:`e_i`, and it is used at the total switching rate
      :math:`Q = \sum_i e_i`, costing :math:`plogp(Q) - \sum_i plogp(e_i)`.
    * **module term** -- each module codebook carries, beyond its nodes, one
      "exit" symbol at rate :math:`x_i`; the extra cost of mixing that exit into
      module :math:`i` (visit rate :math:`p_i`) is
      :math:`plogp(x_i + p_i) - plogp(x_i)`.

    A module's *exit* flow is the flow on links leaving it; its *enter* flow is
    the flow on links entering it. On a directed graph these differ -- the index
    codebook is driven by enter flow -- while on an undirected graph
    ``link_flows`` carries both directions, so they coincide. Module ids may be
    any non-negative integers; empty modules contribute nothing.
    """
    n_modules = (max(module_of.values()) + 1) if module_of else 0

    # p_i: total visit rate of each module (entropy of node names lives here).
    module_visit = [0.0] * n_modules
    for node, visits in visit_rate.items():
        module_visit[module_of[node]] += visits

    # e_i / x_i: flow entering / leaving each module. Only boundary-crossing
    # link flow counts; flow that stays inside a module is never coded by the
    # index codebook.
    module_enter = [0.0] * n_modules
    module_exit = [0.0] * n_modules
    for source, target, flow in link_flows:
        src_module, tgt_module = module_of[source], module_of[target]
        if src_module != tgt_module:
            module_exit[src_module] += flow
            module_enter[tgt_module] += flow

    total_switching = sum(module_enter)  # Q; equals sum(module_exit)
    index_term = _plogp(total_switching) - sum(_plogp(e) for e in module_enter)
    node_term = -sum(_plogp(p) for p in visit_rate.values())
    module_term = sum(
        _plogp(exit_rate + visit) - _plogp(exit_rate)
        for exit_rate, visit in zip(module_exit, module_visit)
    )
    return index_term + node_term + module_term


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
    For directed graphs the second formula replaces $k_c^2$ with $k^{in}_c k^{out}_c$.

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


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight")
def overlapping_modularity(G, communities, *, weight="weight", resolution=1):
    r"""Returns Shen et al.'s extended modularity for an overlapping cover.

    Standard modularity assumes each node belongs to exactly one
    community. Shen et al. [1]_ extend modularity to overlapping
    communities by discounting each node's contribution by the number of
    communities it belongs to:

    .. math::
        EQ = \frac{1}{2m} \sum_{i} \sum_{v \in C_i, w \in C_i}
             \frac{1}{O_v O_w}\!\left[ A_{vw} - \gamma\,\frac{k_v k_w}{2m}\right]

    where the outer sum runs over communities $C_i$ in the cover, $A_{vw}$
    is the (weighted) adjacency, $k_v$ is the (weighted) degree of $v$,
    $O_v$ is the number of communities to which $v$ belongs, $m$ is the
    total (weighted) edge count, and $\gamma$ is the resolution parameter.

    The factor $1 / (O_v O_w)$ discounts contributions from nodes that
    belong to many communities: a node in 3 communities contributes 1/3
    of its modularity share to each.

    The resolution parameter $\gamma$ is not part of the original Shen
    definition; it is added for consistency with
    :func:`~networkx.algorithms.community.quality.modularity`. Setting
    $\gamma = 1$ recovers Shen's EQ exactly.

    Implementation uses the equivalent community-sum form

    .. math::
        EQ = \sum_{i}\!\left[\frac{\tilde{L}_{C_i}}{m}
             - \gamma\!\left(\frac{\tilde{k}_{C_i}}{2m}\right)^{\!2}\right]

    where $\tilde{L}_{C_i} = \sum_{(v,w) \in L_{C_i}} 1/(O_v O_w)$ is the
    overlap-discounted intra-community edge count and
    $\tilde{k}_{C_i} = \sum_{v \in C_i} k_v / O_v$ is the
    overlap-discounted degree sum. When the cover is actually a partition
    ($O_v = 1$ for all $v$), $EQ$ reduces to the standard modularity $Q$.

    Parameters
    ----------
    G : NetworkX Graph
        An undirected graph.

    communities : iterable of sets of nodes
        A cover of `G`'s nodes: every node must appear in at least one
        set, but sets may overlap. Accepts the output of any NetworkX
        overlapping community-detection algorithm such as
        :func:`~networkx.algorithms.community.kclique.k_clique_communities`.

    weight : string or None, optional (default="weight")
        Edge attribute holding the numerical edge weight. If None, or if
        an edge does not have the attribute, that edge has weight 1.

    resolution : float, optional (default=1)
        Resolution parameter $\gamma$. As in standard modularity, values
        smaller than 1 favor larger communities and values greater than
        1 favor smaller communities. The degree of overlap in the cover
        is independent of $\gamma$, since $\gamma$ rescales only the
        null-model term.

    Returns
    -------
    EQ : float
        The extended modularity of the cover.

    Raises
    ------
    NetworkXError
        If `communities` is not a valid cover of the nodes of `G` (some
        node in `G` does not belong to any community).

    NetworkXNotImplemented
        If `G` is directed. Shen's formulation is for undirected graphs.

    Examples
    --------
    On a partition, EQ equals standard modularity (up to floating-point
    summation order):

    >>> G = nx.barbell_graph(3, 0)
    >>> partition = [{0, 1, 2}, {3, 4, 5}]
    >>> Q = nx.community.modularity(G, partition)
    >>> EQ = nx.community.overlapping_modularity(G, partition)
    >>> abs(Q - EQ) < 1e-12
    True

    Evaluate an overlapping cover produced by ``k_clique_communities``.
    Two K_5 cliques sharing nodes 3 and 4 yield a 2-community cover:

    >>> G = nx.complete_graph(5)
    >>> G.add_edges_from(nx.complete_graph(range(3, 8)).edges())
    >>> cover = list(nx.community.k_clique_communities(G, 4))
    >>> round(nx.community.overlapping_modularity(G, cover), 3)
    0.158

    See Also
    --------
    modularity
    is_cover

    References
    ----------
    .. [1] Shen, H., Cheng, X., Cai, K., & Hu, M. B. (2009). "Detect
       overlapping and hierarchical community structure in networks."
       Physica A, 388(8), 1706-1712.
       https://doi.org/10.1016/j.physa.2008.12.021
    .. [2] Lancichinetti, A., Fortunato, S., & Kertesz, J. (2009).
       "Detecting the overlapping and hierarchical community structure
       in complex networks." New J. Phys. 11, 033015. (Cover definition.)
    """
    if not isinstance(communities, list):
        communities = list(communities)
    if not is_cover(G, communities):
        raise nx.NetworkXError("`communities` is not a valid cover of the nodes of G")

    # Membership count O_v for each node
    membership = defaultdict(int)
    for community in communities:
        for node in community:
            if node in G:
                membership[node] += 1

    degree = dict(G.degree(weight=weight))
    deg_sum = sum(degree.values())  # equals 2m for undirected

    if deg_sum == 0:
        return 0.0

    def community_contribution(community):
        comm = set(community)

        # Tilde-L: overlap-discounted intra-community edge weight.
        # Each edge (u, v) with both endpoints in comm contributes
        # w_uv / (O_u * O_v) exactly once.
        L_c_tilde = sum(
            wt / (membership[u] * membership[v])
            for u, v, wt in G.edges(comm, data=weight, default=1)
            if v in comm
        )

        # Tilde-k: overlap-discounted degree sum.
        k_c_tilde = sum(degree[u] / membership[u] for u in comm)

        # Per-community contribution: 2*L_tilde/(2m) - gamma*(k_tilde/(2m))^2.
        return 2 * L_c_tilde / deg_sum - resolution * (k_c_tilde / deg_sum) ** 2

    return sum(community_contribution(c) for c in communities)


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

    dir_factor = 2 if G.is_directed() else 1

    A_prime = community - {node}

    n_A_prime = sum(wt for u, wt in G.nodes(data=node_weight) if u in A_prime)

    u_wt = G.nodes[node][node_weight]

    E_diff = sum(wt for _, v, wt in G.edges({node}, data=weight) if v in A_prime)

    if G.is_directed():
        E_diff += sum(wt for _, v, wt in G.edges(A_prime, data=weight) if v in {node})

    return resolution * dir_factor * n_A_prime * u_wt - E_diff


def _cpm_delta_partial_eval_add(
    G, node, community, resolution, weight="weight", node_weight="node_weight"
):
    r"""
    One of a pair of partial evaluation functions. See

        _cpm_delta_partial_eval_remove

    for more details.
    """
    dir_factor = 2 if G.is_directed() else 1

    n_B = sum(wt for u, wt in G.nodes(data=node_weight) if u in community)

    # could optimise by passing u_wt directly as a parameter rather than
    # making this lookup
    u_wt = G.nodes[node][node_weight]

    E_D = sum(wt for _, v, wt in G.edges({node}, data=weight) if v in community)
    if G.is_directed():
        E_D += sum(wt for _, v, wt in G.edges(community, data=weight) if v in {node})

    return E_D - resolution * dir_factor * n_B * u_wt


def _quality_delta_cpm_directed(
    G, nodes_to_add, community, resolution, weight="weight", node_weight="node_weight"
):
    n_size = sum(G.nodes[u][node_weight] for u in nodes_to_add)
    comm_size = sum(G.nodes[u][node_weight] for u in community)
    E_D_out = sum(
        wt for _, v, wt in G.edges(nodes_to_add, data=weight) if v in community
    )
    E_D_in = sum(
        wt for _, v, wt in G.edges(community, data=weight) if v in nodes_to_add
    )
    return E_D_out + E_D_in - resolution * 2 * n_size * comm_size


def _quality_delta_cpm_undirected(
    G, nodes_to_add, community, resolution, weight="weight", node_weight="node_weight"
):
    n_size = sum(G.nodes[u][node_weight] for u in nodes_to_add)
    comm_size = sum(G.nodes[u][node_weight] for u in community)
    E_D = sum(wt for _, v, wt in G.edges(nodes_to_add, data=weight) if v in community)
    return E_D - resolution * n_size * comm_size


def constant_potts_model(
    G,
    communities,
    weight="weight",
    node_weight="node_weight",
    resolution=1,
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
    is_directed = G.is_directed()
    if is_directed:

        def community_contribution(community):
            comm = set(community)
            E_c = sum(
                wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm
            )

            n_c = sum(G.nodes[node].get(node_weight, 1) for node in community)

            return E_c - resolution * (n_c**2)
    else:

        def community_contribution(community):
            comm = set(community)
            E_c = sum(
                wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm
            )

            n_c = sum(G.nodes[node].get(node_weight, 1) for node in community)

            return E_c - resolution * (n_c**2) / 2

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
           *Physics Reports*, Volume 486, Feb 2010, Issue 3--5 pp. 75--174
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
