"""Modular decomposition."""

import collections
import dataclasses
import functools
import itertools
import uuid

import networkx as nx
from networkx import DiGraph, Graph

__all__ = ["modular_decomposition"]


def _set_parent(graph, node, parent):
    prev_parent = _get_parent(graph, node)
    if prev_parent is not None:
        graph.remove_edge(prev_parent, node)
    if parent is not None:
        graph.add_edge(parent, node)


def _get_parent(graph, node):
    parents = list(graph.predecessors(node))
    if len(parents) > 1:
        raise ValueError(
            f"Tree invariant violation (node {node} has parents {parents})"
        )
    return next(iter(parents), None)


def _maybe_merge(md_tree, root, node_type, node):
    parent = _get_parent(md_tree, node)
    children = list(md_tree.successors(root))
    if md_tree.nodes[root]["type"] == node_type and children:
        md_tree.remove_node(root)
        for child in children:
            md_tree.add_edge(parent, child)
    else:
        md_tree.add_edge(parent, root)


def _check_for_parallel(md_tree, forest, pointers, left, right):
    #
    # No more trees to the "right", so, we can't create a parallel node.
    #
    if right >= len(forest):
        return False

    #
    # Keep going "right" until we either hit a tree whose adjacencies overlap
    # with the current tree's (in which case we create a prime node), or until
    # we can't go more to the "right" (in which case we create a parallel node).
    #
    i = right
    while i <= min(len(forest) - 1, right):
        node_left, node_right = pointers[forest[i]]
        if node_left < left:
            return False
        right = max(right, node_right)
        i += 1

    return True


def _set_left_right_pointers(graph, md_tree, forest):
    def _dfs_preorder_leaves(root):
        yield from (
            node
            for node in nx.dfs_preorder_nodes(md_tree, source=root)
            if md_tree.nodes[node]["type"] == "leaf"
        )

    #
    # For each root in the forest build and save the list of leaves reachable
    # from that root. Then, store the index of the tree each leaf belongs to.
    #
    leaves = {}
    indices = {}
    for i, root in enumerate(forest):
        leaves[root] = list(_dfs_preorder_leaves(root))
        for node in leaves[root]:
            indices[node] = i

    #
    # Compute left and right pointers for each tree in the forest (Algorithm 4.6
    # in [2]). Right is set to one past the maximum adjacent tree index, while
    # left is set to the first non-adjacent tree index before the current tree.
    #
    pointers = {}
    for i, root in enumerate(forest):
        adjacencies = functools.reduce(
            set.union,
            [graph.neighbors(n) for n in leaves[root]],
            set(),
        )
        adjacencies = {indices[n] for n in adjacencies}
        max_module = max(adjacencies) + 1
        min_module = next((j for j in range(i) if j not in adjacencies), i)
        pointers[root] = (min_module, max_module)

    return pointers


def _is_connected_to_pivot(graph, md_tree, root, pivot_neighbors):
    if md_tree.nodes[root]["type"] == "leaf":
        r = root in pivot_neighbors
    else:
        r = any(
            _is_connected_to_pivot(graph, md_tree, child, pivot_neighbors)
            for child in md_tree.successors(root)
        )
    return r


