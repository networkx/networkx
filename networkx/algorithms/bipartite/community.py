"""Community detection and quality functions for bipartite graphs."""

from collections import defaultdict

import networkx as nx
from networkx.algorithms.community.community_utils import is_partition
from networkx.algorithms.community.quality import NotAPartition
from networkx.utils.decorators import not_implemented_for, py_random_state

__all__ = ["modularity", "lpawb_plus_communities"]


@not_implemented_for("directed")
@nx._dispatchable(name="bipartite_modularity", edge_attrs="weight")
def modularity(G, communities, nodes, *, weight="weight", resolution=1):
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
    bipartite adjacency matrix, $k_v$ is the (weighted) degree of red
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
        Resolution parameter $\gamma$. With the default ``resolution=1``,
        $Q_B$ reduces to Barber's original definition. Values smaller
        than 1 favor larger communities; values greater than 1 favor
        smaller communities. The resolution parameter is not part of
        Barber's original definition, but a standard extension
        consistent with :func:`networkx.community.modularity`.

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

    >>> G = nx.Graph([(0, 2), (1, 3)])
    >>> red = {0, 1}
    >>> nx.bipartite.modularity(G, [{0, 2}, {1, 3}], red)
    0.5

    Notes
    -----
    The functions in the bipartite package do not check that `nodes` is
    actually one side of a bipartition of `G`. It is the caller's
    responsibility to provide a valid bipartite graph and a valid
    bipartite node set.

    See Also
    --------
    modularity

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


def _bipartite_modularity_merge_delta(
    G,
    community_a,
    community_b,
    resolution,
    weight="weight",
    *,
    red_degree_attr="red_degree",
    blue_degree_attr="blue_degree",
    m,
):
    r"""Change in bipartite modularity from merging two disjoint communities.

    Computes ``Q_B(P') - Q_B(P)`` where P contains `community_a` and
    `community_b` as separate communities and P' is obtained by replacing
    them with their union ``community_a U community_b``.

    For bipartite modularity ``Q_B = sum_c [L_c/m - gamma k_c d_c / m^2]``,
    the merge delta has the closed form

        merge_delta = E(A, B) / m - gamma * (k_A d_B + k_B d_A) / m^2

    where ``E(A, B)`` is the sum of edge weights between A and B,
    ``k_C`` is the sum of the "red" degrees of nodes in C, and ``d_C``
    is the sum of the "blue" degrees of nodes in C.

    **Attribute-based interface.** Rather than identifying each node
    with a single bipartite side (which breaks once Louvain/Leiden has
    aggregated communities into super-nodes that mix both colors), this
    helper reads per-node ``red_degree_attr`` and ``blue_degree_attr``
    attributes. On the original bipartite graph a red node has
    ``red_degree = G.degree(v)`` and ``blue_degree = 0`` (and vice
    versa). On an aggregated graph each super-node carries the sums
    of both attributes over its constituent nodes; both may be
    nonzero. This is the same pattern used for directed modularity
    (in-degree / out-degree tracked as separate attributes).

    `community_a` and `community_b` must be disjoint and non-empty.
    Self-loops are tolerated: on the original graph they are absent by
    the bipartite convention, and on aggregated graphs they represent
    intra-community edges which are not part of ``E(A, B)`` and are
    correctly excluded by the ``v in community_b`` filter below.

    Parameters
    ----------
    G : NetworkX Graph
        A graph whose nodes carry the red/blue degree attributes. May
        be an original bipartite graph or an aggregated graph produced
        by a multilevel optimizer.
    community_a, community_b : set
        Two disjoint communities to merge.
    resolution : float
        Resolution parameter gamma.
    weight : str or None
        Edge weight attribute.
    red_degree_attr : str
        Keyword-only. Name of the node attribute holding the
        "red-side" contribution to the node's degree.
    blue_degree_attr : str
        Keyword-only. Name of the node attribute holding the
        "blue-side" contribution to the node's degree.
    m : float
        Keyword-only. Total (weighted) edge count, a graph-level
        invariant preserved across aggregation.
    """
    # Iterate over community members rather than all of G.nodes
    nodes = G.nodes
    k_a = sum(nodes[v].get(red_degree_attr, 0) for v in community_a)
    d_a = sum(nodes[v].get(blue_degree_attr, 0) for v in community_a)
    k_b = sum(nodes[v].get(red_degree_attr, 0) for v in community_b)
    d_b = sum(nodes[v].get(blue_degree_attr, 0) for v in community_b)

    # E(A, B): edges with one endpoint in A and the other in B. Iterate
    # edges incident to community_a and keep those landing in community_b.
    # Self-loops (intra-community edges on aggregated super-nodes) are
    # filtered out because they have both endpoints in community_a.
    E_cross = sum(
        wt
        for _, v, wt in G.edges(community_a, data=weight, default=1)
        if v in community_b
    )

    return E_cross / m - resolution * (k_a * d_b + k_b * d_a) / m**2


