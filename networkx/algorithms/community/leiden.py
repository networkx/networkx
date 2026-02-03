"""Functions for detecting communities based on Leiden Community Detection
algorithm.

These functions do not have NetworkX implementations.
They may only be run with an installable :doc:`backend </backends>`
that supports them.
"""

import itertools
from collections import deque

import networkx as nx
from networkx.utils import not_implemented_for, py_random_state

__all__ = ["leiden_communities", "leiden_partitions"]

"""Functions for detecting communities based on Louvain Community Detection
Algorithm"""

import itertools
import random
from collections import defaultdict, deque

import networkx as nx
from networkx.utils import py_random_state

from networkx.algorithms.community.quality import constant_potts_model
import math

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
    theta=0.1
):
    r"""Find the best partition of a graph using the Louvain Community Detection
    Algorithm.

    Louvain Community Detection Algorithm is a simple method to extract the community
    structure of a network. This is a heuristic method based on modularity optimization. [1]_

    The algorithm works in 2 steps. On the first step it assigns every node to be
    in its own community and then for each node it tries to find the maximum positive
    modularity gain by moving each node to all of its neighbor communities. If no positive
    gain is achieved the node remains in its original community.

    The modularity gain obtained by moving an isolated node $i$ into a community $C$ can
    easily be calculated by the following formula (combining [1]_ [2]_ and some algebra):

    .. math::
        \Delta Q = \frac{k_{i,in}}{2m} - \gamma\frac{ \Sigma_{tot} \cdot k_i}{2m^2}

    where $m$ is the size of the graph, $k_{i,in}$ is the sum of the weights of the links
    from $i$ to nodes in $C$, $k_i$ is the sum of the weights of the links incident to node $i$,
    $\Sigma_{tot}$ is the sum of the weights of the links incident to nodes in $C$ and $\gamma$
    is the resolution parameter.

    For the directed case the modularity gain can be computed using this formula according to [3]_

    .. math::
        \Delta Q = \frac{k_{i,in}}{m}
        - \gamma\frac{k_i^{out} \cdot\Sigma_{tot}^{in} + k_i^{in} \cdot \Sigma_{tot}^{out}}{m^2}

    where $k_i^{out}$, $k_i^{in}$ are the outer and inner weighted degrees of node $i$ and
    $\Sigma_{tot}^{in}$, $\Sigma_{tot}^{out}$ are the sum of in-going and out-going links incident
    to nodes in $C$.

    The first phase continues until no individual move can improve the modularity.

    The second phase consists in building a new network whose nodes are now the communities
    found in the first phase. To do so, the weights of the links between the new nodes are given by
    the sum of the weight of the links between nodes in the corresponding two communities. Once this
    phase is complete it is possible to reapply the first phase creating bigger communities with
    increased modularity.

    The above two phases are executed until no modularity gain is achieved (or is less than
    the `threshold`, or until `max_levels` is reached).

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
    node_weight:
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
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.petersen_graph()
    >>> nx.community.leiden_communities(G, seed=123)
    [{0, 4, 5, 7, 9}, {1, 2, 3, 6, 8}]

    Notes
    -----
    The order in which the nodes are considered can affect the final output. In the algorithm
    the ordering happens using a random shuffle.

    References
    ----------
    .. [1] Blondel, V.D. et al. Fast unfolding of communities in
       large networks. J. Stat. Mech 10008, 1-12(2008). https://doi.org/10.1088/1742-5468/2008/10/P10008
    .. [2] Traag, V.A., Waltman, L. & van Eck, N.J. From Louvain to Leiden: guaranteeing
       well-connected communities. Sci Rep 9, 5233 (2019). https://doi.org/10.1038/s41598-019-41695-z
    .. [3] Nicolas Dugué, Anthony Perez. Directed Louvain : maximizing modularity in directed networks.
        [Research Report] Université d’Orléans. 2015. hal-01231784. https://hal.archives-ouvertes.fr/hal-01231784

    See Also
    --------
    louvain_partitions
    :any:`leiden_communities`
    """

    partitions = leiden_partitions(G, weight, node_weight, resolution, threshold, seed, quality_function, theta)

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
    weight='weight',
    node_weight=None,
    resolution=1.0,
    threshold=0.0000001,
    seed=None,
    quality_function=constant_potts_model,
    theta=0.1
):
    """Yield partitions for each level of the Louvain Community Detection Algorithm

    Louvain Community Detection Algorithm is a simple method to extract the community
    structure of a network. This is a heuristic method based on modularity optimization. [1]_

    The partitions at each level (step of the algorithm) form a dendrogram of communities.
    A dendrogram is a diagram representing a tree and each level represents
    a partition of the G graph. The top level contains the smallest communities
    and as you traverse to the bottom of the tree the communities get bigger
    and the overall modularity increases making the partition better.

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
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.

    References
    ----------
    .. [1] Blondel, V.D. et al. Fast unfolding of communities in
       large networks. J. Stat. Mech 10008, 1-12(2008)

    See Also
    --------
    louvain_communities
    :any:`leiden_partitions`
    """
    partition = [{u} for u in G.nodes()]
    if nx.is_empty(G):
        yield partition
        return
    


    is_directed = G.is_directed()
    if G.is_multigraph():
        graph = _convert_multigraph(G, weight, is_directed)
        weight='weight'
    else:
        if weight:
            graph = G.__class__()
            graph.add_nodes_from(G)
            graph.add_weighted_edges_from(G.edges(data=weight, default=1))
            weight = 'weight'
        else:
            weight = 'weight'
            graph = G.__class__()
            graph.add_nodes_from(G)
            graph.add_edges_from(G.edges())
            for e in graph.edges():
                graph.edges[e][weight] = 1
 

    if node_weight:
        for node in G.nodes():
            graph.nodes[node]['node_weight'] = G.nodes[node][node_weight]
    else:
        node_weight='node_weight'
        for node in G.nodes():
                graph.nodes[node][node_weight] = 1

    quality = quality_function(graph, partition, resolution=resolution, weight=weight, node_weight=node_weight)

    inner_partition = None
    improvement = True

    while improvement:
               
       
        partition, inner_partition, improvement = _move_nodes_fast(
            graph,
            partition,
            inner_partition,
            quality_function,
            resolution,
            seed=seed
        )
        
        inner_partition_refined = _refine_partition(
            graph,
            inner_partition,
            resolution,
            quality_function,
            seed,
            theta
        )
        
        new_quality = quality_function(
            graph, inner_partition_refined, resolution=resolution, weight='weight', node_weight='node_weight'
        )

        graph = _gen_graph(graph, inner_partition_refined)
        
        partition = _update_partition(graph, partition)

        yield [s.copy() for s in partition]
        
        if new_quality - quality <= threshold:
            return

        quality = new_quality


