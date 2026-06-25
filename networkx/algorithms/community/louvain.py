"""Detecting communities based on the Louvain Community Detection algorithm"""

import itertools
from collections import defaultdict, deque

import networkx as nx
from networkx.algorithms.community import modularity
from networkx.utils import py_random_state

__all__ = ["louvain_communities", "louvain_partitions"]


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def louvain_communities(
    G, weight="weight", resolution=1, threshold=0.0000001, max_level=None, seed=None
):
    r"""Find the best partition of a graph using the Louvain Community Detection
    Algorithm.

    Louvain Community Detection seeks to extract the community structure of a
    network. It is a heuristic algorithm based on modularity optimization. [1]_

    The algorithm starts with every node in its own community and then repeatedly
    updates by merging communities. Each update consists of two phases.
    First, each node is examined to find the maximum positive modularity gain
    obtained by moving it to a different community. If no positive gain can be
    achieved the node remains in its original community. The next node is then
    considered. Nodes containue to be examined until no improvement in
    modularity can be obtained by moving nodes. The second phase shifting to
    an aggregated network where each community of the original network is a
    node in the new network with edges connnecting then if nodes in those
    two communities connect to each other. The edge weights and node attributes
    of the new network are the sums of edge and node attributes from the
    communities in the previous network. These two phases are repeated until
    no modularity gain is achieved (or is less than a `threshold`, or until
    `max_levels` updates have occured).

    The modularity gain obtained by moving an isolated node $i$ into a community
    $C$ can be calculated by the following formula
    (combining [1]_ [2]_ and some algebra):

    .. math::
        \Delta Q = \frac{k_{i,in}}{2m} - \gamma\frac{ \Sigma_{tot} \cdot k_i}{2m^2}

    where $m$ is the size of the graph; $k_{i,in}$ is the sum of the edge weights
    from $i$ to nodes in $C$; $k_i$ is the sum of the edge weights incident to
    node $i$; $\Sigma_{tot}$ is the sum of the edge weights incident to nodes in $C$;
    and $\gamma$ is the resolution parameter. Higher resolution produces smaller
    communities. Low resolution produces larger communities.

    For the directed case the modularity gain can be computed (see [3]_) using
    the formula:

    .. math::
        \Delta Q = \frac{k_{i,in}}{m}
        - \gamma\frac{k_i^{out} \cdot\Sigma_{tot}^{in} + k_i^{in} \cdot \Sigma_{tot}^{out}}{m^2}

    where $k_i^{out}$, $k_i^{in}$ are the outer and inner weighted degrees of node
    $i$; $\Sigma_{tot}^{in}$ and $\Sigma_{tot}^{out}$ are the sum of in-going and
    out-going edge weights incident to nodes in $C$.

    Be careful with self-loops in the input graph. These are treated as
    previously reduced communities -- as if the process had been started
    in the middle of the algorithm. Large self-loop edge weights thus
    represent strong communities and in practice may be hard to add
    other nodes to.  If your input graph edge weights for self-loops
    do not represent already reduced communities you may want to remove
    the self-loops before using that graph.

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
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

    Returns
    -------
    list
        A list of sets (partition of `G`). Each set represents one community
        and contains all the nodes in that community.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.petersen_graph()
    >>> nx.community.louvain_communities(G, seed=123)
    [{0, 4, 5, 7, 9}, {1, 2, 3, 6, 8}]

    Notes
    -----
    The order in which the nodes are considered can affect the final output.
    In the algorithm the ordering happens using a random shuffle.

    References
    ----------
    .. [1] Blondel, V.D. et al. Fast unfolding of communities in large networks.
           J. Stat. Mech 10008, 1-12(2008).
           https://doi.org/10.1088/1742-5468/2008/10/P10008
    .. [2] Traag, V.A., Waltman, L. & van Eck, N.J.
           From Louvain to Leiden: guaranteeing well-connected communities.
           Sci Rep 9, 5233 (2019). https://doi.org/10.1038/s41598-019-41695-z
    .. [3] Nicolas Dugué, Anthony Perez.
           Directed Louvain : maximizing modularity in directed networks.
           [Research Report] Université d’Orléans. 2015.
           hal-01231784. https://hal.archives-ouvertes.fr/hal-01231784

    See Also
    --------
    louvain_partitions
    :any:`leiden_communities`
    """

    partitions = louvain_partitions(G, weight, resolution, threshold, seed)
    if max_level is not None:
        if max_level <= 0:
            raise ValueError("max_level argument must be a positive integer or None")
        partitions = itertools.islice(partitions, max_level)
    final_partition = deque(partitions, maxlen=1)
    return final_partition.pop()


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def louvain_partitions(
    G, weight="weight", resolution=1, threshold=0.0000001, seed=None
):
    """Yield partitions for each level of the Louvain Community Detection Algorithm

    Louvain Community Detection seeks to extract the community structure of a
    network. It is a heuristic algorithm based on modularity optimization. [1]_

    The partitions at each level (step of the algorithm) form a dendrogram of
    communities. A dendrogram is a diagram representing a tree and each level
    represents a partition of the G graph. The first level contains the smallest
    communities and as you traverse to later levels the communities get bigger
    and the overall modularity increases.

    Each level is generated by executing the two phases of the Louvain Community
    Detection Algorithm.

    Be careful with self-loops in the input graph. These are treated as
    previously reduced communities -- as if the process had been started
    in the middle of the algorithm. Large self-loop edge weights thus
    represent strong communities and in practice may be hard to add
    other nodes to.  If your input graph edge weights for self-loops
    do not represent already reduced communities you may want to remove
    the self-loops before inputting that graph.

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    resolution : float, optional (default=1)
        If resolution is less than 1, the algorithm favors larger communities.
        Greater than 1 favors smaller communities
    threshold : float, optional (default=0.0000001)
        Modularity gain threshold for each level. If the gain of modularity
        between 2 levels of the algorithm is less than the given threshold
        then the algorithm stops and returns the resulting communities.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Yields
    ------
    list
        A list of sets (partition of `G`). Each set represents one community
        and contains all the nodes in that community.

    References
    ----------
    .. [1] Blondel, V.D. et al. Fast unfolding of communities in large networks.
           J. Stat. Mech 10008, 1-12(2008).
           http://dx.doi.org/10.1088/1742-5468/2008/10/P10008

    See Also
    --------
    louvain_communities
    :any:`leiden_partitions`
    """
    P = [{u} for u in G]
    if nx.is_empty(G):
        yield P
        return

    mod = modularity(G, P, resolution=resolution, weight=weight)

    is_directed = G.is_directed()
    orig_G = G
    G = nx.DiGraph() if is_directed else nx.Graph()
    G.add_nodes_from(orig_G)

    if orig_G.is_multigraph():
        for u, v, wt in orig_G.edges(data=weight, default=1):
            if G.has_edge(u, v):
                G[u][v]["weight"] += wt
            else:
                G.add_edge(u, v, weight=wt)
    else:
        G.add_weighted_edges_from(orig_G.edges(data=weight, default=1))

    m = orig_G.size(weight=weight)
    P, inner_P, _ = _one_level(G, P, m, resolution, is_directed, seed)
    improvement = True
    while improvement:
        # use copy to protect P from manipulation of the yielded sets (see gh-5901)
        yield [C.copy() for C in P]
        new_mod = modularity(G, inner_P, resolution=resolution, weight="weight")
        if new_mod - mod <= threshold:
            return

        mod = new_mod
        G = _aggregate_graph(G, inner_P)
        P, inner_P, improvement = _one_level(G, P, m, resolution, is_directed, seed)


