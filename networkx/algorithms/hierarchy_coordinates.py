"""
========================
Hierarchy Coordinates
========================
Functions to calculate hierarchy coordinates for directed networks.

Hierarchy coordinates consist of treeness, feedforwardness, and orderability, which collectively create a
'hierarchy morphospace' classifying all network structures. In loose terms, treeness describes how consistently
nodes higher on the hierarchy (maximal nodes) branch into more nodes, while feedforwardness considers the extent
information passes vertically (vs horizontally) within a hierarchy, and orderability considers what fraction of the
network is vertically hierarchical.

Originally from [1]_, adapted implementation accommodates weighted network. For details, see _[2]

.. [1] "On the origins of hierarchy in complex networks."
 Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
 Proceedings of the National Academy of Sciences 110, no. 33 (2013)

.. [2] Appendix of 2013 paper: https://www.pnas.org/highwire/filestream/613265/field_highwire_adjunct_files/0/sapp.pdf

"""

import networkx as nx
from networkx.utils import not_implemented_for
import numpy as np
import copy

# from sklearn.preprocessing import normalize

__all__ = [
    "node_weighted_condense",
    "weight_nodes_by_condensation",
    "max_min_layers",
    "leaf_removal",
    "recursive_leaf_removal",
    "orderability",
    "feedforwardness",
    "graph_entropy",
    "infographic_graph_entropy",
    "treeness",
    "hierarchy_coordinates",
]


# Hierarchy Coordinate Functions
def node_weighted_condense(A, num_thresholds=8, threshold_distribution=None):
    """Creates a series of networkx graphs based on generated edge weight thresholds, and returns their node weighted
    condensed and original graphs.

    Unweighted graphs will always lead to single graph outputs, whereas weighted graphs output a series of graphs
     according to the number of thresholds and the distribution. Empty graphs are dropped.
    Node weighted condense simply assigns the number of nodes in a cycle as the weight of the resultant node in the DAG[1]_.

    Parameters
    ----------
    A: numpy array
        Adjacency matrix, as square 2d numpy array
    num_thresholds: int, default: 8
        Number of thresholds and resultant sets of node-weighted Directed Acyclic Graphs
    threshold_distribution: float, optional
        If true or float, distributes the thresholds exponentially, with an exponent equal to the float input.
        Alternatively, a (lambda) function may be passed for custom distributions.

    Returns
    -------
    largest_condensed_graphs: list of networkX Graphs
        list of node weighted condensed networkx graphs reduced from unweighted digraphs determined by thresholds. (See note)
    nx_graphs: list of networkX Graphs
        list of unweighted graphs produced from applying thresholds to the original weighted network

    Examples
    --------
    Graphing the resultant network is recommended, as otherwise this is difficult to visualize...

    See Also
    --------
    weight_nodes_by_condensation, graph_entropy, treeness

    >>> a = np.array([
    ...     [0, 0.2, 0, 0, 0],
    ...     [0, 0, 0, 0.7, 0],
    ...     [0, 0.4, 0, 0, 0],
    ...     [0, 0, 0.1, 0, 1.0],
    ...     [0, 0, 0, 0, 0],
    ... ])
    >>> condensed_networks, base_binary_networks = nx.node_weighted_condense(a)
    >>> for network in condensed_networks:
    ...     print(f'{network}, total weight: {nx.get_node_attributes(network, "weight")}')
    DiGraph with 3 nodes and 2 edges, total weight: {0: 1, 1: 3, 2: 1}
    DiGraph with 5 nodes and 4 edges, total weight: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}
    DiGraph with 4 nodes and 3 edges, total weight: {0: 1, 1: 1, 2: 1, 3: 1}
    DiGraph with 4 nodes and 3 edges, total weight: {0: 1, 1: 1, 2: 1, 3: 1}
    DiGraph with 3 nodes and 2 edges, total weight: {0: 1, 1: 1, 2: 1}
    DiGraph with 3 nodes and 2 edges, total weight: {0: 1, 1: 1, 2: 1}
    DiGraph with 2 nodes and 1 edges, total weight: {0: 1, 1: 1}
    DiGraph with 2 nodes and 1 edges, total weight: {0: 1, 1: 1}

    Notes
    ------
    WIP TODO: As multiple independent graphs may form from applying threshold cutoffs to a weighted graph,
    only the largest is considered. This might be worth considering in re-evaluating the meaning of
    weighted network hierarchy coordinate evaluations. (See pages 7, 8 of [1]_, supplementary material)

    An threshold_distribution of None results in a linear distribution, otherwise
     the exponential distribution is sampled from exp(x) \in (0, 1)

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    """

    if np.array_equal(np.unique(A), [0, 1]):  # binary check
        num_thresholds = 1
    else:
        num_thresholds = num_thresholds

    # Establishing Thresholds
    if num_thresholds == 1 or np.isclose(np.max(A) - np.min(A), 0, 1e-2):
        nx_graphs = [nx.from_numpy_matrix(A, create_using=nx.DiGraph)]
    else:
        if threshold_distribution is None:
            try:
                thresholds = list(
                    np.round(
                        np.arange(
                            np.min(A),
                            np.max(A),
                            (np.max(A - np.min(A))) / num_thresholds,
                        ),
                        4,
                    )
                )  # linear distribution
            except:
                thresholds = [np.max(A)] * num_thresholds
        else:
            thresholds = _distribute(
                dist=threshold_distribution,
                end_value_range=(np.min(A), np.max(A)),
                n=num_thresholds,
            )
        # Converting to binary nx_graphs according to thresholds:
        nx_graphs = [
            nx.from_numpy_matrix(np.where(A > threshold, 1, 0), create_using=nx.DiGraph)
            for threshold in thresholds
        ]
    # removes isolated nodes (0 in & out degree) from binary nodes. (not needed for consolidation)
    for index in range(len(nx_graphs)):
        nx_graphs[index].remove_nodes_from(list(nx.isolates(nx_graphs[index])))

    nx_graphs = [
        graph for graph in nx_graphs if not nx.is_empty(graph)
    ]  # eliminates empty graphs
    condensed_graphs = [
        nx.condensation(nx_graphs[index]) for index in range(len(nx_graphs))
    ]
    largest_condensed_graphs = []
    for condensed_graph in condensed_graphs:
        largest_condensed_graphs.append(
            nx.convert_node_labels_to_integers(
                max(
                    [
                        condensed_graph.subgraph(cc).copy()
                        for cc in nx.weakly_connected_components(condensed_graph)
                    ],
                    key=len,
                )
            )
        )
        members = nx.get_node_attributes(largest_condensed_graphs[-1], "members")
        node_weights = [len(w) for w in members.values()]
        for node_index in range(len(node_weights)):
            largest_condensed_graphs[-1].nodes[node_index]["weight"] = node_weights[
                node_index
            ]

    return largest_condensed_graphs, nx_graphs


