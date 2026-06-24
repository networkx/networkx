"""Detecting communities based on the Leiden Community Detection algorithm"""

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

    The algorithm works in 3 phases. In the first phase, starting with a partition
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
    metric : {"cpm", "modularity"}, default="cpm"
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
    list of sets of nodes
        A partition of `G` as a list of disjoint sets of nodes. Each set represents
        one community of nodes and each node of `G` appears in exactly one set.

    Examples
    --------
    >>> G = nx.barbell_graph(3, 4)
    >>> cpm_comm = nx.community.leiden_communities(G, resolution=0.2, seed=62537113)
    >>> len(cpm_comm)
    3
    >>> sorted(sorted(c) for c in cpm_comm)
    [[0, 1, 2], [3, 4, 5, 6], [7, 8, 9]]

    Higher resolution produces smaller sub-communities:

    >>> cpm_comm = nx.community.leiden_communities(G, resolution=0.4, seed=62537114)
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
    level represents a partition of the graph `G`. The top level contains the
    smallest communities and as you traverse the tree the communities get
    bigger and the overall partition quality metric increases.

    Each level is generated by executing the three phases of the
    :ref:`Leiden Community Detection algorithm <leiden_communities>`.

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    metric : {"cpm", "modularity"}, default="cpm"
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

    if nx.is_empty(G):
        yield partition
        return

    # Initialization steps while copying G to graph
    # - edge weights set as "weight" in graph, summed if G.is_multigraph()
    # - node attributes initialized based on metric impact on node_weights aggregated
    # - define the metric function based on metric
    # - define the corresponding delta function
    # - set node_attributes dict keyed by node attr to dict keyed by node

    # delta function gives change in metric when merging two communities.
    # The change due to splitting a set U from C is negating e.g. -delta_func(U, C-U)
    # For one node, the change from moving node u from A to B is:
    # q_delta = delta_func(u, B) - delta_func(u, A-{u})

    orig_G = G  # make copy of original G to allow mutations
    is_directed = orig_G.is_directed()
    if orig_G.is_multigraph():
        # Convert Multi(Di)Graph to (Di)Graph by summing edges
        G = nx.DiGraph() if is_directed else nx.Graph()
        G.add_nodes_from(orig_G)
        G.add_edges_from(orig_G.edges())
        if weight is None:
            edge_wts = {
                u: {v: len(kd) for v, kd in nbrs.items()}
                for u, nbrs in orig_G._adj.items()
            }
            if is_directed:
                in_edge_wts = {
                    u: {v: len(kd) for v, kd in nbrs.items()}
                    for u, nbrs in orig_G._pred.items()
                }
        else:
            edge_wts = {
                u: {
                    v: sum(dd.get(weight, 1) for dd in kd.values())
                    for v, kd in nbrs.items()
                }
                for u, nbrs in orig_G._adj.items()
            }
            if is_directed:
                in_edge_wts = {
                    u: {
                        v: sum(dd.get(weight, 1) for dd in kd.values())
                        for v, kd in nbrs.items()
                    }
                    for u, nbrs in orig_G._pred.items()
                }
    else:
        # same nodes & class as orig_G
        G = nx.empty_graph(orig_G, create_using=orig_G.__class__)
        G.add_edges_from(orig_G.edges)
        if weight is None:
            edge_wts = {u: {v: 1 for v in nbrs} for u, nbrs in orig_G._adj.items()}
            if is_directed:
                in_edge_wts = {
                    u: {v: 1 for v in nbrs} for u, nbrs in orig_G._pred.items()
                }
        else:
            edge_wts = {
                u: {v: dd.get(weight, 1) for v, dd in nbrs.items()}
                for u, nbrs in orig_G._adj.items()
            }
            if is_directed:
                in_edge_wts = {
                    u: {v: dd.get(weight, 1) for v, dd in nbrs.items()}
                    for u, nbrs in orig_G._pred.items()
                }
    G.graph["edge_wts"] = edge_wts
    if is_directed:
        G.graph["in_edge_wts"] = in_edge_wts

    # node attr "nodes" holds the original nodes represented by this current node
    # initialize to point to itself
    nx.set_node_attributes(G, {n: {n} for n in orig_G}, "nodes")

    if metric == "cpm":
        # Setup for constant potts model
        metric_function = functools.partial(
            constant_potts_model,
            resolution=resolution,
            node_weight="node_weight",
            weight="weight",
        )

        node_weights = dict.fromkeys(G, 1)
        node_attributes = {"node_weight": node_weights}

        if is_directed:
            # Setup for directed constant potts model
            gamma = 2 * resolution

            # Note: delta_func uses objects in defining namespace:
            # - gamma
            # - node_weights
            # - edge_wts
            # - in_edge_wts
            def delta_func(nodes_to_add, community):
                comm_size = sum(node_weights[u] for u in community)
                if isinstance(nodes_to_add, set):
                    nodes_size = sum(node_weights[u] for u in nodes_to_add)

                    if len(nodes_to_add) <= len(community):
                        A, C = nodes_to_add, community
                    else:
                        A, C = community, nodes_to_add
                    E_in = sum(
                        wt for u in A for v, wt in in_edge_wts[u].items() if v in C
                    )
                    E_out = sum(
                        wt for u in A for v, wt in edge_wts[u].items() if v in C
                    )
                else:
                    nodes_size = node_weights[nodes_to_add]

                    u, C = nodes_to_add, community
                    E_in = sum(wt for v, wt in in_edge_wts[u].items() if v in C)
                    E_out = sum(wt for v, wt in edge_wts[u].items() if v in C)

                return E_in + E_out - gamma * comm_size * nodes_size

        else:
            # Setup for undirected constant potts model
            gamma = resolution

            # Note: delta_func uses objects in defining namespace:
            # - gamma
            # - node_weights
            # - edge_wts
            def delta_func(nodes_to_add, community):
                comm_size = sum(node_weights[u] for u in community)
                if isinstance(nodes_to_add, set):
                    nodes_size = sum(node_weights[u] for u in nodes_to_add)

                    if len(nodes_to_add) <= len(community):
                        A, C = nodes_to_add, community
                    else:
                        A, C = community, nodes_to_add
                    E = sum(wt for u in A for v, wt in edge_wts[u].items() if v in C)
                else:
                    nodes_size = node_weights[nodes_to_add]

                    u, C = nodes_to_add, community
                    E = sum(wt for v, wt in edge_wts[u].items() if v in C)

                return E - gamma * comm_size * nodes_size

    elif metric == "modularity":
        # Setup for (unipartite) modularity
        metric_function = functools.partial(
            modularity,
            resolution=resolution,
            weight="weight",
        )

        if is_directed:
            # Setup for directed modularity
            gamma = 2 * resolution

            # scale edge weights by total so m == 1 and can be removed from formulas
            m = sum(wt for u, nbrs in edge_wts.items() for v, wt in nbrs.items())
            for u, nbrs in in_edge_wts.items():
                for v, wt in nbrs.items():
                    in_edge_wts[u][v] /= m
            for u, nbrs in edge_wts.items():
                for v, wt in nbrs.items():
                    edge_wts[u][v] /= m

            in_degrees = {u: sum(nbrs.values()) for u, nbrs in in_edge_wts.items()}
            out_degrees = {u: sum(nbrs.values()) for u, nbrs in edge_wts.items()}
            node_attributes = {"in_degree": in_degrees, "out_degree": out_degrees}

            # Note: delta_func uses objects in defining namespace:
            # - gamma
            # - in_degrees
            # - out_degrees
            # - in_edge_wts
            # - edge_wts
            def delta_func(nodes_to_add, community):
                if isinstance(nodes_to_add, set):
                    if len(nodes_to_add) <= len(community):
                        A, C = nodes_to_add, community
                    else:
                        A, C = community, nodes_to_add

                    A_in = sum(in_degrees[u] for u in A)
                    A_out = sum(out_degrees[u] for u in A)
                    C_in = sum(in_degrees[u] for u in C)
                    C_out = sum(out_degrees[u] for u in C)

                    E_in = sum(
                        wt for u in A for v, wt in in_edge_wts[u].items() if v in C
                    )
                    E_out = sum(
                        wt for u in A for v, wt in edge_wts[u].items() if v in C
                    )
                else:
                    A_in = in_degrees[nodes_to_add]
                    A_out = out_degrees[nodes_to_add]
                    C_in = sum(in_degrees[u] for u in community)
                    C_out = sum(out_degrees[u] for u in community)

                    u, C = nodes_to_add, community
                    E_in = sum(wt for v, wt in in_edge_wts[u].items() if v in C)
                    E_out = sum(wt for v, wt in edge_wts[u].items() if v in C)

                return E_in + E_out - gamma * (A_in * C_out + A_out * C_in)

        else:
            # Setup for undirected modularity
            gamma = 2 * resolution

            # scale edge weights by total so m == 1 and can be removed from formulas
            m = sum(wt for u, nbrs in edge_wts.items() for v, wt in nbrs.items())
            for u, nbrs in edge_wts.items():
                for v, wt in nbrs.items():
                    edge_wts[u][v] /= m

            degrees = {u: sum(nbrs.values()) for u, nbrs in edge_wts.items()}
            node_attributes = {"degree": degrees}

            # Note: delta_func uses objects in defining namespace:
            # - gamma
            # - degrees
            # - edge_wts
            def delta_func(nodes_to_add, community):
                comm_size = sum(degrees[u] for u in community)
                if isinstance(nodes_to_add, set):
                    nodes_size = sum(degrees[u] for u in nodes_to_add)

                    if len(nodes_to_add) <= len(community):
                        A, C = nodes_to_add, community
                    else:
                        A, C = community, nodes_to_add
                    E = sum(wt for u in A for v, wt in edge_wts[u].items() if v in C)
                else:
                    nodes_size = degrees[nodes_to_add]

                    u, C = nodes_to_add, community
                    E = sum(wt for v, wt in edge_wts[u].items() if v in C)

                return E - gamma * nodes_size * comm_size

    elif metric == "barber_modularity":
        # Setup for undirected bipartite barber modularity (not fully implemented)

        if is_directed:
            raise nx.NetworkXError("barber_modularity not implemented for DiGraph")

        # metric should be defined inline rather than
        # importing nx.bipartite.community.modularity as the
        # function within this algorithm needs to accept the
        # aggregated graphs which are not bipartite and therefore
        # requires a variation of the algorithm

        def barber_modularity():
            return

        metric_function = barber_modularity

        # scale edge weights by total so m == 1 and can be removed from formulas
        m = sum(wt for u, nbrs in edge_wts.items() for v, wt in nbrs.items())
        for u, nbrs in edge_wts.items():
            for v, wt in nbrs.items():
                edge_wts[u][v] /= m

        red_nodes = {u for u, c in G.nodes(data="bipartite") if c == 0}
        blue_nodes = {u for u, c in G.nodes(data="bipartite") if c == 1}
        # TODO add check for this being a bipartite graph

        red_degrees = {u: sum(edge_wts[u].values()) for u in red_nodes}
        red_degrees.update((u, 0) for u in blue_nodes)
        blue_degrees = {u: sum(edge_wts[u].values()) for u in blue_nodes}
        blue_degrees.update((u, 0) for u in red_nodes)

        node_attributes = {"red_degree": red_degrees, "blue_degree": blue_degrees}

        # Note: delta_func uses objects in defining namespace:
        # - gamma
        # - red_degrees
        # - blue_degrees
        # - edge_wts
        def delta_func(nodes_to_add, community):
            comm_red = sum(red_degrees[u] for u in community)
            comm_blue = sum(blue_degrees[u] for u in community)
            if isinstance(nodes_to_add, set):
                nodes_red = sum(red_degrees[u] for u in nodes_to_add)
                nodes_blue = sum(blue_degrees[u] for u in nodes_to_add)

                if len(nodes_to_add) <= len(community):
                    A, C = nodes_to_add, community
                else:
                    A, C = community, nodes_to_add
                E = sum(wt for u in A for v, wt in edge_wts[u].items() if v in C)
            else:
                nodes_red = red_degrees[nodes_to_add]
                nodes_blue = blue_degrees[nodes_to_add]

                u, C = nodes_to_add, community
                E = sum(wt for v, wt in edge_wts[u].items() if v in C)

            return E - resolution * (nodes_red * comm_blue + nodes_blue * comm_red)

        raise nx.NetworkXError("barber_modularity not implemented for leiden")
    else:
        raise nx.NetworkXError(
            f'leiden only supports metrics "cpm" and "modularity". Got: {metric}'
        )

    # The setup phase has ended, the main algorithm now begins.
    Q = metric_function(G, partition)

    improvement_made = True
    node2com = {node: i for i, node in enumerate(G)}

    while improvement_made:
        # _move_nodes_fast (name from paper) is like _one_level in nx.louvain
        # Move nodes to new community with greatest increase in quality/matric
        # Start with the unrefined partition from previous stage.
        P = _move_nodes_fast(G, node2com, delta_func, seed=seed)

        # Refine the communities using _merge_node_subset (name from paper)
        P_refined = [_merge_node_subset(C, delta_func, seed, theta) for C in P]
        P_refined_flat = [comm for p in P_refined for comm in p]

        # Stop when overall change is close to zero.
        Q_new = metric_function(G, P_refined_flat)
        improvement_made = (Q_new - Q) > 0.0000001
        Q = Q_new

        # Aggregate communities into the nodes for the next stage.
        # Edges in next stage if any edges between nodes at this stage.
        # Sum node and edge data to get aggregated graph data.
        G, node2com = _create_aggregate_graph(G, P_refined, node_attributes)

        # Each node in G represents a community in the original graph
        # held in G.nodes(data="nodes").
        # Yield a copy to protect this data structure for later stages.
        yield [nodes.copy() for _, nodes in G.nodes(data="nodes")]

        # unpack node data of new G to this namespace so delta_func() can use it
        edge_wts = G.graph["edge_wts"]
        if is_directed:
            in_edge_wts = G.graph["in_edge_wts"]

        if metric == "cpm":
            node_weights = node_attributes["node_weight"]
        elif metric == "modularity":
            if is_directed:
                in_degrees = node_attributes["in_degree"]
                out_degrees = node_attributes["out_degree"]
            else:
                degrees = node_attributes["degree"]
        elif metric == "barber_modularity":
            red_degrees = node_attributes["red_degree"]
            blue_degrees = node_attributes["blue_degree"]
    return


