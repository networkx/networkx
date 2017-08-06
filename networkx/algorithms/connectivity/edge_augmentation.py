# -*- coding: utf-8 -*-
#    Copyright (C) 2004-2017 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Jon Crall (erotemic@gmail.com)
"""
Algorithms for finding k-edge-augmentations

A k-edge-augmentation is a set of edges, that once added to a graph, ensures
that the graph is k-edge-connected. Typically, the goal is to find the
augmentation with minimum weight. In general, it is not gaurenteed that a
k-edge-augmentation exists.
"""
import random
import itertools as it
import networkx as nx
from networkx.utils import not_implemented_for
from collections import defaultdict

__all__ = [
    'k_edge_augmentation',
    'is_k_edge_connected',
]


def _ordered(u, v):
    return (u, v) if u < v else (v, u)


def _group_items(items):
    """ for each key/val pair, appends val to the list specified by key """
    # Initialize a dict of lists
    groupid_to_items = defaultdict(list)
    # Insert each item into the correct group
    for groupid, item in items:
        groupid_to_items[groupid].append(item)
    return groupid_to_items


@not_implemented_for('multigraph')
def is_k_edge_connected(G, k):
    """
    Tests to see if a graph is k-edge-connected
    """
    if k < 1:
        raise ValueError('k must be positive, not {}'.format(k))
    # First try to quickly determine if G is not k-edge-connected
    if G.number_of_nodes() < k + 1:
        return False
    elif min(d for n, d in G.degree()) < k:
        return False
    else:
        # Otherwise perform the full check
        if k == 1:
            return nx.is_connected(G)
        elif k == 2:
            return not nx.has_bridges(G)
        else:
            return nx.edge_connectivity(G) >= k


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def k_edge_augmentation(G, k, avail=None, weight=None, partial=False):
    """Finds set of edges to k-edge-connect G.

    This function uses the most efficient function available (depending on the
    value of k and if the problem is weighted or unweighted) to search for a
    minimum weight subset of available edges that k-edge-connects G.
    In general, finding a k-edge-augmentation is NP-hard, so solutions are not
    garuenteed to be minimal.


    Parameters
    ----------
    G : NetworkX graph

    k : Integer
        Desired edge connectivity

    avail : set 2 or 3 tuples
        The available edges that can be used in the augmentation.

        If unspecified, then all edges in the complement of G are available.
        Otherwise, each item is an available edge (with an optinal weight).

        In the unweighted case, each item is an edge ``(u, v)``.

        In the weighted case, each item is a 3-tuple ``(u, v, d)``.
        The third item, ``d``, can be a dictionary or a real number.
        If ``d`` is a dictionary ``d[weight]`` correspondings to the weight.

    weight : string
        key to use to find weights if avail is a set of 3-tuples where the
        third item in each tuple is a dictionary.

    partial : Boolean
        If partial is True and no feasible k-edge-augmentation exists, then all
        available edges are returned.

    Returns
    -------
    aug_edges : a generator of edges. If these edges are added to G, then
        the G would become k-edge-connected. If partial is False, an error
        is raised if this is not possible. Otherwise, all available edges
        are generated.

    Notes
    -----
    When k=1 this returns an optimal solution.

    When k=2 and avail is None, this returns an optimal solution.
    Otherwise when k=2, this returns a 2-approximation of the optimal solution.

    For k>3, this problem is NP-hard and this uses a randomized algorithm that
        produces a feasible solution, but provides no gaurentees on the
        solution weight.

    Example
    -------
    >>> # Unweighted cases
    >>> G = nx.path_graph((1, 2, 3, 4))
    >>> G.add_node(5)
    >>> list(k_edge_augmentation(G, k=1))
    [(1, 5)]
    >>> list(k_edge_augmentation(G, k=2))
    [(4, 5), (1, 5)]
    >>> list(k_edge_augmentation(G, k=3))
    [(4, 5), (1, 4), (3, 1), (5, 1), (5, 2)]
    >>> complement = list(k_edge_augmentation(G, k=5, partial=True))
    >>> G.add_edges_from(complement)
    >>> nx.edge_connectivity(G)
    4

    Example
    -------
    >>> # Weighted cases
    >>> G = nx.path_graph((1, 2, 3, 4))
    >>> G.add_node(5)
    >>> avail = [(1, 5, {'weight': 11}), (2, 5, {'weight': 10})]
    >>> list(k_edge_augmentation(G, k=1, avail=avail, weight='weight'))
    [(2, 5)]
    >>> avail = [(1, 5, 11), (2, 5, 10), (4, 3, 1), (4, 5, 51)]
    >>> list(k_edge_augmentation(G, k=2, avail=avail, weight='weight'))

    >>> aug = list(k_edge_augmentation(G, k=2, avail=avail, weight='weight'))
    >>> G2 = G.copy()
    >>> G2.add_edges_from(aug)
    >>> nx.edge_connectivity(G2)
    [(4, 5), (1, 5)]
    >>> list(k_edge_augmentation(G, k=3))
    [(4, 5), (1, 4), (3, 1), (5, 1), (5, 2)]
    >>> complement = list(k_edge_augmentation(G, k=5, partial=True))
    >>> G.add_edges_from(complement)
    >>> nx.edge_connectivity(G)
    4
    """
    try:
        if k <= 0:
            raise ValueError('k must be a positive integer, not {}'.format(k))
        elif G.number_of_nodes() < k + 1:
            raise nx.NetworkXUnfeasible(
                ('impossible to {} connect in graph with less than {} '
                 'nodes').format(k, k + 1))
        elif avail is not None and len(avail) == 0:
            if not nx.is_k_edge_connected(G, k):
                raise nx.NetworkXUnfeasible('no available edges')
        elif k == 1:
            aug_edges = one_edge_augmentation(G, avail=avail, weight=weight)
        elif k == 2:
            aug_edges = bridge_augmentation(G, avail=avail, weight=weight)
        else:
            aug_edges = randomized_k_edge_augmentation(
                G, k=k, avail=avail, partial=partial, seed=0)
            # raise NotImplementedError('not implemented for k>2. k={}'.format(k))
    except nx.NetworkXUnfeasible:
        if partial:
            # Return all available edges
            if avail is None:
                aug_edges = complement_edges(G)
            else:
                aug_edges = (t[0:2] for t in avail)
        else:
            raise
    return aug_edges