@not_implemented_for("directed")
@py_random_state("seed")
@nx._dispatchable(name="lpawb_plus_communities", edge_attrs="weight")
def lpawb_plus_communities(G, nodes, weight="weight", seed=None):
    r"""Find communities in a bipartite graph using LPAwb+.

    LPAwb+ (Beckett, 2016) [1]_ is a two-stage algorithm that maximizes
    Barber's weighted bipartite modularity $Q_B$ [2]_:

    .. math::

        Q_B = \sum_{c} \left[\frac{L_c}{m} - \frac{k_c d_c}{m^2}\right]

    where $m$ is the total (weighted) number of edges, $L_c$ is the
    (weighted) internal edge count of community $c$, and $k_c$, $d_c$
    are the degree sums of the two bipartite sets within $c$. See
    :func:`modularity` for details.

    The algorithm proceeds as follows. Each node starts in its own
    community.

    **Stage 1 (label propagation):** blue-side and red-side labels are
    alternately updated in random order; each node picks the community
    label that maximizes its local contribution to $Q_B$ using the
    update rule of Beckett Eq. 2.5. For a red node $x$ the best label
    $g$ is

    .. math::

        g_x^\text{new} = \operatorname*{argmax}_g
            \left( N_{xg} - \frac{y_x Z_g}{M} \right)

    where $N_{xg}$ is the sum of edge weights from $x$ to blue nodes
    with label $g$, $y_x$ is the strength of $x$, $Z_g$ is the total
    strength of blue nodes with label $g$, and $M$ is the total edge
    weight. Blue nodes use the symmetric rule. Ties (including ties
    with the node's current label) are broken in favor of keeping the
    current label, which guarantees monotonic improvement. Stage 1
    repeats until no label changes.

    **Stage 2 (agglomeration):** each existing module looks for its
    "best partner" --- the other module whose merger gives the largest
    positive increase in $Q_B$. If a pair of modules is mutually each
    other's best partner and merging them strictly increases $Q_B$,
    they are merged. Stage 1 is then re-run on the coarsened partition.
    The outer loop repeats until no improving merge is found.

    The merge delta for two modules $A$ and $B$ is

    .. math::

        \Delta Q_B = \frac{e_{AB}}{m}
            - \frac{k_A d_B + k_B d_A}{m^2}

    where $e_{AB}$ is the (weighted) number of edges between nodes
    labelled $A$ and nodes labelled $B$, and $k_\cdot$, $d_\cdot$ are
    per-module red/blue degree sums.

    Parameters
    ----------
    G : NetworkX Graph
        An undirected bipartite graph. May be weighted.

    nodes : container of nodes
        A container with all the nodes in one bipartite set. The other
        set is inferred as ``set(G) - set(nodes)``. Following the
        bipartite subpackage convention, the caller is responsible for
        providing a valid bipartite graph and a valid node set.

    weight : string or None, optional (default="weight")
        Edge attribute holding the numerical weight. If ``None`` or the
        attribute is missing, every edge is treated as having weight 1.

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`. LPAwb+ is stochastic: stage 1
        visits each side's nodes in a random order and breaks ties among
        equally-good labels uniformly at random. Run with multiple seeds
        and keep the best :func:`modularity` value for small networks.

    Returns
    -------
    communities : list of sets
        A list of sets of nodes, one per community, sorted by size
        (largest first). Communities may contain nodes from both
        bipartite sets.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is directed.

    Notes
    -----
    Per the paper, the smaller of the two bipartite sets is treated as
    the "red" side internally for computational efficiency; this does
    not affect the returned communities, which are unordered node
    sets.

    LPAwb+ is local and heuristic: it converges to a local optimum of
    $Q_B$ and is not guaranteed to find the global maximum. Running
    with several seeds and keeping the best-scoring partition is the
    standard practice.

    See Also
    --------
    modularity

    References
    ----------
    .. [1] Beckett, S. J. (2016). "Improved community detection in
       weighted bipartite networks." Royal Society open science, 3(1),
       140536. https://doi.org/10.1098/rsos.140536
    .. [2] Barber, M. J. (2007). "Modularity and community detection in
       bipartite networks." Physical Review E, 76(6), 066102.
    """
    red = set(nodes)
    blue = set(G) - red

    # Per paper, treat the smaller side as "red" internally.
    if len(red) > len(blue):
        red, blue = blue, red

    if G.number_of_edges() == 0 or not red or not blue:
        return [{n} for n in G]

    strength = dict(G.degree(weight=weight))
    # Total edge weight = sum of red-side strengths (each bipartite
    # edge has exactly one red endpoint).
    M = sum(strength[v] for v in red)

    if M == 0:
        return [{n} for n in G]

    # Start with every node in its own community.
    labels = {v: i for i, v in enumerate(G)}
    label_strength_red = {labels[v]: strength[v] for v in red}
    label_strength_blue = {labels[v]: strength[v] for v in blue}
    # Reverse index: nodes carrying each label. Avoids O(N) scans of
    # ``labels`` when stage 2 needs to find every member of a community
    # being merged, and lets stage 1 incrementally maintain the picture.
    members = {labels[v]: {v} for v in G}

    # ``inter[(a, b)]`` (with ``a < b``) is the total weight of edges
    # whose endpoints carry different labels ``a`` and ``b``. Rebuilding
    # this from scratch in stage 2 dominates wall time on large graphs,
    # so we keep it incrementally up to date through stage 1 label
    # changes and stage 2 merges.
    inter = defaultdict(float)
    for u, v, wt in G.edges(data=weight, default=1):
        label_u, label_v = labels[u], labels[v]
        if label_u != label_v:
            inter[(label_u, label_v) if label_u < label_v else (label_v, label_u)] += wt

    def _best_label(x, opposite_strength):
        """Return the label maximizing x's Eq. 2.5 score.

        Ties including x's current label keep the current label.
        """
        y_x = strength[x]
        neighbor_weight = defaultdict(float)
        for v, edge_data in G[x].items():
            neighbor_weight[labels[v]] += edge_data.get(weight, 1)

        current = labels[x]
        current_score = neighbor_weight.get(current, 0) - (
            y_x * opposite_strength.get(current, 0) / M
        )

        # Find the best non-current label, breaking ties uniformly at
        # random via reservoir replacement (probability 1/k for the k-th
        # tied candidate seen).
        best_score = current_score
        best = current
        ties = 0
        for g, n_xg in neighbor_weight.items():
            if g == current:
                continue
            score = n_xg - y_x * opposite_strength.get(g, 0) / M
            if score > best_score:
                best_score = score
                best = g
                ties = 1
            elif score == best_score and ties > 0:
                ties += 1
                if seed.random() < 1 / ties:
                    best = g
        # If the best found still ties with current, keep current.
        if best_score == current_score:
            return current
        return best

    # Paper convention: update blue, then red, repeat until stable.
    # Each side carries its own dirty set. A node is "dirty" when one of
    # its neighbors (or its own community's strength tables) changed
    # since its last visit, so its best label may now be different.
    #
    # This propagation is a heuristic: only direct neighbors of a moved
    # node are dirtied, so a node whose best label shifts purely because
    # the strength of a non-neighboring label changed may be missed and
    # stay at a stale label. The algorithm still converges to a local
    # optimum; it just isn't necessarily the same one a full-sweep
    # variant would find. Empirically, deviation is well below typical
    # seed-to-seed Q_B variance, we include it because it provides a ~50x
    # speedup.
    dirty_blue = set(blue)
    dirty_red = set(red)
    sides = (
        # (self_table, opposite_strength, self_dirty, other_dirty)
        (label_strength_blue, label_strength_red, dirty_blue, dirty_red),
        (label_strength_red, label_strength_blue, dirty_red, dirty_blue),
    )

    def _apply_label_change(x, old, new, self_table, other_dirty):
        """Bookkeeping for a single ``labels[x]: old -> new`` transition.

        Walks ``x``'s edges exactly once to update ``inter`` and mark
        the affected opposite-side neighbors dirty.
        """
        node_strength = strength[x]
        self_table[old] -= node_strength
        if self_table[old] <= 0:
            del self_table[old]
        self_table[new] = self_table.get(new, 0) + node_strength
        labels[x] = new
        members[old].remove(x)
        if not members[old]:
            del members[old]
        members[new].add(x)

        for v, edge_data in G[x].items():
            wt = edge_data.get(weight, 1)
            neighbor_label = labels[v]
            if old != neighbor_label:
                key = (
                    (old, neighbor_label)
                    if old < neighbor_label
                    else (neighbor_label, old)
                )
                inter[key] -= wt
                if inter[key] <= 0:
                    del inter[key]
            if new != neighbor_label:
                key = (
                    (new, neighbor_label)
                    if new < neighbor_label
                    else (neighbor_label, new)
                )
                inter[key] += wt
            other_dirty.add(v)

    def _stage1():
        while dirty_blue or dirty_red:
            for self_table, opposite_strength, self_dirty, other_dirty in sides:
                if not self_dirty:
                    continue
                todo = list(self_dirty)
                self_dirty.clear()
                seed.shuffle(todo)
                for x in todo:
                    old = labels[x]
                    new = _best_label(x, opposite_strength)
                    if new != old:
                        _apply_label_change(x, old, new, self_table, other_dirty)

    def _merge_strength(table, dst, src):
        """Move ``src``'s strength into ``dst``, dropping ``src``."""
        val = table.pop(src, 0)
        if val:
            table[dst] = table.get(dst, 0) + val

    def _stage2():
        """Perform one mutual-best merge with positive ΔQ. Return True if merged.

        Modules with no inter-module edge cannot have a beneficial merge:
        ΔQ_B = e_AB/M - (k_A·d_B + k_B·d_A)/M², and the cross term is
        always non-negative, so e_AB == 0 forces ΔQ_B ≤ 0. We therefore
        enumerate only the (a, b) pairs in ``inter`` -- at most O(E) and
        typically far less than O(M²).
        """
        if not inter:
            return False

        best_partner = {}
        for (a, b), e in inter.items():
            cross = label_strength_red.get(a, 0) * label_strength_blue.get(
                b, 0
            ) + label_strength_red.get(b, 0) * label_strength_blue.get(a, 0)
            delta = e / M - cross / (M * M)
            if a not in best_partner or delta > best_partner[a][0]:
                best_partner[a] = (delta, b)
            if b not in best_partner or delta > best_partner[b][0]:
                best_partner[b] = (delta, a)

        for a in sorted(best_partner):
            best_delta, partner = best_partner[a]
            if best_delta <= 0:
                continue
            _, back_partner = best_partner[partner]
            if back_partner == a:
                # Merge ``partner`` into ``a``. Use the reverse index to
                # enumerate the community in O(|community|) instead of
                # scanning all labels.
                for node in members[partner]:
                    labels[node] = a
                    if node in red:
                        dirty_red.add(node)
                        dirty_blue.update(G[node])
                    else:
                        dirty_blue.add(node)
                        dirty_red.update(G[node])
                members[a].update(members.pop(partner))
                _merge_strength(label_strength_red, a, partner)
                _merge_strength(label_strength_blue, a, partner)

                # Patch ``inter``: edges between ``a`` and ``partner`` are
                # now intra-module; every other ``partner`` cross-edge
                # becomes an ``a`` cross-edge.
                inter.pop((a, partner) if a < partner else (partner, a), None)
                partner_edges = [k for k in inter if partner in k]
                for key in partner_edges:
                    other = key[1] if key[0] == partner else key[0]
                    cross_weight = inter.pop(key)
                    new_key = (a, other) if a < other else (other, a)
                    inter[new_key] += cross_weight
                return True
        return False

    _stage1()
    while _stage2():
        _stage1()

    return sorted(members.values(), key=len, reverse=True)
