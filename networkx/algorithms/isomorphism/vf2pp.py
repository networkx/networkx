"""
***************
VF2++ Algorithm
***************

An implementation of the VF2++ algorithm [1]_ for Graph Isomorphism testing.

The simplest interface to use this module is to call:

`vf2pp_is_isomorphic`: check whether two graphs are isomorphic.
`vf2pp_isomorphism`: obtain the node isomorphism mapping between two graphs,
if they are isomorphic.
`vf2pp_all_isomorphisms`: generate all possible isomorphism mappings between
two graphs, if isomorphic.

`vf2pp_is_subgraph_isomorphic`: check whether a specified graph
is isomorphic to an induced subgraph of the other graph.
`vf2pp_subgraph_isomorphism`: obtain the node isomorphism mapping between a
specified graph and any induced subgraph of the other graph, if possible.
`vf2pp_all_subgraph_isomorphisms`: generate all possible isomorphism mappings
between the specified induced subgraph and the graph.

`vf2pp_is_monomorphic`: check whether two graphs are monomorphic. That is,
the node and edge sets of one are subsets of the other's node and edge sets.
`vf2pp_monomorphism`: obtain the node monomorphism mapping between a
specified graph and any subgraph of the other graph, if possible.
`vf2pp_all_monomorphisms`: generate all possible monomorphism mappings
between the specified subgraph and the graph.

Introduction
------------
The VF2++ algorithm, follows a similar logic to that of VF2, while also
introducing new easy-to-check cutting rules and determining the optimal access
order of nodes. It is also implemented in a non-recursive manner, which saves
both time and space, when compared to its previous counterpart.

An improved node ordering is obtained after taking into consideration both the
degree and the label rarity of each node.
This way we consider the nodes that eliminate the most branches of the possible
mapping search tree, so we can cut out unfruitful branches early in the process.

Warning: The VF2++ paper uses the symbols `G1` and `G2` for the two graphs of
interest just as the VF2 paper does. But for subgraph functions the first graph
is smaller in VF2++ while the second is smaller for VF2 and for ISMAGS. This
implementation, VF2pp, matches the VF2 and ISMAGS notation with the second
input being no larger than the first. To avoid confusion with the papers we
name the graphs `FG` and `SG` for full graph and smaller graph. For VF2pp,
`SG` corresponds to the paper's `G1` while `FG` corresponds to `G2`. This does
not matter for the isomorphism functions (where the graphs have the same size).

Examples
--------

Suppose SG and FG are Isomorphic Graphs. Verification is as follows:

Without node labels:

>>> import networkx as nx
>>> SG = nx.path_graph(4)
>>> FG = nx.path_graph(4)
>>> nx.vf2pp_is_isomorphic(FG, SG, node_label=None)
True
>>> nx.vf2pp_isomorphism(FG, SG, node_label=None)
{1: 1, 2: 2, 0: 0, 3: 3}

With node labels:

>>> mapped = {1: 1, 2: 2, 3: 3, 0: 0}
>>> nx.set_node_attributes(
...     SG, dict(zip(SG, ["blue", "red", "green", "yellow"])), "label"
... )
>>> nx.set_node_attributes(
...     FG, dict(zip(FG, ["blue", "red", "green", "yellow"])), "label"
... )
>>> nx.vf2pp_is_isomorphic(FG, SG, node_label="label")
True
>>> nx.vf2pp_isomorphism(FG, SG, node_label="label")
{1: 1, 2: 2, 0: 0, 3: 3}

For subgraph isomorphism we look for induced subgraphs of FG that are
isomorphic to SG. The process is similar to graph isomorphism with a
different function:

>>> SG = nx.path_graph(3)
>>> FG = nx.path_graph(4)
>>> nx.vf2pp_is_subgraph_isomorphic(FG, SG, node_label=None)
True
>>> nx.vf2pp_subgraph_isomorphism(FG, SG, node_label=None)
{1: 1, 2: 2, 0: 0}

With node labels:

>>> mapped = {1: 1, 2: 2, 3: 3, 0: 0}
>>> nx.set_node_attributes(SG, dict(zip(SG, ["blue", "red", "green"])), "label")
>>> nx.set_node_attributes(
...     FG, dict(zip(FG, ["blue", "red", "green", "yellow"])), "label"
... )
>>> nx.vf2pp_is_subgraph_isomorphic(FG, SG, node_label="label")
True
>>> nx.vf2pp_subgraph_isomorphism(FG, SG, node_label="label")
{1: 1, 2: 2, 0: 0}

For subgraph monomorphism we look for possibly non-induced subgraphs
of FG that are isomorphic to SG. That means we only need a subset of nodes
and edges of the first that map to nodes and edges of the second. But
not all edges in the second graph need to be mapped to, even if that edge
involves two nodes that are mapped to.

A classic example of this is a path graph mapping to a subgraph of a
cycle graph with the same number of nodes. The missing edge in the path
graph means that no subgraph isomorphism exists. But a monomorphism exists
because not all induced edges need to be mapped to.

>>> SG = nx.path_graph(4)
>>> FG = nx.cycle_graph(4)
>>> nx.vf2pp_is_monomorphic(FG, SG, node_label=None)
True
>>> nx.vf2pp_monomorphism(FG, SG, node_label=None)
{1: 1, 2: 2, 0: 0}

With node labels:

>>> mapped = {1: 1, 2: 2, 3: 3, 0: 0}
>>> nx.set_node_attributes(SG, dict(zip(SG, ["blue", "red", "green"])), "label")
>>> nx.set_node_attributes(
...     FG, dict(zip(FG, ["blue", "red", "green", "yellow"])), "label"
... )
>>> nx.vf2pp_is_monomorphic(FG, SG, node_label="label")
True
>>> nx.vf2pp_monomorphism(FG, SG, node_label="label")
{1: 1, 2: 2, 0: 0}

References
----------
.. [1] Jüttner, Alpár & Madarasi, Péter. (2018). "VF2++—An improved subgraph
   isomorphism algorithm". Discrete Applied Mathematics. 242.
   https://doi.org/10.1016/j.dam.2018.02.018

"""

