from collections import Counter

import networkx as nx


def get_partitions_from_attributes(attributes, neighbors):
    """Assign nodes to partitions based on the nodes' attributes.

    Nodes with identical attribute-derived invariants are assigned to the same partition.

    Parameters
    ----------
    attributes : dict
        Mapping from nodes to their attributes.
    neighbors : dict
        Mapping from nodes to their neighbors.

    Returns
    -------
    tuple
        The mapping from nodes to their partitions and the number of partitions.
    """
    invariants = []
    for node, attribute in attributes.items():
        # Node degree (i.e., number of neighbors) is encoded in length of neighbor_attrs.
        neighbor_attrs = [attributes[neighbor] for neighbor in neighbors[node]]
        neighbor_attrs.sort()
        neighbor_attrs.insert(0, attribute)
        invariants.append(tuple(neighbor_attrs))

    unique_invariants = sorted(set(invariants))
    unique_invariants_to_partitions = {
        invariant: partition for partition, invariant in enumerate(unique_invariants)
    }
    partitions = dict(
        zip(
            attributes,
            (unique_invariants_to_partitions[invariant] for invariant in invariants),
            strict=True,
        )
    )

    return partitions, len(unique_invariants)


def refine_partitions(partitions, node_neighbors):
    """Iteratively refine partitions with the Weisfeiler-Leman algorithm [1]_.

    The refinement stops once the partitions don't change.

    Parameters
    ----------
    partitions : dict
        Mapping from nodes to their partitions.
    node_neighbors : dict
        Mapping from nodes to their neighbors.

    Returns
    -------
    tuple
        The refined partitions and number of partitions.

    References
    ----------
    .. [1] Kiefer, Sandra. “The Weisfeiler-Leman Algorithm.”
       ACM SIGLOG News 7, no. 3 (2020): 5–27.
       https://doi.org/10.1145/3436980.3436982.
    """
    refined_partitions = dict(partitions)

    while True:
        next_partitions, n_partitions = get_partitions_from_attributes(
            refined_partitions, node_neighbors
        )
        if next_partitions == refined_partitions:
            return refined_partitions, n_partitions

        refined_partitions = next_partitions


def get_partitioning(partitions, edges):
    """Compute a partitioning.

    Each edge contributes a sorted pair of its endpoints' partitions.
    The partitioning is the sorted tuple of these edge pairs.
    """
    return tuple(
        sorted(tuple(sorted((partitions[u], partitions[v]))) for u, v in edges)
    )


def filter_duplicate_partitionings(partitions_list, edges):
    """Filter out duplicate partitionings with isomorphisms testing.

    Parameters
    ----------
    partitions_list : list
        Mappings from nodes to their partitions.
    edges : list
        The edges of the graph.

    Returns
    -------
    list
        Unique partitionings.
    """
    buckets = {}
    unique = []
    for partitions in partitions_list:
        G = nx.Graph()
        G.add_nodes_from((node, {"partition": p}) for node, p in partitions.items())
        G.add_edges_from(edges)
        bucket = buckets.setdefault(get_partitioning(partitions, edges), [])
        if any(nx.vf2pp_is_isomorphic(G, H, node_label="partition") for H, _ in bucket):
            continue
        bucket.append((G, partitions))
        unique.append(partitions)

    return unique


def get_refinement_tree_node_children(partitions, node_neighbors):
    """Yield the children of a node in the partition-refinement tree.

    Each node in the most populated partition is assigned a new
    singleton partition in turn, and the resulting partitioning is refined.

    Parameters
    ----------
    partitions : dict
        Mapping from nodes to their partitions.
    node_neighbors : dict
        Mapping from nodes to their neighbors.

    Yields
    ------
    dict
        Mapping from nodes to refined partitions.
    """
    n_partitions = len(set(partitions.values()))
    partition_sizes = Counter(sorted(partitions.values()))
    largest_partition = max(partition_sizes, key=partition_sizes.__getitem__)

    for node, partition in partitions.items():
        if partition != largest_partition:
            continue

        # Artificially split the most populated partition.
        individualized = dict(partitions)
        individualized[node] = n_partitions  # Partitions are zero-based.

        yield refine_partitions(individualized, node_neighbors)[0]


def partitioning_is_discrete(partitions):
    """Determine whether a partitioning is discrete.

    A partitioning is discrete when each node is in its own partition; that is,
    there are as many partitions as nodes.

    Parameters
    ----------
    partitions : dict
        Mapping from nodes to their partitions.

    Returns
    -------
    bool
        ``True`` if every node is in its own partition, otherwise ``False``.
    """
    return len(set(partitions.values())) == len(partitions)


def get_refinement_tree_levels(partitions, node_neighbors, edges):
    """Yield the levels of a breadth-first partition-refinement tree [1]_.

    The initial level contains only the refined input partitions. Subsequent
    levels contain the children of the preceding level. Refinement stops on the
    level that contains only discrete partitions.

    Parameters
    ----------
    partitions : dict
        Mapping from nodes to their initial partitions.
    node_neighbors : dict
        Mapping from nodes to their neighbors.
    edges : list
        The edges of the graph.

    Yields
    ------
    list
        The partition mappings at one level of the refinement tree.

    References
    ----------
    .. [1] https://pallini.di.uniroma1.it/SearchTree.html
    """
    parents = [refine_partitions(partitions, node_neighbors)[0]]

    while parents:
        yield parents
        if all(map(partitioning_is_discrete, parents)):
            return

        children = [
            child
            for parent in parents
            for child in get_refinement_tree_node_children(parent, node_neighbors)
        ]
        parents = filter_duplicate_partitionings(children, edges)


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def canonical_labeling(G, node_attributes=None):
    """Compute a canonical labeling for ``G``.

    An implementation of graph canonicalization using the refinement-individualization paradigm [1]_.

    Parameters
    ----------
    G : NetworkX graph
        The graph to label. ``G`` is not modified.
    node_attributes : list of str, default=None
        Optional node attribute names used to distinguish nodes. Every node
        must have all requested attributes.

    Returns
    -------
    dict
        Mapping from nodes to their zero-based canonical labels.

    Raises
    ------
    KeyError
        If a node is missing any requested attribute.

    References
    ----------
    .. [1] McKay, Brendan D., and Adolfo Piperno.
       "Practical graph isomorphism, II."
       Journal of symbolic computation 60 (2014): 94-112.
       https://doi.org/10.1016/j.jsc.2013.09.003
    """
    if node_attributes is None:
        node_attributes = []

    attributes = {}
    for node, _attributes in G.nodes(data=True):
        missing = [
            attribute for attribute in node_attributes if attribute not in _attributes
        ]
        if missing:
            missing_str = ", ".join(missing)
            raise KeyError(f"Node {node} is missing attributes: {missing_str}")
        attributes[node] = tuple(
            _attributes[attribute] for attribute in node_attributes
        )

    neighbors = {node: tuple(G[node]) for node in G}
    edges = list(G.edges())

    # Assign initial partitions based on the attribute-derived node-invariant.
    partitions, _ = get_partitions_from_attributes(attributes, neighbors)

    # Compute all discrete partitionings using refinement-individualization.
    discrete_partitionings = list(
        get_refinement_tree_levels(partitions, neighbors, edges)
    )[-1]

    # Choose lexicographically largest partitioning as canonical labeling.
    canonical_labeling = max(
        discrete_partitionings, key=lambda partition: get_partitioning(partition, edges)
    )

    return canonical_labeling
