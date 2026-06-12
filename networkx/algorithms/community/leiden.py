"""Functions for detecting communities based on Leiden Community Detection
algorithm.
"""

import functools
import itertools
import math
import random
from collections import deque

import networkx as nx
from networkx.algorithms.community.quality import constant_potts_model, modularity
from networkx.utils import not_implemented_for, py_random_state

__all__ = ["leiden_communities", "leiden_partitions"]


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def leiden_communities(
    G,
    *,
    weight="weight",
    resolution=1.0,
    max_level=None,
    seed=None,
    metric="cpm",
    theta=0.01,
):
    r"""Return best node communities of `G`.

    This function uses the Leiden Community Detection algorithm [1]_ to estimate
    the community structure based on metric optimization. The metric can be
    modularity or Constant Potts Model (CPM). Leiden ensures that the communities
    are well connected whereas Louvain does not.
    The functions which compute those two metrics are
    :func:`~networkx.algorithms.community.quality.modularity` and
    :any:`constant_potts_model`

    The algorithm works in 3 phases. On the first phase, starting with a partition
    of all singleton nodes, and a randomly shuffled queue of all nodes, each node
    in the queue is considered in order and moved to the current community which
    most increases the metric value. The node can stay in its current community.
    If it moves, all neighbors of the moved node which are not currently in the
    queue are added to the end of the queue to be considered for moving in turn.
    The first phase continues until the queue is empty, resulting in a node
    partition $P$.

    The second phase refines $P$ to obtain $P_{refined}$. Each community in $P$
    is considered on its own and split into subcommunities using a method closely
    resembling the first phase. Starting from a subpartition of singleton nodes,
    and a randomly ordered queue, subcommunities are merged only if both are
    sufficiently well connected. This is determined randomly using a distribution
    based on edge weights and controlled by the parameter `theta`. The merging
    results in a splitting or refinement of the communities in $P$ such that
    each set in $P_{refined}$ is a subset of one community in $P$. Thus each
    community in $P$ also represents a community of subcommunities from $P_{refined}$.

    The third phase involves creating an aggregate network of community connections.
    The communities in $P_{refined}$ act as nodes in the new network. Edges exist
    between communities that have underlying nodes connected to nodes in the other
    community. The weight of each such edge is the sum of the original graph edge
    weights for edges between nodes in the two partitions. An initial partition of
    the new network is provided via $P$ by joining the subcommunities of each
    community in $P$ into an aggregated community of the new network. Each
    subcommunity from $P_{refined}$ is a subset of one community in $P$ and thus
    belongs to one community in the new network.

    The result of the 3 phases is a new network (level of aggregation) which encodes
    a new partition of the original network. We can reapply the 3 phases
    to create bigger aggregations with increased metric value. At each level
    the network is smaller with fewer nodes and edges, so convergence is guaranteed.
    The three phases are repeatedly applied until no gain is achieved or
    `max_level` applications have been performed.

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    metric : str (default="cpm")
        The name of the partition quality metric that the algorithm optimises.
        Allowed names are "cpm" and "modularity" for constant potts model and
        modularity respectively. See functions
        :func:`~networkx.algorithms.community.quality.modularity` and
        :any:`constant_potts_model` for more info.
    resolution : float, optional (default=1)
        Resolution should be a positive number indicating the coarseness of
        the communities produced. With a lower resolution, larger communities
        are produced. To see the smaller sub-communities, use a higher resolution.
    max_level : int or None, optional (default=None)
        The maximum number of levels (steps of the algorithm) to compute.
        Must be a positive integer or None indicating the process is reapplied
        until no increase in metric is obtained.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    theta : float (default=0.01)
        Parameter that determines the degree of randomness in the second phase
        _refine_partition step of the algorithm,

    Returns
    -------
    list
        A partition of `G` as a list of disjoint sets of nodes. Each set represents
        one community of nodes and each node of `G` appears in exactly one set.

    Examples
    --------

    >>> G = nx.barbell_graph(3, 4)
    >>> cpm_comm = nx.community.leiden_communities(G, resolution=0.2, seed=62537129)
    >>> len(cpm_comm)
    3
    >>> sorted(sorted(c) for c in cpm_comm)
    [[0, 1, 2], [3, 4, 5, 6], [7, 8, 9]]

    Higher resolution produces smaller sub-communities:

    >>> cpm_comm = nx.community.leiden_communities(G, resolution=0.4, seed=62537129)
    >>> len(cpm_comm)
    4
    >>> sorted(sorted(c) for c in cpm_comm)
    [[0, 1, 2], [3, 4], [5, 6], [7, 8, 9]]

    Notes
    -----
    The order in which the nodes are considered can affect the final output.
    In the algorithm the ordering happens using a random shuffle controlled by
    `seed` which also controls the randomness involved in selecting communities
    to merge during the refining (2nd) stage.

    References
    ----------
    .. [1] Traag, V.A., Waltman, L. & van Eck, N.J.
       From Louvain to Leiden: guaranteeing well-connected communities.
       Sci Rep 9, 5233 (2019).
       https://doi.org/10.1038/s41598-019-41695-z

    See Also
    --------
    leiden_partitions
    :any:`louvain_communities`
    :func:`networkx.algorithms.community.quality.modularity`
    :any:`constant_potts_model`
    """

    partitions = leiden_partitions(
        G, weight=weight, resolution=resolution, seed=seed, metric=metric, theta=theta
    )

    if max_level is not None:
        if max_level <= 0:
            raise ValueError("max_level argument must be a positive integer or None")
        partitions = itertools.islice(partitions, max_level)
    final_partition = deque(partitions, maxlen=1)
    return final_partition.pop()


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def leiden_partitions(
    G,
    *,
    weight="weight",
    metric="cpm",
    resolution=1.0,
    seed=None,
    theta=0.01,
):
    """Yield partitions at each level of Leiden Community Detection

    Leiden Community Detection is an algorithm to extract the community
    structure of a network based on modularity optimization.

    The partitions across levels (steps of the algorithm) form a dendrogram
    of communities. A dendrogram is a diagram representing a tree and each
    level represents a partition of the G graph. The top level contains the
    smallest communities and as you traverse the tree the communities get
    bigger and the overall partition quality metric increases.

    Each level is generated by executing the three phases of the Leiden Community
    Detection algorithm. See :any:`leiden_communities`.

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    metric : str (default="cpm")
        The name of the partition quality metric that the algorithm optimises.
        Allowed names are "cpm" and "modularity".
    resolution : float, optional (default=1)
        Resolution should be a positive number indicating the coarseness of
        the communities produced. With a lower resolution, larger communities
        are produced. To see the smaller sub-communities, use a higher resolution.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    theta : float (default=0.01)
        Parameter that determines the degree of randomness in the second phase
        _refine_partition step of the algorithm,

    Yields
    ------
    list of sets of nodes
        A partition of `G` as a list of disjoint sets of nodes. Each set represents
        one community of nodes and each node of `G` appears in exactly one set.
        The quality metric of the yielded partitions increases with each iteration.

    References
    ----------
    .. [1] Traag, V.A., Waltman, L. & van Eck, N.J.
       From Louvain to Leiden: guaranteeing well-connected communities.
       Sci Rep 9, 5233 (2019).
       https://doi.org/10.1038/s41598-019-41695-z

    See Also
    --------
    leiden_communities
    :any:`louvain_partitions`
    """

    partition = [{u} for u in G]
    refinement_mapping = None

    if nx.is_empty(G):
        yield partition
        return

    is_directed = G.is_directed()
    if G.is_multigraph():
        # this is the same as how louvain handles multigraph inputs
        graph = _convert_multigraph(G, weight, is_directed)
    else:
        # if the weight parameter is defined then we use this value for
        # edge weights within the algorithm, defaulting to 1 where the
        # attribute does not exist
        # else if weight is None then all edges are given a weight of 1
        if weight:
            graph = G.__class__()
            graph.add_nodes_from(G)
            graph.add_weighted_edges_from(G.edges(data=weight, default=1))
        else:
            graph = G.__class__()
            graph.add_nodes_from(G)
            graph.add_edges_from(G.edges())
            nx.set_edge_attributes(graph, 1, name="weight")

    # The following setup stage depends on the choice of quality
    # function. In particular, this stage must set three things:
    # 1) set the function metric
    # 2) set the corresponding quality_delta function
    # 3) set the specific attributes required to compute the
    #    metric and quality_delta

    # the quality_delta function computes the partial quality delta contributed by
    # adding nodes_to_add to community.
    # Corresponding value from removing U from C is computed by taking
    # the negative  -1 * quality_delta(U, C-U)
    # to compute the overall quality delta from moving node u from A to B we have
    # q_delta = quality_delta({u}, B) - quality_delta({u}, A-{u})

    if metric == "cpm":
        # Setup for constant potts model
        node_attributes = ["node_weight"]
        nx.set_node_attributes(graph, 1, name="node_weight")

        metric = functools.partial(
            constant_potts_model,
            resolution=resolution,
            node_weight="node_weight",
            weight="weight",
        )

        if is_directed:
            # Setup for directed constant potts model
            gamma = 2 * resolution

            def quality_delta(nodes_to_add, community):
                comm_size = sum(graph.nodes[u]["node_weight"] for u in community)
                nodes_size = sum(graph.nodes[u]["node_weight"] for u in nodes_to_add)
                E_in = sum(
                    wt
                    for _, v, wt in graph.edges(nodes_to_add, data="weight")
                    if v in community
                )
                E_out = sum(
                    wt
                    for _, v, wt in graph.edges(community, data="weight")
                    if v in nodes_to_add
                )
                return E_in + E_out - gamma * comm_size * nodes_size
        else:
            # Setup for undirected constant potts model
            gamma = resolution

            def quality_delta(nodes_to_add, community):
                comm_size = sum(graph.nodes[u]["node_weight"] for u in community)
                nodes_size = sum(graph.nodes[u]["node_weight"] for u in nodes_to_add)
                E = sum(
                    wt
                    for _, v, wt in graph.edges(nodes_to_add, data="weight")
                    if v in community
                )
                return E - gamma * comm_size * nodes_size

    elif metric == "modularity":
        # Setup for (unipartite) modularity

        # the modualrity function throws an zero division error
        # if the graph consists of only a single node.
        # if leiden aggregates the graph to a single node then
        # we just need to retun a value that ensure the algorithm
        # stops
        def guarded_modularity(G, P):

            try:
                return modularity(G, P, resolution=resolution)
            except ZeroDivisionError:
                return float("inf")

        metric = guarded_modularity
        if is_directed:
            # Setup for directed modularity
            node_attributes = ["in_degree", "out_degree"]
            in_degrees = graph.in_degree(weight="weight")
            out_degrees = graph.out_degree(weight="weight")

            m = sum(wt for u, wt in in_degrees) + sum(wt for u, wt in out_degrees)
            for u, v, data in graph.edges(data=True):
                data["weight"] *= 1 / m

            nx.set_node_attributes(
                graph, {u: in_deg / m for u, in_deg in in_degrees}, "in_degree"
            )
            nx.set_node_attributes(
                graph, {u: out_deg / m for u, out_deg in out_degrees}, "out_degree"
            )

            gamma = 2 * resolution

            def quality_delta(nodes_to_add, community):
                nodes_in = sum(graph.nodes[u]["in_degree"] for u in nodes_to_add)
                nodes_out = sum(graph.nodes[u]["out_degree"] for u in nodes_to_add)
                comm_in = sum(graph.nodes[u]["in_degree"] for u in community)
                comm_out = sum(graph.nodes[u]["out_degree"] for u in community)
                E_to = sum(
                    wt
                    for _, v, wt in graph.edges(nodes_to_add, data="weight")
                    if v in community
                )
                E_from = sum(
                    wt
                    for _, v, wt in graph.edges(community, data="weight")
                    if v in nodes_to_add
                )
                return (E_to + E_from) - gamma * (
                    nodes_in * comm_out + nodes_out * comm_in
                )

        else:
            # Setup for undirected modularity
            node_attributes = ["degree"]
            degrees = graph.degree(weight="weight")

            m = sum(deg for u, deg in degrees) / 2
            for u, v, data in graph.edges(data=True):
                data["weight"] *= 1 / m
            nx.set_node_attributes(graph, {u: deg / m for u, deg in degrees}, "degree")
            gamma = 2 * resolution

            def quality_delta(nodes_to_add, community):
                nodes_size = sum(graph.nodes[u]["degree"] for u in nodes_to_add)
                comm_size = sum(graph.nodes[u]["degree"] for u in community)
                E_D = sum(
                    wt
                    for u, v, wt in graph.edges(nodes_to_add, data="weight")
                    if v in community
                )
                return E_D - gamma * nodes_size * comm_size

    elif metric == "barber_modularity":
        # Setup for undirected bipartite barber modularity (not yet fully implemented)

        if is_directed:
            raise nx.NetworkXError("barber_modularity not implemented for DiGraph")

        # metric should be defined inline rather than
        # importing nx.bipartite.community.modularity as the
        # function within this algorithm needs to accept the
        # aggregated graphs which are not bipartite and therefore
        # requires a variation of the algorithm

        def barber_modularity():
            return

        metric = barber_modularity

        node_attributes = ["red_degree", "blue_degree"]

        red_nodes = {u for u, c in G.nodes(data="bipartite") if c == 0}
        blue_nodes = {u for u, c in G.nodes(data="bipartite") if c == 1}

        # expect the bipartite graph G to follow the NetworkX convention to have node
        # a node attribe bipartite taking value 0 or 1, so should check this using
        # something like the following:
        #
        # if len(red_nodes.union(blue_nodes)) < len(G):
        #    raise nx.NetworkXError(
        #         "expecting node attribute 'bipartite', with values 0 or 1"
        #     )

        degrees = graph.degree(weight="weight")
        m = sum(deg for u, deg in degrees) / 2

        red_degree = {u: G.degree(u, weight="weight") / m for u in red_nodes}
        for u in blue_nodes:
            red_degree[u] = 0

        blue_degree = {u: G.degree(u, weight="weight") / m for u in blue_nodes}
        for u in red_nodes:
            blue_degree[u] = 0

        nx.set_node_attributes(graph, red_degree, "red_degree")
        nx.set_node_attributes(graph, blue_degree, "blue_degree")

        for u, v, data in graph.edges(data=True):
            data["weight"] *= 1 / m

        def quality_delta(nodes_to_add, community):
            nodes_red = sum(graph.nodes[u]["red_degree"] for u in nodes_to_add)
            nodes_blue = sum(graph.nodes[u]["blue_degree"] for u in nodes_to_add)
            comm_red = sum(graph.nodes[u]["red_degree"] for u in community)
            comm_blue = sum(graph.nodes[u]["blue_degree"] for u in community)
            E = sum(
                wt
                for _, v, wt in graph.edges(nodes_to_add, data="weight")
                if v in community
            )
            return E - resolution * (nodes_red * comm_blue + nodes_blue * comm_red)

        raise nx.NetworkXError("barber_modularity not implemented for leiden")
    else:
        raise nx.NetworkXError(
            f'leiden only supports metrics "cpm" and "modularity". Got: {metric}'
        )

    # The setup phase has ended, the main algorithm now begins.
    Q = metric(graph, partition)

    improvement_made = True

    while improvement_made:
        # _move_nodes_fast plays the same role as _one_level in the
        # networkx implementation of the louvain algorithm
        # when moving nodes to find the greatest increase in quality,

        # leiden initialises nodes into communities based on the
        # unrefined partition of the previous stage. The dict
        # refinement_mapping specifies how these initial communities
        # are to be set
        P = _move_nodes_fast(graph, refinement_mapping, quality_delta, seed=seed)

        P_refined = _refine_partition(graph, P, quality_delta, seed=seed, theta=theta)

        P_refined_flat = [comm for P_ref in P_refined for comm in P_ref]

        # Stop when overall change in quality is close to zero.
        Q_new = metric(graph, P_refined_flat)
        improvement_made = (Q_new - Q) > 0.0000001
        Q = Q_new

        graph, refinement_mapping = _create_aggregate_graph(
            graph, P_refined, node_attributes
        )

        # the partition of the original underlying graph is read from
        # the node attribute 'nodes', which is set during _create_aggregate_graph(...)
        # Each node in graph represents a community in the original graph
        # and the node holds this information in the attribute 'nodes'.
        yield [set(graph.nodes[u]["nodes"]).copy() for u in graph]

    return