@not_implemented_for("undirected")
def weight_nodes_by_condensation(condensed_graph):
    """Weights nodes according to the number of other nodes they condensed (sum of constituent cycle of DAG node).

    As, proposed in _[1]:  e.g. if a cycle contained 3 nodes (and became one in condensation)
    the resulting node of the condensed graph would then gain weight = 3.
    Single (non-cyclic) nodes are weighted as 1.

    Parameters
    ----------
    condensed_graph: NetworkX Graph
        result of a networkx.condensation call, such that the 'members'
        attribute is populated with constituent cyclical nodes

    Return
    ------
    condensed_graph: NetworkX Graph
        node weighted condensed graph

    Examples
    --------
    Visualization also recommended here (with node size prop. weighting)
    >>> b = np.array([
    ...     [0, 0.2, 0, 0, 0],
    ...     [0, 0, 0, 0.7, 0],
    ...     [0, 0.4, 0, 0, 0],
    ...     [0, 0, 0.1, 0, 1.0],
    ...     [0, 0, 0, 0, 0],
    ... ])

    >>> num_thresholds = 2
    >>> condensed_networks, _ = nx.node_weighted_condense(b, num_thresholds=num_thresholds)
    >>> for network_index in range(num_thresholds):
    ...     for node_index in range(len(condensed_networks[network_index].nodes)):
    ...         print(f"Node {node_index}, new weight:", condensed_networks[network_index].nodes[node_index]["weight"])
    Node 0, new weight: 1
    Node 1, new weight: 3
    Node 2, new weight: 1
    Node 0, new weight: 1
    Node 1, new weight: 1
    Node 2, new weight: 1

    Raises
    ------
    NetworkXError
        If input not a directed acyclic graph

    Note:
    ------
    TODO: Might wish to eliminate return, or enable copying?

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)

    See Also
    --------
    node_weighted_condense, graph_entropy
    """
    if not nx.is_directed_acyclic_graph(condensed_graph):
        raise nx.NetworkXError(
            "G must be a directed acyclic graph for node weighted condensation"
        )

    node_weights = [
        len(w) for w in nx.get_node_attributes(condensed_graph, "members").values()
    ]
    for node_index in range(len(node_weights)):
        condensed_graph.nodes[node_index]["weight"] = node_weights[node_index]
    return condensed_graph  # WIP TODO: May not be necessary, as the graph itself is updated (not copied)?


@not_implemented_for("undirected")
def max_min_layers(G, max_layer=True):
    """Returns the maximal (k_in = 0) layer or the minimal layer (k_out = 0)

    Returns the maximal (k_in = 0, highest in hierarchy) layer (those nodes with in degree = 0)
     or the minimal layer (k_out = 0) of a directed network.

    Parameters
    ----------
    G: NetworkX Graph
        A directed graph.
    max_layer: bool, default: True
        if True, returns maximal layer (k_in = 0), else returns nodes for which k_out = 0, minimal layer

    Return
    ------
    min/max_layer: list
        list of node indices as ints

    Examples:
    >>> a = np.array([
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 1, 0],
    ...     [0, 0, 0, 0, 0, 1, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])

    >>> G = nx.from_numpy_matrix(a, create_using=nx.DiGraph)
    >>> print(nx.max_min_layers(G))
    [0, 1]
    >>> print(nx.max_min_layers(G, max_layer=False))
    [4, 5, 6]

    Raises
    ------
    NetworkXError
        If input not a directed graph

    Notes:
    -------

    """
    if not G.is_directed():
        raise nx.NetworkXError("G must be a DiGraph for min/max layer evaluation")
    if max_layer:
        return [node for node in G.nodes() if G.in_degree(node) == 0]
    else:
        return [node for node in G.nodes() if G.out_degree(node) == 0]