def _move_nodes_fast(G, node2com, delta_func, seed):
    P = [set() for _ in node2com]
    for node, comm in node2com.items():
        P[comm].add(node)

    rand_nodes = list(node2com)
    seed.shuffle(rand_nodes)

    # Use dict as a partial deque (pop_left, pop and update_right with no dups).
    # pop_left takes two steps using next(iter()) and pop.
    # update adds to the end only if not in queue already.
    # membership check is O(1) (speedup over deque).
    dict_deque = dict.fromkeys(rand_nodes)
    while dict_deque:
        # pop first node in queue
        u = next(iter(dict_deque))
        dict_deque.pop(u)

        old_com = node2com[u]
        # get neighbors (both in & out when directed)
        u_nbrs = set(nx.all_neighbors(G, u))
        nbr_coms = {node2com[v] for v in u_nbrs} - {old_com}
        if not nbr_coms:
            continue

        # find community to move u to with biggest increase in metric
        best_add, best_com = max((delta_func(u, P[c]), c) for c in nbr_coms)

        # decrease in metric when u is removed from its old community
        P_old_com = P[old_com]
        u_rem = delta_func(u, P_old_com - {u})

        if best_add > u_rem:
            node2com[u] = best_com
            P_old_com.remove(u)
            P[best_com].add(u)

            # Requeue nbrs from other coms if not already in queue
            # Add to end of queue (revisit after currently queued nodes)
            nodes_to_revisit = u_nbrs - P[best_com]
            dict_deque.update(dict.fromkeys(nodes_to_revisit))

    # remove empty sets from P
    return [p for p in P if p]


