"""
========================
Hierarchy Coordinates
========================
Functions to calculate hierarchy coordinates for directed networks.

Hierarchy coordinates consist of treeness, feedforwardness, and orderability,
which collectively create a 'hierarchy morphospace' classifying all network
structures. In loose terms, treeness describes how consistently nodes higher
on the hierarchy (maximal nodes) branch into more nodes, while feedforwardness
considers the extent information passes vertically (vs horizontally) within
a hierarchy, and orderability considers what fraction of the network is
vertically hierarchical.

Originally from [1]_, adapted implementation accommodates weighted network.
For details, see _[2]

.. [1] "On the origins of hierarchy in complex networks."
 Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
 Proceedings of the National Academy of Sciences 110, no. 33 (2013)

.. [2] Appendix of 2013 paper:
https://www.pnas.org/highwire/filestream/613265/field_highwire_adjunct_files/0/sapp.pdf

"""

import networkx as nx
from networkx.utils import not_implemented_for
import copy

# from sklearn.preprocessing import normalize

__all__ = [
    "graphs_from_thresholds",
    "node_weighted_condense",
    "weight_nodes_by_condensation",
    "max_min_layers",
    "leaf_removal",
    "recursive_leaf_removal",
    "orderability",
    "feedforwardness",
    "analytic_graph_entropy",
    "graph_entropy",
    "treeness",
    "hierarchy_coordinates",
]


def graphs_from_thresholds(
    A, num_thresholds=8, threshold_distribution=None, verbose=False
):
    r"""Creates a series of networkx graphs based on generated edge weight thresholds

    Transforms a weighted NetworkX DiGraph into a set of unweighted NetworkX DiGraphs.
    The series of output graphs are determined by the number of thresholds and
    the distribution, with empty graphs dropped. Unweighted input graphs will always
     lead to single graph outputs.

    Parameters
    ----------
    A: numpy array
        Adjacency matrix, as square 2d numpy array
    num_thresholds: int, default: 8
        Number of thresholds and resultant sets of node-weighted
        Directed Acyclic Graphs
    threshold_distribution: float, optional
        If true or float, distributes the thresholds exponentially,
        with an exponent equal to the float input.
        Alternatively, a (lambda) function may be passed for custom distributions or
        custom thresholds may also be given via a list.
    verbose: bool, optional
        If true, returns thresholds used to make undirected graphs

    Returns
    -------
    nx_graphs: list of networkX Graphs
        list of unweighted graphs produced from applying thresholds to the
        original weighted network

    Examples
    --------
    >>> import numpy as np
    >>> a = np.array([
    ...     [0, 1, 0],
    ...     [0, 0, 0.4],
    ...     [0, 0, 0]
    ... ])
    >>> unweighted_networks_from_thresholds = nx.graphs_from_thresholds(a, num_thresholds=2)
    >>> for network in unweighted_networks_from_thresholds:
    ...     print(network, ":", network.edges)
    DiGraph with 3 nodes and 2 edges : [(0, 1), (1, 2)]
    DiGraph with 2 nodes and 1 edges : [(0, 1)]

    See Also
    --------
    weight_nodes_by_condensation, graph_entropy, treeness

    Notes
    ------
    An threshold_distribution of None results in a linear distribution, otherwise
    the exponential distribution is sampled from exp(x) \in (0, 1)

    .. [1] "On the origins of hierarchy in complex networks."
    Corominas-Murtra, Bernat, Joaquín Goñi, Ricard V. Solé, and Carlos Rodríguez-Caso,
    Proceedings of the National Academy of Sciences 110, no. 33 (2013)
    """
    import numpy as np

    # binary check
    A_elements = set(A.flat)
    if len(A_elements) == 2 and 0 in A_elements:
        num_thresholds = 1
    elif isinstance(threshold_distribution, list):
        num_thresholds = len(threshold_distribution)
    else:
        num_thresholds = num_thresholds

    # Establishing Thresholds
    if num_thresholds == 1 or np.isclose(np.max(A) - np.min(A), 0, 1e-15):
        nx_graphs = [nx.from_numpy_array(A, create_using=nx.DiGraph)]
        if verbose:
            print("0 Threshold used (edge values identical or threshold singular)")
    else:
        if threshold_distribution is None:
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
        elif isinstance(threshold_distribution, list):
            if max(threshold_distribution) > np.max(A) or min(
                threshold_distribution
            ) < np.min(threshold_distribution):
                raise Exception(ValueError)
            thresholds = threshold_distribution
        else:
            thresholds = _distribute(
                dist=threshold_distribution,
                end_value_range=(np.min(A), np.max(A)),
                n=num_thresholds,
            )
        # Converting to binary nx_graphs according to thresholds:
        if verbose:
            print(f"Thresholds: {thresholds}")
        nx_graphs = [
            nx.from_numpy_array(np.where(A > threshold, 1, 0), create_using=nx.DiGraph)
            for threshold in thresholds
        ]
    # removes isolated nodes (0 in & out degree) from binary nodes. (not needed for consolidation)
    for G in nx_graphs:
        G.remove_nodes_from(list(nx.isolates(G)))

    # eliminates empty graphs
    return [graph for graph in nx_graphs if not nx.is_empty(graph)]