import collections
import operator

import networkx as nx

__all__ = [
    "vf2pp_isomorphism",
    "vf2pp_is_isomorphic",
    "vf2pp_all_isomorphisms",
    "vf2pp_subgraph_isomorphism",
    "vf2pp_is_subgraph_isomorphic",
    "vf2pp_all_subgraph_isomorphisms",
    "vf2pp_monomorphism",
    "vf2pp_is_monomorphic",
    "vf2pp_all_monomorphisms",
]

_GraphInfo = collections.namedtuple(
    "_GraphInfo",
    [
        "SG_fits",  # function to check if SG fits in FG for subgraph(or not) PT
        "MONO_fits",  # function to check if SG fits in FG for monomorphism(or not) PT
        "directed",
        "SG",
        "FG",
        "SG_labels",
        "FG_labels",
        "SG_degree",
        "FG_degree",
        "FG_by_label",
    ],
)

_StateInfo = collections.namedtuple(
    "_StateInfo",
    [
        "mapping",
        "rev_map",
        "T1",  # border_outgoing unmapped nodes connected from SG mapped nodes
        "T1_in",  # border_incoming of unmapped nodes connected from SG mapped nodes
        "T1_tilde",  # wilds (not mapped or on border)
        "T2",  # border_out of mapping in FG
        "T2_in",  # border_in of mapping in FG
        "T2_tilde",  # wilds (unseen nodes) in FG
    ],
)