def _move_nodes_fast(G, refinement_mapping, quality_delta_func, seed):

    # Unlike louvain, instead of beginning each iteration with the singleton
    # partition, each iteration uses the (unrefined) partition from the previous
    # step as the starting communities when moving nodes.
    # This section of code initilises nodes into those communities.
    # if no partition is passed from the previous step (i.e. during the
    # first iteration) then this is skipped and the singleton partition is used.
    if refinement_mapping:
        P = [set() for _ in range(len(refinement_mapping.values()))]
        node2com = {}
        for i, u in enumerate(G):
            P[refinement_mapping[i]].add(u)
            node2com[u] = refinement_mapping[i]
    else:
        P = [{u} for u in G]
        node2com = {u: i for i, u in enumerate(G)}

    rand_nodes = list(G.nodes)
    seed.shuffle(rand_nodes)
    node_queue = deque(rand_nodes)

    while node_queue:
        u = node_queue.pop()
        neighbor_coms = {node2com[v] for v in nx.all_neighbors(G, u)}

        best_delta = 0
        old_com = node2com[u]
        best_com = old_com

        # this value is the overall change in quality that occurs
        # when node u is removed from its current community
        q_rem = quality_delta_func({u}, P[old_com] - {u})

        # for each node in the queue, we measure the change in quality
        # from moving that node to each other community, keeping track of
        # the community that gives the greatest improvement best_com
        for new_com in neighbor_coms:
            if new_com != old_com:
                # this quantity is the overall change in quality that
                # occurs when the node u is added to the new community
                q_add = quality_delta_func({u}, P[new_com])

                # the overall change in quality therefore from moving
                # node u from old_com to new_com is as follows
                Q_delta = q_add - q_rem

                if Q_delta > best_delta:
                    best_delta = Q_delta
                    best_com = new_com

        if best_delta > 0:
            node2com[u] = best_com

            P[old_com].remove(u)
            P[best_com].add(u)

            neighbours = set(G.adj[u])
            nodes_to_visit = neighbours - P[best_com]

            for v in nodes_to_visit:
                if v not in node_queue:
                    node_queue.appendleft(v)

    P = list(filter(None, P))

    return P