def node_weighted_condense(nx_graphs):
    """Condenses graphs and reassigns node weight according to original graph.

    Condenses NetworkX DiGraphs with resultant node weight equal to number of nodes
    in original strongly connected component, and reassigns node indices to match
    length of the new NetworkX DiGraphs.

    Parameters
    ----------
    nx_graphs: (list of) NetworkX DiGraph(s)
        List of NetworkX Digraphs, or single NetworkX DiGraph

    Returns
    -------
    largest_condensed_graphs: list of NetworkX DiGraph(s)
        Largest (by number of nodes, not node weight) graphs made of each
        original nx_graph, with resultant node weight equal to the number
        of nodes in the original graphs (now compressed) strongly
        connected components.

    Raises
    -------
    NetworkXNotImplemented
        If G is undirected

    Examples
    -------
    >>> import numpy as np
    >>> a = np.array([
    ...     [0, 1, 0, 0],
    ...     [0, 0, 1, 0],
    ...     [0, 1, 0, 1],
    ...     [0, 0, 0, 0]
    ... ])
    >>> A = nx.from_numpy_array(a, create_using=nx.DiGraph)
    >>> condensed_a = nx.node_weighted_condense(A)[0]
    >>> for n, w in A.nodes.data('weight'):
    ...    print(f'Original Node {n}: Weight {w}')
    Original Node 0: Weight None
    Original Node 1: Weight None
    Original Node 2: Weight None
    Original Node 3: Weight None
    >>> for n, w in condensed_a.nodes.data('weight'):
    ...    print(f'Condensed Node {n}: Weight {w}')
    Condensed Node 0: Weight 1
    Condensed Node 1: Weight 2
    Condensed Node 2: Weight 1

    See Also
    -------
    weakly_connected_components
    weight_nodes_by_condensation

    Notes
    -------
    WIP TODO: As multiple independent graphs may result from applying threshold cutoffs to a weighted graph,
        only the largest is considered. This might be worth considering in re-evaluating the meaning of
        weighted network hierarchy coordinate evaluations. (See pages 7, 8 of [1]_, supplementary material)

    Total node weight is preserved, graphs are relabeled to remain internally consistent,
        e.g. if a graph's first 3 nodes are a strongly connected component, they will
        combine into a single node of weight 3, which will be relabeled as node one.
    """
    if isinstance(nx_graphs, list):
        condensed_graphs = [nx.condensation(G) for G in nx_graphs]
    elif isinstance(nx_graphs, nx.DiGraph):
        condensed_graphs = [nx.condensation(nx_graphs)]
    else:
        raise Exception(TypeError)

    largest_condensed_graphs = []
    for condensed_graph in condensed_graphs:
        largest_condensed_graphs.append(
            nx.convert_node_labels_to_integers(
                condensed_graph.subgraph(
                    max(nx.weakly_connected_components(condensed_graph), key=len)
                )
            ).copy()
        )
        for node, attrs in largest_condensed_graphs[-1].nodes.data():
            attrs["weight"] = len(attrs["members"])

    return largest_condensed_graphs


