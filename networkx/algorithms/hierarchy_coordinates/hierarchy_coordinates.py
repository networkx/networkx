import numpy as np
import networkx as nx
import copy
from utils import distribute, matrix_normalize

"""
Implementation of the hierarchy coordinates via networkX from 
Hierarchy in Complex Networks: The Possible and the Actual [B Corominas-Murtra - 2013]  [*] - Supporting Information

Though implemented for unweighted networkX graphs, in the context of its original application, 
these are applied to weighted graphs by averaging over the unweighted graphs resulting from 
applying thresholds to normalized weighted graphs. 
"""


# Hierarchy Coordinate Functions
def weakly_connected_component_subgraphs(G, copy=True):
    """Generate weakly connected components as subgraphs. Re-imported to ensure later NetworkX compatibility

    Parameters
    ----------
    G : NetworkX Graph
       A directed graph.

    copy : bool
        If copy is True, graph, node, and edge attributes are copied to the
        subgraphs.

    Notes
    -----
    Simply brought in from earlier version of NetworkX to ensure compatibility with later versions.
    Not sure why it was dropped...
    """
    for comp in nx.weakly_connected_components(G):
        if copy:
            yield G.subgraph(comp).copy()
        else:
            yield G.subgraph(comp)


def node_weighted_condense(A, num_thresholds=8, threshold_distribution=None):
    """Returns a series of node_weighted condensed graphs (DAGs) [1]_ and their original nx_graphs.

    Parameters
    ----------
    A: numpy array
        Adjacency matrix, as square 2d numpy array
    num_thresholds: int, default: 8
        Number of thresholds and resultant sets of node-weighted Directed Acyclic Graphs
    threshold_distribution: float, optional
        If true or float, distributes the thresholds exponentially, with an exponent equal to the float input.

    Returns
    -------
    largest_condensed_graphs: list of networkX Graphs
        list of node weighted condensed networkx graphs reduced from unweighted digraphs determined by thresholds. (See note)
    nx_graphs: list of networkX Graphs
        list of unweighted graphs produced from applying thresholds to the original weighted network

    Examples
    --------
    Graphing the resultant network is recommended, as otherwise this is difficult to visualize...

    a = np.array([
        [0, 0.2, 0, 0, 0],
        [0, 0, 0, 0.7, 0],
        [0, 0.4, 0, 0, 0],
        [0, 0, 0.1, 0, 1.0],
        [0, 0, 0, 0, 0],
    ])
    condensed_networks, base_binary_networks = hc.node_weighted_condense(a)
    for network in condensed_networks:
        print(nx.to_numpy_array(network))

    Notes
    ------
    TODO: As multiple independent graphs may form from applying threshold cutoffs to a weighted graph,
    only the largest is considered. This might be worth considering in re-evaluating the meaning of
    weighted network hierarchy coordinate evaluations. (See pages 7, 8 of [1]_, supplementary material)

    An threshold_distribution of None results in a linear distribution, otherwise
     the exponential distribution is sampled from exp(x) \in (0, 1)

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    """

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
            thresholds = distribute(
                dist=threshold_distribution,
                end_value_range=(np.min(A), np.max(A)),
                n=num_thresholds,
            )
        # Converting to binary nx_graphs according to thresholds:
        nx_graphs = [
            nx.from_numpy_matrix(np.where(A > threshold, 1, 0), create_using=nx.DiGraph)
            for threshold in thresholds
        ]
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
                    weakly_connected_component_subgraphs(condensed_graph, copy=True),
                    key=len,
                )
            )
        )
        # networkx.weakly_connected_component_subgraphs comes from networkx 1.10 documentation, and has sense been discontinued.
        # For ease of access and future networkx compatibility, it was copied directly to this file before the class declaration.
        members = nx.get_node_attributes(largest_condensed_graphs[-1], "members")
        node_weights = [len(w) for w in members.values()]
        for node_index in range(len(node_weights)):
            largest_condensed_graphs[-1].nodes[node_index]["weight"] = node_weights[
                node_index
            ]

    return largest_condensed_graphs, nx_graphs


