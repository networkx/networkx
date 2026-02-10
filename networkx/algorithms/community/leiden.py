"""Functions for detecting communities based on Leiden Community Detection
algorithm.
"""

import itertools
import math
import random
from collections import defaultdict, deque

import networkx as nx
from networkx.algorithms.community.quality import constant_potts_model
from networkx.utils import not_implemented_for, py_random_state

__all__ = ["leiden_communities", "leiden_partitions"]


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
        G, weight, node_weight, resolution, threshold, seed, quality_function, theta
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
    theta=0.01,
):
    """ """

    partition = [{u} for u in G.nodes()]
    inner_partition = None

    if nx.is_empty(G):
        yield partition
        return

    is_directed = G.is_directed()
    if G.is_multigraph():
        graph = _convert_multigraph(G, weight, is_directed)
        weight = "weight"
    else:
        if weight:
            graph = G.__class__()
            graph.add_nodes_from(G)
            graph.add_weighted_edges_from(G.edges(data=weight, default=1))
            weight = "weight"
        else:
            weight = "weight"
            graph = G.__class__()
            graph.add_nodes_from(G)
            graph.add_edges_from(G.edges())
            for e in graph.edges():
                graph.edges[e][weight] = 1

    if node_weight:
        for node in G.nodes():
            graph.nodes[node]["node_weight"] = G.nodes[node][node_weight]
    else:
        node_weight = "node_weight"
        for node in G.nodes():
            graph.nodes[node][node_weight] = 1

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
            graph, inner_partition, quality_function, resolution, seed=seed
        )

        inner_partition_refined = _refine_partition(
            graph, inner_partition, resolution, quality_function, seed, theta
        )

        new_quality = quality_function(
            graph,
            inner_partition_refined,
            resolution=resolution,
            weight="weight",
            node_weight="node_weight",
        )

        graph = _gen_graph(graph, inner_partition_refined)

        # the partition of the underlying graph is read from the
        # node attribute 'nodes', which is set during _gen_graph
        partition = [set() for _ in graph.nodes()]
        for i, u in enumerate(graph.nodes()):
            partition[i].update(graph.nodes[u]["nodes"])

        yield [s.copy() for s in partition]

        improvement_made = (new_quality - quality) > threshold
        quality = new_quality

    return


def _move_nodes_fast(
    G,
    seed_partition,
    quality_function,
    resolution,
    seed=None,
):
    inner_partition = [{u} for u in G.nodes()]
    node2com = {u: i for i, u in enumerate(G.nodes())}

    # unlike louvain, instead of beginning each iteration with the singleton
    # partition, each iteration uses the (unrefined) partition from the previous
    # step as the starting communities when moving nodes
    # this section of code initilises nodes into those communities.
    # if no partition is passed from the previous step (i.e. during the
    # first iteration) then this is skipped and the singleton partition is used.
    if seed_partition:
        for i, u in enumerate(G.nodes()):
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

        # for each node in the queue, we measure the change in quality
        # from moving that node to each other community, keeping track of
        # the community that gives the greatest improvement best_com
        for new_com in set(node2com.values()):
            if new_com != old_com:
                q1 = quality_function(
                    G,
                    [inner_partition[new_com], inner_partition[old_com]],
                    resolution=resolution,
                    allow_partial=True,
                )

                inner_partition[old_com].remove(u)
                inner_partition[new_com].add(u)

                q2 = quality_function(
                    G,
                    [inner_partition[new_com], inner_partition[old_com]],
                    resolution=resolution,
                    allow_partial=True,
                )

                quality_delta = q2 - q1

                if quality_delta > best_delta:
                    best_delta = quality_delta
                    best_com = new_com

                inner_partition[new_com].remove(u)
                inner_partition[old_com].add(u)

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


def _refine_partition(G, partition, resolution, quality_function, seed, theta):
    node2com = {u: i for i, u in enumerate(G.nodes())}
    inner_partition_refined = [{u} for u in G.nodes()]

    for C in partition:
        inner_partition_refined, node2com = _merge_node_subset(
            G,
            inner_partition_refined,
            node2com,
            C,
            resolution,
            quality_function,
            seed,
            theta,
        )

    inner_partition_refined = list(filter(len, inner_partition_refined))
    return inner_partition_refined


def _merge_node_subset(
    G, partition, node2com, S, resolution, quality_function, seed, theta
):
    S_size = _size_of_node_set(G, S, "node_weight")

    R = set()
    for u in S:
        u_size = _get_node_size(G, u, "node_weight")
        community_factor = _community_edge_size(G, {u}, S - {u}, "weight")
        factor_comparison = resolution * u_size * (S_size - u_size)

        if community_factor > factor_comparison:
            R.add(u)

    for u in R:
        comm = node2com[u]
        if len(partition[comm]) == 1:
            candidate_comm = []
            candidate_comm_delta = []
            for i, C in enumerate(partition):
                if comm == i:
                    pass
                elif len(C) == 0:
                    pass
                elif C.issubset(S):
                    E = _community_edge_size(G, C, S - C, "weight")
                    C_size = _size_of_node_set(G, C, "node_weight")
                    comm_comparison = resolution * C_size * (S_size - C_size)
                    if E > comm_comparison:
                        q1 = quality_function(
                            G,
                            [partition[comm], partition[i]],
                            resolution=resolution,
                            allow_partial=True,
                        )

                        partition[comm].remove(u)
                        partition[i].add(u)

                        q2 = quality_function(
                            G,
                            [partition[comm], partition[i]],
                            resolution=resolution,
                            allow_partial=True,
                        )

                        quality_delta = q2 - q1

                        if quality_delta > 0:
                            candidate_comm.append(i)
                            # it is quite easy to get overflow in this math.exp(...)
                            # numpy handles this more elegantly
                            try:
                                val = math.exp(quality_delta / theta)
                            except OverflowError:
                                val = float("inf")
                            candidate_comm_delta.append(val)
                        partition[comm].add(u)
                        partition[i].remove(u)

            if len(candidate_comm) > 0:

                def _sample_from_discrete(vals):
                    # if there is overflow error then vals can contain
                    # the value float('inf') in which case we will have
                    #
                    # cumsum_vals = float('inf')
                    # max_val = float('inf')
                    # random_val = float('inf')
                    #
                    # and the function will always return
                    # i = <index of the first float('inf') in vals>

                    # I do not know if this is desirable behaviour

                    cumsum_vals = _cumulative_sum(vals)
                    max_val = cumsum_vals[-1]
                    random_val = seed.uniform(0, max_val)

                    for i, v in enumerate(cumsum_vals):
                        if random_val <= v:
                            return i

                random_index = _sample_from_discrete(candidate_comm_delta)
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
    size = G.nodes[node].get(node_weight, 1)
    return size


def _size_of_node_set(G, nodes, node_weight):
    size = 0
    for u in nodes:
        size += _get_node_size(G, u, node_weight)
    return size


def _community_edge_size(G, C1, C2, weight):
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