@nx._dispatchable(graphs={"FG": 0, "SG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_isomorphism(FG, SG, node_label=None, default_label=None):
    """Return an isomorphic mapping between `SG` and `FG` if it exists.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
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
        mapping = next(_all_morphisms(FG, SG, node_label, default_label, PT="ISO"))
        return mapping
    except StopIteration:
        return None


@nx._dispatchable(graphs={"SG": 0, "FG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_is_isomorphic(FG, SG, node_label=None, default_label=None):
    """Examines whether SG and FG are isomorphic.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
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
    try:
        next(_all_morphisms(FG, SG, node_label, default_label, PT="ISO"))
        return True
    except StopIteration:
        return False


@nx._dispatchable(graphs={"FG": 0, "SG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_all_isomorphisms(FG, SG, node_label=None, default_label=None):
    """Yields all the possible mappings between SG and FG.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
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
        Isomorphic mapping between the nodes in `SG` and `FG`.
    """
    yield from _all_morphisms(FG, SG, node_label, default_label, PT="ISO")


@nx._dispatchable(graphs={"FG": 0, "SG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_subgraph_isomorphism(FG, SG, node_label=None, default_label=None):
    """Return an isomorphic mapping between nodes of `SG` and `FG` if it exists.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
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
        Isomorphism mapping nodes of one graph to nodes of the other.
        If not subgraph isomorphic, return None.
    """
    try:
        mapping = next(_all_morphisms(FG, SG, node_label, default_label, PT="IND"))
        return mapping
    except StopIteration:
        return None


@nx._dispatchable(graphs={"FG": 0, "SG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_is_subgraph_isomorphic(FG, SG, node_label=None, default_label=None):
    """Examines whether SG and FG are isomorphic.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
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
    try:
        next(_all_morphisms(FG, SG, node_label, default_label, PT="IND"))
        return True
    except StopIteration:
        return False


@nx._dispatchable(graphs={"FG": 0, "SG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_all_subgraph_isomorphisms(FG, SG, node_label=None, default_label=None):
    """Yields all the possible subgraph isomorphisms between SG and FG.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
        The two graphs to check for subgraph isomorphisms.

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
        Subgraph isomorphisms mapping the nodes in `SG` to nodes in `FG`.
    """
    yield from _all_morphisms(FG, SG, node_label, default_label, PT="IND")


@nx._dispatchable(graphs={"FG": 0, "SG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_monomorphism(FG, SG, node_label=None, default_label=None):
    """Return a monomorphic mapping between `SG` and `FG` if it exists.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
        The two graphs to check for monomorphism.

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
        mapping = next(_all_morphisms(FG, SG, node_label, default_label, PT="MONO"))
        return mapping
    except StopIteration:
        return None


@nx._dispatchable(graphs={"FG": 0, "SG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_is_monomorphic(FG, SG, node_label=None, default_label=None):
    """Examines whether SG and FG are monomorphic.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
        The two graphs to check for monomorphism.

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
        True if the two graphs are monomorphic, False otherwise.
    """
    try:
        next(_all_morphisms(FG, SG, node_label, default_label, PT="MONO"))
        return True
    except StopIteration:
        return False


@nx._dispatchable(graphs={"FG": 0, "SG": 1}, node_attrs={"node_label": "default_label"})
def vf2pp_all_monomorphisms(FG, SG, node_label=None, default_label=None):
    """Yields all the possible monomorphisms between nodes of SG and FG.

    A monomorphism means that edges between two nodes in SG must connect the
    image nodes of those two nodes in FG, but that edges in FG do not have
    to have pre-image edges in SG. The mapping is injective not bijective.
    The mapped nodes have to maintain the SG connections, but not the SG
    disconnections. Maintaining edges and non-edges is provided by the
    subgraph isomorphism functions.

    Parameters
    ----------
    FG, SG : NetworkX Graph or MultiGraph instances.
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
        Isomorphic mapping between the nodes in `SG` and `FG`.
    """
    yield from _all_morphisms(FG, SG, node_label, default_label, PT="MONO")


def _all_morphisms(FG, SG, node_label, default_label, PT):
    N1, N2 = len(SG), len(FG)
    if N1 == 0 or N2 == 0:
        return False

    directed = SG.is_directed()
    if directed != FG.is_directed():
        raise nx.NetworkXError("SG and FG must have the same directedness")

    if directed:
        find_candidates = _find_candidates_Di
        restore_Tinout = _restore_Tinout_Di
    else:
        find_candidates = _find_candidates
        restore_Tinout = _restore_Tinout

    # Cache needed info about degree labels and problem type (PT)
    graph_info, state_info = _init_info(FG, SG, node_label, default_label, PT)
    SG_fits, _, _, _, _, SG_labels, FG_labels, _, _, FG_by_label = graph_info

    if not SG_fits(N1, N2):
        print(f"failed by number_of_nodes: {N1=} {N2=} {SG_fits=}")
        return False

    # Not Part of VF2++.  Maybe include in another alg.
    #    if PT == "ISO":
    #        # For ISO Check that both graphs have the same degree sequence
    #        deg_seq1, deg_seq2 = sorted(SG_degree.values()), sorted(FG_degree.values())
    #        if deg_seq1 != deg_seq2:
    #            return False
    #    else:
    #        # it is harder to check the degree sequence for PT in "IND", "MONO". Let's not.
    #        pass

    # precheck label properties:
    # Check if SG and FG have the same labels, and check that the
    # number of nodes per label fits between the two graphs
    SG_by_label = nx.utils.groups(SG_labels)
    if any(
        label not in SG_by_label or not SG_fits(len(SG_by_label[label]), len(nodes))
        for label, nodes in FG_by_label.items()
    ):
        print("failed by labels")
        return False

    # Calculate the optimal node ordering
    node_order = _matching_order(graph_info)
    order_index = {node: i for i, node in enumerate(node_order)}
    start_node = node_order[0]
    args = (graph_info, state_info)

    # Initialize the stack
    stack = [(start_node, iter(find_candidates(start_node, *args)))]

    mapping = state_info.mapping
    rev_map = state_info.rev_map

    # Index of the node from the order, currently being examined
    node_number = 0

    while stack:
        current_node, candidate_iter = stack[-1]

        try:
            candidate = next(candidate_iter)
        except StopIteration:
            # No more candidates. Can we throw out this node and still get a morphism?
            if N1 - N2 > node_number - len(mapping):
                node_number += 1
                node = node_order[node_number]
                stack[-1] = (node, iter(find_candidates(node, *args)))
                continue
            # No new nodes to try. We must backtrack and try a new branch
            stack.pop()
            if stack:
                # Go to previous node and update state
                node = stack[-1][0]
                node_number = order_index[node]

                cand = mapping[node]
                mapping.pop(node)
                rev_map.pop(cand)
                restore_Tinout(node, cand, graph_info, state_info)
                continue
            return

        if _feasibility(current_node, candidate, graph_info, state_info):
            # Yield mapping if extended to all SG
            if len(mapping) == SG.number_of_nodes() - 1:
                cp_mapping = mapping.copy()
                cp_mapping[current_node] = candidate
                yield cp_mapping
                continue

            # Feasibility rules pass, so extend the mapping and update Tinout
            mapping[current_node] = candidate
            rev_map[candidate] = current_node
            _update_Tinout(current_node, candidate, graph_info, state_info)
            # Append the next node and its candidates to the stack
            node_number += 1
            node = node_order[node_number]
            tmp = find_candidates(node, *args)
            stack.append((node, iter(tmp)))
            continue


def _init_info(FG, SG, node_label, default_label, PT):
    SG_fits = operator.eq if PT == "ISO" else operator.le
    MONO_fits = operator.eq if PT != "MONO" else operator.le
    directed = SG.is_directed()

    # Create the labels dicts based on node_label and default_label
    SG_labels = dict(SG.nodes(data=node_label, default=default_label))
    FG_labels = dict(FG.nodes(data=node_label, default=default_label))
    FG_by_label = nx.utils.groups(FG_labels)

    # Create the degree dicts based on graph type
    if directed:
        SG_degree = {n: (i, o) for (n, i), (_, o) in zip(SG.in_degree, SG.out_degree)}
        FG_degree = {n: (i, o) for (n, i), (_, o) in zip(FG.in_degree, FG.out_degree)}
    else:
        SG_degree = dict(SG.degree)
        FG_degree = dict(FG.degree)

    graph_info = _GraphInfo(
        SG_fits,
        MONO_fits,
        directed,
        FG,
        SG,
        SG_labels,
        FG_labels,
        SG_degree,
        FG_degree,
        FG_by_label,
    )

    mapping, rev_mapping = {}, {}
    T1, T1_in = set(), set()
    T2, T2_in = set(), set()
    T1_tilde = set(SG.nodes())
    T2_tilde = set(FG.nodes())

    state_info = _StateInfo(
        mapping, rev_mapping, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde
    )

    return graph_info, state_info


def _matching_order(graph_info):
    """The node ordering as introduced in VF2++.

    Notes
    -----
    Taking into account the structure of the Graph and the node labeling, the
    nodes are placed in an order such that, most of the unfruitful/infeasible
    branches of the search space can be pruned on high levels, significantly
    decreasing the number of visited states. The premise is that, the algorithm
    will be able to recognize inconsistencies early, proceeding to go deep into
    the search tree only if it's needed.

    Returns
    -------
    node_order: list
        The ordering of the nodes.
    """
    _, _, directed, FG, SG, SG_labels, _, _, _, nodes_of_FGLabels = graph_info

    if directed:
        SG = SG.to_undirected(as_view=True)

    V1_unordered = set(SG.nodes())
    label_rarity = {label: len(nodes) for label, nodes in nodes_of_FGLabels.items()}
    used_degrees = {node: 0 for node in SG}
    node_order = []

    while V1_unordered:
        max_rarity = min(label_rarity[SG_labels[x]] for x in V1_unordered)
        rarest_nodes = [
            n for n in V1_unordered if label_rarity[SG_labels[n]] == max_rarity
        ]
        max_node = max(rarest_nodes, key=SG.degree.__getitem__)

        for dlevel_nodes in nx.bfs_layers(SG, max_node):
            nodes_to_add = dlevel_nodes.copy()
            while nodes_to_add:
                max_used_degree = max(used_degrees[n] for n in nodes_to_add)
                max_used_degree_nodes = [
                    n for n in nodes_to_add if used_degrees[n] == max_used_degree
                ]
                max_degree = max(SG.degree[n] for n in max_used_degree_nodes)
                max_degree_nodes = [
                    n for n in max_used_degree_nodes if SG.degree[n] == max_degree
                ]
                next_node = min(
                    max_degree_nodes, key=lambda x: label_rarity[SG_labels[x]]
                )

                node_order.append(next_node)
                for node in SG.neighbors(next_node):
                    used_degrees[node] += 1

                nodes_to_add.remove(next_node)
                label_rarity[SG_labels[next_node]] -= 1
                V1_unordered.discard(next_node)

    return node_order


def _find_candidates(u, graph_info, state_info):
    """Given node u of SG, finds the candidates of u from FG."""
    # TODO: move checks that don't depend on state to _init_info and store in
    # dict keyed by node to sets of cands based solely on label/degree/loop
    # Then find_candidate shrinks this for any rules determined by the mapping
    # state. That is syntatic feasibility. This moves "CUT" into find_candidates.
    # The point is: why put more candidates on the stack if we can test them here?
    SG_fits, MONO_fits, _, FG, SG, SG_lbls, _, SG_deg, FG_deg, FG_by_label = graph_info
    mapping, rev_map, _, _, _, _, _, T2_tilde = state_info
    u_label, u_deg, u_loops = SG_lbls[u], SG_deg[u], SG.number_of_edges(u, u)

    covered_nbrs = [nbr for nbr in SG[u] if nbr in mapping]
    if covered_nbrs:
        # cands = FG_by_label[u_label].difference(rev_map)
        nbr = covered_nbrs[0]
        cands = FG._adj[mapping[nbr]].keys() & FG_by_label[u_label]
        cands -= rev_map.keys()

        for nbr in covered_nbrs[1:]:
            cands.intersection_update(FG._adj[mapping[nbr]])

        result = {
            n
            for n in cands
            if MONO_fits(u_loops, FG.number_of_edges(n, n))
            if SG_fits(u_deg, FG_deg[n])
        }
        # if no cands, return for ISO or IND, but for MONO go on as if no covered nbrs
        if result or MONO_fits == operator.eq:
            return result

    # covered nbrs don't give any candidates. Look at uncovered nbrs
    cands = {v for v in FG_by_label[u_label] if SG_fits(u_deg, FG_deg[v])}
    if MONO_fits == operator.eq:
        cands.intersection_update(T2_tilde)
    else:
        cands.difference_update(rev_map)
    result = {n for n in cands if MONO_fits(u_loops, FG.number_of_edges(n, n))}
    return result


def _find_candidates_Di(u, graph_info, state_info):
    SG_fits, MONO_fits, _, FG, SG, SG_lbls, _, SG_deg, FG_deg, FG_by_label = graph_info
    mapping, rev_map, _, _, _, _, _, T2_tilde = state_info
    u_label, u_deg, u_loops = SG_lbls[u], SG_deg[u], SG.number_of_edges(u, u)

    covered_successors = [succ for succ in SG[u] if succ in mapping]
    covered_predecessors = [pred for pred in SG.pred[u] if pred in mapping]

    if covered_successors or covered_predecessors:
        if covered_successors:
            succ = covered_successors[0]
            cands = FG._pred[mapping[succ]].keys() - rev_map.keys()

            for succ in covered_successors[1:]:
                cands.intersection_update(FG._pred[mapping[succ]])
        else:
            pred = covered_predecessors.pop()
            cands = set(FG._adj[mapping[pred]])
            cands.difference_update(rev_map)

        for pred in covered_predecessors:
            cands.intersection_update(FG._adj[mapping[pred]])

        cands.intersection_update(FG_by_label[u_label])
        result = {
            v
            for v in cands
            if MONO_fits(u_loops, FG.number_of_edges(v, v))
            if all(SG_fits(ud, vd) for ud, vd in zip(u_deg, FG_deg[v]))
        }
        # if no cands, return for ISO or IND, but for MONO go on as if no covered nbrs
        if result or MONO_fits == operator.eq:
            return result

    # covered nbrs don't give any candidates. Look at uncovered nbrs
    cands = set(FG_by_label[u_label])
    if MONO_fits == operator.eq:
        cands.intersection_update(T2_tilde)
    else:
        cands.difference_update(rev_map)
    result = {
        n
        for n in cands
        if MONO_fits(u_loops, FG.number_of_edges(n, n))
        if all(SG_fits(*ds) for ds in zip(u_deg, FG_deg[n]))
    }
    return result


def _feasibility(node1, node2, graph_info, state_info):
    """Given a candidate pair of nodes u and v from SG and FG respectively,
    checks if it's feasible to extend the mapping, i.e. if u and v can be matched.

    Notes
    -----
    This function performs all the necessary checking by applying both consistency
    and cutting rules.
    """
    SG = graph_info.SG

    # does this node pair follow the rules of morphism PT
    if not _feasible_node_pair(node1, node2, graph_info, state_info):
        return False

    # if we look ahead to the next nodes mapped will this fail then?
    if not _feasible_look_ahead(node1, node2, graph_info, state_info):
        return False

    return True


def _feasible_look_ahead(u, v, graph_info, state_info):
    SG_fits, MONO_fits, directed, FG, SG, SG_labels, FG_labels, _, _, _ = graph_info
    _, _, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde = state_info
    multigraph = SG.is_multigraph() or FG.is_multigraph()

    unbrs, vnbrs = SG._adj[u], FG._adj[v]
    u_labels_successors = nx.utils.groups({nbr: SG_labels[nbr] for nbr in unbrs})
    v_labels_successors = nx.utils.groups({nbr: FG_labels[nbr] for nbr in vnbrs})

    if not SG_fits(u_labels_successors.keys(), v_labels_successors.keys()):
        return False

    if directed:
        upreds, vpreds = SG._pred[u], FG._pred[v]
        u_labels_predecessors = nx.utils.groups({n1: SG_labels[n1] for n1 in upreds})
        v_labels_predecessors = nx.utils.groups({n2: FG_labels[n2] for n2 in vpreds})

        # check matching pred labels before looping over individual successors
        if not SG_fits(u_labels_predecessors.keys(), v_labels_predecessors.keys()):
            return False

    if v_labels_successors:
        for label, unbrs in u_labels_successors.items():
            vnbrs = v_labels_successors[label]

            if multigraph:
                # Check multiedges to ensure enough edges in G to fit SG
                # use sorted edge counts. cut if len_G < len(SG) for any count-pair
                ucnts = sorted((SG.number_of_edges(u, x) for x in unbrs), reverse=True)
                vcnts = sorted((FG.number_of_edges(v, x) for x in vnbrs), reverse=True)
                if any(not MONO_fits(uc, vc) for uc, vc in zip(ucnts, vcnts)):
                    return False
            if not SG_fits(len(T1 & unbrs), len(T2 & vnbrs)):
                return False
            if directed and not SG_fits(len(T1_in & unbrs), len(T2_in & vnbrs)):
                return False
            if MONO_fits is not operator.le:  # Only check if PT is not MONO
                if not SG_fits(len(T1_tilde & unbrs), len(T2_tilde & vnbrs)):
                    return False
    if not directed:
        return True

    # same for predecessors
    if v_labels_predecessors:
        for label, upred in u_labels_predecessors.items():
            vpred = v_labels_predecessors[label]

            if multigraph:
                ucnts = sorted((SG.number_of_edges(u, x) for x in upred), reverse=True)
                vcnts = sorted((FG.number_of_edges(v, x) for x in vpred), reverse=True)
                mess = [(uc, vc) for uc, vc in zip(ucnts, vcnts)]
                if any(not MONO_fits(uc, vc) for uc, vc in zip(ucnts, vcnts)):
                    return False
            if not SG_fits(len(T1 & upred), len(T2 & vpred)):
                return False
            if directed and not SG_fits(len(T1_in & upred), len(T2_in & vpred)):
                return False
            if MONO_fits is not operator.le:  # Only check if PT is not MONO
                if not SG_fits(len(T1_tilde & upred), len(T2_tilde & vpred)):
                    return False
    return True


def _feasible_node_pair(u, v, graph_info, state_info):
    _, MONO_op, directed, FG, SG, *_ = graph_info
    mapping, rev_map = state_info.mapping, state_info.rev_map
    multigraph = SG.is_multigraph() or FG.is_multigraph()
    unbrs, vnbrs = SG._adj[u], FG._adj[v]
    if directed:
        upreds, vpreds = SG._pred[u], FG._pred[v]

    if not multigraph:
        if any(mapping[n] not in vnbrs for n in unbrs if n in mapping):
            return False
        if MONO_op == operator.eq:
            if any(rev_map[n] not in unbrs for n in vnbrs if n in rev_map):
                return False

        if not directed:
            return True

        if any(mapping[n] not in vpreds for n in upreds if n in mapping):
            return False
        if MONO_op == operator.eq:
            if any(rev_map[n] not in upreds for n in vpreds if n in rev_map):
                return False
        return True

    else:
        SGne, FGne = SG.number_of_edges, FG.number_of_edges
        if not all(
            MONO_op(SGne(u, n), FGne(v, mapping[n])) for n in unbrs if n in mapping
        ):
            return False
        if MONO_op == operator.eq:
            if not all(
                MONO_op(SGne(u, rev_map[n]), FGne(v, n)) for n in vnbrs if n in rev_map
            ):
                return False

        if not directed:
            return True

        if not all(
            MONO_op(SGne(n, u), FGne(mapping[n], v)) for n in upreds if n in mapping
        ):
            return False
        if MONO_op == operator.eq:
            if any(SGne(rev_map[n], u) != FGne(n, v) for n in vpreds if n in rev_map):
                return False
        return True


def _update_Tinout(new_node1, new_node2, graph_info, state_info):
    """Updates the Ti/Ti_out (i=1,2) when a new node pair u-v is added to the mapping.

    Notes
    -----
    This function should be called right after the feasibility checks are passed,
    and node1 is mapped to node2. The purpose of this function is to avoid brute
    force computing of Ti/Ti_out by iterating over all nodes of the graph and
    checking which nodes satisfy the necessary conditions. Instead, in every step
    of the algorithm we focus exclusively on the two nodes that are being added
    to the mapping, incrementally updating Ti/Ti_out.
    """
    _, _, directed, FG, SG, *_ = graph_info
    mapping, rev_mapping, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde = state_info

    uncovered_successors_SG = {s for s in SG[new_node1] if s not in mapping}
    uncovered_successors_FG = {s for s in FG[new_node2] if s not in rev_mapping}

    # Add the uncovered neighbors of node1 and node2 in T1 and T2 respectively
    T1.update(uncovered_successors_SG)
    T2.update(uncovered_successors_FG)
    T1.discard(new_node1)
    T2.discard(new_node2)

    T1_tilde.difference_update(uncovered_successors_SG)
    T2_tilde.difference_update(uncovered_successors_FG)
    T1_tilde.discard(new_node1)
    T2_tilde.discard(new_node2)

    if not directed:
        return

    uncovered_preds_SG = {p for p in SG.pred[new_node1] if p not in mapping}
    uncovered_preds_FG = {p for p in FG.pred[new_node2] if p not in rev_mapping}

    T1_in.update(uncovered_preds_SG)
    T2_in.update(uncovered_preds_FG)
    T1_in.discard(new_node1)
    T2_in.discard(new_node2)

    T1_tilde.difference_update(uncovered_preds_SG)
    T2_tilde.difference_update(uncovered_preds_FG)
    T1_tilde.discard(new_node1)
    T2_tilde.discard(new_node2)


def _restore_Tinout(popped_node1, popped_node2, graph_info, state_info):
    """Restores the previous version of Ti/Ti_out when a node pair is deleted
    from the mapping.
    """
    # If node to remove from the mapping has >=1 covered neighbor, add it to T1
    _, _, directed, FG, SG, *_ = graph_info
    mapping, rev_map, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde = state_info

    is_added = False
    for neighbor in SG[popped_node1]:
        if neighbor in mapping:
            # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
            is_added = True
            T1.add(popped_node1)
        else:
            # check if its neighbor has another connection with a covered node.
            # If not, only then exclude it from T1
            if any(nbr in mapping for nbr in SG[neighbor]):
                continue
            T1.discard(neighbor)
            T1_tilde.add(neighbor)

    # Case where the node is not present in neither the mapping nor T1.
    # By definition, it should belong to T1_tilde
    if not is_added:
        T1_tilde.add(popped_node1)

    is_added = False
    for neighbor in FG[popped_node2]:
        if neighbor in rev_map:
            is_added = True
            T2.add(popped_node2)
        else:
            if any(nbr in rev_map for nbr in FG[neighbor]):
                continue
            T2.discard(neighbor)
            T2_tilde.add(neighbor)

    if not is_added:
        T2_tilde.add(popped_node2)


def _restore_Tinout_Di(popped_node1, popped_node2, graph_info, state_info):
    # If the node to remove from the mapping has >=1 covered neighbor, add it to T1.
    _, _, directed, FG, SG, *_ = graph_info
    mapping, rev_map, T1, T1_in, T1_tilde, T2, T2_in, T2_tilde = state_info

    is_added = False
    for successor in SG[popped_node1]:
        if successor in mapping:
            # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
            is_added = True
            T1_in.add(popped_node1)
        else:
            # check if its neighbor has another connection with a covered node.
            # If not, only then exclude it from T1
            if not any(pred in mapping for pred in SG.pred[successor]):
                T1.discard(successor)

            if not any(succ in mapping for succ in SG[successor]):
                T1_in.discard(successor)

            if successor not in T1:
                if successor not in T1_in:
                    T1_tilde.add(successor)

    for predecessor in SG.pred[popped_node1]:
        if predecessor in mapping:
            # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
            is_added = True
            T1.add(popped_node1)
        else:
            # check if its neighbor has another connection with a covered node.
            # If not, only then exclude it from T1
            if not any(pred in mapping for pred in SG.pred[predecessor]):
                T1.discard(predecessor)

            if not any(succ in mapping for succ in SG[predecessor]):
                T1_in.discard(predecessor)

            if not (predecessor in T1 or predecessor in T1_in):
                T1_tilde.add(predecessor)

    # Case where the node is not present in neither the mapping nor T1.
    # By definition it should belong to T1_tilde
    if not is_added:
        T1_tilde.add(popped_node1)

    is_added = False
    for successor in FG[popped_node2]:
        if successor in rev_map:
            is_added = True
            T2_in.add(popped_node2)
        else:
            if not any(pred in rev_map for pred in FG.pred[successor]):
                T2.discard(successor)

            if not any(succ in rev_map for succ in FG[successor]):
                T2_in.discard(successor)

            if successor not in T2:
                if successor not in T2_in:
                    T2_tilde.add(successor)

    for predecessor in FG.pred[popped_node2]:
        if predecessor in rev_map:
            # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
            is_added = True
            T2.add(popped_node2)
        else:
            # check if its neighbor has another connection with a covered node.
            # If not, only then exclude it from T1
            if not any(pred in rev_map for pred in FG.pred[predecessor]):
                T2.discard(predecessor)

            if not any(succ in rev_map for succ in FG[predecessor]):
                T2_in.discard(predecessor)

            if not (predecessor in T2 or predecessor in T2_in):
                T2_tilde.add(predecessor)

    if not is_added:
        T2_tilde.add(popped_node2)