@not_implemented_for("undirected")
def leaf_removal(G, top=True):
    """Returns a pruned network, with either maximal (k_in=0)
    or minimal (k_out = 0) nodes removed upon call.

    Parameters
    -----------
    G: NetworkX Graph
        A directed graph.

    top: bool, default: True
        if True, prunes from k_in=0 nodes

    Return
    -------
    NetworkX Graph:
        copy of the original graph G without either maximal or minimal nodes

    Examples:
    ---------
    >>> a = np.array([
    ...   [0, 0, 1, 1, 0, 0, 0],
    ...   [0, 0, 1, 1, 0, 0, 0],
    ...   [0, 0, 0, 0, 1, 1, 0],
    ...   [0, 0, 0, 0, 0, 1, 1],
    ...   [0, 0, 0, 0, 0, 0, 0],
    ...   [0, 0, 0, 0, 0, 0, 0],
    ...   [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> G = nx.from_numpy_matrix(a, create_using=nx.DiGraph)
    >>> print(nx.to_numpy_array(nx.leaf_removal(G)))
    [[0. 0. 1. 1. 0.]
     [0. 0. 0. 1. 1.]
     [0. 0. 0. 0. 0.]
     [0. 0. 0. 0. 0.]
     [0. 0. 0. 0. 0.]]

    >>> print(nx.to_numpy_array(nx.leaf_removal(G, top=False)))
    [[0. 0. 1. 1.]
     [0. 0. 1. 1.]
     [0. 0. 0. 0.]
     [0. 0. 0. 0.]]

    Raises
    ------
    NetworkXError
        If input not a directed acyclic graph

    Notes
    ------
    Crafted as a component of the leaf-removal algorithm given in [1]_;

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)


    See Also
    --------
    recursive_leaf_removal, max_min_layers
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("G must be a directed, acyclic graph for leaf removal")
    layer = max_min_layers(G, max_layer=top)
    peeled_graph = copy.deepcopy(G)
    for node in layer:
        peeled_graph.remove_node(node)
    return peeled_graph


@not_implemented_for("undirected")
def recursive_leaf_removal(G, from_top=True, keep_linkless_layer=False):
    """Prunes nodes from top (maximal) or bottom (minimal) recursively. Original DAG is given as first element

    Useful for examinations of hierarchy layer by layer. Note that the *remaining* graph is returned, not the layers

    Parameters
    ----------
    G: NetworkX graph
        A directed graph.
    from_top: bool, default: True
        Determines whether nodes are removed from the top or bottom of the hierarchy
    keep_linkless_layer: bool, default: False
        if True, empty, single node and all zero layers are preserved

    Return
    -------
    list of NetworkX Graphs:
        Starting with the initial DAG and with successively pruned hierarchy layers

    Examples
    ---------
    >>> a = np.array([
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 1, 0],
    ...     [0, 0, 0, 0, 0, 1, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> G = nx.from_numpy_matrix(a, create_using=nx.DiGraph)
    >>> pruned_to_ground = nx.recursive_leaf_removal(G, from_top=True)
    >>> pruned_from_ground = nx.recursive_leaf_removal(G, from_top=False)
    >>> for pruned_tree in pruned_to_ground:
    ...     print(pruned_tree)
    DiGraph with 7 nodes and 8 edges
    DiGraph with 5 nodes and 4 edges
    >>> for pruned_tree in pruned_from_ground:
    ...     print(pruned_tree)
    DiGraph with 7 nodes and 8 edges
    DiGraph with 4 nodes and 4 edges

    Raises
    ------
    NetworkXError
        If input not a directed acyclic graph

    See Also
    --------
    leaf_removal, max_min_layers

    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("G must be a directed, acyclic graph for leaf removal")
    dissected_graphs = [copy.deepcopy(G)]
    while len(dissected_graphs[-1].nodes()) > 1:
        dissected_graphs.append(leaf_removal(dissected_graphs[-1], top=from_top))
    if not keep_linkless_layer:
        while (
            nx.is_empty(dissected_graphs[-1]) and len(dissected_graphs) > 1
        ):  # catches empty graphs, which are eliminated in node condense
            dissected_graphs = dissected_graphs[
                :-1
            ]  # removes empty or single node layer
    return dissected_graphs


@not_implemented_for("undirected")
def orderability(
    G, condensed_nx_graph=None, num_thresholds=8, threshold_distribution=None
):
    """Evaluates orderability, a measure of how vertically hierarchical a network is.

    Given as intersection of the nodes inside the consdensed and original network,
    divided by the total number of nodes in the original network.

    Adapted for weighted networks from the original algorithm found here: [1]_.

    Parameters
    ----------
    G: NetworkX Graph
        A directed graph.
    condensed_nx_graph: optional
        Directed acyclic networkX graph if already evaluated to save computational time
    num_thresholds: int, optional
        only applicable as node_weighted_condense parameter if G is weighted
    threshold_distribution: float, optional
        only applicable as node_weighted_condense parameter if G is weighted

    Return
    -------
    float: orderability
        Hierarchy coordinate


    Examples
    ---------
    >>> a = np.array([
    ...     [0, 0.2, 0, 0, 0],
    ...     [0, 0, 0, 0.7, 0],
    ...     [0, 0.4, 0, 0, 0],
    ...     [0, 0, 0.1, 0, 1.0],
    ...     [0, 0, 0, 0, 0],
    ... ])

    >>> G = nx.from_numpy_matrix(a, create_using=nx.DiGraph)
    >>> print(nx.orderability(G))
    0.925

    Notes
    ______
    TODO: Not sure what's proper re: optional num_thresholds and threshold_distribution parameter
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)

    See Also
    --------
    treeness, feedforwardness, hierarchy_coordinates
    """
    if not G.is_directed():
        raise nx.NetworkXError(
            "G must be a directed graph for any hierarchy coordinate evaluation"
        )

    if not np.array_equal(
        np.unique(nx.to_numpy_array(G)), [0, 1]
    ):  # unweighted (non-binary) check
        o = 0
        condensed_graphs, original_graphs = node_weighted_condense(
            nx.to_numpy_array(G),  # creates binary graphs
            num_thresholds=num_thresholds,
            threshold_distribution=threshold_distribution,
        )

        for index in range(len(condensed_graphs)):
            o += orderability(original_graphs[index], condensed_graphs[index])
        return o / len(condensed_graphs)

    if condensed_nx_graph is None:
        condensed_nx_graph = weight_nodes_by_condensation(nx.condensation(G))
    non_cyclic_nodes = [
        node[0]
        for node in nx.get_node_attributes(condensed_nx_graph, "weight").items()
        if node[1] == 1
    ]
    total_acyclic_node_weight = sum(
        [
            weight
            for weight in nx.get_node_attributes(condensed_nx_graph, "weight").values()
        ]
    )
    return len(non_cyclic_nodes) / total_acyclic_node_weight


@not_implemented_for("undirected")
def _feedforwardness_iteration(G):
    """Performs a single iteration of the feedforward algorithm described in [1]_

    Parameters
    ----------
    G: NetworkX Graph
        a directed, acyclic graph [1]_

    Return
    --------
    g: float
        sum of feedforwardness for a single Directed Acyclic Graph
    num_paths: int
        sum total paths considered

    Notes
    ______
    g(G) = sum of F over all paths from maximal to minimal nodes

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)

    See Also
    --------
    feedforwardness
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError(
            "G must be a directed acyclic graph for feedforwardness evaluation"
        )

    max_layer = max_min_layers(G, max_layer=True)
    min_layer = max_min_layers(G, max_layer=False)
    weights = nx.get_node_attributes(G, "weight")
    g = 0
    num_paths = 0
    for max_node in max_layer:
        for min_node in min_layer:
            for path in nx.all_simple_paths(G, source=max_node, target=min_node):
                g += len(path) / sum(
                    [weights[node] for node in path]
                )  # where each path calculation is F(path)
                num_paths += 1
    return g, num_paths


@not_implemented_for("undirected")
def feedforwardness(DAG):
    """Returns feedforwardness hierarchy coordinates, ~extent information passes vertically
    (vs horizontally) within a hierarchy.

    Based on a weighted sum which considers how much each path from every maximal node to every minimal node
    traverses through cyclic (flat hierarchy) components. This calculation is then repeated for every subgraph
    produced through maximal layer removal.

    The original algorithm was given in "On the origins of hierarchy in complex networks."[1]_ and with details
    given in their appendix.[2]_

    Parameters
    ----------
    DAG: NetworkX Graph
        A Directed, Acyclic Graph.

    Return
    -------
    float:
        feedforwardness, hierarchy coordinate

    Examples
    ---------
    >>> a = np.array([
    ...     [0, 0.2, 0, 0, 0],
    ...     [0.4, 0, 0, 0.7, 0],
    ...     [0, 0.4, 0, 0, 0],
    ...     [0, 0, 0.1, 0, 1.0],
    ...     [0, 0, 0, 0, 0],
    ... ])
    >>> condensed_networks, base_binary_networks = nx.node_weighted_condense(a)
    >>> for network in condensed_networks:
    ...     print("DAG: ", network)
    ...     print("Feedforwardness: {0}".format(nx.feedforwardness(network)))
    DAG:  DiGraph with 2 nodes and 1 edges
    Feedforwardness: 0.4
    DAG:  DiGraph with 4 nodes and 3 edges
    Feedforwardness: 0.7388888888888889
    DAG:  DiGraph with 5 nodes and 4 edges
    Feedforwardness: 1.0
    DAG:  DiGraph with 5 nodes and 4 edges
    Feedforwardness: 1.0
    DAG:  DiGraph with 3 nodes and 2 edges
    Feedforwardness: 1.0
    DAG:  DiGraph with 3 nodes and 2 edges
    Feedforwardness: 1.0
    DAG:  DiGraph with 2 nodes and 1 edges
    Feedforwardness: 1.0
    DAG:  DiGraph with 2 nodes and 1 edges
    Feedforwardness: 1.0


    Notes
    ______
    feedforwardness is calculated by pruning layers of the original graph and averaging
    over subsequent feedforwardness calculations.

    TODO: Not sure what's proper re: optional num_thresholds and threshold_distribution parameter
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    .. [2] Appendix of 2013 paper:
    https://www.pnas.org/highwire/filestream/613265/field_highwire_adjunct_files/0/sapp.pdf

    See Also
    --------
    treeness, orderability, hierarchy_coordinates
    """
    # Must be fed the set of graphs with nodes lower on the hierarchy eliminated first
    if not nx.is_directed_acyclic_graph(DAG):
        raise nx.NetworkXError(
            "DAG must be a directed acyclic graph for feedforwardness evaluation"
        )

    if nx.get_node_attributes(DAG, "weight") == {}:
        raise nx.NetworkXError(
            "Ensure feedforwardness is fed nodes weighted by consdensation"
            ", e.g. G = nx.weight_nodes_by_condensation(nx.condensation(G))"
        )

    successively_peeled_nx_graphs = recursive_leaf_removal(DAG, from_top=False)
    if (
        len(successively_peeled_nx_graphs) == 1
        and len(successively_peeled_nx_graphs[0].nodes()) == 1
    ):
        return 0

    f = 0
    total_num_paths = 0
    for nx_graph in successively_peeled_nx_graphs:
        g, paths = _feedforwardness_iteration(nx_graph)
        f += g
        total_num_paths += paths
    return f / total_num_paths


@not_implemented_for("undirected")
def graph_entropy(DAG, forward_entropy=False):
    """Measures uncertainty in following all directed paths through the network.

    computed by summing over the probability of transition from every maximal (minimal) node to all others,
    to yield forward (backward) entropy. transition probabilities are calculated via powers of the modified adjacency matrix.

    Parameters
    ----------
    DAG: NetworkX Graph
        Directed Acyclic Graph
    forward_entropy: Bool, default: False
        if True, calculates entropy from maximal nodes (k_in = 0) nodes to others.
        Otherwise calculates using paths from the bottom (minimal nodes) of the network.

    Return
    -------
    entropy: float
        graph entropy, in [1]_, eq.14/16 ( H_b/f (G_C) )

    Examples
    ---------
    >>> b = np.array([
    ...     [0, 0, 1, 0, 0, 0, 1],
    ...     [0, 0, 1, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 0, 0],
    ...     [0, 0, 1, 0, 1, 0, 0],
    ...     [0, 0, 0, 0, 0, 1, 0],
    ...     [0, 0, 0, 1, 0, 0, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])

    >>> condensed_network_layers = nx.recursive_leaf_removal(nx.condensation(nx.from_numpy_matrix(b, create_using=nx.DiGraph)))
    >>> fwd_graph_entropy = [round(nx.graph_entropy(net, forward_entropy=True), 3) for net in condensed_network_layers]
    >>> bkwd_graph_entropy = [round(nx.graph_entropy(net), 3) for net in condensed_network_layers]
    >>> print("graph entropy (from top | bottom): {0} | {1}".format(fwd_graph_entropy, bkwd_graph_entropy))
    graph entropy (from top | bottom): [0.52, 0.0] | [1.04, 0.0]

    Notes
    ______
    WIP: Detail after confirmation of methodology from Prof. Sole.

    As described in the text of _[1], proposed and developed in _[2], _[3]:
    Graph Entropy, is measure of probability of crossing a node n_j when following a path from n_i.

    _Forward_ entropy:
    .. math:: H_f(G_C) = \frac{1}{|M|} \sum_{v_i \in M} \sum_{v_k \in V \setminus \mu} P(v_i \right v_k) \cdot log k_{out}(v_k)
    _Backward_ entropy:
    .. math:: H_b(G_C) = \frac{1}{|\mu|} \sum_{v_i \in \mu} \sum_{v_k \in V_C \setminus M} P(v_i \leftarrow v_k) \cdot log k_{in}(v_k)
    where :math:`\mu` (M) is the set of minimal (maximal) nodes, and :math:`P(v_i \leftarrow v_k)` indicates
    the probability of transition between :math:`v_k` and :math:`v_i`.

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)

    .. [2] "Topological reversibility and causality in feed-forward networks."
      Corominas-Murtra, Bernat, Carlos Rodríguez-Caso, Joaquín Goñi, and Ricard Solé.
      New Journal of Physics 12, no. 11 (2010): pg 113051

    .. [3] "Measuring the hierarchy of feedforward networks."
    Corominas-Murtra, Bernat, Carlos Rodríguez-Caso, Joaquin Goni, and Ricard Solé.
    Chaos: An Interdisciplinary Journal of Nonlinear Science 21, no. 1 (2011): pg 016108.

    """
    if not nx.is_directed_acyclic_graph(DAG):
        raise nx.NetworkXError(
            "G must be a directed acyclic graph for graph entropy evaluation"
        )

    dag = nx.convert_node_labels_to_integers(DAG)
    L_GC = len(
        recursive_leaf_removal(DAG)
    )  # Could be passed in most contexts to reduce redundant computation

    if forward_entropy:
        # as w sklearn: B_prime = normalize(nx.to_numpy_array(dag), axis=1, norm='max')  # Row normalization
        B_prime = _matrix_normalize(nx.to_numpy_array(dag), row_normalize=True)
        P = sum(
            [np.power(B_prime, k) for k in range(1, L_GC + 1)]
        )  # +1 as k \in ( 1, L(G_C) )
        # TODO: Not so sure about this unless k coincides with the number of steps already taken (and the sum is odd)
        # (Presently awaiting response from original authors for clarification)
    else:
        # as w sklearn: B = normalize(nx.to_numpy_array(dag), axis=0, norm='max')  # Column normalization
        B = _matrix_normalize(nx.to_numpy_array(dag), row_normalize=False)
        P = sum([np.power(B, k) for k in range(1, L_GC + 1)])

    boundary_layer = max_min_layers(dag, max_layer=forward_entropy)
    non_extremal_nodes = set(dag.nodes() - boundary_layer)
    entropy = 0
    for layer_node in boundary_layer:
        for non_extremal_node in non_extremal_nodes:
            if forward_entropy:
                entropy += P[layer_node][non_extremal_node] * np.log(
                    dag.out_degree(layer_node)
                )  # nan for 0 outdegree
            else:
                entropy += P[non_extremal_node][layer_node] * np.log(
                    dag.in_degree(layer_node)
                )
    entropy /= len(boundary_layer)
    return entropy


@not_implemented_for("undirected")
def infographic_graph_entropy(DAG, forward_entropy=False):
    """Measures uncertainty in following all directed paths through the network.

    Computed by summing over the probability of transition from every maximal (minimal) node to all others,
    to yield forward (backward) entropy. Transition probabilities are calculated via brute force computation
    considering the number of branches along each path.

    Parameters
    ----------
    DAG: NetworkX Graph
        Directed Acyclic Graph
    forward_entropy: Bool, default: False
        if True, calculates entropy from maximal nodes (k_in = 0) nodes to others.
        Otherwise calculates using paths from the bottom (minimal nodes) of the network.

    Return
    -------
    entropy: float
        graph entropy

    Examples
    ---------
    >>> b = np.array([
    ...     [0, 0, 1, 0, 0, 0, 0],
    ...     [0, 0, 1, 0, 0, 0, 1],
    ...     [0, 0, 0, 0, 1, 0, 0],
    ...     [0, 0, 1, 0, 1, 0, 0],
    ...     [0, 0, 0, 0, 0, 1, 0],
    ...     [0, 0, 0, 1, 0, 0, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])

    >>> condensed_network_layers = nx.recursive_leaf_removal(nx.condensation(nx.from_numpy_matrix(b, create_using=nx.DiGraph)))
    >>> fwd_graph_entropy = [round(nx.infographic_graph_entropy(net, forward_entropy=True), 3) for net in condensed_network_layers]
    >>> bkwd_graph_entropy = [round(nx.infographic_graph_entropy(net), 3) for net in condensed_network_layers]
    >>> print("graph entropy (from top | bottom): {0} | {1}".format(fwd_graph_entropy, bkwd_graph_entropy))
    graph entropy (from top | bottom): [0.347, 0.0] | [1.04, 0.0]

    Notes
    ______
    WIP: Detail after confirmation of methodology from Prof. Sole.

    As described in the text of _[1], proposed and developed in _[2], _[3]:
    Graph Entropy, is measure of probability of crossing a node n_j when following a path from n_i.

    _Forward_ entropy:
    .. math:: H_f(G_C) = \frac{1}{|M|} \sum_{v_i \in M} \sum_{v_k \in V \setminus \mu} P(v_i \right v_k) \cdot log k_{out}(v_k)
    _Backward_ entropy:
    .. math:: H_b(G_C) = \frac{1}{|\mu|} \sum_{v_i \in \mu} \sum_{v_k \in V_C \setminus M} P(v_i \leftarrow v_k) \cdot log k_{in}(v_k)
    where :math:`\mu` (M) is the set of minimal (maximal) nodes, and :math:`P(v_i \leftarrow v_k)` indicates
    the probability of transition between :math:`v_k` and :math:`v_i`, as the inverse of the sum of non-binary branchings.

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)

    .. [2] "Topological reversibility and causality in feed-forward networks."
      Corominas-Murtra, Bernat, Carlos Rodríguez-Caso, Joaquín Goñi, and Ricard Solé.
      New Journal of Physics 12, no. 11 (2010): pg 113051

    .. [3] "Measuring the hierarchy of feedforward networks."
    Corominas-Murtra, Bernat, Carlos Rodríguez-Caso, Joaquin Goni, and Ricard Solé.
    Chaos: An Interdisciplinary Journal of Nonlinear Science 21, no. 1 (2011): pg 016108.
    """
    if not nx.is_directed_acyclic_graph(DAG):
        raise nx.NetworkXError(
            "G must be a directed acyclic graph for graph entropy evaluation"
        )

    dag = nx.convert_node_labels_to_integers(DAG)
    start_layer = max_min_layers(dag, max_layer=forward_entropy)
    end_layer = max_min_layers(dag, max_layer=not forward_entropy)
    entropy = 0
    for start_node in start_layer:
        for end_node in end_layer:
            if forward_entropy:
                paths = list(
                    nx.all_simple_paths(dag, source=start_node, target=end_node)
                )
            else:
                paths = list(
                    nx.all_simple_paths(
                        dag.reverse(copy=True), source=start_node, target=end_node
                    )
                )
            for path in paths:
                if forward_entropy:
                    n = sum(
                        [
                            dag.out_degree(node)
                            for node in path[:-1]
                            if dag.out_degree(node) != 1
                        ]
                    )
                    # Except ones as they don't indicate further possible paths
                    if n == 0:
                        n = 1
                else:
                    n = sum(
                        [
                            dag.in_degree(node)
                            for node in path[:-1]
                            if dag.in_degree(node) != 1
                        ]
                    )
                    if n == 0:
                        n = 1
                entropy += np.log(n) / n
    entropy /= len(start_layer)
    return entropy


@not_implemented_for("undirected")
def _single_graph_treeness(DAG):
    """Evaluates treeness of a directed, acyclic, unweighted graph.

    Treeness measures how consistently the network branches along the directed connections.
    Alternatively, how maximal nodes feed to otherwise maximal nodes;
    do edges connect to nodes with more edges further down the hierarchy?

    Parameters
    ----------
    DAG: NetworkX Graph
        Directed acyclic graph

    Return
    -------
    float:
        treeness for a single DAG (equation 17 from [1])

    Examples
    ---------
    >>> a = np.array([
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 1, 0],
    ...     [0, 0, 0, 0, 0, 1, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> condensed_network = nx.node_weighted_condense(a)[0][0]
    >>> print("treeness (single graph): {0}".format(np.round(_single_graph_treeness(condensed_network), 3)))
    treeness (single graph): 0.667

    Notes
    ______
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    """
    if len(DAG.nodes()) == 1:
        return 0
    forward_entropy = graph_entropy(DAG, forward_entropy=True)
    backward_entropy = graph_entropy(DAG, forward_entropy=False)
    if forward_entropy == 0 and backward_entropy == 0:
        return 0

    return (forward_entropy - backward_entropy) / max(forward_entropy, backward_entropy)


@not_implemented_for("undirected")
def treeness(DAG):
    """Treeness describes how consistently nodes higher on the hierarchy (maximal nodes) branch into more nodes.

    Based on `graph_entropy` a measure dependant on the probability of transitioning between any two given nodes,
     Treeness measures the expansion or contraction of paths from maximal nodes, yielding positive or negative
      values respectively.

    The original algorithm was given in "On the origins of hierarchy in complex networks."[1]_ and with details
    given in their appendix.[2]_

    Parameters
    ----------
    DAG: NetworkX Graph
        Directed Acyclic networkX Graph

    Return
    -------
    float:
        Treeness, hierarchy coordinate, Equation 18 from _[1]

    Examples
    ---------
    >>> a = np.array([
    ...     [0, 0, 1, 0, 0, 0, 1],
    ...     [0, 0, 1, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 0, 0],
    ...     [0, 0, 1, 0, 1, 0, 0],
    ...     [0, 0, 0, 0, 0, 1, 0],
    ...     [0, 0, 0, 1, 0, 0, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> dag = nx.condensation(nx.from_numpy_matrix(a, create_using=nx.DiGraph))
    >>> print("treeness: {0}".format(nx.treeness(dag)))
    treeness: -0.5

    Notes
    ______
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    .. [2] Appendix of 2013 paper:
    https://www.pnas.org/highwire/filestream/613265/field_highwire_adjunct_files/0/sapp.pdf

    See Also
    --------
    feedforwardness, orderability, hierarchy_coordinates
    """
    if not nx.is_directed_acyclic_graph(DAG):
        raise nx.NetworkXError(
            "DAG must be a directed acyclic graph for treeness evaluation"
        )

    pruned_from_top = recursive_leaf_removal(G=DAG, from_top=True)
    pruned_from_bottom = recursive_leaf_removal(G=DAG, from_top=False)
    # removal of original graphs from subsets:
    pruned_from_top = pruned_from_top[1:]
    pruned_from_bottom = pruned_from_bottom[1:]

    entropy_sum = _single_graph_treeness(DAG)
    for index in range(len(pruned_from_top)):
        entropy_sum += _single_graph_treeness(pruned_from_top[index])
    for index in range(len(pruned_from_bottom)):
        entropy_sum += _single_graph_treeness(pruned_from_bottom[index])
    return entropy_sum / (1 + len(pruned_from_bottom) + len(pruned_from_top))


def hierarchy_coordinates(A, num_thresholds=8, threshold_distribution=None):
    """Returns hierarchy coordinates: treeness, feedforwardness & orderability.

    Hierarchy coordinates can classifying all network structures, and their respective hierarchy,
     though certain combinations are theoretically impossible to acheive.

    Adapted for weighted networks from "On the origins of hierarchy in complex networks."[1]_ and with details
    given in their appendix.[2]_


    Parameters
    ----------
    A: 2d numpy array or networkX graph
        numpy Adjacency matrix or networkx of which hierarchy coordinates will be calculated

    num_thresholds: int, optional
        specifies number of weighted graph subdivisions

    threshold_distribution: None, float or lambda fct ptr, default: None
        determines the distribution of threshold values used to create unweighted from weighted networks.
        if None, creates a linear distribution of thresholds spanning the set of weights evenly.
        if float, is the coefficient of exp(Ax) sampled between (0, 1) and rescaled appropriately.
        if a lambda expression, determines a custom distribution sampled between (0, 1) and rescaled appropriately.

    Return
    -------
    tuple of floats:
        (treeness, feedforwardness, orderability) hierarchy coordinates

    Examples
    ---------
    >>> a = np.array([
    ...     [0, 0.2, 0, 0, 0],
    ...     [0, 0, 0, 0.7, 0],
    ...     [0, 0.4, 0, 0, 0],
    ...     [0, 0.3, 0.1, 0, 1.0],
    ...     [0, 0, 0, 0, 0],
    ... ])
    >>> b = np.array([
    ...     [0, 0, 1, 0, 0, 0, 1],
    ...     [0, 0, 1, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 0, 0],
    ...     [0, 0, 1, 0, 1, 0, 0],
    ...     [0, 0, 0, 0, 0, 1, 0],
    ...     [0, 0, 0, 1, 0, 0, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> print('(a) Treeness: {0} | Feedforwardness: {1} | Orderability: {2}'.format(*np.round(nx.hierarchy_coordinates(a), 2)))
    (a) Treeness: -0.04 | Feedforwardness: 0.87 | Orderability: 0.81
    >>> print('(b) Treeness: {0} | Feedforwardness: {1} | Orderability: {2}'.format(*np.round(nx.hierarchy_coordinates(b), 2)))
    (b) Treeness: -0.5 | Feedforwardness: 0.56 | Orderability: 0.43

    Notes
    ______
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    returns the averaged hierarchy coordinates given the adjacency matrix A

    See Also
    --------
    feedforwardness, orderability, treeness
    """
    np_A = []
    if (
        isinstance(A, nx.DiGraph)
        or isinstance(A, nx.Graph)
        or isinstance(A, nx.MultiGraph)
        or isinstance(A, nx.MultiDiGraph)
    ):
        np_A = nx.to_numpy_array(A)
    elif isinstance(A, np.ndarray):
        np_A = A
    else:
        print(
            "A must be given as either a networkx graph or adjacency matrix (as nested list or 2d numpy array)"
        )

    if np.array_equal(np.unique(np_A), [0]):  # null check
        # raise Exception("Unconnected graph; trivially 0 hierarchy")  # TODO: Raise exception if undefined instead
        return 0, 0, 0

    o, f, t = 0, 0, 0
    condensed_graphs, original_graphs = node_weighted_condense(
        A=np_A,
        num_thresholds=num_thresholds,
        threshold_distribution=threshold_distribution,
    )
    for index in range(len(condensed_graphs)):
        t += treeness(condensed_graphs[index])
        f += feedforwardness(condensed_graphs[index])
        o += orderability(original_graphs[index], condensed_graphs[index])
    t /= len(condensed_graphs)
    f /= len(condensed_graphs)
    o /= len(condensed_graphs)
    return t, f, o


# Utilities for hierarchy coordinates
def _distribute(n, end_value_range=None, dist=1, sampled_range_of_dist=(0, 1)):
    """Returns n floats distributed as within the sampled range of provided distribution, rescaled to end_value_range
    Defaults to an exponential distribution e^x, x = (0, 1), where int/float values of dist modify the coefficient on x

    Parameters
    ----------
    n : int
        Number of exponentially distributed points returned
    end_value_range : tuple, optional
        Range which final values of the distributed points occupy.
        Defaults to the distribution's native range
    dist : float, default: 1
       A in np.exp(A*x)
    dist: overloaded: types.FunctionType, optional
        Alternate distribution yielding single samples from 1d input
    sampled_range_of_dist: tuple, default: (0, 1)
        Range of distribution sampled

    Returns
    -------
    pts: numpy array
        numpy array of n floats

    Examples
    --------
    n, Max, Min = 100, 10, -10
    exp_dist_0 = nx.distribute(n=n, end_value_range=(Min, Max))
    exp_dist_1 = nx.distribute(n=n, dist=-2, end_value_range=(Min, Max), sampled_range_of_dist=(1, 2))

    dist = lambda x: 4*x*x - 3*x*x*x
    parabolic_dist = nx.distribute(n=n, dist=dist, end_value_range=(Min, Max), sampled_range_of_dist=(0, 2))

    # Visualization of sampling
    plt.xlabel('# samples')
    plt.ylabel('sampled value')
    plt.plot(exp_dist_0, label='e^x: (0, 1)')
    plt.plot(exp_dist_1, label='e^-2x: (1, 2)')
    plt.plot(parabolic_dist, label='4x^2 - 3x^3: (0, 2)')
    plt.legend()
    plt.show()
    """
    if isinstance(dist, float) or isinstance(dist, int):
        distribution = lambda x: np.exp(dist * x)
    else:
        distribution = dist

    x_increment = np.abs(max(sampled_range_of_dist) - min(sampled_range_of_dist)) / n
    pts = np.array([distribution(x_increment * i) for i in range(n)])
    pts /= abs(max(pts) - min(pts))

    if end_value_range is not None:
        pts = pts * (max(end_value_range) - min(end_value_range)) + min(end_value_range)
    return pts


def _matrix_normalize(matrix, row_normalize=False):
    """normalizes 2d matrices.
    Parameters
    ----------
    matrix: square 2d numpy array, nested list,
        matrix to be normalized
    row_normalize: bool
        normalizes row *instead* of default columns if True
    Returns
    -------
    numpy array:
        column or row normalized array
    Examples
    --------
    a = np.repeat(np.arange(1, 5), 4).reshape(4, 4)
    print(a)
    print(np.round(hc.matrix_normalize(a), 2))
    print(np.round(hc.matrix_normalize(a, row_normalize=True), 2))
    Notes
    -----
    Should be replaced with appropriate generalized, efficient version
    """

    if row_normalize:
        row_sums = matrix.sum(axis=1)
        return np.array(
            [
                matrix[index, :] / row_sums[index]
                if row_sums[index] != 0
                else [0] * row_sums.size
                for index in range(row_sums.size)
            ]
        )
    else:
        column_sums = matrix.sum(axis=0)
        return np.array(
            [
                matrix[:, index] / column_sums[index]
                if column_sums[index] != 0
                else [0] * column_sums.size
                for index in range(column_sums.size)
            ]
        ).T