def weight_nodes_by_condensation(condensed_graph):
    """Weights nodes according to the integer number of other nodes they condensed. Proposed in _[1]
    e.g. if a cycle contained 3 nodes (and became one in condensation)
    the resulting node of the condensed graph would then gain weight = 3.

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
    b = np.array([
        [0, 0.2, 0, 0, 0],
        [0, 0, 0, 0.7, 0],
        [0, 0.4, 0, 0, 0],
        [0, 0, 0.1, 0, 1.0],
        [0, 0, 0, 0, 0],
    ])

    num_thresholds = 2
    condensed_networks, _ = hc.node_weighted_condense(b, num_thresholds=num_thresholds)
    for network_index in range(num_thresholds):
        print(f"Network {network_index}:")
        for node_index in range(len(condensed_networks[network_index].nodes)):
            print(f"Node {node_index}, new weight:", condensed_networks[network_index].nodes[node_index]["weight"])
        print()

    Note:
    ------
    TODO: Might wish to eliminate return, or enable copying?
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    """
    node_weights = [
        len(w) for w in nx.get_node_attributes(condensed_graph, "members").values()
    ]
    for node_index in range(len(node_weights)):
        condensed_graph.nodes[node_index]["weight"] = node_weights[node_index]
    return (
        condensed_graph  # Not be necessary, as the graph itself is updated (not copied)
    )


def max_min_layers(G, max_layer=True):
    """
    Returns the maximal (k_in = 0, highest in hierarchy) layer (those nodes with in degree = 0) or the minimal layer (k_out = 0)

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
    a = np.array([
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ])

    G = nx.from_numpy_matrix(a, create_using=nx.DiGraph)
    print(hc.max_min_layers(G))
    print(hc.max_min_layers(G, max_layer=False))

    Notes:
    -------
    TODO: Should be two functions?
    """
    if max_layer:
        return [node for node in G.nodes() if G.in_degree(node) == 0]
    else:
        return [node for node in G.nodes() if G.out_degree(node) == 0]


def leaf_removal(G, forward=True):
    """Returns a pruned network, with either maximal (k_in=0)
    or minimal (k_out = 0) nodes removed upon call.

    Parameters
    -----------
    G: NetworkX Graph
        A directed graph.

    forward: bool, default: True
        if True, prunes from k_in=0 nodes

    Return
    -------
    NetworkX Graph:
        copy of the original graph G without either maximal or minimal nodes

    Examples:
    ---------
    a = np.array([
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ])

    G = nx.from_numpy_matrix(a, create_using=nx.DiGraph)
    print(nx.to_numpy_array(hc.leaf_removal(G)))
    print(nx.to_numpy_array(hc.leaf_removal(G, forward=False)))

    Raises
    ------
    TODO: NonDAG: will loop infinitely for cyclic input

    Notes
    ------
    Crafted as a component of the leaf-removal algorithm given in [1]_;

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)

    """
    layer = max_min_layers(G, max_layer=forward)
    peeled_graph = copy.deepcopy(G)
    for node in layer:
        peeled_graph.remove_node(node)
    return peeled_graph


def recursive_leaf_removal(G, from_top=True, keep_linkless_layer=False):
    """Prunes nodes from top (maximal) or bottom (minimal) recursively. Original DAG is given as first element
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
    a = np.array([
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ])
    G = nx.from_numpy_matrix(a, create_using=nx.DiGraph)
    pruned_to_ground = hc.recursive_leaf_removal(G, from_top=True)
    pruned_from_ground = hc.recursive_leaf_removal(G, from_top=False)
    print("Pruned from top:")
    for pruned_tree in pruned_to_ground:
        print(nx.to_numpy_array(pruned_tree))
    print("Pruned from bottom:")
    for pruned_tree in pruned_from_ground:
        print(nx.to_numpy_array(pruned_tree))

    """
    dissected_graphs = [copy.deepcopy(G)]
    while len(dissected_graphs[-1].nodes()) > 1:
        dissected_graphs.append(leaf_removal(dissected_graphs[-1], forward=from_top))
    if not keep_linkless_layer:
        while (
            nx.is_empty(dissected_graphs[-1]) and len(dissected_graphs) > 1
        ):  # catches empty graphs, which are eliminated in node condense
            dissected_graphs = dissected_graphs[
                :-1
            ]  # removes empty or single node layer
    return dissected_graphs