@not_implemented_for("undirected")
def weight_nodes_by_condensation(condensed_graph):
    """Weights nodes according to the number of other nodes they condensed

    Nodes condensed are the sum of constituent cycle of DAG nodes as proposed
     in _[1]:  e.g. if a cycle contained 3 nodes (and thus became one in
    condensation) the resulting node of the condensed graph would then gain
    weight = 3.  Single (non-cyclic) nodes are weighted as 1.
    Graphs are updated in-place, modifying the graph passed in as a parameter.

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
    >>> import numpy as np
    >>> b = np.array([
    ...     [0, 0.2, 0, 0, 0],
    ...     [0, 0, 0, 0.7, 0],
    ...     [0, 0.4, 0, 0, 0],
    ...     [0, 0, 0.1, 0, 1.0],
    ...     [0, 0, 0, 0, 0],
    ... ])

    >>> num_thresholds = 2
    >>> condensed_networks = nx.node_weighted_condense(graphs_from_thresholds(b, num_thresholds=num_thresholds))
    >>> for cG in condensed_networks:
    ...     for node, weight in cG.nodes.data("weight"):
    ...         print(f"Node {node}, new weight: {weight}")
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

    for node, attrs in condensed_graph.nodes.data():
        attrs["weight"] = len(attrs["members"])
    return condensed_graph


@not_implemented_for("undirected")
def max_min_layers(G, max_layer=True):
    """Returns the maximal (k_in = 0) layer or the minimal layer (k_out = 0)

    Returns the maximal or minimal layer of a directed network.
    Layers here are defined with respect to repeated application of this function;
    maximal (minimal) nodes are those with 0 out (in) degree, and thus the
    first layer are those nodes meeting these requirements for the initial graph,
    and the second layer are those which meet these requirements after removing
    a 'layer' of maximal (minimal) nodes.

    Parameters
    ----------
    G: NetworkX Graph
        A directed graph.
    max_layer: bool, default: True
        if True, returns maximal layer (k_in = 0),
            else returns nodes for which k_out = 0, minimal layer

    Return
    ------
    min/max_layer: list
        list of node indices as ints

    Examples:
    >>> import numpy as np
    >>> a = np.array([
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 1, 0],
    ...     [0, 0, 0, 0, 0, 1, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])

    >>> G = nx.from_numpy_array(a, create_using=nx.DiGraph)
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
        For unconnected graphs, returns the set of minimal nodes in the order of their
        appearance in the original (unconnected) network, e.g.
    >>> unconnected_G = nx.DiGraph()
    >>> unconnected_G.add_edges_from([(0, 2), (2, 3), (1, 2), ('a', 'b'), ('b', 'c')])
    >>> print(f'{nx.max_min_layers(unconnected_G, max_layer=True)}')
    [0, 1, 'a']
    """
    if not G.is_directed():
        raise nx.NetworkXError("G must be a DiGraph for min/max layer evaluation")
    if max_layer:
        return [node for node, deg in G.in_degree if deg == 0]
    else:
        return [node for node, deg in G.out_degree if deg == 0]


@not_implemented_for("undirected")
def leaf_removal(G, top=True):
    """Returns a pruned network with either maximal or minimal nodes removed.

    Maximal (minimal) nodes are those with k_in = 0 (k_out = 0).
    The 'pruned network' is thus the network which remains afters its maximal
    or minimal nodes have been removed, e.g. for a 3 node path graph, leaf_removal
    would yield from (0, 1, 2) -> (1, 2) if removing maximal nodes (from top)
     or (0, 1, 2) -> (0, 1) if removing minimal nodes, (from bottom, top=False)


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
    >>> import numpy as np
    >>> a = np.array([
    ...   [0, 0, 1, 1, 0, 0, 0],
    ...   [0, 0, 1, 1, 0, 0, 0],
    ...   [0, 0, 0, 0, 1, 1, 0],
    ...   [0, 0, 0, 0, 0, 1, 1],
    ...   [0, 0, 0, 0, 0, 0, 0],
    ...   [0, 0, 0, 0, 0, 0, 0],
    ...   [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> G = nx.from_numpy_array(a, create_using=nx.DiGraph)
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
    """Prunes nodes from top (maximal) or bottom (minimal) recursively. Original
    DAG is given as first element

    Useful for examinations of hierarchy layer by layer. Note that the
    *remaining* graph is returned, not the layers

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
    >>> import numpy as np
    >>> a = np.array([
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 1, 0],
    ...     [0, 0, 0, 0, 0, 1, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> G = nx.from_numpy_array(a, create_using=nx.DiGraph)
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
        # catches empty graphs, which are eliminated in node condense
        while nx.is_empty(dissected_graphs[-1]) and len(dissected_graphs) > 1:
            dissected_graphs = dissected_graphs[:-1]
    # removes empty or single node layer
    return dissected_graphs


@not_implemented_for("undirected")
def orderability(
    G, condensed_nx_graph=None, num_thresholds=8, threshold_distribution=None
):
    """Evaluates orderability, a measure of how vertically hierarchical a
    network is.

    Given as intersection of the nodes inside the consdensed and original
    network, divided by the total number of nodes in the original network.

    Adapted for weighted networks from the original algorithm found here: [1]_.

    Parameters
    ----------
    G: NetworkX Graph
        A directed graph.
    condensed_nx_graph: optional
        Directed acyclic networkX graph if already evaluated to save computational time
    num_thresholds: int, optional
        only applicable as graphs_from_thresholds parameter if G is weighted
    threshold_distribution: float, optional
        only applicable as graphs_from_thresholds parameter if G is weighted

    Return
    -------
    float: orderability
        Hierarchy coordinate


    Examples
    ---------
    >>> import numpy as np
    >>> a = np.array([
    ...     [0, 0.2, 0, 0, 0],
    ...     [0, 0, 0, 0.7, 0],
    ...     [0, 0.4, 0, 0, 0],
    ...     [0, 0, 0.1, 0, 1.0],
    ...     [0, 0, 0, 0, 0],
    ... ])

    >>> G = nx.from_numpy_array(a, create_using=nx.DiGraph)
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
    import numpy as np

    if not G.is_directed():
        raise nx.NetworkXError(
            "G must be a directed graph for any hierarchy coordinate evaluation"
        )
    # unweighted (non-binary) check
    if not np.array_equal(np.unique(nx.to_numpy_array(G)), [0, 1]):
        original_graphs = graphs_from_thresholds(
            nx.to_numpy_array(G),
            num_thresholds,
            threshold_distribution,
        )
        condensed_graphs = node_weighted_condense(original_graphs)

        o = sum(
            orderability(OG, CG) for CG, OG in zip(condensed_graphs, original_graphs)
        )
        return o / len(condensed_graphs)

    if condensed_nx_graph is None:
        condensed_nx_graph = weight_nodes_by_condensation(nx.condensation(G))
    weights = nx.get_node_attributes(condensed_nx_graph, "weight").values()
    total_acyclic_node_weight = sum(weights)
    number_non_cyclic_nodes = sum(1 for wt in weights if wt == 1)
    return number_non_cyclic_nodes / total_acyclic_node_weight


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
                # where each path calculation is F(path)
                g += len(path) / sum(weights[node] for node in path)
                num_paths += 1
    return g, num_paths


@not_implemented_for("undirected")
def feedforwardness(DAG):
    """Returns feedforwardness hierarchy coordinate.

    The feedforwardness heierarchy coordinate represents the extent information
    passes vertically, as opposed to horizontally, within a hierarchy. That is,
    how much does information pass through unreciprocated connections versus how
    much through cyclic (reciprocated) connections.

    Based on a weighted sum which considers how much each path from every
    maximal node to every minimal node traverses through cyclic (flat hierarchy)
    components. As this is performed over a DAG whose node weights represent the
    number of cyclic nodes so condensed, the ratio of nodes to their total
    weight in a given path yields precisely this measure. Feedforwardness is
    then given by the mean of this ratio for all paths on a given layer, and
    then summing over all layers pruned through repeated removal of maximal
    nodes.


    More formally, total feedfowardness is given by
    .. math::

        F(G) = \frac{g(G_C) + \\sum_{k < L(G_C)} g(G_k)}{|\\prod_{M \\mu}(G_c)|
        + \\sum_{k < L_{G_C}} |\\prod_{M \\mu} (G_k)|}

    where :math:`\\mu` (M) is the set of minimal (maximal) nodes, :math:`G_C` is
    the DAG, :math:`\\prod_{M \\mu}` is the set of paths from maximal to minimal
    nodes, :math:`L_{G_C}` is the set of layers produced by removing maximal nodes,
    and :math:`g(G_k) = \\sum_{\\pi_i \\in \\prod_{M \\mu}(G_k)} F(\\pi_i)` where
    :math:`F(\\pi_k) = \frac{|v(\\pi_k)|}{\\sum_{v_i \\in v(\\pi_k)} \alpha_i}`,
    with :math:`v_k` the k-th node and :math:`\alpha_k` its weight.

    The original algorithm was given in
        "On the origins of hierarchy in complex networks."[1]_
        and with details given in their appendix.[2]_

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
    >>> infographic_network = [
    ...     (0, 2),
    ...     (1, 2),
    ...     (1, 6),
    ...     (2, 4),
    ...     (3, 2),
    ...     (3, 4),
    ...     (4, 5),
    ...     (5, 3),
    ...     (5, 6),
    ... ]
    >>> # requires a node weighted directed acyclic graph
    >>> G = nx.weight_nodes_by_condensation(nx.condensation(nx.DiGraph(infographic_network)))
    >>> print(round(nx.feedforwardness(G), 2))
    0.56

    Notes
    ______
    feedforwardness is calculated by pruning layers of the original graph and
    averaging over subsequent feedforwardness calculations.

    TODO: Not sure what's proper re: optional num_thresholds and
    threshold_distribution parameter

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

    if len(DAG) == 1:
        return 0

    successively_peeled_nx_graphs = recursive_leaf_removal(DAG, from_top=False)

    f = 0
    total_num_paths = 0
    for nx_graph in successively_peeled_nx_graphs:
        g, paths = _feedforwardness_iteration(nx_graph)
        f += g
        total_num_paths += paths
    return f / total_num_paths


@not_implemented_for("undirected")
def analytic_graph_entropy(DAG, forward_entropy=False):
    """Measures uncertainty in following all directed paths through the network.

    computed by summing over the probability of transition from every maximal
    (minimal) node to all others, to yield forward (backward) entropy.
    transition probabilities are calculated via powers of the modified adjacency
    matrix.

    Parameters
    ----------
    DAG: NetworkX Graph
        Directed Acyclic Graph
    forward_entropy: Bool, default: False
        if True, calculates entropy from maximal nodes (k_in = 0) to others.
        Otherwise calculates using paths from minimal nodes the bottom.

    Return
    -------
    entropy: float
        graph entropy, in [1]_, eq.14/16 ( H_b/f (G_C) )

    Examples
    ---------
    >>> import numpy as np
    >>> b = np.array([
    ...     [0, 0, 1, 0, 0, 0, 1],
    ...     [0, 0, 1, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 0, 0],
    ...     [0, 0, 1, 0, 1, 0, 0],
    ...     [0, 0, 0, 0, 0, 1, 0],
    ...     [0, 0, 0, 1, 0, 0, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])

    >>> A = nx.from_numpy_array(b, create_using=nx.DiGraph)
    >>> condensed_layers = nx.recursive_leaf_removal(nx.condensation(A))
    >>> fwd_entropy, bkwd_entropy = [], []
    >>> for net in condensed_layers:
    ...     fwd_entropy.append(round(nx.graph_entropy(net, forward_entropy=True), 3))
    ...     bkwd_entropy.append(round(nx.graph_entropy(net), 3))
    >>> print(f"graph entropy, fwds: {fwd_entropy}; bkwd: {bkwd_entropy}")
    graph entropy, fwds: [0.347, 0.0]; bkwd: [1.04, 0.0]

    Notes
    ______
    As described in the text of _[1], proposed and developed in _[2], _[3]:
    Graph Entropy, is measure of probability of crossing a node n_j when
    following a path from n_i.

    _Forward_ entropy:
    .. math::
        H_f(G_C) = \frac{1}{|M|} \\sum_{v_i \\in M} \\sum_{v_k \\in V \\setminus \\mu}
        P(v_i \right v_k) \\cdot log k_{out}(v_k)

    _Backward_ entropy:
    .. math::
        H_b(G_C) = \frac{1}{|\\mu|} \\sum_{v_i \\in \\mu} \\sum_{v_k \\in V_C \\setminus M}
        P(v_i \\leftarrow v_k) \\cdot log k_{in}(v_k)

    where :math:`\\mu` (M) is the set of minimal (maximal) nodes,
    and :math:`P(v_i \\leftarrow v_k)` indicates the probability of
    transition between :math:`v_k` and :math:`v_i`.

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
    import numpy as np

    if not nx.is_directed_acyclic_graph(DAG):
        raise nx.NetworkXError(
            "G must be a directed acyclic graph for graph entropy evaluation"
        )

    dag = nx.convert_node_labels_to_integers(DAG)
    # Could be passed in most contexts to reduce redundant computation
    L_GC = len(recursive_leaf_removal(DAG))

    axis = 1 if forward_entropy else 0
    B = nx.to_numpy_array(dag)  # .T
    # normalize so rows (forward_entropy) or columns (backward_entropy) sum to 1.
    sums = B.sum(axis=axis, keepdims=True)
    sums[sums == 0] = 1
    B = B / sums
    B = B if forward_entropy else B.T
    # +1 as k \in ( 1, L(G_C) )
    P = sum(np.linalg.matrix_power(B, k) for k in range(1, L_GC + 1))
    boundary_layer = max_min_layers(dag, max_layer=forward_entropy)
    non_extremal_nodes = set(dag.nodes() - boundary_layer)
    # Eliminates zero degree nodes from log; as
    opposite_boundary_layer = max_min_layers(dag, max_layer=not forward_entropy)
    non_extremal_nodes = set(non_extremal_nodes - set(opposite_boundary_layer))

    deg = dag.out_degree if forward_entropy else dag.in_degree
    e = sum(
        P[u][v] * np.log(deg(v)) for u in boundary_layer for v in non_extremal_nodes
    )
    entropy = e / len(boundary_layer)
    return entropy


@not_implemented_for("undirected")
def graph_entropy(DAG, forward_entropy=False):
    """Measures uncertainty in following all directed paths through the network.

    Computed by summing over the probability of transition from every maximal
    (minimal) node to all others, to yield forward (backward) entropy.
    Transition probabilities are calculated via brute force computation
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
    >>> import numpy as np
    >>> b = np.array([
    ...     [0, 0, 1, 0, 0, 0, 0],
    ...     [0, 0, 1, 0, 0, 0, 1],
    ...     [0, 0, 0, 0, 1, 0, 0],
    ...     [0, 0, 1, 0, 1, 0, 0],
    ...     [0, 0, 0, 0, 0, 1, 0],
    ...     [0, 0, 0, 1, 0, 0, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])

    >>> A = nx.from_numpy_array(b, create_using=nx.DiGraph)
    >>> condensed_layers = nx.recursive_leaf_removal(nx.condensation(A))
    >>> fwd_entropy, bkwd_entropy = [], []
    >>> for net in condensed_layers:
    ...     fwd_entropy.append(round(nx.graph_entropy(net, forward_entropy=True), 3))
    ...     bkwd_entropy.append(round(nx.graph_entropy(net), 3))
    >>> print(f"graph entropy, fwds: {fwd_entropy}; bkwd: {bkwd_entropy}")
    graph entropy, fwds: [0.347, 0.0]; bkwd: [1.04, 0.0]

    Notes
    ______
    As described in the text of _[1], proposed and developed in _[2], _[3]:
    Graph Entropy, is measure of probability of crossing a node n_j when
    following a path from n_i.

    _Forward_ entropy:
    .. math::
        H_f(G_C) = \frac{1}{|M|} \\sum_{v_i \\in M} \\sum_{v_k \\in V \\setminus \\mu}
        P(v_i \right v_k) \\cdot log k_{out}(v_k)

    _Backward_ entropy:
    .. math::
        H_b(G_C) = \frac{1}{|\\mu|} \\sum_{v_i \\in \\mu} \\sum_{v_k \\in V_C \\setminus M}
        P(v_i \\leftarrow v_k) \\cdot log k_{in}(v_k)

    where :math:`\\mu` (M) is the set of minimal (maximal) nodes,
    and :math:`P(v_i \\leftarrow v_k)` indicates the probability of
    transition between :math:`v_k` and :math:`v_i`, as the inverse
    of the sum of non-binary branchings.

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
    import numpy as np

    if not nx.is_directed_acyclic_graph(DAG):
        raise nx.NetworkXError(
            "G must be a directed acyclic graph for graph entropy evaluation"
        )

    dag = nx.convert_node_labels_to_integers(DAG)
    start_layer = max_min_layers(dag, max_layer=forward_entropy)
    end_layer = max_min_layers(dag, max_layer=not forward_entropy)
    entropy = 0
    if not forward_entropy:
        dag = dag.reverse(copy=True)
    for start_node in start_layer:
        for end_node in end_layer:
            paths = list(nx.all_simple_paths(dag, source=start_node, target=end_node))
            for path in paths:
                n = sum(d for _, d in dag.out_degree(path[:-1]) if d != 1)
                # Except ones as they don't indicate further possible paths
                if n == 0:
                    n = 1
                entropy += np.log(n) / n
    entropy /= len(start_layer)
    return entropy


@not_implemented_for("undirected")
def _single_graph_treeness(DAG):
    """Evaluates treeness of a directed, acyclic, unweighted graph.

    Treeness measures how consistently the network branches along the directed
    connections.  Alternatively, how maximal nodes feed to otherwise maximal
    nodes; how much do edges connect to nodes with more edges further down the
    hierarchy?

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
    >>> import numpy as np
    >>> a = np.array([
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 1, 1, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 1, 0],
    ...     [0, 0, 0, 0, 0, 1, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> condensed_network = nx.node_weighted_condense(graphs_from_thresholds(a))[0]
    >>> print("treeness (single graph): {0}".format(np.round(_single_graph_treeness(condensed_network), 3)))
    treeness (single graph): 0.333

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
    """Treeness describes how consistently nodes higher on the hierarchy
    (maximal nodes) branch into more nodes.

    Based on `graph_entropy` a measure dependant on the probability of
    transitioning between any two given nodes, Treeness measures the expansion
    or contraction of paths from maximal nodes, yielding positive or negative
    values respectively.

    The original algorithm was given in "On the origins of hierarchy in complex
    networks."[1]_ and with details given in their appendix.[2]_

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
    >>> import numpy as np
    >>> a = np.array([
    ...     [0, 0, 1, 0, 0, 0, 1],
    ...     [0, 0, 1, 0, 0, 0, 0],
    ...     [0, 0, 0, 0, 1, 0, 0],
    ...     [0, 0, 1, 0, 1, 0, 0],
    ...     [0, 0, 0, 0, 0, 1, 0],
    ...     [0, 0, 0, 1, 0, 0, 1],
    ...     [0, 0, 0, 0, 0, 0, 0],
    ... ])
    >>> dag = nx.condensation(nx.from_numpy_array(a, create_using=nx.DiGraph))
    >>> print("treeness: {0}".format(np.round(nx.treeness(dag), 2)))
    treeness: -0.56

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
    for pruned_tree in pruned_from_top:
        entropy_sum += _single_graph_treeness(pruned_tree)
    for pruned_tree in pruned_from_bottom:
        entropy_sum += _single_graph_treeness(pruned_tree)
    return entropy_sum / (1 + len(pruned_from_bottom) + len(pruned_from_top))


def hierarchy_coordinates(A, num_thresholds=8, threshold_distribution=None):
    """Returns hierarchy coordinates: treeness, feedforwardness & orderability.

    Hierarchy coordinates can classifying all network structures, and their
    respective hierarchy, though certain combinations are theoretically
    impossible to acheive.

    Adapted for weighted networks from "On the origins of hierarchy in complex
    networks."[1]_ and with details given in their appendix.[2]_


    Parameters
    ----------
    A: 2d numpy array or networkX graph
        numpy Adjacency matrix or networkx of which hierarchy coordinates
            will be calculated

    num_thresholds: int, optional
        specifies number of weighted graph subdivisions

    threshold_distribution: None, float or lambda fct ptr, default: None
        determines the distribution of threshold values used to
            create unweighted from weighted networks.
        if None, creates a linear distribution of thresholds spanning
            the set of weights evenly.
        if float, is the coefficient of exp(Ax) sampled between (0, 1)
            and rescaled appropriately.
        if a lambda expression, determines a custom distribution sampled
            between (0, 1) and rescaled appropriately.

    Return
    -------
    tuple of floats:
        (treeness, feedforwardness, orderability) hierarchy coordinates

    Examples
    ---------
    >>> import numpy as np
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
    (a) Treeness: -0.08 | Feedforwardness: 0.87 | Orderability: 0.81
    >>> print('(b) Treeness: {0} | Feedforwardness: {1} | Orderability: {2}'.format(*np.round(nx.hierarchy_coordinates(b), 2)))
    (b) Treeness: -0.56 | Feedforwardness: 0.56 | Orderability: 0.43

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
    import numpy as np

    if isinstance(A, nx.DiGraph):
        np_A = nx.to_numpy_array(A)
    elif isinstance(A, np.ndarray):
        np_A = A
    else:
        raise nx.NetworkXError("A must be a networkx graph or numpy adjacency array")

    if np.array_equal(np.unique(np_A), [0]):  # null check
        # raise Exception("Unconnected graph; trivially 0 hierarchy")  # TODO: Raise exception if undefined instead
        return 0, 0, 0

    original_graphs = graphs_from_thresholds(
        np_A, num_thresholds, threshold_distribution
    )
    condensed_graphs = node_weighted_condense(original_graphs)

    t = sum(treeness(G) for G in condensed_graphs) / len(condensed_graphs)
    f = sum(feedforwardness(G) for G in condensed_graphs) / len(condensed_graphs)
    o = sum(
        orderability(OG, CG) for OG, CG in zip(original_graphs, condensed_graphs)
    ) / len(condensed_graphs)
    return t, f, o


# Utilities for hierarchy coordinates
def _distribute(n, end_value_range=None, dist=1, sampled_range_of_dist=(0, 1)):
    """Returns n floats distributed as within the sampled range of provided
    distribution, rescaled to end_value_range Defaults to an exponential
    distribution e^x, x = (0, 1), where int/float values of dist modify the
    coefficient on x

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
    import numpy as np

    if isinstance(dist, float) or isinstance(dist, int):
        distribution = lambda x: np.exp(dist * x)
    else:
        distribution = dist

    x_increment = abs(max(sampled_range_of_dist) - min(sampled_range_of_dist)) / n
    pts = np.array([distribution(x_increment * i) for i in range(n)])
    pts /= abs(max(pts) - min(pts))

    if end_value_range is not None:
        pts = pts * (max(end_value_range) - min(end_value_range)) + min(end_value_range)
    return pts