def _unpack_available_edges(avail, weight=None):
    """Helper to separate avail into edges and corresponding weights """
    if weight is None:
        weight = 'weight'
    avail_uv = [tup[0:2] for tup in avail]
    def _try_getitem(d):
        try:
            return d[weight]
        except TypeError:
            return d
    avail_w = [1 if len(tup) == 2 else _try_getitem(tup[-1]) for tup in avail]
    return avail_uv, avail_w


@not_implemented_for('multigraph')
@not_implemented_for('directed')
def one_edge_augmentation(G, avail=None, weight=None, partial=False):
    """Finds minimum weight set of edges to connect G.

    Notes
    -----
    Uses either :func:`unconstrained_one_edge_augmentation` or
    :func:`weighted_one_edge_augmentation` depending on whether ``avail`` is
    specified. Both algorithms are based on finding a minimum spanning tree.
    As such both algorithms find optimal solutions and run in linear time.
    """
    if avail is None:
        return unconstrained_one_edge_augmentation(G)
    else:
        return weighted_one_edge_augmentation(G, avail=avail, weight=weight,
                                              partial=partial)


def unconstrained_one_edge_augmentation(G):
    """Finds the smallest set of edges to connect G.

    This is a variant of the unweighted MST problem.
    If G is not empty, a feasible solution always exists.

    Example
    -------
    >>> G = nx.Graph([(1, 2), (2, 3), (4, 5)])
    >>> G.add_nodes_from([6, 7, 8])
    >>> list(unconstrained_one_edge_augmentation(G))
    [(1, 4), (4, 6), (6, 7), (7, 8)]
    """
    ccs1 = list(nx.connected_components(G))
    C = collapse(G, ccs1)
    # When we are not constrained, we can just make a meta graph tree.
    meta_nodes = list(C.nodes())
    # build a path in the metagraph
    meta_aug = list(zip(meta_nodes, meta_nodes[1:]))
    # map that path to the original graph
    # inverse = ut.group_pairs(C.graph['mapping'].items())
    inverse = _group_items(map(reversed, C.graph['mapping'].items()))
    for mu, mv in meta_aug:
        yield (inverse[mu][0], inverse[mv][0])