def _assembly(graph, md_tree, pivot, forest):
    #
    # Add pivot in the MD-tree.
    #
    md_tree.add_node(pivot, type="leaf", left=False, right=False, left_of_pivot=False)
    parent = pivot

    #
    # Add pivot node in the current forest at the appropriate index. All trees
    # connected to the pivot go to the "left" of pivot and then all trees not
    # connected to pivot go to the "right" of pivot.
    #
    pivot_neighbors = list(graph.neighbors(pivot))
    i = 1
    while i < len(forest) and _is_connected_to_pivot(
        graph, md_tree, forest[i], pivot_neighbors
    ):
        i += 1
    forest.insert(i, pivot)

    pointers = _set_left_right_pointers(graph, md_tree, forest)

    current_left = i
    current_right = i + 1
    included_left = i
    included_right = i + 1

    while current_left > 0 or current_right < len(forest):
        indices = []
        added_left = False
        added_right = False

        if _check_for_parallel(md_tree, forest, pointers, current_left, current_right):
            indices.append(current_right)
            current_right += 1
            added_right = True
        else:
            indices.append(current_left - 1)
            current_left -= 1
            added_left = True

        while indices:
            i = indices.pop(0)
            left, right = pointers[forest[i]]

            if left < current_left:
                indices += list(range(current_left - 1, left - 1, -1))
                current_left = left
                added_left = True

            if right > current_right:
                indices += list(range(current_right, right))
                current_right = right
                added_right = True

        node_type = "parallel"
        if added_left and added_right:
            node_type = "prime"
        elif added_left:
            node_type = "series"
        node = uuid.uuid1()
        md_tree.add_node(
            node, type=node_type, left=False, right=False, left_of_pivot=False
        )
        md_tree.add_edge(node, parent)

        for i in range(current_left, included_left):
            _maybe_merge(md_tree, forest[i], node_type, parent)

        for i in range(included_right, current_right):
            _maybe_merge(md_tree, forest[i], node_type, parent)

        parent = node
        included_left = current_left
        included_right = current_right

    return parent


def _clear_left_right(md_tree, node):
    md_tree.nodes[node]["left"] = False
    md_tree.nodes[node]["right"] = False
    for child in md_tree.successors(node):
        _clear_left_right(md_tree, child)


def _get_promoted_tree(md_tree, node):
    forest = []

    if md_tree.nodes[node]["left"]:
        for child in list(md_tree.successors(node)):
            if md_tree.nodes[child]["left"]:
                _set_parent(md_tree, child, None)
                forest += _get_promoted_tree(md_tree, child)

    forest.append(node)

    if md_tree.nodes[node]["right"]:
        for child in list(md_tree.successors(node)):
            if md_tree.nodes[child]["right"]:
                _set_parent(md_tree, child, None)
                forest += _get_promoted_tree(md_tree, child)

    return forest


def _promotion(md_tree, forest):
    promoted_forest = []
    for root in forest:
        promoted_forest += _get_promoted_tree(md_tree, root)

    #
    # Clean-up step.
    #
    new_promoted_forest = []
    for root in promoted_forest:
        if md_tree.nodes[root]["left"] or md_tree.nodes[root]["right"]:
            children = list(md_tree.successors(root))
            if children:
                if len(children) == 1:
                    _set_parent(md_tree, children[0], None)
                    md_tree.remove_node(root)
                    new_promoted_forest.append(children[0])
                else:
                    new_promoted_forest.append(root)
            elif md_tree.nodes[root]["type"] == "leaf":
                new_promoted_forest.append(root)
            else:
                md_tree.remove_node(root)
        else:
            new_promoted_forest.append(root)

    for root in new_promoted_forest:
        _clear_left_right(md_tree, root)

    return new_promoted_forest


def _mark_lr_children(md_tree, node, left):
    for child in md_tree.successors(node):
        _mark_lr(md_tree, child, left)


def _mark_lr_ancestors(md_tree, node, left):
    parent = _get_parent(md_tree, node)
    if parent is not None:
        _mark_lr(md_tree, parent, left)
        _mark_lr_ancestors(md_tree, parent, left)


def _mark_lr(md_tree, node, left):
    if left:
        md_tree.nodes[node]["left"] = True
    else:
        md_tree.nodes[node]["right"] = True


def _construct_tree(md_tree, node, children):
    if len(children) > 1:
        root = uuid.uuid1()
        md_tree.add_node(
            root,
            type=md_tree.nodes[node]["type"],
            left=False,
            right=False,
            left_of_pivot=False,
        )
        for child in children:
            _set_parent(md_tree, child, root)
    else:
        root = children[0]
        _set_parent(md_tree, root, None)
    return root