def _is_valid_refinement(p, ref_p):
    
    val = True
    for c1 in ref_p:
        for c2 in p:
            if c1.issubset(c2):
                break
        else:
            val = False
    return val

def _update_partition(G, partition):
    partition = [set() for _ in range(len(G.nodes()))]
    for i, u in enumerate(G.nodes()):
        partition[i].update(G.nodes[u]['nodes'])

    return partition



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
            theta
        )

    inner_partition_refined = list(filter(len, inner_partition_refined))
    return inner_partition_refined

def _merge_node_subset(G, partition, node2com, S, resolution, quality_function, seed, theta):
    S_size = _size_of_node_set(G, S, 'node_weight')

    R = set()
    for u in S:
        u_size = _get_node_size(G, u, 'node_weight')
        community_factor = _community_edge_size(G, {u}, S-{u}, 'weight')
        factor_comparison = resolution*u_size*(S_size - u_size)

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
                    E = _community_edge_size(G, C, S-C, 'weight')
                    C_size = _size_of_node_set(G, C, 'node_weight')
                    comm_comparison = resolution*C_size*(S_size - C_size)
                    if E > comm_comparison:
                
                        q1 = quality_function(
                            G,
                            [partition[comm], partition[i]],
                            resolution=resolution,
                            allow_partial=True
                        )

                        partition[comm].remove(u)
                        partition[i].add(u)

                        q2 = quality_function(
                            G,
                            [partition[comm], partition[i]],
                            resolution=resolution,
                            allow_partial=True
                        )

                        quality_delta = q2 - q1

                        if quality_delta > 0:
                            candidate_comm.append(i)
                            try:
                                val = math.exp(quality_delta/theta)
                            except:
                                val = float('inf')
                            candidate_comm_delta.append(val)
                        partition[comm].add(u)
                        partition[i].remove(u)

            if len(candidate_comm)>0:

                def _sample_from_discrete(vals):
                    cumsum_vals = _cumulative_sum(vals)
                    max_val = cumsum_vals[-1]
    
                    random_val = seed.uniform(0,max_val)
    
                    for i, v in enumerate(cumsum_vals):
                        if random_val <= v:
                            return i

                random_index = _sample_from_discrete(candidate_comm_delta)
                new_comm = candidate_comm[random_index]
                partition[comm].remove(u)
                partition[new_comm].add(u)
                node2com[u] = new_comm
                
                move = f'moving node {u} from {comm} to {new_comm}'
                

    return partition, node2com


