"""Functions for detecting communities based on Leiden Community Detection
algorithm.
"""

import itertools
import math
import random
from collections import deque

import networkx as nx
from networkx.algorithms.community.quality import (
    _cpm_delta_partial_eval_add,
    _cpm_delta_partial_eval_remove,
    constant_potts_model,
)
from networkx.utils import not_implemented_for, py_random_state

__all__ = ["leiden_communities", "leiden_partitions"]


def _get_quality_delta_partial_eval_remove(quality_function):
    """
    Returns a function quality_delta_partial_eval_remove which is used within
    the _move_nodes_fast and _refine_partiton stages in conjunction
    with a similarly defined quality_delta_partial_eval_add function which together
    are used to efficiently compute quality_deltas when moving
    nodes between communities.

    Optimising these functions has a significant impact on
    overall performance.

    Parameters
    ----------
    quality_function : function
        The algorithm optimises for a measure of quality of a partition.
        Requires a functions accepts the same parameters as contant_potts_model

    Returns
    -------
    function

        Returns a function quality_delta_partial_eval_remove which has the
        following behaviour: for a node u and community A

            quality_delta_partial_eval_remove(G, u, A, quality_function, resolution)

        returns the overall change in quality (as defined
        by the quality_function) that occurs when the node u
        is removed from the community A.
    """

    # This method allows us to invoke optimised versions of these
    # delta functions, i.e we could have something like
    #
    if quality_function == constant_potts_model:
        return _cpm_delta_partial_eval_remove
    #
    # if qualty_function == modularity:
    #  return modularity_remove_cost
    #
    # etc...

    # if no optimised version exists then a version is
    # created using a simpler wrapper around quality_function
    # this gives flexibility to adding new functions, while
    # still allowing the use of more efficient methods where
    # they exist.

    def quality_delta_partial_eval_remove(
        G, node, community, resolution, weight="weight", node_weight="node_weight"
    ):

        q_before = quality_function(
            G,
            [community],
            resolution=resolution,
            weight=weight,
            node_weight="node_weight",
        )

        q_after = quality_function(
            G,
            [community - {node}],
            resolution=resolution,
            weight=weight,
            node_weight="node_weight",
        )

        return q_after - q_before

    return quality_delta_partial_eval_remove


