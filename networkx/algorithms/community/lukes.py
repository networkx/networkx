from copy import deepcopy
from functools import lru_cache
from itertools import product
from random import choice

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['lukes_partitioning']

D_EDGE_W = 'weight'
D_NODE_W = 'weight'


def lukes_partitioning(G, max_size: int, node_weight=None, edge_weight=None):
    """Partition a tree into size-limited, weighted node blocks with optimal (minimum) edge cut,
    using the Lukes[1] algorithm.

    This algorithm paritions a connected, acyclic graph into sets of nodes whose total weight
    does not exceed max_size, in such a way that the edges that are cut by the partition
    have minimum weight.

    Parameters
    ----------
    G : graph

    max_size : int
        Maximum weight a partition can have in terms of sum of
        node_weight for all nodes in the partition

    edge_weight : key
        Edge data key to use as weight. If None, the weights are all
        set to one.

    node_weight : key
        Node data key to use as weight. If None, the weights are all
        set to one. The data must be int.

    Returns
    -------
    partition : tuple
        A tuple of sets of nodes representing the partition.

    Raises
    -------
    NotATree
        If G is not a tree.
    TypeError
        If any of the values of node_weight is not int.

    References
    ----------
    .. Lukes, J. A. (1974).
       "Efficient Algorithm for the Partitioning of Trees."
       IBM Journal of Research and Development, 18(3), 217–224.

    """
    # First sanity check and tree preparation
    if not nx.is_tree(G):
        raise nx.NotATree('lukes_clustering works only on trees')
    else:
        if nx.is_directed(G):
            root = [n for n, d in G.in_degree() if d == 0]
            assert len(root) == 1
            d_graph = deepcopy(G)
        else:
            root = choice(list(G.nodes))
            d_graph = nx.dfs_tree(G, root)  # this has the desirable side effect of not inheriting any attributes

    # Since we do not want to screw up the original graph, if we have a blank attribute, we make a deepcopy
    if edge_weight is None or node_weight is None:
        safe_G = deepcopy(G)
        if edge_weight is None:
            nx.set_edge_attributes(safe_G, 1.0, D_EDGE_W)
            edge_weight = D_EDGE_W
        if node_weight is None:
            nx.set_node_attributes(safe_G, 1, D_NODE_W)
            node_weight = D_NODE_W
    else:
        safe_G = G

    # Second sanity check
    # The values of node_weight MUST BE int, and that's it.
    # I cannot see any space for duck typing without incurring serious danger of subtle bugs.
    all_n_attr = nx.get_node_attributes(safe_G, node_weight).values()
    for x in all_n_attr:
        if not isinstance(x, int):
            raise TypeError('lukes_clustering needs integer values for node_weight ({})'.format(node_weight))

    # todo check that the values of edge_weight implement <= and sum() in an algebraically closed fashion

    # this functions are defined here for two reasons linked to their signatures:
    # - brevity: we can leverage "graph" from lukes_clustering namespace
    # - caching: by having to pass just hashable arguments, we can directly lru_cache

    @not_implemented_for('undirected')
    def _leaves(gr):  # this is intended to be called only on d_graph
        for x in gr.nodes:
            if not nx.descendants(gr, x):
                yield x

    @not_implemented_for('undirected')
    def _one_node_just_over_leaves(gr):
        tleaves = set(_leaves(gr))
        for n in set(gr.nodes) - tleaves:
            if all([x in tleaves for x in nx.descendants(gr, n)]):
                return n

    @lru_cache(2048)
    def _value_of_cluster(cluster: frozenset):
        valid_edges = [e for e in safe_G.edges if e[0] in cluster and e[1] in cluster]
        return sum([safe_G.edges[e][edge_weight] for e in valid_edges])

    def _value_of_partition(partition: list):
        return sum([_value_of_cluster(frozenset(c)) for c in partition])

    @lru_cache(2048)
    def _weight_of_cluster(cluster: frozenset):
        return sum([safe_G.nodes[n][node_weight] for n in cluster])

    def _pivot(partition: list, node):
        ccx = [c for c in partition if node in c]
        assert len(ccx) == 1
        return ccx[0]

    def _concatenate_merge(partition_1: list, partition_2: list, x, i, ref_weigth):

        ccx = _pivot(partition_1, x)
        cci = _pivot(partition_2, i)
        merged_xi = ccx.union(cci)

        # we first check if we can do the merge. If so, we do the actual calculations, otherwise we concatenate
        if _weight_of_cluster(frozenset(merged_xi)) <= ref_weigth:
            cp1 = list(filter(lambda x: x != ccx, partition_1))
            cp2 = list(filter(lambda x: x != cci, partition_2))

            option_2 = [merged_xi] + cp1 + cp2
            return option_2, _value_of_partition(option_2)
        else:
            option_1 = partition_1 + partition_2
            return option_1, _value_of_partition(option_1)

    # INITIALIZATION -----------------------
    leaves = set(_leaves(d_graph))
    for lv in leaves:
        d_graph.nodes[lv]['partitions'] = dict()
        slot = safe_G.nodes[lv][node_weight]
        d_graph.nodes[lv]['partitions'][slot] = [{lv}]
        d_graph.nodes[lv]['partitions'][0] = [{lv}]

    for inner in [x for x in d_graph.nodes if x not in leaves]:
        d_graph.nodes[inner]['partitions'] = dict()
        slot = safe_G.nodes[inner][node_weight]
        d_graph.nodes[inner]['partitions'][slot] = [{inner}]

    # CORE ALGORITHM -----------------------
    while True:
        x_node = _one_node_just_over_leaves(d_graph)
        weight_of_x = safe_G.nodes[x_node][node_weight]
        best_value = 0
        best_partition = None
        bp_buffer = dict()
        x_descendants = nx.descendants(d_graph, x_node)
        for i in x_descendants:
            for j in range(weight_of_x, max_size + 1):
                for a, b in product(range(weight_of_x, max_size + 1), range(0, max_size + 1)):
                    if not a + b == j:
                        continue  # we are only interested in a, b couples that sum to j
                    if a in d_graph.nodes[x_node]['partitions'].keys() \
                            and b in d_graph.nodes[i]['partitions'].keys():
                        part1 = d_graph.nodes[x_node]['partitions'][a]
                        part2 = d_graph.nodes[i]['partitions'][b]
                    else:
                        continue  # it's not possible to form this particular weight sum value

                    part, value = _concatenate_merge(part1, part2, x_node, i, j)

                    if j not in bp_buffer.keys() or bp_buffer[j][1] < value:
                        bp_buffer[j] = part, value  # we annotate in the buffer what's the best partition for this j

                    if best_value <= value:  # we also keep track of the best-holding partition of the x node
                        best_value = value
                        best_partition = part

            # as illustrated in Lukes, once we finished a child, we can discharge (the key phrase is make all x == x')
            # the partitions we found inside the graph (so that they are used by the subsequent children)
            for w, (best_part_for_vl, vl) in bp_buffer.items():
                d_graph.nodes[x_node]['partitions'][w] = best_part_for_vl  # discharge the buffer before next node
            bp_buffer.clear()

        # the absolute best partition for this node across all weights has to be stored in 0
        d_graph.nodes[x_node]['partitions'][0] = best_partition
        d_graph.remove_nodes_from(x_descendants)

        if x_node == root:
            # the 0-labeled partition of root is the optimal one for the tree
            return d_graph.nodes[root]['partitions'][0]