def weighted_one_edge_augmentation(G, avail, weight=None, partial=False):
    """Finds the minimum weight set of edges to connect G if one exists.

    This is a variant of the weighted MST problem.

    Example
    -------
    >>> G = nx.Graph([(1, 2), (2, 3), (4, 5)])
    >>> G.add_nodes_from([6, 7, 8])
    >>> # any edge not in avail has an implicit weight of infinity
    >>> avail = [(1, 3), (1, 5), (4, 7), (4, 8), (6, 1), (8, 1), (8, 2)]
    >>> list(weighted_one_edge_augmentation(G, avail))
    [(1, 5), (6, 1), (4, 7), (4, 8)]
    >>> # find another solution by giving large weights to edges in the
    >>> # previous solution
    >>> avail = [(1, 3), (1, 5, 99), (4, 7, 99), (6, 1, 99), (8, 1), (8, 2)]
    >>> list(weighted_one_edge_augmentation(G, avail))
    [(8, 1), (1, 5), (6, 1), (4, 7)]
    """
    ccs1 = list(nx.connected_components(G))

    avail_uv, avail_w = _unpack_available_edges(avail, weight)
    avail_uvw = list(zip(avail_uv, avail_w))

    # Find an MST of the metagraph instead of the original graph
    C = collapse(G, ccs1)
    mapping = C.graph['mapping']

    avail_uv, avail_w = _unpack_available_edges(avail, weight)
    mapped_avail = [(mapping[u], mapping[v]) for u, v in avail_uv]

    # only need exactly 1 edge at most between each CC, so choose lightest
    avail_uvw = zip(avail_uv, avail_w)
    grouped_uvw = _group_items(zip(mapped_avail, avail_uvw))
    candidates = []
    for meta_edge, choices in grouped_uvw.items():
        edge, w = min(choices, key=lambda t: t[1])
        candidates.append((meta_edge, edge, w))
    candidates = sorted(candidates, key=lambda t: t[2])

    # kruskals algorithm on metagraph to find the best connecting edges
    subtrees = nx.utils.UnionFind()
    for (mu, mv), (u, v), w in candidates:
        if subtrees[mu] != subtrees[mv]:
            yield (u, v)
        subtrees.union(mu, mv)
        if not partial:
            C.add_edge(mu, mv)

    if not partial and not nx.is_connected(C):
        raise nx.NetworkXUnfeasible(
            'Not possible to connect G with available edges')
    # This commented implementation re-uses the mst algorithm, but the above
    # algorithm is slightly more efficient.
    # G2 = G.copy()
    # nx.set_edge_attributes(G2, name='weight', values=0)
    # G2.add_edges_from([
    #     (u, v, {'weight': w}) for (u, v), w in zip(avail_uv, avail_w)])
    # mst = nx.minimum_spanning_tree(G2)
    # if not nx.is_connected(mst):
    #     raise nx.NetworkXUnfeasible(
    #         'Not possible to connect G with available edges')
    # for u, v in avail_uv:
    #     if mst.has_edge(u, v):
    #         yield (u, v)


@not_implemented_for('multigraph')
@not_implemented_for('directed')
def bridge_augmentation(G, avail=None, weight=None):
    """Finds the a set of edges that bridge connects G.

    Adding these edges to G will make it 2-edge-connected.
    If no constraints are specified the returned set of edges is minimum an
    optimal, otherwise the solution is approximated.

    Notes
    -----
    If there are no constraints the solution can be computed in linear time
    using :func:`unconstrained_bridge_augmentation`. Otherwise, the problem
    becomes NP-hard and is the solution is approximated by
    :func:`weighted_bridge_augmentation`.
    """
    if G.number_of_nodes() < 3:
        raise nx.NetworkXUnfeasible(
            'impossible to bridge connect less than 3 nodes')
    if avail is None:
        return unconstrained_bridge_augmentation(G)
    else:
        return weighted_bridge_augmentation(G, avail, weight=weight)


