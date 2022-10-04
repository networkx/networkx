"""
***************
VF2++ Algorithm
***************

An implementation of the VF2++ algorithm for Graph Isomorphism testing.

The simplest interface to use this module is to call:

`vf2pp_is_isomorphic`: to check whether two graphs are isomorphic.
`vf2pp_isomorphism`: to obtain the node mapping between two graphs,
in case they are isomorphic.
`vf2pp_all_isomorphisms`: to generate all possible mappings between two graphs,
if isomorphic.

Introduction
------------
The VF2++ algorithm, follows a similar logic to that of VF2, while also
introducing new easy-to-check cutting rules and determining the optimal access
order of nodes. It is also implemented in a non-recursive manner, which saves
both time and space, when compared to its previous counterpart.

The optimal node ordering is obtained after taking into consideration both the
degree but also the label rarity of each node.
This way we place the nodes that are more likely to match, first in the order,
thus examining the most promising branches in the beginning.
The rules also consider node labels, making it easier to prune unfruitful
branches early in the process.

Examples
--------

Suppose G1 and G2 are Isomorphic Graphs. Verification is as follows:

Without node labels:

>>> import networkx as nx
>>> G1 = nx.path_graph(4)
>>> G2 = nx.path_graph(4)
>>> nx.vf2pp_is_isomorphic(G1, G2, node_label=None)
True
>>> nx.vf2pp_isomorphism(G1, G2, node_label=None)
{1: 1, 2: 2, 0: 0, 3: 3}

With node labels:

>>> G1 = nx.path_graph(4)
>>> G2 = nx.path_graph(4)
>>> mapped = {1: 1, 2: 2, 3: 3, 0: 0}
>>> nx.set_node_attributes(G1, dict(zip(G1, ["blue", "red", "green", "yellow"])), "label")
>>> nx.set_node_attributes(G2, dict(zip([mapped[u] for u in G1], ["blue", "red", "green", "yellow"])), "label")
>>> nx.vf2pp_is_isomorphic(G1, G2, node_label="label")
True
>>> nx.vf2pp_isomorphism(G1, G2, node_label="label")
{1: 1, 2: 2, 0: 0, 3: 3}

"""
import collections

import networkx as nx

from .vf2pp_helpers.candidates import _find_candidates, _find_candidates_Di
from .vf2pp_helpers.feasibility import _feasibility
from .vf2pp_helpers.node_ordering import _matching_order
from .vf2pp_helpers.state import _restore_Tinout, _restore_Tinout_Di, _update_Tinout

__all__ = ["vf2pp_isomorphism", "vf2pp_is_isomorphic", "vf2pp_all_isomorphisms"]

_GraphParameters = collections.namedtuple(
    "_GraphParameters",
    [
        "G1",
        "G2",
        "G1_labels",
        "G2_labels",
        "nodes_of_G1Labels",
        "nodes_of_G2Labels",
        "G2_nodes_of_degree",
    ],
)

_StateParameters = collections.namedtuple(
    "_StateParameters",
    [
        "mapping",
        "reverse_mapping",
        "T1",
        "T1_in",
        "T1_tilde",
        "T1_tilde_in",
        "T2",
        "T2_in",
        "T2_tilde",
        "T2_tilde_in",
    ],
)


def vf2pp_isomorphism(G1, G2, node_label=None, default_label=None):
    """Return an isomorphic mapping between `G1` and `G2` if it exists.

    Parameters
    ----------
    G1, G2 : NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism.

    node_label : str, optional
        The name of the node attribute to be used when comparing nodes.
        The default is `None`, meaning node attributes are not considered
        in the comparison. Any node that doesn't have the `node_label`
        attribute uses `default_label` instead.

    default_label : scalar
        Default value to use when a node doesn't have an attribute
        named `node_label`. Default is `None`.

    Returns
    -------
    dict or None
        Node mapping if the two graphs are isomorphic. None otherwise.
    """
    try:
        mapping = next(vf2pp_all_isomorphisms(G1, G2, node_label, default_label))
        return mapping
    except StopIteration:
        return None


def vf2pp_is_isomorphic(G1, G2, node_label=None, default_label=None):
    """Examines whether G1 and G2 are isomorphic.

    Parameters
    ----------
    G1, G2 : NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism.

    node_label : str, optional
        The name of the node attribute to be used when comparing nodes.
        The default is `None`, meaning node attributes are not considered
        in the comparison. Any node that doesn't have the `node_label`
        attribute uses `default_label` instead.

    default_label : scalar
        Default value to use when a node doesn't have an attribute
        named `node_label`. Default is `None`.

    Returns
    -------
    bool
        True if the two graphs are isomorphic, False otherwise.
    """
    if vf2pp_isomorphism(G1, G2, node_label, default_label) is not None:
        return True
    return False