def orderability(
    G, condensed_nx_graph=None, num_thresholds=8, threshold_distribution=None
):
    """Evaluates orderability, or number of nodes which were not condensed
     over total number of nodes in original uncondensed graph. Evaluated as in [1]_

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
    a = np.array([
        [0, 0.2, 0, 0, 0],
        [0, 0, 0, 0.7, 0],
        [0, 0.4, 0, 0, 0],
        [0, 0, 0.1, 0, 1.0],
        [0, 0, 0, 0, 0],
    ])

    G = nx.from_numpy_matrix(a, create_using=nx.DiGraph)
    print(hc.orderability(G))


    Notes
    ______
    TODO: Not sure what's proper re: optional num_thresholds and threshold_distribution parameter
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    """

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


def feedforwardness_iteration(G):
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

    Examples
    ---------
    a = np.array([
        [0, 0.2, 0, 0, 0],
        [0, 0, 0, 0.7, 0],
        [0, 0.4, 0, 0, 0],
        [0, 0, 0.1, 0, 1.0],
        [0, 0, 0, 0, 0],
    ])
    condensed_networks, base_binary_networks = hc.node_weighted_condense(a)
    for network in condensed_networks:
        print(nx.to_numpy_array(network))
        g, paths = hc.feedforwardness_iteration(network)
        print('g: {0}, # paths: {1}'.format(g, paths))

    Notes
    ______
    g(G) = sum of F over all paths from maximal to minimal nodes

    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)

    """
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


def feedforwardness(DAG):
    """
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
    a = np.array([
        [0, 0.2, 0, 0, 0],
        [0.4, 0, 0, 0.7, 0],
        [0, 0.4, 0, 0, 0],
        [0, 0, 0.1, 0, 1.0],
        [0, 0, 0, 0, 0],
    ])
    condensed_networks, base_binary_networks = hc.node_weighted_condense(a)
    for network in condensed_networks:
        print("\nDAG: \n", nx.to_numpy_array(network))
        print("Feedforwardness: {0}".format(hc.feedforwardness(network)))

    Notes
    ______
    feedforwardness is calculated by pruning layers of the original graph and averaging
    over subsequent feedforwardness calculations.
    """
    # Must be fed the set of graphs with nodes lower on the hierarchy eliminated first
    successively_peeled_nx_graphs = recursive_leaf_removal(DAG, from_top=False)
    if (
        len(successively_peeled_nx_graphs) == 1
        and len(successively_peeled_nx_graphs[0].nodes()) == 1
    ):
        return 0

    f = 0
    total_num_paths = 0
    for nx_graph in successively_peeled_nx_graphs:
        g, paths = feedforwardness_iteration(nx_graph)
        f += g
        total_num_paths += paths
    return f / total_num_paths


def graph_entropy(DAG, forward_entropy=False):
    """
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
    b = np.array([
        [0, 0, 1, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0],
    ])

    condensed_network_layers = hc.recursive_leaf_removal(nx.condensation(nx.from_numpy_matrix(b, create_using=nx.DiGraph)))
    fwd_graph_entropy = [round(hc.graph_entropy(net, forward_entropy=True), 3) for net in condensed_network_layers]
    bkwd_graph_entropy = [round(hc.graph_entropy(net), 3) for net in condensed_network_layers]
    print("fwd graph entropy (from top | bottom): {0} | {1}".format(fwd_graph_entropy, bkwd_graph_entropy))

    Notes
    ______
    As described in the text of _[1]:
    Graph Entropy, B(G)_ij, is measure of probability of crossing a node n_j when following a path from n_i.
    Found in _[1], proposed and developed in _[2], _[3].

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
    dag = nx.convert_node_labels_to_integers(DAG)
    L_GC = len(
        recursive_leaf_removal(DAG)
    )  # Could be passed in most contexts to reduce redundant computation

    if forward_entropy:
        B_prime = matrix_normalize(nx.to_numpy_array(dag), row_normalize=True)
        P = sum(
            [np.power(B_prime, k) for k in range(1, L_GC + 1)]
        )  # +1 as k \in ( 1, L(G_C) )
        # TODO: Not so sure about this unless k coincides with the number of steps already taken (and the sum is odd)
    else:
        B = matrix_normalize(nx.to_numpy_array(dag), row_normalize=False)
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