def _merge_node_subset(C, delta_func, seed, theta):
    C_refined = [{u} for u in C]
    # R contains well-connected nodes within C
    R = {u: i for i, u in enumerate(C) if delta_func(u, C - {u}) > 0}

    # T[i] > 0 means community i is well connected to others
    # Definition of T in line 37 of pseudocode in paper (supplemental mat.)
    # uses condition for "cpm" matric: E(C, S-C) >= gamma * |C| * (|S| - |C|)
    # where |X| is the node_weight of the set X of nodes.
    # We generalize to any metric by using condition T(i) > 0
    T = {i: delta_func(u, C - {u}) for i, u in enumerate(C)}

    for u, comm_i in R.items():
        # Only process nodes that are still in a singleton community {u}
        # - Find candidate communities for u to merge with
        # - Select one randomly based on relative delta for each community
        #   Note: not choosing the best one
        if len(C_refined[comm_i]) != 1:
            continue

        cand_comms = []
        cand_comm_deltas = []
        # Note: delta for removing u from current comm is 0 (singleton comm)
        for i, new_comm in enumerate(C_refined):
            # Main condition is T[i] > 0. also not empty and not same community
            if comm_i == i or not new_comm or T[i] <= 0:
                continue

            Q_delta = delta_func(u, new_comm)
            if Q_delta > 0:
                cand_comms.append(i)
                cand_comm_deltas.append(Q_delta)

        # select one candidate community at random
        if cand_comms:
            # probability of each candidate comm determined by Q_delta
            # Relative frequency is proportional to
            #       math.exp(Q_delta/theta)
            # Large exponentials can overflow so normalize to
            #       math.exp((Q_delta - max_Q_delta)/theta)
            max_delta = max(cand_comm_deltas)
            cand_wts = [math.exp((x - max_delta) / theta) for x in cand_comm_deltas]
            new_comm_i = seed.choices(cand_comms, weights=cand_wts)[0]

            C_refined[comm_i].remove(u)
            T[comm_i] = 0
            new_comm = C_refined[new_comm_i]
            new_comm.add(u)
            # Note: delta_func here has a set as 1st arg:
            #       returns delta when combining the two sets.
            T[new_comm_i] = delta_func(new_comm, C - new_comm)

    return [c for c in C_refined if c]