def unconstrained_bridge_augmentation(G):
    """Finds an optimal 2-edge-augmentation of G using the fewest edges.

    This is an implementation of the algorithm detailed in [1]_.
    It chooses a set of edges from avail to add to G that renders it
    2-edge-connected if such a subset exists. This is done by finding a
    minimum spanning arborescence of a specially constructed metagraph.

    References
    ----------
    .. [1] Eswaran, Kapali P., and R. Endre Tarjan. (1975) Augmentation problems.
        http://epubs.siam.org/doi/abs/10.1137/0205044

    Example
    -------
    >>> G = nx.path_graph((1, 2, 3, 4, 5, 6, 7))
    >>> list(unconstrained_bridge_augmentation(G))
    [(1, 7)]
    """
    # find the 2-edge-connected components of G
    bridge_ccs = nx.connectivity.bridge_components(G)
    # condense G into an forest C
    C = collapse(G, bridge_ccs)
    # Connect each tree in the forest to construct an arborescence
    roots = [min(cc, key=C.degree) for cc in nx.connected_components(C)]
    forest_bridges = list(zip(roots, roots[1:]))
    C.add_edges_from(forest_bridges)
    # order the leaves of C by preorder
    leafs = [n for n in nx.dfs_preorder_nodes(C) if C.degree(n) == 1]
    # construct edges to bridge connect the tree
    tree_bridges = list(zip(leafs, leafs[1:]))
    # collect the edges used to augment the original forest
    aug_tree_edges = tree_bridges + forest_bridges

    # ensure that you choose a pair that does not yet exist
    inverse = _group_items(map(reversed, C.graph['mapping'].items()))
    # sort so we choose minimum degree nodes first
    inverse = {augu: sorted(mapped, key=lambda u: (G.degree(u), u))
               for augu, mapped in inverse.items()}
    for augu, augv in aug_tree_edges:
        # Find the first available edge that doesn't exist and return it
        for u, v in it.product(inverse[augu], inverse[augv]):
            if not G.has_edge(u, v):
                yield u, v
                break