def vf2pp_all_isomorphisms(G1, G2, node_label=None, default_label=None):
    """Yields all the possible mappings between G1 and G2.

    Parameters
    ----------
    G1, G2 : NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism.

    node_label : str, optional
        The name of the node attribute to be used when comparing nodes.
        The default is `None`, meaning node attributes are not considered
        in the comparison. Any node that doesn't have the `node_label`
        attribute uses `default_label` instead.

    default_label : scalar
        Default value to use when a node doesn't have an attribute
        named `node_label`. Default is `None`.

    Yields
    ------
    dict
        Isomorphic mapping between the nodes in `G1` and `G2`.
    """
    if G1.number_of_nodes() == 0 or G2.number_of_nodes() == 0:
        return False

    # Create the degree dicts based on graph type
    if G1.is_directed():
        G1_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(G1.in_degree, G1.out_degree)
        }
        G2_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(G2.in_degree, G2.out_degree)
        }
    else:
        G1_degree = dict(G1.degree)
        G2_degree = dict(G2.degree)

    if not G1.is_directed():
        find_candidates = _find_candidates
        restore_Tinout = _restore_Tinout
    else:
        find_candidates = _find_candidates_Di
        restore_Tinout = _restore_Tinout_Di

    # Check that both graphs have the same number of nodes and degree sequence
    if G1.order() != G2.order():
        return False
    if sorted(G1_degree.values()) != sorted(G2_degree.values()):
        return False

    # Initialize parameters and cache necessary information about degree and labels
    graph_params, state_params = _initialize_parameters(
        G1, G2, G2_degree, node_label, default_label
    )

    # Check if G1 and G2 have the same labels, and that number of nodes per label is equal between the two graphs
    if not _precheck_label_properties(graph_params):
        return False

    # Calculate the optimal node ordering
    node_order = _matching_order(graph_params)

    # Initialize the stack
    stack = []
    candidates = iter(
        find_candidates(node_order[0], graph_params, state_params, G1_degree)
    )
    stack.append((node_order[0], candidates))

    mapping = state_params.mapping
    reverse_mapping = state_params.reverse_mapping

    # Index of the node from the order, currently being examined
    matching_node = 1

    while stack:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
        except StopIteration:
            # If no remaining candidates, return to a previous state, and follow another branch
            stack.pop()
            matching_node -= 1
            if stack:
                # Pop the previously added u-v pair, and look for a different candidate _v for u
                popped_node1, _ = stack[-1]
                popped_node2 = mapping[popped_node1]
                mapping.pop(popped_node1)
                reverse_mapping.pop(popped_node2)
                restore_Tinout(popped_node1, popped_node2, graph_params, state_params)
            continue

        if _feasibility(current_node, candidate, graph_params, state_params):
            # Terminate if mapping is extended to its full
            if len(mapping) == G2.number_of_nodes() - 1:
                cp_mapping = mapping.copy()
                cp_mapping[current_node] = candidate
                yield cp_mapping
                continue

            # Feasibility rules pass, so extend the mapping and update the parameters
            mapping[current_node] = candidate
            reverse_mapping[candidate] = current_node
            _update_Tinout(current_node, candidate, graph_params, state_params)
            # Append the next node and its candidates to the stack
            candidates = iter(
                find_candidates(
                    node_order[matching_node], graph_params, state_params, G1_degree
                )
            )
            stack.append((node_order[matching_node], candidates))
            matching_node += 1


def _precheck_label_properties(graph_params):
    G1, G2, G1_labels, G2_labels, nodes_of_G1Labels, nodes_of_G2Labels, _ = graph_params
    if any(
        label not in nodes_of_G1Labels or len(nodes_of_G1Labels[label]) != len(nodes)
        for label, nodes in nodes_of_G2Labels.items()
    ):
        return False
    return True


def _initialize_parameters(G1, G2, G2_degree, node_label=None, default_label=-1):
    """Initializes all the necessary parameters for VF2++

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively

    Returns
    -------
    graph_params: namedtuple
        Contains all the Graph-related parameters:

        G1,G2
        G1_labels,G2_labels: dict

    state_params: namedtuple
        Contains all the State-related parameters:

        mapping: dict
            The mapping as extended so far. Maps nodes of G1 to nodes of G2

        reverse_mapping: dict
            The reverse mapping as extended so far. Maps nodes from G2 to nodes of G1. It's basically "mapping" reversed

        T1, T2: set
            Ti contains uncovered neighbors of covered nodes from Gi, i.e. nodes that are not in the mapping, but are
            neighbors of nodes that are.

        T1_out, T2_out: set
            Ti_out contains all the nodes from Gi, that are neither in the mapping nor in Ti
    """
    G1_labels = dict(G1.nodes(data=node_label, default=default_label))
    G2_labels = dict(G2.nodes(data=node_label, default=default_label))

    graph_params = _GraphParameters(
        G1,
        G2,
        G1_labels,
        G2_labels,
        nx.utils.groups(G1_labels),
        nx.utils.groups(G2_labels),
        nx.utils.groups(G2_degree),
    )

    T1, T1_in = set(), set()
    T2, T2_in = set(), set()
    if G1.is_directed():
        T1_tilde, T1_tilde_in = (
            set(G1.nodes()),
            set(),
        )  # todo: do we need Ti_tilde_in? What nodes does it have?
        T2_tilde, T2_tilde_in = set(G2.nodes()), set()
    else:
        T1_tilde, T1_tilde_in = set(G1.nodes()), set()
        T2_tilde, T2_tilde_in = set(G2.nodes()), set()

    state_params = _StateParameters(
        dict(),
        dict(),
        T1,
        T1_in,
        T1_tilde,
        T1_tilde_in,
        T2,
        T2_in,
        T2_tilde,
        T2_tilde_in,
    )

    return graph_params, state_params