def _create_aggregate_graph(G, P_refined, node_attributes):
    """Return a new graph based on P_refined. Each community becomes a node.

    Note: `node_attributes` is changed in place by this function!

    P_refined is a list of lists of community sets. The outer list indicates
    communities in the new graph which comes from P. Each inner list holds
    the refined sets of nodes each of which becomes a new node. So P_refined
    contains P as the outer list and its refinement as the inner lists which
    hold the refined community sets that make up the new graph's nodes.

    node_attributes is a dict keyed by each attribute name to be aggregated
    which depends on the metric being used.
    The value is a dict for that attribute keyed by node to the attribute value.
    Aggregate means sum within a G community into a new node in H.
    After this function the incoming dict values are replaced by aggregated dicts.
    """
    G_original_nodes = G.nodes(data="nodes")

    nodes_G2H = {}
    H = G.__class__()
    H_node2com = {}
    H_node_id = 0
    H_node_attributes = {attr_name: {} for attr_name in node_attributes}
    for H_comm_id, refined_comms in enumerate(P_refined):
        for refined_comm in refined_comms:
            # each set from the refined_sets defines
            # a node in the new aggregated graph. Name it new_node_id.
            H_node2com[H_node_id] = H_comm_id
            agg_vals = {attribute: 0 for attribute in node_attributes}

            # contains the original graph nodes defining this new community
            original_nodes = set()

            # G_node is node from previous stage, not original graph
            for G_node in refined_comm:
                nodes_G2H[G_node] = H_node_id

                # aggregate node attributes
                original_nodes.update(G_original_nodes[G_node])
                for attr_name, attr_dict in node_attributes.items():
                    agg_vals[attr_name] += attr_dict[G_node]

            H.add_node(H_node_id, nodes=original_nodes)
            for attr_name in node_attributes:
                H_node_attributes[attr_name][H_node_id] = agg_vals[attr_name]
            H_node_id += 1
    # load H_node_attr into node_attributes dict (overwrites G data)
    # This is a hack to morph node info in main function so delta_func can use it
    # We could store this info as graph node data, but that is slower and fatter.
    for attr_name in node_attributes:
        node_attributes[attr_name] = H_node_attributes[attr_name]

    # Handle edge_wts and in_edge_wts
    is_directed = H.is_directed()
    H_edge_wts = {H_node: {} for H_node in H}
    if is_directed:
        H_in_edge_wts = {H_node: {} for H_node in H}
    for u, nbrs in G.graph["edge_wts"].items():
        H_u = nodes_G2H[u]
        H_unbrs = H_edge_wts[H_u]
        for v, uv_weight in nbrs.items():
            H_v = nodes_G2H[v]
            if H_u != H_v:
                if H_v in H_unbrs:
                    H_unbrs[H_v] += uv_weight
                    if is_directed:
                        H_in_edge_wts[H_v][H_u] += uv_weight
                else:
                    H.add_edge(H_u, H_v)
                    H_unbrs[H_v] = uv_weight
                    if is_directed:
                        H_in_edge_wts[H_v][H_u] = uv_weight
    H.graph["edge_wts"] = H_edge_wts
    if is_directed:
        H.graph["in_edge_wts"] = H_in_edge_wts
    return H, H_node2com