def weighted_bridge_augmentation(G, avail, weight=None):
    """Finds an approximate min-weight 2-edge-augmentation of G.

    This is an implementation of the approximation algorithm detailed in [1]_.
    It chooses a set of edges from avail to add to G that renders it
    2-edge-connected if such a subset exists.  This is done by finding a
    minimum spanning arborescence of a specially constructed metagraph.

    Parameters
    ----------
    G : NetworkX graph

    avail : set of 2 or 3 tuples.
        candidate edges (with optional weights) to choose from

    weight : string
        key to use to find weights if avail is a set of 3-tuples where the
        third item in each tuple is a dictionary.

    Returns
    -------
    aug_edges (set): subset of avail chosen to augment G

    Notes
    -----
    Finding a weighted 2-edge-augmentation is NP-hard.
    Any edge not in ``avail`` is considered to have a weight of infinity.
    The approximation factor is 2 if ``G`` is connected and 3 if it is not.
    Runs in :math:`O(m + n log(n))` time

    References
    ----------
    .. [1] Khuller, Samir, and Ramakrishna Thurimella. (1993) Approximation
        algorithms for graph augmentation.
        http://www.sciencedirect.com/science/article/pii/S0196677483710102

    Example
    -------
    >>> G = nx.path_graph((1, 2, 3, 4))
    >>> # When the weights are equal, (1, 4) is the best
    >>> avail = [(1, 4, 1), (1, 3, 1), (2, 4, 1)]
    >>> list(weighted_bridge_augmentation(G, avail))
    [(1, 4)]
    >>> # Giving (1, 4) a high weight makes the two edge solution the best.
    >>> avail = [(1, 4, 1000), (1, 3, 1), (2, 4, 1)]
    >>> list(weighted_bridge_augmentation(G, avail))
    [(1, 3), (2, 4)]
    >>> #------
    >>> G = nx.path_graph((1, 2, 3, 4))
    >>> G.add_node(5)
    >>> avail = [(1, 5, 11), (2, 5, 10), (4, 3, 1), (4, 5, 1)]
    >>> list(weighted_bridge_augmentation(G, avail=avail))
    [(4, 5), (1, 5)]
    >>> #
    >>> avail = [(1, 5, 11), (2, 5, 10), (4, 3, 1), (4, 5, 51)]
    >>> list(weighted_bridge_augmentation(G, avail=avail))
    [(2, 5), (1, 5), (4, 5)]
    """

    if weight is None:
        weight = 'weight'

    # If input G is not connected the approximation factor increases to 3
    if not nx.is_connected(G):
        H = G.copy()
        connectors = list(one_edge_augmentation(H, avail=avail, weight=weight))
        H.add_edges_from(connectors)

        for u, v in connectors:
            yield (u, v)
    else:
        H = G

    # assert nx.is_connected(H), 'should have been one-connected'

    if len(avail) == 0:
        if list(nx.bridges(H)):
            raise nx.NetworkXUnfeasible('no augmentation possible')

    # Collapse input into a metagraph. Meta nodes are bridge-ccs
    bridge_ccs = nx.connectivity.bridge_components(H)
    C = collapse(H, bridge_ccs)

    avail_uv, avail_w = _unpack_available_edges(avail, weight)

    # Remove any edges previously used in the one-edge-augmentation
    flags = [(H.has_node(u) and H.has_node(v) and not H.has_edge(u, v))
             for u, v in avail_uv]
    avail_uv = list(it.compress(avail_uv, flags))
    avail_w = list(it.compress(avail_w, flags))
    avail_uvw = list(zip(avail_uv, avail_w))

    # Use the meta graph to filter out a small feasible subset of avail
    # Choose the minimum weight edge from each group.
    mapping = C.graph['mapping']
    mapped_avail = [(mapping[u], mapping[v]) for u, v in avail_uv]

    # Choose the minimum weight feasible edge in each group
    grouped_uvw = _group_items(zip(mapped_avail, avail_uvw))
    feasible_uvw = [min(group, key=lambda t: t[1])
                    for key, group in grouped_uvw.items()
                    if key[0] != key[1]]
    feasible_mapped_uvw = {
        _ordered(mapping[u], mapping[v]): (_ordered(u, v), w)
        for (u, v), w in feasible_uvw}

    if len(feasible_mapped_uvw) > 0:
        # """
        # Mapping of terms from (Khuller and Thurimella):
        #     C         : G^0 = (V, E^0)
        #     mapped_uv : E - E^0  # they group both avail and given edges in E
        #     T         : \Gamma
        #     D         : G^D = (V, E_D)
        #     The paper uses ancestor because children point to parents,
        #     in the networkx context this would be descendant.
        #     So, lowest_common_ancestor = most_recent_descendant
        # """
        # Pick an arbitrary leaf from C as the root
        root = next(n for n in C.nodes() if C.degree(n) == 1)
        # Root C into a tree T by directing all edges towards the root
        T = nx.reverse(nx.dfs_tree(C, root))
        # Add to D the directed edges of T and set their weight to zero
        # This indicates that it costs nothing to use edges that were given.
        D = T.copy()
        nx.set_edge_attributes(D, name='weight', values=0)
        # Add in feasible edges with respective weights
        for (u, v), (_, w) in feasible_mapped_uvw.items():
            mrd = _most_recent_descendant(T, u, v)
            if mrd == u:
                # If u is descendant of v, then add edge u->v
                D.add_edge(mrd, v, weight=w, generator=(u, v))
            elif mrd == v:
                # If v is descendant of u, then add edge v->u
                D.add_edge(mrd, u, weight=w, generator=(u, v))
            else:
                # If neither u nor v is a descendant of the other
                # let t = mrd(u, v) and add edges t->u and t->v
                # Need to track the original edge that GENERATED these edges.
                D.add_edge(mrd, u, weight=w, generator=(u, v))
                D.add_edge(mrd, v, weight=w, generator=(u, v))

        # root the graph by removing all predecessors to `root`.
        D_ = D.copy()
        D_.remove_edges_from([(u, root) for u in D.predecessors(root)])

        # Then compute a minimum rooted branching
        # https://www.cs.umd.edu/class/spring2011/cmsc651/lec07.pdf
        # A branching of G is a subgraph that is spanning (ignoring directions)
        # and which contains a directed path from r to every other vertex.
        try:
            A = nx.minimum_spanning_arborescence(D_)
        except nx.NetworkXException:
            # If there is no arborescence then augmentation is not possible
            raise nx.NetworkXUnfeasible('no 2-edge-augmentation possible')

        # For each edge e, in the branching that did not belong to the directed
        # tree T, add the correponding edge that **GENERATED** e (this is not
        # necesarilly e itself!)

        chosen_mapped = []
        for u, v in A.edges():
            data = D.get_edge_data(u, v)
            if 'generator' in data:
                # Add the avail edge that generated the branching edge.
                edge = _ordered(*data['generator'])
                assert edge in feasible_mapped_uvw
                chosen_mapped.append(edge)

        for edge in chosen_mapped:
            orig_edge, w = feasible_mapped_uvw[edge]
            yield orig_edge

    if False:
        import plottool as pt
        # C2 = C.copy()
        # C2.add_edges_from(chosen_mapped, implicit=True)

        import utool as ut
        nx.set_edge_attributes(
            D, name='label', values=ut.map_vals(str, nx.get_edge_attributes(D, 'weight')))
        # nx.set_edge_attributes(
        #     D, name='implicit', values={e: not H.has_edge(*e) for e in D.edges()})
        nx.set_edge_attributes(
            D, name='implicit', values={e: D.get_edge_data(*e)['weight'] > 0 for e in D.edges()})

        nx.set_edge_attributes(
            D_, name='implicit', values=ut.map_vals(
                lambda w: w > 0, nx.get_edge_attributes(D_, 'weight')))

        import utool as ut
        nx.set_edge_attributes(
            D_, name='label', values=ut.map_vals(str, nx.get_edge_attributes(D_, 'weight')))

        G2 = G.copy()
        G2.add_edges_from(aug_edges, implicit=True)
        C_labels = {k: '{}:\n{}'.format(k, v)
                    for k, v in nx.get_node_attributes(C, 'members').items()}
        nx.set_node_attributes(C, name='label', values=C_labels)

        C2 = C.copy()
        C2.add_edges_from(feasible_mapped_uvw.keys(), implicit=True)
        print('is_strongly_connected(D) = %r' % nx.is_strongly_connected(D))
        pnum_ = pt.make_pnum_nextgen(nSubplots=6)
        _ = pt.show_nx(C2, arrow_width=2, fnum=1, pnum=pnum_(), title='C')
        _ = pt.show_nx(T, arrow_width=2, fnum=1, pnum=pnum_(), title='T')
        _ = pt.show_nx(D, arrow_width=2, fnum=1, pnum=pnum_(), title='D')
        _ = pt.show_nx(D_, arrow_width=2, fnum=1, pnum=pnum_(), title='D_')
        _ = pt.show_nx(A, arrow_width=2, fnum=1, pnum=pnum_(), title='A')
        # _ = pt.show_nx(G, arrow_width=2, fnum=1, pnum=pnum_(), title='G')
        _ = pt.show_nx(G2, arrow_width=2, fnum=1, pnum=pnum_(), title='G2')
        _ = _  # NOQA