def _one_level(G, partition, m, resolution, is_directed, seed):
    """Calculate one level of the Louvain partitions tree

    Parameters
    ----------
    G : NetworkX Graph/DiGraph
        The graph from which to detect communities
    m : number
        The size of `G`
    partition : list of sets of nodes
        A valid partition of the graph `G`
    resolution : positive number
        The resolution parameter for computing the modularity of a partition
    is_directed : bool
        True if `G` is a directed graph.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    """
    node2com = {u: i for i, u in enumerate(G)}
    inner_partition = [{u} for u in G]
    if is_directed:
        gamma = resolution
        in_degrees = dict(G.in_degree(weight="weight"))
        out_degrees = dict(G.out_degree(weight="weight"))
        Stot_in = list(in_degrees.values())
        Stot_out = list(out_degrees.values())
        # Compute weights for both in and out nbrs, ignoring self-loops
        nbrs = {}
        for u in G:
            nbrs[u] = defaultdict(float)
            for _, n, wt in G.out_edges(u, data="weight"):
                if u != n:
                    nbrs[u][n] += wt
            for n, _, wt in G.in_edges(u, data="weight"):
                if u != n:
                    nbrs[u][n] += wt
    else:
        gamma = resolution / 2
        degrees = dict(G.degree(weight="weight"))
        Stot = list(degrees.values())
        nbrs = {u: {v: dd["weight"] for v, dd in G[u].items() if v != u} for u in G}

    rand_nodes = list(G)
    seed.shuffle(rand_nodes)
    nb_moves = 1
    improvement = False
    while nb_moves > 0:
        nb_moves = 0
        for u in rand_nodes:
            u_com = node2com[u]
            u_deg_by_com = defaultdict(float)
            for nbr, wt in nbrs[u].items():
                u_deg_by_com[node2com[nbr]] += wt

            if is_directed:
                in_degree = in_degrees[u]
                out_degree = out_degrees[u]
                Stot_in[u_com] -= in_degree
                Stot_out[u_com] -= out_degree
                x = out_degree * Stot_in[u_com] + in_degree * Stot_out[u_com]
            else:
                degree = degrees[u]
                Stot[u_com] -= degree
                x = Stot[u_com] * degree
            remove_cost = -u_deg_by_com[u_com] / m + gamma * x / m**2

            best_mod = 0
            best_com = u_com
            for nbr_com, wt in u_deg_by_com.items():
                if is_directed:
                    x = out_degree * Stot_in[nbr_com] + in_degree * Stot_out[nbr_com]
                else:
                    x = Stot[nbr_com] * degree
                gain = remove_cost + wt / m - gamma * x / m**2
                if gain > best_mod:
                    best_mod = gain
                    best_com = nbr_com

            if is_directed:
                Stot_in[best_com] += in_degree
                Stot_out[best_com] += out_degree
            else:
                Stot[best_com] += degree

            if best_com != u_com:
                u_nodes = G.nodes[u].get("nodes", {u})
                partition[u_com].difference_update(u_nodes)
                partition[best_com].update(u_nodes)
                inner_partition[u_com].remove(u)
                inner_partition[best_com].add(u)
                improvement = True
                nb_moves += 1
                node2com[u] = best_com
    partition = [p for p in partition if p]
    inner_partition = [p for p in inner_partition if p]
    return partition, inner_partition, improvement


def _aggregate_graph(G, partition):
    """Generate a new graph based on the partitions of a given graph"""
    H = G.__class__()
    node2com = {}
    for i, part in enumerate(partition):
        nodes = set()
        for node in part:
            node2com[node] = i
            nodes.update(G.nodes[node].get("nodes", {node}))
        H.add_node(i, nodes=nodes)

    for node1, node2, wt in G.edges(data="weight"):
        com1 = node2com[node1]
        com2 = node2com[node2]
        if H.has_edge(com1, com2):
            H.add_edge(com1, com2, weight=wt + H._adj[com1][com2]["weight"])
        else:
            H.add_edge(com1, com2, weight=wt)
    return H
