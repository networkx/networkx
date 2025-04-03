"""Modular decomposition."""

import collections
import dataclasses
import enum
import itertools
from collections.abc import Callable, Iterator
from typing import Any

import networkx as nx
from networkx import DiGraph, Graph

__all__ = ["Tree", "Node", "NodeType", "modular_decomposition"]


NodeList = list[Any]
ActiveEdges = dict[Any, list[Any]]
LeftNodes = dict[Any, bool]


class Tree(DiGraph):
    """Represents a MD-tree.

    It's called a "tree", but basically represents a forest of MD-trees. When
    the algorithm terminates, it should contain a single tree, hence the name.
    Nodes in this tree are either nodes of the original graph, in which case
    they are leaves, or instances of `Node`, in which case they are internal
    non-leaf nodes. Methods of this class attempt to preserve the tree invariant
    (i.e. that all nodes have at most one parent).
    """

    def root(self, node: Any) -> Any:
        """Return the root of the tree that contains `node`.

        Parameters
        ----------
        node : Any
            Node to start traversing upwards from.

        Returns
        -------
        Any
            The root of tree that contains `node`.
        """
        parent = self.parent(node)
        while parent:
            node = parent
            parent = self.parent(node)
        return node

    def parent(self, node: Any) -> Any | None:
        """Return the unique parent of `node`, if one exists.

        Parameters
        ----------
        node : Any
            Node whose parent to return.

        Returns
        -------
        Any
            The parent of `node`, or `None` if `node` has no parent.
        """
        parents = list(self.predecessors(node))
        if len(parents) > 1:
            raise ValueError(
                f"Tree invariant violation (node {node} has parents {parents})"
            )
        return next(iter(parents), None)

    def set_parent(self, node: Any, parent: Any | None) -> None:
        """Make `parent` the single parent of `node`.

        If `parent` is `None`, the existing parent is removed and `node` becomes
        a root node. In any case, the previous parent edge, if any, is removed.

        Parameters
        ----------
        node : Any
            Node whose parent to set/unset.
        parent : Any
            New parent node or `None`.
        """
        prev_parent = self.parent(node)
        if prev_parent is not None:
            self.remove_edge(prev_parent, node)
        if parent is not None:
            self.add_edge(parent, node)

    def children(self, node: Any) -> NodeList:
        """Return the list of children of `node`.

        Parameters
        ----------
        node : Any
            Node whose children to return.

        Returns
        -------
        list[Any]
            List of children.
        """
        return list(self.successors(node))

    def add_child(self, parent: Any, child: Any) -> None:
        """Make `child` a child of `parent`.

        Parameters
        ----------
        parent : Any
            Parent node.
        child : Any
            Child node.
        """
        self.set_parent(child, parent)


@enum.unique
class NodeType(enum.IntEnum):
    """Represents the type of a non-leaf node in the MD-tree.

    A node can be `PARALLEL`, `SERIES` or `PRIME`.
    """

    PARALLEL = 0
    SERIES = 1
    PRIME = 2


@dataclasses.dataclass(slots=True)
class NodeData:
    is_left: bool = False
    is_right: bool = False
    left_of_pivot: bool = False


class Node:
    """Represents internal non-leaf nodes of MD-trees.

    We define a separate class for these nodes, which effectively creates a
    separate node namespace, that avoids conflicts with nodes of the original
    graph.

    Attributes
    ----------
    node_id : int
        Unique node identifier.
    node_type : NodeType
        Node type (`PARALLEL`, `SERIES`, `PRIME`).
    """

    __slots__ = ("_node_id", "_node_type")

    _num_nodes: int = 0

    def __init__(self, node_type: NodeType) -> None:
        super().__init__()
        self._node_id = Node._num_nodes
        self._node_type = node_type
        Node._num_nodes += 1

    def __str__(self) -> str:
        return f"Node[{self.node_id}, {self.node_type.name}]"

    @property
    def node_id(self) -> int:
        return self._node_id

    @property
    def node_type(self) -> NodeType:
        return self._node_type