def _most_recent_descendant(D, u, v):
    # Find a closest common descendant
    assert nx.is_directed_acyclic_graph(D), 'Must be DAG'
    v_branch = nx.descendants(D, v).union({v})
    u_branch = nx.descendants(D, u).union({u})
    common = v_branch & u_branch
    node_depth = (
        ((c, (nx.shortest_path_length(D, u, c) +
              nx.shortest_path_length(D, v, c)))
         for c in common))
    mrd = min(node_depth, key=lambda t: t[1])[0]
    return mrd


def _lowest_common_anscestor(D, u, v):
    # Find a common ancestor furthest away
    assert nx.is_directed_acyclic_graph(D), 'Must be DAG'
    v_branch = nx.anscestors(D, v).union({v})
    u_branch = nx.anscestors(D, u).union({u})
    common = v_branch & u_branch
    node_depth = (
        ((c, (nx.shortest_path_length(D, c, u) +
              nx.shortest_path_length(D, c, v)))
         for c in common))
    mrd = max(node_depth, key=lambda t: t[1])[0]
    return mrd


def collapse(G, grouped_nodes):
    """Collapses each group of nodes into a single node.

    This is similar to condensation, but works on undirected graphs.

    Parameters
    ----------
    G : NetworkX Graph
       A directed graph.

    grouped_nodes:  list or generator
       Grouping of nodes to collapse. The grouping must be disjoint.
       If grouped_nodes are strongly_connected_components then this is
       equivalent to condensation.

    Returns
    -------
    C : NetworkX Graph
       The collapsed graph C of G with respect to the node grouping.  The node
       labels are integers corresponding to the index of the component in the
       list of strongly connected components of G.  C has a graph attribute
       named 'mapping' with a dictionary mapping the original nodes to the
       nodes in C to which they belong.  Each node in C also has a node
       attribute 'members' with the set of original nodes in G that form the
       group that the node in C represents.

    Examples
    --------
    >>> # Collapses a graph using disjoint groups, but not necesarilly connected
    >>> G = nx.Graph([(1, 0), (2, 3), (3, 1), (3, 4), (4, 5), (5, 6), (5, 7)])
    >>> G.add_node('A')
    >>> grouped_nodes = [{0, 1, 2, 3}, {5, 6, 7}]
    >>> C = collapse(G, grouped_nodes)
    >>> assert nx.get_node_attributes(C, 'members') == {
    ...     0: {0, 1, 2, 3}, 1: {5, 6, 7}, 2: {4}, 3: {'A'}
    ... }
    """
    mapping = {}
    members = {}
    C = G.__class__()
    i = 0  # required if G is empty
    remaining = set(G.nodes())
    for i, group in enumerate(grouped_nodes):
        group = set(group)
        assert remaining.issuperset(group), (
            'grouped nodes must exist in G and be disjoint')
        remaining.difference_update(group)
        members[i] = group
        mapping.update((n, i) for n in group)
    # remaining nodes are in their own group
    for i, node in enumerate(remaining, start=i + 1):
        group = set([node])
        members[i] = group
        mapping.update((n, i) for n in group)
    number_of_groups = i + 1
    C.add_nodes_from(range(number_of_groups))
    C.add_edges_from((mapping[u], mapping[v]) for u, v in G.edges()
                     if mapping[u] != mapping[v])
    # Add a list of members (ie original nodes) to each node (ie scc) in C.
    nx.set_node_attributes(C, name='members', values=members)
    # Add mapping dict as graph attribute
    C.graph['mapping'] = mapping
    return C


