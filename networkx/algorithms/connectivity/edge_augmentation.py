# -*- coding: utf-8 -*-
import networkx as nx


def one_edge_augmentation(G, avail=None):
    """Finds minimum weight set of edges to connect G.

    Adding these edges to G will make it connected.

    Parameters
    ----------
    G : NetworkX graph

    avail : list
        available edges, if None nx.complement(G) is assumed.
        if each item is a (u, v), the problem is unweighted.
        if each item is a (u, v, d), the problem is weighted.
        with d[weight] corresponding to the weight.
    """
    if avail is not None:
        for edge in weighted_one_edge_augmentation(G, avail):
            yield edge
    else:
        ccs1 = list(nx.connected_components(G))
        C = collapse(G, ccs1)
        mapping = C.graph['mapping']
        # When we are not constrained, we can just make a meta graph tree.
        meta_nodes = list(C.nodes())
        # build a path in the metagraph
        meta_aug = list(zip(meta_nodes, meta_nodes[1:]))
        # map that path to the original graph
        inverse = ut.group_pairs(C.graph['mapping'].items())
        for mu, mv in meta_aug:
            yield (inverse[mu][0], inverse[mv][0])


def weighted_one_edge_augmentation(G, avail):
    """ this is the MST problem """
    ccs1 = list(nx.connected_components(G))
    C = collapse(G, ccs1)
    mapping = C.graph['mapping']

    avail_uv = [tup[0:2] for tup in avail]
    avail_w = [1 if len(tup) == 2 else tup[-1][weight] for tup in avail]
    meta_avail_uv = [(mapping[u], mapping[v]) for u, v in avail_uv]

    # only need exactly 1 edge at most between each CC, so choose lightest
    avail_ew = zip(avail_uv, avail_w)
    grouped_we = ut.group_items(avail_ew, meta_avail_uv)
    candidates = []
    for meta_edge, choices in grouped_we.items():
        edge, w = min(choices, key=lambda t: t[1])
        candidates.append((meta_edge, edge, w))
    candidates = sorted(candidates, key=lambda t: t[2])

    # kruskals algorithm on metagraph to find the best connecting edges
    subtrees = nx.utils.UnionFind()
    for (mu, mv), (u, v), w in candidates:
        if subtrees[mu] != subtrees[mv]:
            yield (u, v)
        subtrees.union(mu, mv)
    # G2 = G.copy()
    # nx.set_edge_attributes(G2, 'weight', 0)
    # G2.add_edges_from(avail, weight=1)
    # mst = nx.minimum_spanning_tree(G2)
    # aug_edges = [(u, v) for u, v in avail if mst.has_edge(u, v)]
    # return aug_edges



def bridge_augmentation(G, avail=None):
    """Finds the a set of edges that bridge connects G.

    Adding these edges to G will make it 2-edge-connected.
    If no constraints are specified the returned set of edges is minimum an
    optimal, otherwise the solution is approximated.

    Notes
    -----
    This is an implementation of the algorithm from _[1].
    If there are no constraints the solution can be computed in linear time.
    When the available edges have weights the problem becomes NP-hard.
    If G is connected the approximation ratio is 2, otherwise it is 3.

    References
    ----------
    .. [1] Eswaran, Kapali P., and R. Endre Tarjan. Augmentation problems.
        http://epubs.siam.org/doi/abs/10.1137/0205044
    """
    if G.number_of_nodes() < 3:
        raise ValueError('impossible to bridge connect less than 3 verticies')
    if avail is not None:
        return weighted_bridge_augmentation(G, avail)
    else:
        # find the bridge-connected components of G
        bridge_ccs = bridge_connected_compoments(G)
        # condense G into an forest C
        C = collapse(G, bridge_ccs)
        # Connect each tree in the forest to construct an arborescence
        # (I think) these must use nodes with minimum degree
        roots = [min(cc, key=C.degree) for cc in nx.connected_components(C)]
        forest_bridges = list(zip(roots, roots[1:]))
        C.add_edges_from(forest_bridges)
        # order the leaves of C by preorder
        leafs = [n for n in nx.dfs_preorder_nodes(C) if C.degree(n) == 1]
        # construct edges to bridge connect the tree
        tree_bridges = list(zip(leafs, leafs[1:]))
        # collect the edges used to augment the original forest
        aug_tree_edges = tree_bridges + forest_bridges
        # map these edges back to edges in the original graph
        inverse = {v: k for k, v in C.graph['mapping'].items()}
        bridge_edges = [(inverse[u], inverse[v]) for u, v in aug_tree_edges]
        return bridge_edges