def _refinement_non_prime(forest, md_tree, node, marked, left_split):
    a_set = []
    b_set = []

    for child in md_tree.successors(node):
        if child in marked:
            a_set.append(child)
        else:
            b_set.append(child)

    if a_set and b_set:
        a_root = _construct_tree(md_tree, node, a_set)
        b_root = _construct_tree(md_tree, node, b_set)

        parent = _get_parent(md_tree, node)

        if parent is not None:
            _set_parent(md_tree, a_root, node)
            _set_parent(md_tree, b_root, node)
        else:
            root_left = md_tree.nodes[node]["left"]
            root_right = md_tree.nodes[node]["right"]
            root_left_of_pivot = md_tree.nodes[node]["left_of_pivot"]
            i = forest.index(node)

            md_tree.nodes[a_root]["left"] = root_left
            md_tree.nodes[a_root]["right"] = root_right
            md_tree.nodes[a_root]["left_of_pivot"] = root_left_of_pivot

            md_tree.nodes[b_root]["left"] = root_left
            md_tree.nodes[b_root]["right"] = root_right
            md_tree.nodes[b_root]["left_of_pivot"] = root_left_of_pivot

            if left_split:
                forest[i] = a_root
                forest.insert(i + 1, b_root)
            else:
                forest[i] = b_root
                forest.insert(i + 1, a_root)

            md_tree.remove_node(node)

        _mark_lr(md_tree, a_root, left_split)
        _mark_lr_ancestors(md_tree, a_root, left_split)
        _mark_lr(md_tree, b_root, left_split)
        _mark_lr_ancestors(md_tree, b_root, left_split)


def _refinement_prime(md_tree, node, left_split):
    _mark_lr(md_tree, node, left_split)
    _mark_lr_ancestors(md_tree, node, left_split)
    _mark_lr_children(md_tree, node, left_split)


def _mark(md_tree, nodes):
    num_marked_children = collections.defaultdict(int)
    marked = []

    #
    # Consume the nodes argument. We don't use it in the caller anyway.
    #
    while nodes:
        node = nodes.pop(0)

        #
        # For leaf nodes of the MD-tree, the following predicate is always
        # trivially true.
        #
        if md_tree.out_degree(node) == num_marked_children[node]:
            marked.append(node)
            parent = _get_parent(md_tree, node)
            if parent is not None:
                num_marked_children[parent] += 1
                if parent not in nodes:
                    nodes.append(parent)

    for node in marked:
        parent = _get_parent(md_tree, node)
        if parent is None or parent not in marked:
            nodes.append(node)

    return nodes


def _refinement(graph, md_tree, pivot, active_edges, left_nodes, forest):
    def _get_root(node):
        parent = _get_parent(md_tree, node)
        while parent is not None:
            node = parent
            parent = _get_parent(md_tree, node)
        return node

    for u in (u for u in graph if u != pivot):
        marked = _mark(md_tree, [v for v in active_edges[u] if v in md_tree])

        marked_parents = []
        for v in marked:
            parent = _get_parent(md_tree, v)
            if parent is not None and parent not in marked_parents:
                marked_parents.append(parent)

        for v in marked_parents:
            root = _get_root(v)
            left_split = left_nodes[u] or md_tree.nodes[root]["left_of_pivot"]
            if md_tree.nodes[v]["type"] == "prime":
                _refinement_prime(md_tree, v, left_split)
            else:
                _refinement_non_prime(forest, md_tree, v, marked, left_split)