def _get_quality_delta_partial_eval_add(quality_function):
    """
    Returns a function quality_delta_partial_eval_add which is used within
    the _move_nodes_fast and _refine_partiton stages in conjunction
    with a similarly defined quality_delta_partial_eval_remove function which together
    are used to efficiently compute quality_deltas when moving
    nodes between communities.

    Optimising these functions has a significant impact on
    overall performance.

    Parameters
    ----------
    quality_function : function
        The algorithm optimises for a measure of quality of a partition.
        Requires a functions accepts the same parameters as contant_potts_model

    Returns
    -------
    function

        Returns a function quality_delta_partial_eval_remove which has the
        following behaviour: for a node u and community B

            quality_delta_partial_eval_add(G, u, A, quality_function, resolution)

        returns the overall change in quality (as defined
        by the quality_function) that occurs when the node u
        is added to the community B.
    """

    # This method allows us to invoke optimised versions of these
    # delta functions, i.e we could have something like
    #
    if quality_function == constant_potts_model:
        return _cpm_delta_partial_eval_add
    #
    # if qualty_function == modularity:
    #  return modularity_add_cost
    #
    # etc...

    # if no optimised version exists then a version is
    # created using a simpler wrapper around quality_function
    # this gives flexibility to adding new functions, while
    # still allowing the use of more efficient methods where
    # they exist.

    def quality_delta_partial_eval_add(
        G, node, community, resolution, weight="weight", node_weight="node_weight"
    ):
        q_before = quality_function(
            G,
            [community],
            resolution=resolution,
            weight=weight,
            node_weight="node_weight",
        )

        q_after = quality_function(
            G,
            [community.union({node})],
            resolution=resolution,
            weight=weight,
            node_weight="node_weight",
        )

        return q_after - q_before

    return quality_delta_partial_eval_add


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def leiden_communities(
    G,
    weight="weight",
    node_weight=None,
    resolution=1.0,
    threshold=0.0000001,
    max_level=None,
    seed=None,
    quality_function=constant_potts_model,
    quality_delta_partial_eval_remove=None,
    quality_delta_partial_eval_add=None,
    theta=0.01,
):
    r"""Find the best partition of a graph using the Leiden Community Detection
    Algorithm [1]_.

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
    threshold : float, optional (default=0.0000001)
        Modularity gain threshold for each level. If the gain of modularity
        between 2 levels of the algorithm is less than the given threshold
        then the algorithm stops and returns the resulting communities.
    max_level : int or None, optional (default=None)
        The maximum number of levels (steps of the algorithm) to compute.
        Must be a positive integer or None. If None, then there is no max
        level and the threshold parameter determines the stopping condition.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    quality_function : function (default="constant_potts_model")
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
        node_weight=node_weight,
        resolution=resolution,
        threshold=threshold,
        seed=seed,
        quality_function=quality_function,
        quality_delta_partial_eval_remove=None,
        quality_delta_partial_eval_add=None,
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
    node_weight=None,
    resolution=1.0,
    threshold=0.0000001,
    seed=None,
    quality_function=constant_potts_model,
    quality_delta_partial_eval_remove=None,
    quality_delta_partial_eval_add=None,
    theta=0.01,
):
    """
    TODO - doc string
    """

    # as well as providing a custom quality function for the algorithm
    # the user can define a pair of functions that partially evaluate
    # the quality delta associated with moving a node from one
    # community to another.

    # note that the partial_eval functions are not necessary at all
    # for the algorithm to run correctly, they are purely for
    # making the computations more efficient. We could include an
    # assertion that checks the relationship between quality_function
    # and the pair of partial evaluation functions on a simple
    # graph in order to provide the user with an error/warning if these
    # are not behaving as expected.

    if quality_delta_partial_eval_add is None:
        quality_delta_partial_eval_add = _get_quality_delta_partial_eval_add(
            quality_function
        )

    if quality_delta_partial_eval_remove is None:
        quality_delta_partial_eval_remove = _get_quality_delta_partial_eval_remove(
            quality_function
        )

    partition = [{u} for u in G]
    inner_partition = None

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

    # if a node_weight value is set, then the values with this name are
    # set as the 'node_weight' attribute. For nodes that do not have the
    # node_weight attribute, the 'node_weight' is set to 1

    # I don't know if this is the right way to handle this, and instead
    # raise an exception. Is it better to make the user set missing
    # node_weight attributes explicitly before calling the function?

    # if node_weight is not set then all nodes are initialised with the
    # value 1.

    if node_weight:
        nx.set_node_attributes(
            graph, {u: G.nodes[u].get(node_weight, 1) for u in G}, name="node_weight"
        )
    else:
        nx.set_node_attributes(graph, 1, name="node_weight")

    quality = quality_function(
        graph,
        partition,
        resolution=resolution,
        weight="weight",
        node_weight="node_weight",
    )

    improvement_made = True

    while improvement_made:
        # _move_nodes_fast plays the same role as _one_level in the
        # networkx implementation of the louvain algorithm
        inner_partition = _move_nodes_fast(
            graph,
            inner_partition,
            quality_function,
            quality_delta_partial_eval_remove,
            quality_delta_partial_eval_add,
            resolution,
            seed=seed,
        )

        inner_partition_refined = _refine_partition(
            graph,
            inner_partition,
            resolution,
            quality_function,
            quality_delta_partial_eval_remove,
            quality_delta_partial_eval_add,
            seed,
            theta,
        )

        new_quality = quality_function(
            graph,
            inner_partition_refined,
            resolution=resolution,
            weight="weight",
            node_weight="node_weight",
        )

        graph = _gen_graph(graph, inner_partition_refined)

        # the partition of the original underlying graph is read from
        # the node attribute 'nodes', which is set during _gen_graph(...)
        # Each node in graph represents a community in the original graph
        # and the node holds this information in the attribute 'nodes'.

        # This is different to how louvain keeps track of the global
        # partition, which is tracked through the individual moves in
        # _one_level(...). For leiden, these changes would have to be
        # tracked through both _move_nodes_fast and _refine_partition
        # but _refine_partition resets to a singleton partition anyway
        # so it wasn't clear to me: 1) how to do this; and, 2) whether
        # it's worth doing this.

        partition = [set() for _ in graph]
        for i, u in enumerate(graph):
            partition[i].update(graph.nodes[u]["nodes"])

        yield [s.copy() for s in partition]

        # We stop once the overall change in quality between iterations is
        # close to zero.
        improvement_made = (new_quality - quality) > threshold
        quality = new_quality

    return


def _move_nodes_fast(
    G,
    seed_partition,
    quality_function,
    quality_delta_partial_eval_remove,
    quality_delta_partial_eval_add,
    resolution,
    seed=None,
):
    inner_partition = [{u} for u in G]
    node2com = {u: i for i, u in enumerate(G)}

    # Unlike louvain, instead of beginning each iteration with the singleton
    # partition, each iteration uses the (unrefined) partition from the previous
    # step as the starting communities when moving nodes.
    # This section of code initilises nodes into those communities.
    # if no partition is passed from the previous step (i.e. during the
    # first iteration) then this is skipped and the singleton partition is used.
    if seed_partition:
        for i, u in enumerate(G):
            for j, C in enumerate(seed_partition):
                if u in C:
                    old_com = i
                    best_com = j
                    node2com[u] = best_com
                    inner_partition[old_com].remove(u)
                    inner_partition[best_com].add(u)

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
        q_A = quality_delta_partial_eval_remove(
            G, node=u, community=inner_partition[old_com], resolution=resolution
        )

        # for each node in the queue, we measure the change in quality
        # from moving that node to each other community, keeping track of
        # the community that gives the greatest improvement best_com
        for new_com in set(node2com.values()):
            if new_com != old_com:
                # this quantity is the overall change in quality that
                # occurs wen the node u is added the the new community
                q_B = quality_delta_partial_eval_add(
                    G, node=u, community=inner_partition[new_com], resolution=resolution
                )

                # the overall change in quality therefore from moving
                # node u from old_com to new_com is as follows
                quality_delta = q_A + q_B

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

    inner_partition = list(filter(len, inner_partition))

    return inner_partition


def _refine_partition(
    G,
    partition,
    resolution,
    quality_function,
    quality_delta_partial_eval_remove,
    quality_delta_partial_eval_add,
    seed,
    theta,
):

    node2com = {u: i for i, u in enumerate(G)}
    inner_partition_refined = [{u} for u in G]

    for C in partition:
        inner_partition_refined, node2com = _merge_node_subset(
            G,
            inner_partition_refined,
            node2com,
            C,
            resolution,
            quality_function,
            quality_delta_partial_eval_remove,
            quality_delta_partial_eval_add,
            seed,
            theta,
        )

    inner_partition_refined = list(filter(len, inner_partition_refined))
    return inner_partition_refined


def _merge_node_subset(
    G,
    partition,
    node2com,
    S,
    resolution,
    quality_function,
    quality_delta_partial_eval_remove,
    quality_delta_partial_eval_add,
    seed,
    theta,
):
    S_size = _size_of_node_set(G, S, "node_weight")

    # first, the sufficiently well-connected nodes within S
    # are identified and added to the set R.
    R = set()
    for u in S:
        u_size = _get_node_size(G, u, "node_weight")
        community_factor = _community_edge_size(G, {u}, S - {u}, "weight")
        factor_comparison = resolution * u_size * (S_size - u_size)
        if community_factor > factor_comparison:
            R.add(u)

    # TODO this section of the code has many nested if statements which
    # makes me think there's probably a more elegant solution. However,
    # this approach does closely follow the pseudocode in the paper [1]
    for u in R:
        comm = node2com[u]
        if partition[comm] == {u}:
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
            candidate_comm_prob = []

            # this is the change in quality that occurs from removing node
            # u from its current community
            q_A = quality_delta_partial_eval_remove(
                G, node=u, community=partition[comm], resolution=resolution
            )

            for i, C in enumerate(partition):
                if comm == i:
                    # we only want to consider moving u to a different
                    # community, not its current community.
                    pass

                elif C.issubset(S):
                    # We only consider merging u into a community that
                    # is within S. This is what is means for the resulting
                    # partition to be a refinement of S.

                    E = _community_edge_size(G, C, S - C, "weight")
                    C_size = _size_of_node_set(G, C, "node_weight")

                    comm_comparison = resolution * C_size * (S_size - C_size)

                    if E > comm_comparison:
                        # the change in quality the occurs from moving node u
                        # into the new community
                        q_B = quality_delta_partial_eval_add(
                            G, node=u, community=partition[i], resolution=resolution
                        )

                        # the overall quality delta is therefore the sum
                        # of the change in quality from removing u from its
                        # starting community, and the change of quality
                        # from adding it to the new community

                        quality_delta = q_A + q_B

                        if quality_delta > 0:
                            # since moving u to the candidate community C
                            # (at index i) we will add it to the list of
                            # candidate communities
                            candidate_comm.append(i)

                            # we also need to keep track of the probability
                            # that u will be added to C, as opposed to another
                            # candidate in the list. The relative probability
                            # is calcualted at as e^(quality_delta/theta)

                            # it is quite easy to get overflow in this math.exp(...)
                            # numpy handles this more elegantly.
                            try:
                                val = math.exp(quality_delta / theta)
                            except OverflowError:
                                val = float("inf")

                            candidate_comm_prob.append(val)

            # if there are candidate communities identified i.e.
            # if candidate_comm is not empty, then the next stage
            # selects the community to move u into.

            if len(candidate_comm) > 0:
                # This function is an inverse transform sampling of the list
                # of relative probability values.

                # the reason this function is defined inline is to make the
                # randomness determined by the same seed value making the
                # entire algorithm deterministic for set seed values. There
                # may be a more elegant way to get this same behaviour.

                def _inverse_transform_sample(vals):
                    """
                    This function takes a list of values representing
                    relative probabilities and randomly returns an index:

                    e.g. for vals = [1, 2, 2], the function should return
                    0 half as often as 1. It should return 1 and 2 with the
                    same relative frequency.

                    The function first calculates the cumulative sum of
                    values, e.g.

                    cumsum_vals = [1, 3, 5].

                    Then random_val uniformly sampled from the range (0,5).
                    The function  then returns the index from the first value
                    in cumsum_vals that is greater than this random_val.
                    """

                    cumsum_vals = _cumulative_sum(vals)
                    max_val = cumsum_vals[-1]
                    random_val = seed.uniform(0, max_val)

                    # if there is overflow math.exp(...) such that
                    # candidate_comm_prob contains an float('inf') value,
                    # then we will have:
                    #
                    #     max_val = float('inf')
                    #     random_val = float('inf')
                    #
                    # and the function will always return
                    #
                    #    i = <index of the first float('inf') in vals>

                    # I do not know if this is desirable behaviour

                    for i, v in enumerate(cumsum_vals):
                        if random_val <= v:
                            # by construction random_val <= cumsum_vals[-1],
                            # thereore this function will always return a
                            # valid index value
                            return i

                # The community to move u into is chosen at random
                random_index = _inverse_transform_sample(candidate_comm_prob)
                new_comm = candidate_comm[random_index]

                partition[comm].remove(u)
                partition[new_comm].add(u)
                node2com[u] = new_comm

    return partition, node2com


def _cumulative_sum(val_list):
    """
    returns the cumulative sum of a list of numerical values
    same as the np.cumsum(val_array)
    """
    cumsum_vals = []

    running_total = 0
    for val in val_list:
        running_total += val
        cumsum_vals.append(running_total)

    return cumsum_vals


def _gen_graph(G, partition):
    """
    Generate a new graph based on the partitions of a given graph

    New node weight is the sum of existing node weights.

    Edge weight between new nodes is the sum of edge weights
    over the edges connecting pairs of communities.
    """

    H = G.__class__()
    node2com = {}

    for i, part in enumerate(partition):
        new_size = 0

        nodes = set()

        for node in part:
            new_size += _get_node_size(G, node, "node_weight")
            node2com[node] = i
            nodes.update(G.nodes[node].get("nodes", {node}))

        H.add_node(i, nodes=nodes, node_weight=new_size)

    for u, v, d in G.edges(data=True):
        uv_weight = d["weight"]
        com_u = node2com[u]
        com_v = node2com[v]
        if com_u != com_v:
            if H.has_edge(com_u, com_v):
                H.edges[(com_u, com_v)]["weight"] += uv_weight
            else:
                H.add_edge(com_u, com_v, weight=uv_weight)

    return H


def _get_node_size(G, node, node_weight):
    """
    The leiden algorithm uses a size value for nodes, where
    in the aggregated graphs, the size of a node is defined
    as the sum of the sizes of its member nodes.

    By default nodes are initialised with size 1, but the
    algorithm can accept arbitrary float node weights
    """
    return G.nodes[node].get(node_weight, 1)


def _size_of_node_set(G, C, node_weight):
    """
    Returns sum of the node weights of a set of nodes.
    i.e. the quantity n_C from the leiden docs.
    """
    return sum(wt for u, wt in G.nodes(data=node_weight) if u in C)


def _community_edge_size(G, C1, C2, weight):
    """
    Returns the sum of all edge weight for edges between communites C1 and
    C2 i.e. the quantity E(C1, C2) from the leiden docs.
    """
    return sum(wt for u, v, wt in G.edges(C1, data=weight) if u in C1 and v in C2)


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
