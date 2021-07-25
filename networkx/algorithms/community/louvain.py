"""Function for detecting communities base on Louvain Community Detection
Algorithm"""

from collections import deque, defaultdict
import random

import networkx as nx
from networkx.algorithms.community import modularity
from networkx.utils import py_random_state

__all__ = ["louvain_communities", "generate_dendrogram"]


@py_random_state("seed")
def louvain_communities(G, weight="weight", threshold=0.0000001, seed=None):
    r"""Find the best partition of G using the Louvain Community Detection
    Algorithm.

    The algorithm works in 2 steps. On the first step it assigns every node to be
    in its own community and then for each node it tries to find the maximum positive
    modularity gain by moving each node to all of its neighbor communities. If no positive
    gain is achieved the node remains in its original community.

    The modularity gain obtained by moving an isolated node $i$ into a community $C$ can
    easily be calculated by the following formula:

    .. math::
        \Delta Q = \frac{k_{i,in}}{2m} - \frac{ \Sigma_{tot} \cdot k_i}{2m^2}

    where $m$ is the size of the graph, $k_{i,in}$ is the sum of the weights of the links
    from $i$ to nodes in $C$, $k_i$ is the sum of the weights of the links incident to node $i$
    and \Sigma_{tot} is the sum of the weights of the links incident to nodes in $C$.

    The first phase continues until no individual move can improve the modularity.

    > Note: The order in which the nodes are considered can affect the final output.

    The second phase consists in building a new network whose nodes are now the communities
    found in the first phase. Once this phase is complete it is possible to reapply the
    first phase creating bigger communities with increased modularity.

    The above two phases are executed until no modularity gain is achieved (or is less than
    the `threshold`).

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    threshold : float, optional (default=0.0000001)
        Modularity gain threshold for each level. If the gain of modularity
        between 2 levels of the algorithm is less than the given threshold
        then the algorithm stops and returns the resulting communities.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    list
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.

    References
    ----------
    .. [1] Blondel, V.D. et al. Fast unfolding of communities in
       large networks. J. Stat. Mech 10008, 1-12(2008)
    """

    d = generate_dendrogram(G, weight, threshold, seed)
    q = deque(d, maxlen=1)
    return q.pop()


@py_random_state("seed")
def generate_dendrogram(G, weight="weight", threshold=0.0000001, seed=None):
    """Compute the communities in G and generate the associated dendrogram

    A dendrogram is a diagram representing a tree and each level represents
    a partition of the G graph. The top level contains the smallest communities
    and as you traverse to the bottom of the tree the communities get bigger
    and the overal modularity increases making the partition better.

    Each level is generated by executing the two phases of the Louvain Community
    Detection Algorithm.

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
     The name of an edge attribute that holds the numerical value
     used as a weight. If None then each edge has weight 1.
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
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.

    References
    ----------
    .. [1] Blondel, V.D. et al. Fast unfolding of communities in
       large networks. J. Stat. Mech 10008, 1-12(2008)
    """

    partition = [{u} for u in G.nodes()]
    mod = modularity(G, partition, weight=weight)
    if G.is_multigraph():
        graph = _convert_multigraph(G, weight)
    else:
        graph = G.__class__()
        graph.add_nodes_from(G)
        graph.add_weighted_edges_from(G.edges(data=weight, default=1))

    m = graph.size(weight="weight")
    while True:
        partition, inner_partition, improvement = _one_level(graph, m, partition, seed)
        if not improvement:
            break
        new_mod = modularity(graph, inner_partition, weight="weight")
        if new_mod - mod <= threshold:
            break
        graph = _gen_graph(graph, inner_partition)
        yield partition


def _one_level(G, m, partition, seed=None):
    """Calculate one level of the tree

    Input `m` is the size of the graph `G`.
    Input `partition` is a valid partition of the graph `G` given as a list of sets of
    nodes.
    """
    node2com = {u: i for i, u in enumerate(G.nodes())}
    inner_partition = [{u} for u in G.nodes()]
    degrees = dict(G.degree(weight="weight"))
    total_weights = [deg for deg in degrees.values()]
    nbrs = {u: {v: data["weight"] for v, data in G[u].items() if v != u} for u in G}
    rand_nodes = list(G.nodes)
    seed.shuffle(rand_nodes)
    nb_moves = 1
    improvement = False
    while nb_moves > 0:
        nb_moves = 0
        for u in rand_nodes:
            best_mod = 0
            best_com = node2com[u]
            weights2com = _neighbor_weights(u, nbrs[u], node2com)
            degree = degrees[u]
            total_weights[best_com] -= degree
            for nbr_com, wt in weights2com.items():
                gain = wt - (total_weights[nbr_com] * degree) / m
                if gain > best_mod:
                    best_mod = gain
                    best_com = nbr_com
            total_weights[best_com] += degree
            if best_com != node2com[u]:
                com = G.nodes[u].get("nodes", {u})
                partition[node2com[u]].difference_update(com)
                inner_partition[node2com[u]].remove(u)
                partition[best_com].update(com)
                inner_partition[best_com].add(u)
                improvement = True
                nb_moves += 1
                node2com[u] = best_com
    partition = list(filter(len, partition))
    inner_partition = list(filter(len, inner_partition))
    return partition, inner_partition, improvement


def _neighbor_weights(node, nbrs, node2com):
    """Calculate weights between node its neighbor communities.

    Input `nbrs` should be a dict of the node's neighbors.

    `node2com` is a dict with nodes as keys and community index as values.
    """
    weights = defaultdict(float)
    for nbr, wt in nbrs.items():
        weights[node2com[nbr]] += 2 * wt
    return weights


def _gen_graph(G, partition):
    """Generate a new graph based on the partitions of a given graph"""
    H = nx.Graph()
    node2com = {}
    for i, part in enumerate(partition):
        nodes = set()
        for node in part:
            node2com[node] = i
            nodes.update(G.nodes[node].get("nodes", {node}))
        H.add_node(i, nodes=nodes)

    for node1, node2, wt in G.edges(data=True):
        wt = wt["weight"]
        com1 = node2com[node1]
        com2 = node2com[node2]
        temp = H.get_edge_data(com1, com2, {"weight": 0})["weight"]
        H.add_edge(com1, com2, **{"weight": wt + temp})
    return H


def _convert_multigraph(G, weight):
    """Convert a Multigraph to normal Graph"""
    H = nx.Graph()
    H.add_nodes_from(G)
    for u, v, wt in G.edges(data=weight, default=1):
        if H.has_edge(u, v):
            H[u][v]["weight"] += wt
        else:
            H.add_edge(u, v, weight=wt)
    return H