def _maybe_merge(md_tree: Tree, root: Any, node_type: NodeType, node: Any) -> None:
    parent = md_tree.parent(node)
    children = md_tree.children(root)
    if isinstance(root, Node) and root.node_type == node_type and children:
        md_tree.remove_node(root)
        for child in children:
            md_tree.add_edge(parent, child)
    else:
        md_tree.add_edge(parent, root)


def _check_for_parallel(
    md_tree: Tree,
    forest: NodeList,
    pointers: dict[Any, tuple[int, int]],
    left: int,
    right: int,
) -> bool:
    if right >= len(forest):
        return False
    i = right
    right += 1
    while i < right:
        root = forest[i]
        node_left, node_right = pointers[root]
        if node_left < left:
            return False
        if node_right > right:
            right = node_right
        i += 1
    return True


def _dfs_preorder_leaves(md_tree: Tree, root: Any) -> Iterator[Any]:
    yield from (
        node
        for node in nx.dfs_preorder_nodes(md_tree, source=root)
        if isinstance(node, int)
    )


def _set_left_right_pointers(
    graph: Graph, md_tree: Tree, forest: NodeList
) -> dict[Any, tuple[int, int]]:
    indices = dict.fromkeys(graph, -1)
    for i, node in enumerate(forest):
        if isinstance(node, Node):
            for node in _dfs_preorder_leaves(md_tree, node):
                indices[node] = i
        else:
            indices[node] = i

    pointers = {}
    for i, node in enumerate(forest):
        root = md_tree.root(node)
        nodes = list(_dfs_preorder_leaves(md_tree, root))

        adjacencies = []
        for n in nodes:
            adjacencies += list(graph.neighbors(n))

        connections = [0] * len(forest)
        max_module = -1
        for v in adjacencies:
            j = indices[v]
            if j > max_module:
                max_module = j
            connections[j] = 1

        min_module = 0
        while min_module < i and connections[min_module]:
            min_module += 1
        max_module += 1
        pointers[root] = (min_module, max_module)

    return pointers


def _is_connected_to_pivot(
    graph: Graph, md_tree: Tree, root: Any, pivot_neighbors: NodeList
) -> bool:
    if isinstance(root, int):
        r = root in pivot_neighbors
    else:
        r = any(
            _is_connected_to_pivot(graph, md_tree, child, pivot_neighbors)
            for child in md_tree.successors(root)
        )
    return r


def _assembly(graph: Graph, md_tree: Tree, pivot: Any, forest: NodeList) -> Node:
    #
    # Add pivot in the MD-tree.
    #
    md_tree.add_node(pivot, data=NodeData())
    parent = pivot

    #
    # Add pivot node in the current forest at the appropriate index. All trees
    # connected to the pivot go to the "left" of pivot and then all trees not
    # connected to pivot go to the "right" of pivot.
    #
    pivot_neighbors = list(graph.neighbors(pivot))
    i = 1
    for i in range(1, len(forest)):
        node = forest[i]
        root = md_tree.root(node)
        if not _is_connected_to_pivot(graph, md_tree, root, pivot_neighbors):
            break
    forest.insert(i, pivot)

    pointers = _set_left_right_pointers(graph, md_tree, forest)

    current_left = i
    current_right = i + 1
    included_left = i
    included_right = i + 1

    while True:
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

        node_type = NodeType.PARALLEL
        if added_left and added_right:
            node_type = NodeType.PRIME
        elif added_left:
            node_type = NodeType.SERIES
        node = Node(node_type)
        md_tree.add_node(node, data=NodeData())
        md_tree.add_edge(node, parent)

        for i in range(current_left, included_left):
            n = forest[i]
            rn = md_tree.root(n)
            _maybe_merge(md_tree, rn, node_type, parent)

        for i in range(included_right, current_right):
            n = forest[i]
            rn = md_tree.root(n)
            _maybe_merge(md_tree, rn, node_type, parent)

        parent = node
        included_left = current_left
        included_right = current_right

        if current_left <= 0 and current_right >= len(forest):
            break

    return parent


def _clear_left_right(md_tree: Tree, node: Any) -> None:
    data = md_tree.nodes[node]["data"]
    data.is_left = False
    data.is_right = False
    for child in md_tree.children(node):
        _clear_left_right(md_tree, child)