def _refine_partition(
    G,
    P,
    quality_delta_func,
    seed,
    theta,
):

    P_refined = []

    for C in P:
        # each community C in the partition P
        # is split into a set of smaller communities
        # resulting in a refined partition

        C_refined = _merge_node_subset(
            G,
            C,
            quality_delta_func,
            seed,
            theta,
        )
        C_refined = list(filter(None, C_refined))
        P_refined.append(C_refined)

    return P_refined


def _merge_node_subset(
    G,
    C,
    quality_delta_func,
    seed,
    theta,
):

    node2com = {u: i for i, u in enumerate(C)}
    C_refined = [{u} for u in C]
    # first, the sufficiently well-connected nodes within S
    # are identified and added to the set R.
    R = {u for u in C if quality_delta_func({u}, C - {u}) > 0}

    for u in R:
        comm = node2com[u]
        if C_refined[comm] != {u}:
            continue
        # if the community that u belongs to is the singleton {u}, then
        # we will proceed to merge it probabilistically with another
        # community within C.

        # first we identify candidate communities to merge u into
        # and then the final community is randomly selected from these
        # according to a probability distribution which is partly
        # defined by the relative quality_delta (bigger increase in
        # quality makes choosing that community more likely, but
        # the algorithm does not greedily choose the greatest increase)

        # we therefore track both the communities and their respective
        # probabilities in order to define the probabilty distribution
        # to select the community that u will be moved into

        # if u is not in a singleton partition then we move on to the
        # next node.
        candidate_comm = []
        candidate_comm_q_delta = []

        # this is the change in quality that occurs from removing node
        # u from its current community
        q_rem = quality_delta_func({u}, C_refined[comm] - {u})
        for i, new_comm in enumerate(C_refined):
            if comm == i:
                # we only want to consider moving u to a different
                # community, not its current community.
                continue

            # We only consider merging u into a community that
            # is within S. This is what is means for the resulting
            # partition to be a refinement of S.

            # this application of quality_delta_func relates to the
            # definition of T in line :37 from pseudocode in paper
            if quality_delta_func(new_comm, C - new_comm) > 0:
                # the change in quality the occurs from moving node u
                # into the new community
                q_add = quality_delta_func({u}, C_refined[i])

                # the overall quality delta is therefore the sum
                # of the change in quality from removing u from its
                # starting community, and the change of quality
                # from adding it to the new community

                Q_delta = q_add - q_rem

                if Q_delta > 0:
                    candidate_comm.append(i)
                    candidate_comm_q_delta.append(Q_delta)

        # if there are candidate communities identified then
        # one is selected at random, and u is added to that
        # community
        if candidate_comm:
            # the probability distribution that the new community is drawn
            # from is defined in terms of the quality delta associated
            # with the move to each community.

            # If moving u to community C results in a quality delta QC,
            # the relative frequency with which C will be chosen is
            # proportional to
            #
            #       math.exp(QC/theta)
            #
            # Since computing large exponentials can cause overflow
            # errors, we use an equivalent form that computes normalised
            # values with the same ratios
            max_delta = max(candidate_comm_q_delta)
            candidate_comm_prob = [
                math.exp((x - max_delta) / theta) for x in candidate_comm_q_delta
            ]

            new_comm = seed.choices(candidate_comm, weights=candidate_comm_prob)[0]

            C_refined[comm].remove(u)
            C_refined[new_comm].add(u)
            node2com[u] = new_comm

    return C_refined