def _recursion(graph, md_tree, pivot_picker):
    distances = dict.fromkeys(graph, -1)
    active_edges = collections.defaultdict(list)
    left_nodes = dict.fromkeys(graph, False)
    pivot = pivot_picker(graph)
    queue = [pivot]
    distances[pivot] = 0
    while queue:
        u = queue.pop(0)
        for v in graph.neighbors(u):
            if distances[v] == -1:
                distances[v] = distances[u] + 1
                queue.append(v)

            #
            # An edge of a graph is called active, if and only if it is adjacent
            # to pivot or connects two vertices from different $N_i$. The next
            # predicate catches both cases.
            #
            if distances[u] != distances[v]:
                active_edges[u].append(v)

            #
            # All neighbors of the pivot are placed to the "left".
            #
            if u == pivot:
                left_nodes[v] = True

    def _sorter(u):
        return distances[u]

    forest = []
    for distance, nodes in itertools.groupby(sorted(graph, key=_sorter), _sorter):
        if distance:
            subgraph = graph.subgraph(nodes)
            root = _modular_decomposition(subgraph, md_tree, pivot_picker)

            #
            # If forest is currently empty, this is the first MD-tree that is to
            # be added. This MD-tree corresponds to nodes at distance 1 from the
            # pivot (i.e. neighbors), so, mark its root as being to the "left".
            #
            if not forest:
                md_tree.nodes[root]["left_of_pivot"] = True
            forest.append(root)

    return pivot, active_edges, left_nodes, forest


def _modular_decomposition_component(graph, md_tree, pivot_picker):
    pivot, active_edges, left_nodes, forest = _recursion(graph, md_tree, pivot_picker)
    _refinement(graph, md_tree, pivot, active_edges, left_nodes, forest)
    forest = _promotion(md_tree, forest)
    return _assembly(graph, md_tree, pivot, forest)


def _modular_decomposition_components(graph, md_tree, pivot_picker):
    root = uuid.uuid1()
    md_tree.add_node(
        root, type="parallel", left=False, right=False, left_of_pivot=False
    )
    for component in sorted(map(tuple, nx.connected_components(graph))):
        subgraph = graph.subgraph(component)
        sub_root = _modular_decomposition(subgraph, md_tree, pivot_picker)
        md_tree.add_edge(root, sub_root)
    return root


def _modular_decomposition(graph, md_tree, pivot_picker):
    number_of_nodes = graph.number_of_nodes()
    if number_of_nodes == 0:
        raise ValueError("Graph has no vertices")
    if number_of_nodes == 1:
        root = next(iter(graph))
        md_tree.add_node(
            root, type="leaf", left=False, right=False, left_of_pivot=False
        )
    elif nx.is_connected(graph):
        root = _modular_decomposition_component(graph, md_tree, pivot_picker)
    else:
        root = _modular_decomposition_components(graph, md_tree, pivot_picker)
    return root


def modular_decomposition(graph, pivot_picker=None):
    """Construct the modular decomposition [1]_ of an undirected graph.

    Modular decomposition is a *unique* decomposition of a graph into *modules*.
    A module is a generalization of a connected component. More specifically,
    for a module $X$, every node $v \\not\\in X$ is either a neighbor of all nodes
    in $X$, or a non-neighbor of all nodes in $X$. Because of its uniqueness, a
    graph's modular decomposition is particularly useful for isomorphism tests,
    optimization problems and for studying further properties of the input graph.

    Parameters
    ----------
    graph : Graph
        Input graph.
    pivot_picker : Callable, optional
        A callable that takes as input subgraphs of the input graph and returns
        the pivot node to be used. If `None`, the default pivot picker is used,
        which returns the first node of the input graph as pivot.

    Returns
    -------
    tuple[DiGraph, Any]
        A tuple holding the MD-tree of the input graph and its root node.

    Notes
    -----
    The implementation, in this module, is based on the work of Luis Goppel [2]_.
    More specifically, this code is a Python port of his C++ implementation,
    found at [3]_, with some minor improvements.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Modular_decomposition
    .. [2] Goppel, Luis. "Efficient Implementation of Modular Graph Decomposition."
    .. [3] https://github.com/LuisGoeppel/ModularDecomposition_v4
    """

    def _pivot_picker(graph):
        return next(iter(graph))

    if not pivot_picker:
        pivot_picker = _pivot_picker
    md_tree = DiGraph()
    root = _modular_decomposition(graph, md_tree, pivot_picker)

    #
    # Save some memory by removing attributes from nodes of the MD-tree. We don't
    # need them any more.
    #
    for node in md_tree:
        del md_tree.nodes[node]["left"]
        del md_tree.nodes[node]["right"]
        del md_tree.nodes[node]["left_of_pivot"]

    return md_tree, root