def _get_promoted_tree(md_tree: Tree, node: Any) -> NodeList:
    forest = []

    data = md_tree.nodes[node]["data"]
    if data.is_left:
        for child in md_tree.children(node):
            child_data = md_tree.nodes[child]["data"]
            if child_data.is_left:
                md_tree.set_parent(child, None)
                forest += _get_promoted_tree(md_tree, child)

    forest.append(node)

    if data.is_right:
        for child in md_tree.children(node):
            child_data = md_tree.nodes[child]["data"]
            if child_data.is_right:
                md_tree.set_parent(child, None)
                forest += _get_promoted_tree(md_tree, child)

    return forest


def _promotion(md_tree: Tree, forest: NodeList) -> NodeList:
    roots = []
    for node in forest:
        root = md_tree.root(node)
        if root is not None and root not in roots:
            roots.append(root)

    promoted_forest = []
    for root in roots:
        promoted_forest += _get_promoted_tree(md_tree, root)

    #
    # Clean-up step.
    #
    roots = []
    for node in promoted_forest:
        root = md_tree.root(node)
        if root is not None and root not in roots:
            roots.append(root)

    new_promoted_forest = []
    for root in roots:
        root_data = md_tree.nodes[root]["data"]
        if root_data.is_left or root_data.is_right:
            children = md_tree.children(root)
            if children:
                if len(children) == 1:
                    md_tree.set_parent(children[0], None)
                    md_tree.remove_node(root)
                    new_promoted_forest.append(children[0])
                else:
                    new_promoted_forest.append(root)
            elif isinstance(root, int):
                new_promoted_forest.append(root)
            else:
                md_tree.remove_node(root)
        else:
            new_promoted_forest.append(root)

    for node in new_promoted_forest:
        root = md_tree.root(node)
        _clear_left_right(md_tree, root)

    return new_promoted_forest


def _mark_lr_children(md_tree: Tree, node: Any, left: bool) -> None:
    for child in md_tree.children(node):
        _mark_lr(md_tree, child, left)


def _mark_lr_ancestors(md_tree: Tree, node: Any, left: bool) -> None:
    parent = md_tree.parent(node)
    if parent is not None:
        _mark_lr(md_tree, parent, left)
        _mark_lr_ancestors(md_tree, parent, left)


def _mark_lr(md_tree: Tree, node: Any, left: bool) -> None:
    data = md_tree.nodes[node]["data"]
    if left:
        data.is_left = True
    else:
        data.is_right = True


def _construct_tree(md_tree: Tree, node: Any, children: NodeList) -> Any:
    if len(children) > 1:
        assert isinstance(node, Node)
        root = Node(node.node_type)
        md_tree.add_node(root, data=NodeData())
        for child in children:
            md_tree.add_child(root, child)
    else:
        root = children[0]
        root_data = md_tree.nodes[root]["data"]
        md_tree.set_parent(root, None)
    return root


def _refinement_non_prime(
    forest: NodeList,
    md_tree: Tree,
    node: Any,
    marked: NodeList,
    left_split: bool,
) -> None:
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

        parent = md_tree.parent(node)

        if parent is not None:
            md_tree.add_child(node, a_root)
            md_tree.add_child(node, b_root)
        else:
            root = md_tree.root(node)
            root_data = md_tree.nodes[root]["data"]
            i = forest.index(root)

            a_data = md_tree.nodes[a_root]["data"]
            a_data.is_left = root_data.is_left
            a_data.is_right = root_data.is_right
            a_data.left_of_pivot = root_data.left_of_pivot

            b_data = md_tree.nodes[a_root]["data"]
            b_data.is_left = root_data.is_left
            b_data.is_right = root_data.is_right
            b_data.left_of_pivot = root_data.left_of_pivot

            if left_split:
                forest[i] = a_root
                forest.insert(i + 1, b_root)
            else:
                forest[i] = b_root
                forest.insert(i + 1, a_root)

            md_tree.remove_node(root)

        _mark_lr(md_tree, a_root, left_split)
        _mark_lr_ancestors(md_tree, a_root, left_split)
        _mark_lr(md_tree, b_root, left_split)
        _mark_lr_ancestors(md_tree, b_root, left_split)


