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
    weight="weight",
    resolution=1.0,
    max_level=None,
    seed=None,
    quality_function="cpm",
    theta=0.01,
):
    r"""Find the best partition of a graph using the Leiden Community Detection
    Algorithm [1]_.

    Leiden Community Detection is an algorithm to extract the community structure
    of a network based on modularity optimization. It is an improvement upon the
    Louvain Community Detection algorithm. See :any:`louvain_communities`.

    Unlike the Louvain algorithm, it guarantees that communities are well connected in addition
    to being faster and uncovering better partitions. [1]_

    The algorithm works in 3 phases. On the first phase, it adds the nodes to a queue randomly
    and assigns every node to be in its own community. For each node it tries to find the
    maximum positive modularity gain by moving each node to all of its neighbor communities.
    If a node is moved from its community, it adds to the rear of the queue all neighbors of
    the node that do not belong to the node’s new community and that are not in the queue.

    The first phase continues until the queue is empty.

    The second phase consists in refining the partition $P$ obtained from the first phase. It starts
    with a singleton partition $P_{refined}$. Then it merges nodes locally in $P_{refined}$ within
    each community of the partition $P$. Nodes are merged with a community in $P_{refined}$ only if
    both are sufficiently well connected to their community in $P$. This means that after the
    refinement phase is concluded, communities in $P$ sometimes will have been split into multiple
    communities.

    The third phase consists of aggregating the network by building a new network whose nodes are
    now the communities found in the second phase. However, the non-refined partition is used to create
    an initial partition for the aggregate network.

    Once this phase is complete it is possible to reapply the first and second phases creating bigger
    communities with increased modularity.

    The above three phases are executed until no modularity gain is achieved or `max_level` number
    of iterations have been performed.
    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    node_weight : string or None, optional (default=None)
        The name of a node attribute that holds the numerical value
        used as a weight for nodes. If None then each node has weight 1.
        Through each iteration of the algorithm, the weight of a node
        is calculated as the sum of the constituent nodes, see [1]_.
    resolution : float, optional (default=1)
        If resolution is less than 1, the algorithm favors larger communities.
        Greater than 1 favors smaller communities
    max_level : int or None, optional (default=None)
        The maximum number of levels (steps of the algorithm) to compute.
        Must be a positive integer or None. If None, then there is no max
        level and the threshold parameter determines the stopping condition.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    quality_function : str (default="cpm")
        The algorithm optimises for a measure of quality. By default
        the constant_potts_model is used, but this can be changed (e.g.
        modularity)
    theta : float (default=0.01)
        Parameter that determines the degree of randomness in the
        _refine_partition step of the algorithm,

    Returns
    -------
    list
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.

    Examples
    --------

    Notes
    -----

    References
    ----------
    .. [1] Traag, V.A., Waltman, L. & van Eck, N.J. From Louvain to Leiden: guaranteeing
       well-connected communities. Sci Rep 9, 5233 (2019). https://doi.org/10.1038/s41598-019-41695-z

    See Also
    --------
    leiden_partitions
    """

    partitions = leiden_partitions(
        G,
        weight=weight,
        resolution=resolution,
        seed=seed,
        quality_function=quality_function,
        theta=theta,
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
    weight="weight",
    resolution=1.0,
    seed=None,
    quality_function="cpm",
    theta=0.01,
):
    """Yield partitions for each level of Leiden Community Detection (backend required)

    Leiden Community Detection is an algorithm to extract the community
    structure of a network based on modularity optimization.

    The partitions across levels (steps of the algorithm) form a dendrogram
    of communities. A dendrogram is a diagram representing a tree and each
    level represents a partition of the G graph. The top level contains the
    smallest communities and as you traverse to the bottom of the tree the
    communities get bigger and the overall modularity increases making
    the partition better.

    Each level is generated by executing the three phases of the Leiden Community
    Detection algorithm. See :any:`leiden_communities`.

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
        A list of disjoint sets (partition of `G`). Each set represents one community.
        All communities together contain all the nodes in `G`. The yielded partitions
        increase modularity with each iteration.

    References
    ----------
    .. [1] Traag, V.A., Waltman, L. & van Eck, N.J. From Louvain to Leiden: guaranteeing
       well-connected communities. Sci Rep 9, 5233 (2019). https://doi.org/10.1038/s41598-019-41695-z

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
    # 1) set the function quality_function
    # 2) set the corresponding quality_delta function
    # 3) set the specific attributes required to compute the
    #    quality_function and quality_delta

    # the quality_delta function computes the partial quality delta contributed by
    # adding nodes_to_add to community.
    # Corresponding value from removing U from C is computed by taking
    # the negative  -1 * quality_delta(U, C-U)
    # to compute the overall quality delta from moving node u from A to B we have
    # q_delta = quality_delta({u}, B) - quality_delta({u}, A-{u})

    if quality_function == "cpm":
        # Setup for constant potts model
        node_attributes = ["node_weight"]
        nx.set_node_attributes(graph, 1, name="node_weight")

        quality_function = functools.partial(
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

    elif quality_function == "modularity":
        # Setup for (unipartite) modularity

        # the modualrity function throws an zero division error
        # if the graph consists of only a single node.
        # if leiden aggregates the graph to a single node then
        # we just need to retun a value that ensure the algorithm
        # stops
        def guarded_modularity(G, P):
            if len(G) == 1:
                return float("inf")
            else:
                return modularity(G, P, resolution=resolution)

        quality_function = guarded_modularity
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

            m = sum(deg for u, deg in degrees)
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

    elif quality_function == "barber_modularity":
        # Setup for undirected bipartite barber modularity (not yet fully implemented)

        is_bipartite = nx.is_bipartite(G)
        if not is_bipartite:
            raise nx.NetworkXError("not a bipartite graph")

        if is_directed:
            raise QualityFunctionNotImplemented(
                "barber_modularity not implemented for DiGraph"
            )

        # quality_function = nx.bipartite.modularity # not implemented yet

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
        m = sum(deg for u, deg in degrees)

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

        raise QualityFunctionNotImplemented(quality_function)

    else:
        raise QualityFunctionNotImplemented(quality_function)

    # The setup phase has ended, the main algorithm now begins.
    quality = quality_function(graph, partition)

    improvement_made = True

    while improvement_made:
        # _move_nodes_fast plays the same role as _one_level in the
        # networkx implementation of the louvain algorithm
        inner_partition = _move_nodes_fast(
            graph,
            refinement_mapping,
            quality_delta,
            seed=seed,
        )

        P_refined = _refine_partition(
            graph, inner_partition, quality_delta, seed=seed, theta=theta
        )

        P_refined_flat = [comm for P_ref in P_refined for comm in P_ref]
        new_quality = quality_function(graph, P_refined_flat)
        graph, refinement_mapping = _gen_graph(graph, P_refined, node_attributes)

        # the partition of the original underlying graph is read from
        # the node attribute 'nodes', which is set during _gen_graph(...)
        # Each node in graph represents a community in the original graph
        # and the node holds this information in the attribute 'nodes'.

        partition = [set() for _ in graph]
        for i, u in enumerate(graph):
            partition[i].update(graph.nodes[u]["nodes"])

        yield [s.copy() for s in partition]

        # We stop once the overall change in quality between iterations is
        # close to zero.
        improvement_made = (new_quality - quality) > 0.0000001
        quality = new_quality

    return


def _move_nodes_fast(
    G,
    refinement_mapping,
    quality_delta_func,
    seed,
):

    # Unlike louvain, instead of beginning each iteration with the singleton
    # partition, each iteration uses the (unrefined) partition from the previous
    # step as the starting communities when moving nodes.
    # This section of code initilises nodes into those communities.
    # if no partition is passed from the previous step (i.e. during the
    # first iteration) then this is skipped and the singleton partition is used.
    if refinement_mapping:
        inner_partition = [set() for _ in range(len(refinement_mapping.values()))]
        node2com = {}
        for i, u in enumerate(G):
            inner_partition[refinement_mapping[i]].add(u)
            node2com[u] = refinement_mapping[i]
    else:
        inner_partition = [{u} for u in G]
        node2com = {u: i for i, u in enumerate(G)}

    rand_nodes = list(G.nodes)
    seed.shuffle(rand_nodes)
    node_queue = deque(rand_nodes)

    while node_queue:
        u = node_queue.pop()

        best_delta = 0
        old_com = node2com[u]
        best_com = old_com

        # this value is the overall change in quality that occurs
        # when node u is removed from its current community
        q_A = quality_delta_func({u}, inner_partition[old_com] - {u})

        # for each node in the queue, we measure the change in quality
        # from moving that node to each other community, keeping track of
        # the community that gives the greatest improvement best_com
        for new_com in set(node2com.values()):
            if new_com != old_com:
                # this quantity is the overall change in quality that
                # occurs wen the node u is added the the new community
                q_B = quality_delta_func({u}, inner_partition[new_com])

                # the overall change in quality therefore from moving
                # node u from old_com to new_com is as follows
                quality_delta = q_B - q_A

                if quality_delta > best_delta:
                    best_delta = quality_delta
                    best_com = new_com

        if best_delta > 0:
            node2com[u] = best_com

            inner_partition[old_com].remove(u)
            inner_partition[best_com].add(u)

            neighbours = set(G.adj[u])
            nodes_to_visit = neighbours - inner_partition[best_com]

            for v in nodes_to_visit:
                if v not in node_queue:
                    node_queue.appendleft(v)

    inner_partition = list(filter(None, inner_partition))

    return inner_partition


def _refine_partition(
    G,
    partition,
    quality_delta_func,
    seed,
    theta,
):

    refined_communities = []

    for C in partition:
        node2com = {u: i for i, u in enumerate(C)}
        P_refined = [{u} for u in C]

        P_refined = _merge_node_subset(
            G,
            P_refined,
            node2com,
            C,
            quality_delta_func,
            seed,
            theta,
        )
        P_refined = list(filter(None, P_refined))
        refined_communities.append(P_refined)

    return refined_communities


def _merge_node_subset(
    G,
    P_refined,
    node2com,
    S,
    quality_delta_func,
    seed,
    theta,
):

    # first, the sufficiently well-connected nodes within S
    # are identified and added to the set R.
    R = {u for u in S if quality_delta_func({u}, S - {u}) > 0}

    for u in R:
        comm = node2com[u]
        if P_refined[comm] != {u}:
            continue
        # if the community that u belongs to is the singleton {u}, then
        # we will proceed to merge it probabilistically with another
        # community within S.

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
        q_A = quality_delta_func({u}, P_refined[comm] - {u})
        for i, C in enumerate(P_refined):
            if comm == i:
                # we only want to consider moving u to a different
                # community, not its current community.
                continue

            # We only consider merging u into a community that
            # is within S. This is what is means for the resulting
            # partition to be a refinement of S.

            # this application of quality_delta_func relates to the
            # definition of T in line :37 from pseudocode in paper
            if quality_delta_func(C, S - C) > 0:
                # the change in quality the occurs from moving node u
                # into the new community
                q_B = quality_delta_func({u}, P_refined[i])

                # the overall quality delta is therefore the sum
                # of the change in quality from removing u from its
                # starting community, and the change of quality
                # from adding it to the new community

                quality_delta = q_B - q_A

                if quality_delta > 0:
                    candidate_comm.append(i)
                    candidate_comm_q_delta.append(quality_delta)

        # if there are candidate communities identified then
        # one is selected at random, and u is added to that
        # community
        if candidate_comm:
            # the probability distribution that the new community it drawn
            # from is defined in terms of the quality delta associated
            # with the move to each community.

            # If moving u to community C results in a quality delta QC,
            # the relative frequency withi which C will be chosen is
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

            P_refined[comm].remove(u)
            P_refined[new_comm].add(u)
            node2com[u] = new_comm

    return P_refined


def _gen_graph(G, partition_list, node_attributes):
    """
    Generate a new graph based on the partitions of a given graph

    node_attributes is a list of attributes that are required for the
    given choice of quality function. When aggregating a community (set
    of nodes) into a new node of the aggregated graph, the value for
    each attribute is the sum of the constituent nodes.
    """

    H = G.__class__()
    node2com = {}

    refinement_mapping = {}
    community_index = 0
    for j, part in enumerate(partition_list):
        for refined_part in part:
            refinement_mapping[community_index] = j

            agg_attribute_vals = {attribute: 0 for attribute in node_attributes}

            nodes = set()

            for node in refined_part:
                for node_attribute in node_attributes:
                    agg_attribute_vals[node_attribute] += G.nodes[node][node_attribute]

                node2com[node] = community_index
                nodes.update(G.nodes[node].get("nodes", {node}))

                H.add_node(community_index, nodes=nodes, **agg_attribute_vals)

            community_index += 1

    for u, v, d in G.edges(data=True):
        uv_weight = d["weight"]
        com_u = node2com[u]
        com_v = node2com[v]
        if com_u != com_v:
            if H.has_edge(com_u, com_v):
                H.edges[(com_u, com_v)]["weight"] += uv_weight
            else:
                H.add_edge(com_u, com_v, weight=uv_weight)

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


def _is_valid_refinement(p, ref_p):
    """
    helper function useful during debugging, checking whether
    a refined partition ref_p is a true refinement of a partition p
    """
    val = True
    for c1 in ref_p:
        for c2 in p:
            if c1.issubset(c2):
                break
        else:
            val = False
    return val


class QualityFunctionNotImplemented(nx.NetworkXError):
    """Raised if quality function is not implemented for leiden"""

    def __init__(self, quality_function):
        msg = f"leiden not implemented for {quality_function}"
        super().__init__(msg)