def _cumulative_sum(val_list):
    cumsum_vals = []
    
    running_total = 0
    for val in val_list:
        running_total += val
        cumsum_vals.append(running_total)

    return cumsum_vals

def _move_nodes_fast(G, partition, seed_partition, quality_function, resolution, seed=None,):
    inner_partition = [{u} for u in G.nodes()]
    node2com = {u: i for i, u in enumerate(G.nodes())}
    if seed_partition:
        for i, u in enumerate(G.nodes()):
            for j, C in enumerate(seed_partition):
                if u in C:
                    old_com = i
                    best_com = j
                    com = G.nodes[u].get("nodes", {u})
                    partition[node2com[u]].difference_update(com)
                    partition[best_com].update(com)
                    node2com[u] = best_com
                    inner_partition[old_com].remove(u)
                    inner_partition[best_com].add(u)

    rand_nodes = list(G.nodes)
    seed.shuffle(rand_nodes)
    node_queue = deque(rand_nodes)

    improvement = False
    
    while node_queue:
        u = node_queue.pop()

        best_delta=0
        old_com = node2com[u]
        best_com = old_com

        for new_com in {i for i in node2com.values()}:

            if new_com != old_com:
                
                q1 = quality_function(
                    G,
                    [inner_partition[new_com], inner_partition[old_com]],
                    resolution=resolution,
                    allow_partial=True
                )

                inner_partition[old_com].remove(u)
                inner_partition[new_com].add(u)

                q2 = quality_function(
                    G,
                    [inner_partition[new_com], inner_partition[old_com]],
                    resolution=resolution,
                    allow_partial=True
                )

                quality_delta = q2 - q1

                if quality_delta > best_delta:
                    best_delta = quality_delta
                    best_com = new_com
                    improvement = True

                inner_partition[new_com].remove(u)
                inner_partition[old_com].add(u)

        if (best_delta > 0) & (improvement==True):
            com = G.nodes[u].get("nodes", {u})
            
            partition[node2com[u]].difference_update(com)
            partition[best_com].update(com)
            node2com[u] = best_com
            
            inner_partition[old_com].remove(u)
            inner_partition[best_com].add(u)
            
            neighbours = set(G.adj[u])
            nodes_to_visit = neighbours - inner_partition[best_com]
            
            improvement = False
            for v in nodes_to_visit:
                if v not in node_queue:
                    node_queue.appendleft(v)

    partition = list(filter(len, partition))
    inner_partition = list(filter(len, inner_partition))

    return partition, inner_partition, improvement


def _gen_graph(G, partition):
    """Generate a new graph based on the partitions of a given graph"""
    H = G.__class__()
    node2com = {}

    for i, part in enumerate(partition):
        new_size = 0

        nodes = set()

        for node in part:
            new_size += _get_node_size(G, node, 'node_weight')
            node2com[node] = i
            nodes.update(G.nodes[node].get("nodes", {node}))

        H.add_node(i, nodes=nodes, node_weight=new_size)
    
    for u, v, d in G.edges(data=True):
        uv_weight = d['weight']
        com_u = node2com[u]
        com_v = node2com[v]
        if com_u != com_v:
            if H.has_edge(com_u, com_v):
                H.edges[(com_u, com_v)]['weight'] += uv_weight
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
            H[u][v]['weight'] += wt
        else:
            H.add_edge(u, v, weight=wt)
    return H