def complement_edges(G):
    """
    Returns the edges in the complement of G
    """
    for n1, nbrs in G.adjacency():
        for n2 in G:
            if n2 not in nbrs and n1 != n2:
                yield (n1, n2)
    # return ((n, n2) for n, nbrs in G.adjacency()
    #         for n2 in G if n2 not in nbrs if n != n2)


@not_implemented_for('multigraph')
@not_implemented_for('directed')
def randomized_k_edge_augmentation(G, k, avail=None, partial=False, seed=None):
    """Randomized algorithm for finding a k-edge-augmentation

    The algorithm is simple. Edges are randomly added between parts of the
    graph that are not yet locally k-edge-connected. Then edges are from the
    augmenting set are pruned as long as local-edge-connectivity is not broken.
    Specific edge weights are not taken into consideration.

    Example
    -------
    >>> G = nx.path_graph((1, 2, 3, 4, 5, 6, 7))
    >>> list(randomized_k_edge_augmentation(G, k=2, seed=5))
    [(1, 7)]
    >>> list(randomized_k_edge_augmentation(G, k=2, seed=4))
    [(5, 7), (4, 1), (6, 4)]
    >>> list(randomized_k_edge_augmentation(G, k=1, avail=[]))
    []
    """
    # Result set
    aug_edges = []

    done = is_k_edge_connected(G, k)
    if done:
        raise StopIteration()
    if avail is None:
        # all edges are available
        avail_uv = list(complement_edges(G))
    else:
        # Get the unique set of unweighted edges
        # avail_uv, avail_w = _unpack_available_edges(avail, weight=None)
        avail_uv = _unpack_available_edges(avail, weight=None)[0]

    # Randomize edge order
    rng = random.Random(seed)
    rng.shuffle(avail_uv)
    H = G.copy()

    # Randomly add edges in until we are k-connected
    for edge in avail_uv:
        done = False
        local_k = nx.connectivity.local_edge_connectivity(H, *edge)
        if local_k < k:
            # Only add edges in parts that are not yet locally k-edge-connected
            aug_edges.append(edge)
            H.add_edge(*edge)
            # Did adding this edge help?
            done = is_k_edge_connected(H, k)
        if done:
            break

    # Check for feasibility
    if not done:
        if partial:
            return avail_uv
        else:
            raise nx.NetworkXUnfeasible(
                'not able to k-edge-connect with available edges')

    # Attempt to reduce the size of the solution
    rng.shuffle(aug_edges)
    for edge in list(aug_edges):
        if min(H.degree(edge), key=lambda t: t[1])[1] <= k:
            continue
        H.remove_edge(*edge)
        aug_edges.remove(edge)
        conn = nx.edge_connectivity(H)
        if conn < k:
            # If removing this edge breaks feasibility, undo
            H.add_edge(*edge)
            aug_edges.append(edge)

    # Generate results
    for edge in aug_edges:
        yield edge