def _refinement_prime(md_tree: Tree, node: Any, left_split: bool) -> None:
    _mark_lr(md_tree, node, left_split)
    _mark_lr_ancestors(md_tree, node, left_split)
    _mark_lr_children(md_tree, node, left_split)


def _mark(md_tree: Tree, nodes: NodeList) -> NodeList:
    num_marked_children: dict[Any, int] = collections.defaultdict(int)
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
            parent = md_tree.parent(node)
            if parent is not None:
                num_marked_children[parent] += 1
                if parent not in nodes:
                    nodes.append(parent)

    for node in marked:
        parent = md_tree.parent(node)
        if parent is None or parent not in marked:
            nodes.append(node)

    return nodes


def _refinement(
    graph: Graph,
    md_tree: Tree,
    pivot: Any,
    active_edges: ActiveEdges,
    left_nodes: LeftNodes,
    forest: NodeList,
) -> None:
    for u in (u for u in graph if u != pivot):
        marked = _mark(md_tree, [v for v in active_edges[u] if v in md_tree])

        marked_parents = []
        for v in marked:
            parent = md_tree.parent(v)
            if parent is not None and parent not in marked_parents:
                marked_parents.append(parent)

        for v in marked_parents:
            root = md_tree.root(v)
            data = md_tree.nodes[root]["data"]
            left_split = left_nodes[u] or data.left_of_pivot
            if v.node_type == NodeType.PRIME:
                _refinement_prime(md_tree, v, left_split)
            else:
                _refinement_non_prime(forest, md_tree, v, marked, left_split)


def _recursion(
    graph: Graph, md_tree: Tree, pivot_picker: Callable
) -> tuple[Any, ActiveEdges, LeftNodes, NodeList]:
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

    def _sorter(u: Any) -> int:
        return distances[u]

    forest: list[Any] = []
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
                data = md_tree.nodes[root]["data"]
                data.left_of_pivot = True
            forest.append(root)

    return pivot, active_edges, left_nodes, forest


def _modular_decomposition_component(
    graph: Graph, md_tree: Tree, pivot_picker: Callable
) -> Node:
    pivot, active_edges, left_nodes, forest = _recursion(graph, md_tree, pivot_picker)
    _refinement(graph, md_tree, pivot, active_edges, left_nodes, forest)
    forest = _promotion(md_tree, forest)
    return _assembly(graph, md_tree, pivot, forest)


def _modular_decomposition_components(
    graph: Graph, md_tree: Tree, pivot_picker: Callable
) -> Node:
    root = Node(NodeType.PARALLEL)
    md_tree.add_node(root, data=NodeData())
    for component in sorted(map(tuple, nx.connected_components(graph))):
        subgraph = graph.subgraph(component)
        sub_root = _modular_decomposition(subgraph, md_tree, pivot_picker)
        md_tree.add_edge(root, sub_root)
    return root


def _modular_decomposition(graph: Graph, md_tree: Tree, pivot_picker: Callable) -> Any:
    number_of_nodes = graph.number_of_nodes()
    if number_of_nodes == 0:
        raise ValueError("Graph has no vertices")
    if number_of_nodes == 1:
        root = next(iter(graph))
        md_tree.add_node(root, data=NodeData())
    elif nx.is_connected(graph):
        root = _modular_decomposition_component(graph, md_tree, pivot_picker)
    else:
        root = _modular_decomposition_components(graph, md_tree, pivot_picker)
    return root


def modular_decomposition(
    graph: Graph, pivot_picker: Callable | None = None
) -> tuple[Tree, Any]:
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
    tuple[Tree, Any]
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

    def _pivot_picker(graph: Graph) -> Any:
        return next(iter(graph))

    if not pivot_picker:
        pivot_picker = _pivot_picker
    md_tree = Tree()
    root = _modular_decomposition(graph, md_tree, pivot_picker)

    #
    # Save some memory by removing the "data" attribute from nodes of the MD-tree.
    # We don't need them any more.
    #
    for node in md_tree:
        del md_tree.nodes[node]["data"]

    return md_tree, root