def infographic_graph_entropy(DAG, forward_entropy=False):
    """
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
    b = np.array([
        [0, 0, 1, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0],
    ])

    condensed_network_layers = hc.recursive_leaf_removal(nx.condensation(nx.from_numpy_matrix(b, create_using=nx.DiGraph)))
    fwd_graph_entropy = [round(hc.infographic_graph_entropy(net, forward_entropy=True), 3) for net in condensed_network_layers]
    bkwd_graph_entropy = [round(hc.infographic_graph_entropy(net), 3) for net in condensed_network_layers]
    print("fwd graph entropy (from top | bottom): {0} | {1}".format(fwd_graph_entropy, bkwd_graph_entropy))

    Notes
    ______
    As described in the infographic of _[1] (figure 14):
    Graph Entropy, B(G)_ij, is measure of probability of crossing a node n_j when following a path from n_i.
    Found in _[1], proposed and developed in _[2], _[3].

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


def single_graph_treeness(DAG):
    """
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
    a = np.array([
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ])
    print("treeness (single graph): {0}".format(hc.single_graph_treeness(condensed_networks)))

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


def treeness(DAG):
    """
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
    b = np.array([
        [0, 0, 1, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0],
    ])
    dag = nx.condensation(nx.from_numpy_matrix(b, create_using=nx.DiGraph))
    print("treeness (b): {0}".format(hc.treeness(dag)))

    Notes
    ______
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    """
    pruned_from_top = recursive_leaf_removal(G=DAG, from_top=True)
    pruned_from_bottom = recursive_leaf_removal(G=DAG, from_top=False)
    # removal of original graphs from subsets:
    pruned_from_top = pruned_from_top[1:]
    pruned_from_bottom = pruned_from_bottom[1:]

    entropy_sum = single_graph_treeness(DAG)
    for index in range(len(pruned_from_top)):
        entropy_sum += single_graph_treeness(pruned_from_top[index])
    for index in range(len(pruned_from_bottom)):
        entropy_sum += single_graph_treeness(pruned_from_bottom[index])
    return entropy_sum / (1 + len(pruned_from_bottom) + len(pruned_from_top))


def hierarchy_coordinates(A, num_thresholds=8, threshold_distribution=None):
    """
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
    a = np.array([
        [0, 0.2, 0, 0, 0],
        [0, 0, 0, 0.7, 0],
        [0, 0.4, 0, 0, 0],
        [0, 0.3, 0.1, 0, 1.0],
        [0, 0, 0, 0, 0],
    ])
    b = np.array([
        [0, 0, 1, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0],
    ])
    print('(a) Treeness: {0} | Feedforwardness: {1}  | Orderability: {2}'.format(*np.round(hc.hierarchy_coordinates(a), 2)))
    print('(b) Treeness: {0} | Feedforwardness: {1}  | Orderability: {2}'.format(*np.round(hc.hierarchy_coordinates(b), 2)))

    Notes
    ______
    .. [1] "On the origins of hierarchy in complex networks."
     Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
     Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    returns the averaged hierarchy coordinates given the adjacency matrix A
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
    if np.array_equal(np.unique(np_A), [0, 1]):  # binary check
        num_thresholds = 1
    else:
        num_thresholds = num_thresholds

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


########################################################################################################################


if __name__ == "__main__":
    # CHECK VERSIONS
    vers_python0 = "3.7.3"
    vers_numpy0 = "1.17.3"
    vers_netx0 = "2.4"

    from sys import version_info
    from networkx import __version__ as vers_netx

    vers_python = "%s.%s.%s" % version_info[:3]
    vers_numpy = np.__version__

    print("\n------------------- Hierarchy Coordinates -----------------------\n")
    print("Required modules:")
    print("Python:        tested for: %s.  Yours: %s" % (vers_python0, vers_python))
    print("numpy:         tested for: %s.  Yours: %s" % (vers_numpy0, vers_numpy))
    print("networkx:      tested for: %s.   Yours: %s" % (vers_netx0, vers_netx))
    print("\n------------------------------------------------------------------\n")