def _create_aggregate_graph(G, refined_communities_list, node_attributes):
    """
    Generate a new graph based on the partitions of a given graph

    node_attributes is a list of attributes that are required for the
    given choice of quality metric. When aggregating a community (set
    of nodes) into a new node of the aggregated graph, the value for
    each attribute is the sum of the constituent nodes.
    """

    H = G.__class__()
    old2new = {}

    refinement_mapping = {}
    new_node_id = 0
    for partition_index, community in enumerate(refined_communities_list):
        for refined_community in community:
            # each refined_community from the refined_partiton defines
            # a node in the new aggregated graph

            refinement_mapping[new_node_id] = partition_index

            agg_vals = {attribute: 0 for attribute in node_attributes}

            # will contain the nodes defining a community
            # in the original graph
            original_nodes = set()

            # old_node is node from the previous iteration
            # i.e. aggregated graph from the previous
            # stage, not the original graph
            for old_node in refined_community:
                for node_attribute in node_attributes:
                    agg_vals[node_attribute] += G.nodes[old_node][node_attribute]

                old2new[old_node] = new_node_id
                original_nodes.update(G.nodes[old_node].get("nodes", {old_node}))

            H.add_node(new_node_id, nodes=original_nodes, **agg_vals)

            new_node_id += 1

    for u, v, uv_weight in G.edges(data="weight"):
        new_u = old2new[u]
        new_v = old2new[v]
        if new_u != new_v:
            if H.has_edge(new_u, new_v):
                H.edges[(new_u, new_v)]["weight"] += uv_weight
            else:
                H.add_edge(new_u, new_v, weight=uv_weight)

    return H, refinement_mapping


def _convert_multigraph(G, weight, is_directed):
    """Convert a Multigraph to normal Graph"""
    if is_directed:
        H = nx.DiGraph()
    else:
        H = nx.Graph()

    H.add_nodes_from(G)
    for u, v, wt in G.edges(data=weight, default=1):
        if H.has_edge(u, v):
            H[u][v]["weight"] += wt
        else:
            H.add_edge(u, v, weight=wt)
    return H