def weighted_bridge_augmentation(G, avail):
    """
    Chooses a set of edges from avail to add to G that renders it
    2-edge-connected if such a subset exists.

    Because we are constrained by edges in avail this problem is NP-hard, and
    this function is a 2-approximation if the input graph is connected, and a
    3-approximation if it is not. Runs in O(m + nlog(n)) time

    Parameters
    ----------
    G : NetworkX graph

    avail : set
        candidate edges to choose from

    Returns
    -------
    aug_edges (set): subset of avail chosen to augment G

    References
    ----------
    .. [1] Khuller, Samir, and Ramakrishna Thurimella. Approximation
        algorithms for graph augmentation.
        http://www.sciencedirect.com/science/article/pii/S0196677483710102
    """
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

    # If input G is not connected the approximation factor increases to 3
    aug_edges = []
    if not nx.is_connected(G):
        H = G.copy()
        connectors = one_connected_augmentation(H, avail)
        H.add_edges_from(connectors)
        aug_edges.extend(connectors)
    else:
        H = G
    if not nx.is_connected(H):
        raise ValueError('no augmentation possible')

    uv_avail = [tup[0:2] for tup in avail]
    uv_avail = [
        (u, v) for u, v in uv_avail if (
            H.has_node(u) and H.has_node(v) and not H.has_edge(u, v))
    ]

    # Collapse input into a metagraph. Meta nodes are bridge-ccs
    bridge_ccs = bridge_connected_compoments(H)
    C = collapse(H, bridge_ccs)

    # Use the meta graph to filter out a small feasible subset of avail
    # Choose the minimum weight edge from each group. TODO WEIGHTS
    mapping = C.graph['mapping']
    mapped_avail = [(mapping[u], mapping[v]) for u, v in uv_avail]
    grouped_avail = ut.group_items(uv_avail, mapped_avail)
    feasible_uv = [
        group[0] for key, group in grouped_avail.items()
        if key[0] != key[1]]
    feasible_mapped_uv = {
        e_(mapping[u], mapping[v]): e_(u, v) for u, v in feasible_uv
    }

    if len(feasible_mapped_uv) > 0:
        """
        Mapping of terms from (Khuller and Thurimella):
            C         : G^0 = (V, E^0)
            mapped_uv : E - E^0  # they group both avail and given edges in E
            T         : \Gamma
            D         : G^D = (V, E_D)

            The paper uses ancestor because children point to parents,
            in the networkx context this would be descendant.
            So, lowest_common_ancestor = most_recent_descendant
        """
        # Pick an arbitrary leaf from C as the root
        root = next(n for n in C.nodes() if C.degree(n) == 1)
        # Root C into a tree T by directing all edges towards the root
        T = nx.reverse(nx.dfs_tree(C, root))
        # Add to D the directed edges of T and set their weight to zero
        # This indicates that it costs nothing to use edges that were given.
        D = T.copy()
        nx.set_edge_attributes(D, 'weight', 0)
        # Add in feasible edges with respective weights
        for u, v in feasible_mapped_uv.keys():
            mrd = _most_recent_descendant(T, u, v)
            # print('(u, v)=({}, {})  mrd={}'.format(u, v, mrd))
            if mrd == u:
                # If u is descendant of v, then add edge u->v
                D.add_edge(mrd, v, weight=1, implicit=True)
            elif mrd == v:
                # If v is descendant of u, then add edge v->u
                D.add_edge(mrd, u, weight=1, implicit=True)
            else:
                # If neither u nor v is a descendant of the other
                # let t = mrd(u, v) and add edges t->u and t->v
                D.add_edge(mrd, u, weight=1, implicit=True)
                D.add_edge(mrd, v, weight=1, implicit=True)

        # root the graph by removing all predecessors to `root`.
        D_ = D.copy()
        D_.remove_edges_from([(u, root) for u in D.predecessors(root)])

        # Then compute a minimum rooted branching
        try:
            A = nx.minimum_spanning_arborescence(D_)
        except nx.NetworkXException:
            # If there is no arborescence then augmentation is not possible
            raise ValueError('There is no 2-edge-augmentation possible')
        else:
            edges = list(A.edges(data=True))

        chosen_mapped = []
        for u, v, d in edges:
            edge = e_(u, v)
            if edge in feasible_mapped_uv:
                chosen_mapped.append(edge)

        for edge in chosen_mapped:
            orig_edge = feasible_mapped_uv[edge]
            aug_edges.append(orig_edge)
    return aug_edges


@profile
def edge_connected_augmentation(G, k, avail=None, hack=False, return_anyway=False):
    r"""
    Finds set of edges to k-edge-connect G. In the case of k=1
    this is a minimum weight set. For k>2 it becomes exact only if avail is
    None
    """
    if avail is not None and len(avail) == 0:
        return []
    if G.number_of_nodes() < k + 1:
        if return_anyway:
            if avail is None:
                avail = list(complement_edges(G))
            else:
                avail = list(avail)
            return avail
        raise ValueError(
            ('impossible to {} connect in graph with less than {} '
             'verticies').format(k, k + 1))
    # if is_edge_connected(G, k):
    #     aug_edges = []
    elif k == 1 and not hack:
        aug_edges = one_connected_augmentation(G, avail)
    elif k == 2 and avail is None and not hack:
        aug_edges = bridge_connected_augmentation(G)
    elif k == 2 and avail is not None:
        aug_edges = weighted_bridge_connected_augmentation(G, avail,
                                                           return_anyway)
    else:
        raise NotImplementedError('not implemented for k>2')
    return aug_edges


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
    Collapses a graph using disjoint groups, but not necesarilly connected
    >>> G = nx.Graph([(1, 0), (2, 3), (3, 1), (3, 4), (4, 5), (5, 6), (5, 7)])
    >>> G.add_node('A')
    >>> grouped_nodes = [{0, 1, 2, 3}, {5, 6, 7}]
    >>> C = collapse(G, grouped_nodes)
    >>> assert nx.get_node_attributes(C, 'members') == {
    >>>     0: {0, 1, 2, 3}, 1: {5, 6, 7}, 2: {4}, 3: {'A'}
    >>> }
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
    nx.set_node_attributes(C, 'members', members)
    # Add mapping dict as graph attribute
    C.graph['mapping'] = mapping
    return C


def complement_edges(G):
    return ((n, n2) for n, nbrs in G.adjacency()
            for n2 in G if n2 not in nbrs if n != n2)
