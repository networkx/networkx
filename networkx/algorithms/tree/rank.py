"""
Generators for ranking spanning arborescences according to graph weight.

This implementation is based on:

    Camerini, P. M., Fratta, L., & Maffioli, F. (1980). Ranking
    arborescences in O (Km log n) time. European Journal of Operational
    Research, 4(4), 235-242.

Proof can be found in:

    Camerini, P. M., Fratta, L., & Maffioli, F. (1980). The k best spanning
    arborescences of a network. Networks, 10(2), 91-109.

"""
from collections import namedtuple
from copy import deepcopy
import math
import sys
from typing import Dict, List, Optional, Set, Tuple

from loguru import logger
import networkx as nx
import numpy as np


__all__ = [
    "DescendSpanningArborescences",
    "AscendSpanningArborescences",
]


_ResultRank = namedtuple("_ResultRank", ["w", "e", "a", "y", "z"])

logger.remove(0)
handler_id = logger.add(sys.stderr, level="SUCCESS")


class DiGraphEnhanced(nx.DiGraph):
    """Mutable objects for directed graph with geographical information."""

    _col_edges = ["source", "target"]
    _col_pos = ["node", "x", "y"]

    def __init__(self, g: Optional[nx.DiGraph] = None):
        """Init an empty directed graph or existing directed graph.

        Args:
            g: an existing directed graph.
        """
        if not g:
            super().__init__()
        else:
            super().__init__(g)

    @property
    def df_edges(self):
        """Collect all edges and their attributes in a data frame.

        Returns:
            All the edges and their attributes in RDF.
        """
        return nx.to_pandas_edgelist(self)


class DiGraphMap(DiGraphEnhanced):
    """Simple directed graph defined by mapping functions."""

    def __init__(
        self,
        nodes: Set[str],
        edges: Set[str],
        source_map: Dict[str, str],
        target_map: Dict[str, str],
        weight_map: Dict[str, float],
    ):
        """Init a directed graph according to lists and maps.

        Args:
            nodes: labels of all the nodes.
            edges: labels of all the edges.
            source_map: the source node of any edge keyed by edge.
            target_map: the target node of any edge keyed by edge.
            weight_map: the weight of any edge keyed by edge.

        """
        super().__init__()

        # Add all the edges based on maps.
        edge_dict = {}
        for edge in edges:
            try:
                if self.has_edge(source_map[edge], target_map[edge]):
                    logger.warning(
                        f'Edge "{source_map[edge]}, {target_map[edge]}" '
                        f"already exist."
                    )
                self.add_edge(
                    u_of_edge=source_map[edge],
                    v_of_edge=target_map[edge],
                    weight=weight_map[edge],
                    label=edge,
                )
                edge_dict[edge] = (source_map[edge], target_map[edge])
            except KeyError:
                logger.error(f'The maps for edge "{edge}" is not complete.')

        # All the node in nodes must be found in node_set.
        node_set = set()
        for node in self.nodes:
            if node not in nodes:
                logger.error(f'Node "{node}" is not specified.')
            else:
                node_set.add(node)

        # Extra node in nodes are not considered
        for node in nodes:
            if node not in self.nodes:
                logger.warning(f'Node "{node}" is not connected.')

        self.node_set = node_set  # Set[str]
        self.edge_dict = edge_dict  # Dict[str, Tuple[str, str, int]]
        self.source_map = {e: source_map[e] for e in edges}
        self.target_map = {e: target_map[e] for e in edges}
        self.weight_map = {e: weight_map[e] for e in edges}

    @classmethod
    def from_nx(cls, dg: nx.DiGraph):
        """Init by extracting dictionaries from a multi directed graph.

        Args:
            dg: an ordinary multi directed graph.

        Returns:
            DiGraphMap: directed graph defined by maps.
        """
        source_map = {}
        target_map = {}
        weight_map = {}
        edges = set()

        # Tuples with three entries are returned.
        for edge in dg.edges.data():
            try:
                label = edge[2]["label"]
                edges.add(label)
                source_map[label] = edge[0]
                target_map[label] = edge[1]
                weight_map[label] = edge[2]["weight"]
            except KeyError:
                logger.error(f'Edge "{edge[0]}, {edge[1]}" is incorrect.')
        return cls(dg.nodes, edges, source_map, target_map, weight_map)

    def edges_inv_map(
        self, value: str, attrname: Optional[str] = "target"
    ) -> List[str]:
        """Find edges with a specified value in a specified map.

        Note that when the map for weights is specified, the value
        should be a float number. If a string is passed, it will be
        converted. An error will be raised if the conversion fails.

        Args:
            value: the value when map with the returned key.
            attrname: which map. Defaults to ``target``, or ``source``,
                ``weight`` can be passed.

        Returns:
            edges with the specified value in the specified map.
        """
        if attrname == "weight":
            try:
                value = float(value)
            except ValueError:
                logger.error("A string representing a float number should be passed.")

        the_map = getattr(self, f"{attrname}_map")
        res = []
        for edge_label in self.edge_dict.keys():
            if the_map[edge_label] == value:
                res.append(edge_label)
        return res

    @property
    def maps(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Get two mapping functions for the graph.

        Returns:
            Two maps, ``sources`` and ``targets``.
        """
        sources = {}
        targets = {}
        for e in self.edges.data():
            label = e[2]["label"]
            sources[label] = e[0]
            targets[label] = e[1]
        return sources, targets


class MultiDiGraphMap(nx.MultiDiGraph):
    """Connected multi directed graph defined by lists and maps.

    ``nodes`` and ``edges`` are indexed mathematical sets in essence.
    To avoid confusion, naming nodes and edges using strings is
    encouraged.

    ``source_map``, ``target_map``, are incidence functions mapping
    edges to their sources and targets.

    ``weight_map`` is weighting function mapping edges to their weights,
    which can be distances or any numerical values.

    """

    def __init__(
        self,
        nodes: Set[str],
        edges: Set[str],
        source_map: Dict[str, str],
        target_map: Dict[str, str],
        weight_map: Dict[str, float],
    ):
        """Init a multi directed graph according to lists and maps.

        There are three important concepts in [camerini1980ranking]_,
        two of which are implemented in this class:

            - Deep cycle. Discussed in
              :func:`MultiDiGraphMap.deep_cycles`.
            - Constained sub-graph. Discussed in
              :func:`MultiDiGraphMap.constrain_subgraph`.

        and the third one, graph collapsed into a deep cycle, is
        discussed in a function in another module
        :func:`EstRDF.graph.utils.collapse_into_cycle`.

        Note:
            - The 'true' names of nodes and edges are represented by
              strings and maps are keyed by these strings.
            - There may be extra items in maps. They are not stored
              after the graph is initiated. For example, maps from a
              larger graph can be passed.
            - If there are extra nodes specified, they are not
              considered. That is, the graph is connected.

        Args:
            nodes: labels of all the nodes.
            edges: labels of all the edges.
            source_map: the source node of any edge keyed by edge.
            target_map: the target node of any edge keyed by edge.
            weight_map: the weight of any edge keyed by edge.
        """
        super().__init__()

        # Add all the edges based on maps.
        edge_dict = {}
        for edge in edges:
            try:
                idx = self.add_edge(
                    u_for_edge=source_map[edge],
                    v_for_edge=target_map[edge],
                    weight=weight_map[edge],
                    label=edge,
                )
                edge_dict[edge] = (source_map[edge], target_map[edge], idx)
            except KeyError:
                logger.error(f'The maps for edge "{edge}" is not complete.')

        # All the node in nodes must be found in node_set.
        node_set = set()
        for node in self.nodes:
            if node not in nodes:
                logger.error(f'Node "{node}" is not specified.')
            else:
                node_set.add(node)

        # Extra node in nodes are not considered
        for node in nodes:
            if node not in self.nodes:
                logger.warning(f'Node "{node}" is not connected.')

        self.node_set = node_set  # Set[str]
        self.edge_dict = edge_dict  # Dict[str, Tuple[str, str, int]]
        self.source_map = {e: source_map[e] for e in edges}
        self.target_map = {e: target_map[e] for e in edges}
        self.weight_map = {e: weight_map[e] for e in edges}

        self.name = "?"

    @classmethod
    def from_nx(cls, dg: nx.MultiDiGraph):
        """Init by extracting dictionaries from a multi directed graph.

        Args:
            dg: a multi directed graph.

        Returns:
            MultiDiGraphMap: multi directed graph defined by maps.
        """
        source_map = {}
        target_map = {}
        weight_map = {}
        edges = set()

        # Tuples with three entries are returned.
        for edge in dg.edges.data():
            try:
                label = edge[2]["label"]
                edges.add(label)
                source_map[label] = edge[0]
                target_map[label] = edge[1]
                weight_map[label] = edge[2]["weight"]
            except KeyError:
                logger.error(f'Edge "{edge[0]}, {edge[1]}" is incorrect.')
        return cls(dg.nodes, edges, source_map, target_map, weight_map)

    @property
    def maps(self) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, float]]:
        """Get three mapping functions for the graph.

        Returns:
            Three maps, ``sources``, ``targets``, ``weights``.
        """
        sources = {}
        targets = {}
        weights = {}
        for e in self.edges.data():
            label = e[2]["label"]
            sources[label] = e[0]
            targets[label] = e[1]
            weights[label] = e[2]["weight"]
        return sources, targets, weights

    def edges_inv_map(
        self, value: str, attrname: Optional[str] = "target"
    ) -> List[str]:
        """Find edges with a specified value in a specified map.

        Note:
            When the map for weights is specified, the value should be a
            float number. If a string is passed, it will be converted.
            An error will be raised if the conversion fails.

        Args:
            value: the value when map with the returned key.
            attrname: which map. Defaults to 'target', or 'source',
                'weight' can be passed.

        Returns:
            All the edges.
        """
        if attrname == "weight":
            try:
                value = float(value)
            except ValueError:
                logger.error("A string representing a float number should be passed.")

        the_map = getattr(self, f"{attrname}_map")
        res = []
        for edge_label in self.edge_dict.keys():
            if the_map[edge_label] == value:
                res.append(edge_label)
        return res

    def get_in_edge_with_max_weight(self, v: int) -> str:
        """Find the in-edge with max weight of a given node.

        Args:
            v: name of a node.

        Returns:
            Name of the edge with max weight among in-edges of the
            specified node.
        """
        if v in self.nodes:
            in_edges_v = list(self.in_edges(v, data=True))

            data = {edge[2]["label"]: edge[2]["weight"] for edge in in_edges_v}
            res = max(data, key=lambda k: data[k])
            logger.info(
                f'Edge "{res}" is the in-edge of node "{v}" '
                f"with max weight {data[res]}."
            )
        else:
            logger.error(f"Node {v} is not in {self.nodes}.")
            res = None

        return res

    def get_nodes_in_branch(self, branch: List[str]) -> Set[str]:
        """Gather all nodes appear in a branching.

        Notes:
            Branchings are represented by lists in this project. In
            thoery, they are subnetworks of some graph.

        Args:
            branch: all the edges in a branching.

        Returns:
            All the nodes corresponding to the branching.
        """
        res = set()
        for edge in branch:
            res.add(self.source_map[edge])
            res.add(self.target_map[edge])

        logger.info(f"Nodes {res} are in the branching {branch}.")
        return res

    def _validate(self, root: str):
        """Check if the specified root is a node.

        Args:
            root (str): the specified root node in the graph.
        """
        if root not in self.nodes:
            logger.error(f"The passed root {root} is incorrect.")

    def first_node_exposed(self, branch: Set[str], root: str) -> str:
        """Get the first exposed node with respect to a branching.

        A node is an **exposed node with respect to a branching** if it
        is not the target of any edge in the branching.

        Note:
            - When the branch is empty, a node is selected to be exposed
              randomly.
            - The root is not considered.
            - It's possible that some edge in the branching is not
              contained in the graph.
            - Both the passed branching and returned exposed node must
              be based on the object itself.

        Args:
            branch: a set of edge names in a branching.
            root: the specified root.

        Returns:
            The first exposed node.
        """
        self._validate(root)

        nodes = list(self.nodes)
        nodes.remove(root)

        if branch:
            for edge in branch:
                if edge in self.edge_dict.keys():
                    node_to_remove = self.target_map[edge]
                    if node_to_remove in nodes:
                        nodes.remove(node_to_remove)
                else:
                    logger.warning(f'Edge "{edge}" in branching is not found in graph.')

        if nodes:
            res = nodes[0]
            logger.info(
                f'Node "{res}" is exposed with respect to ' f"branching {branch}."
            )
        else:
            res = None

        return res

    def validate_deep_cycle(self, nodes_cycle: List[str]) -> Tuple[bool, List[int]]:
        """Check if a cycle is a deep cycle.

        Args:
            nodes_cycle: sorted list of nodes in a cycle.

        Returns:
            If it is a deep cycle and integer indices for edges.
        """
        nodes_cycle.append(nodes_cycle[0])  # There are k nodes
        is_deep = True

        # Check if this is a deep cycle.
        k = len(nodes_cycle)
        edge_keys = [0] * (k - 1)
        for i in range(1, k):
            i -= 1

            # If there are multiple edges in parallel, the one with max
            #    weight will be chosen.
            num_edges = self.number_of_edges(nodes_cycle[i], nodes_cycle[i + 1])
            weights = [
                self.edges[nodes_cycle[i], nodes_cycle[i + 1], key]["weight"]
                for key in range(num_edges)
            ]
            edge_keys[i] = weights.index(max(weights))
            e_i = self.edges[(nodes_cycle[i], nodes_cycle[i + 1], edge_keys[i])][
                "label"
            ]

            edges = self.edges_inv_map(i)
            if not all(self.weight_map(e_i) >= self.weight_map(e) for e in edges):
                is_deep = False

        return is_deep, edge_keys

    def deep_cycles(self, root: str) -> Set[DiGraphMap]:
        """Find deep cycles in this graph with respect to a root.

        A **deep cycle** is a directed cycle of a weighted multi
        directed graph, of which any edge has maximum weight out of
        edges with the same target in the graph, and the specified root
        is not contained in the deep cycle.

        There is another method,
        :func:`MultiDiGraph.validate_deep_cycle`, to validate the
        result.

        Args:
            root: the specified root node in the graph.

        Warning:
            A tuple with ``source``, ``target``, and ``index`` is
            required to find an edge in a multi directed graph.

        Returns:
            All the deep cycles.
        """
        m = nx.MultiDiGraph(self)

        self._validate(root)
        m.remove_node(root)
        cycles = nx.simple_cycles(m)

        res = set()
        for nodes_cycle in cycles:
            is_deep, edge_keys = self.validate_deep_cycle(nodes_cycle)

            if is_deep:
                cycle = self.get_deep_cycle(nodes_cycle, edge_keys)
                # Convert to MDGM and append to result.
                res.add(cycle)

        return res

    def get_deep_cycle(
        self, nodes_cycle: List[str], edge_keys: List[int]
    ) -> DiGraphMap:
        """Init a deep cycle according to given information.

        Args:
            nodes_cycle: sorted list of nodes in a cycle.
            edge_keys: integer indices for edges.

        Returns:
            A deep cycle.
        """
        res = nx.DiGraph()
        k = len(nodes_cycle)
        for i in range(1, k):
            i -= 1
            edge_in_g = self.get_edge_data(
                nodes_cycle[i], nodes_cycle[i + 1], edge_keys[i]
            )
            label = edge_in_g["label"]
            weight = edge_in_g["weight"]
            res.add_edge(nodes_cycle[i], nodes_cycle[i + 1], label=label, weight=weight)

        res = DiGraphMap.from_nx(res)
        return res

    def get_subgraph(self, edges: Set[str]):
        """Get a sub-graph with only specified edges out of an MDG.

        Args:
            edges: names of all the edges in the sub-graph.

        Returns:
            MultiDiGraphMap: the sub-graph.
        """
        res = nx.DiGraph()
        for edge in edges:
            try:
                res.add_edge(
                    self.source_map[edge],
                    self.target_map[edge],
                    weight=self.weight_map[edge],
                    label=edge,
                )
            except KeyError:
                logger.error(f'Edge "{edge}" is not in the {self.name} graph.')
                res = None
                break

        if res:
            res = MultiDiGraphMap.from_nx(res)
        return res

    def constrain_subgraph(self, branch: Set[str], edges: Set[str]):
        """Constrain a sub-graph based on branching and set of edges.

        Warning:
            The branch is not checked.

        Args:
            branch: a branching of the original graph.
            edges: a set of edges of the original graph, and these edges
                are not contained in the branching.

        Returns:
            The contrained sub-graph. None if there is something wrong
            with the arguments.
        """
        if any(edge in branch for edge in edges):
            logger.error(
                "Some passed edge is contained in the passed " "spanning arborescence."
            )
            res = None
        elif any(edge not in self.edge_dict.keys() for edge in edges):
            logger.error("Some passed edge is not contained in the graph.")
            res = None
        else:
            edges_left = set(self.edge_dict.keys())
            for edge in edges:
                edges_left.remove(edge)

            if branch:
                for e in self.edge_dict.keys():
                    for e_prime in {edge for edge in branch if edge != e}:
                        if self.target_map[e] == self.target_map[e_prime]:
                            edges_left.discard(e)

            if not edges_left:
                res = None
            else:
                res = self.get_subgraph(edges_left)
                logger.debug(
                    f"Edges {set(self.edge_dict.keys()) - edges_left} have "
                    "been removed."
                )

        if not res:
            logger.warning("Empty sub-graph has been returned")
        elif not nx.is_connected(nx.Graph(res)):
            logger.error("The constrained sub-graph is not connected.")

        return res


class Arborescence(DiGraphEnhanced):
    """Immutable arborescence.

    Notes:
        The graph will be frozen once it is initiated.

    Attributes:
        root (str): name of the root node.
    """

    def __init__(self, g: nx.DiGraph):
        """Init an immutable rooted tree based on a directed graph.

        Args:
            g: a rooted tree.
        """
        self.root = self._validate(g)
        super().__init__(nx.freeze(g))

    @staticmethod
    def _validate(dg: nx.DiGraph) -> str:
        """Validate if a rooted (directed) tree and return its root.

        Args:
            dg: the directed graph to be checked.

        Raises:
            TypeError: when the graph is not directed.
            TypeError: when the directed graph is not a tree
            ValueError: when the directetd tree doesn't have a root.
            ValueError: when the directetd tree have more than one root.

        Returns:
            Name of the root in this rooted tree.
        """
        if not dg.is_directed():
            raise TypeError("The graph is not directed.")
        if not nx.is_arborescence(dg):
            logger.error(f"There are {len(dg.edges)} edges and {len(dg.nodes)} nodes.")
            raise TypeError("The directed graph is not a arborescence.")

        roots = [n for n, d in dg.in_degree() if d == 0]
        if not roots:
            raise ValueError("The directetd tree doesn't have a root.")
        elif len(roots) > 1:
            raise ValueError("The directetd tree have more than one root.")
        return roots[0]


def collapse_into_cycle(
    g: MultiDiGraphMap,
    cycle: DiGraphMap,
    root: str,
    node_corresponding: Optional[str] = None,
) -> Tuple[MultiDiGraphMap, str]:
    """Collapse a multi directed graph into a deep cycle.

    In [gabow1986efficient]_, what this function does is summarised as
    contracting the deep cycle into a new (super-) node, which has the
    same name as ``node_corresponding``. Weights of some of the kept
    edges will be modified.

    Note:
        - There are ``(n_c - 1)`` nodes outside the cycle and they are
          the nodes of the new graph.
        - If no node is specified to be kept, the node with index 1 in
          the deep cycle will be chosen.

    Raises:
        KeyError: when the specified corresponding node cannot be found
            in the deep cycle.

    Args:
        g: the original graph.
        cycle: a deep cycle.
        root: the specified root node in the graph.
        node_corresponding: which node in the deep cycle to be kept.
            Default to be None, then the first node will be chosen. It
            is referred to as the node corresponding to the deep cycle.

    Returns:
        The graph collapsed into the deep cycle and the corresponding
        node.
    """
    n = len(g.nodes)
    k = len(cycle.nodes) + 1  # There are (k - 1) nodes in the cycle.
    n_c = n - k + 2

    # 1. Get integer-indexed dict for nodes.
    node_dict_c = {}
    node_dict_c[1] = root

    nodes_all = list(g.nodes)
    nodes_all.remove(root)
    for node in list(cycle.nodes):
        if node != root:
            nodes_all.remove(node)

    for i in range(2, n_c):
        node_dict_c[i] = nodes_all[i - 2]

    # Choose any node from the deep cycle
    if not node_corresponding:
        node_dict_c[n_c] = next(iter(cycle.node_set))
        node_corresponding = next(iter(cycle.node_set))
    else:
        if node_corresponding not in cycle.nodes:
            raise KeyError(
                f"The corresponding node {node_corresponding} must be "
                f"in the deep cycle {cycle};"
            )
        else:
            node_dict_c[n_c] = node_corresponding
            logger.info(
                "The corresponding node is specified to be " f"{node_corresponding};"
            )

    # 2. Get integer-indexed dict for edges.
    edges_c = []
    i = 1
    for edge in g.edge_dict.keys():
        if not (
            g.source_map[edge] in cycle.nodes and g.target_map[edge] in cycle.nodes
        ):
            edges_c.append(edge)
            i += 1

    # 3. Get subsets of nodes.
    subsets = {}
    for i in range(1, n_c):
        subsets[i] = [node_dict_c[i]]
    subsets[n_c] = list(cycle.nodes)

    # 4. Get maps.
    source_map_c = {}
    target_map_c = {}
    weight_map_c = {}
    for e_label in edges_c:
        for key, subset in subsets.items():
            if g.source_map[e_label] in subset:
                source_map_c[e_label] = node_dict_c[key]
                break

        for key, subset in subsets.items():
            if g.target_map[e_label] in subset:
                target_map_c[e_label] = node_dict_c[key]
                break

        if g.target_map[e_label] in cycle.nodes:
            e_label_colliding = cycle.edges_inv_map(
                value=g.target_map[e_label], attrname="target"
            )
            if len(e_label_colliding) != 1:
                logger.error(
                    f"There are {len(e_label_colliding)} colliding"
                    "found instead of one and only one."
                )
            else:
                e_label_colliding = e_label_colliding[0]

            weight_map_c[e_label] = (
                g.weight_map[e_label] - cycle.weight_map[e_label_colliding]
            )
        else:
            weight_map_c[e_label] = g.weight_map[e_label]

    res = MultiDiGraphMap(
        list(node_dict_c.values()), edges_c, source_map_c, target_map_c, weight_map_c
    )

    logger.info(
        f"A collapsed graph with edges {list(res.edge_dict.keys())} is "
        f"created. The corresponding node is {node_corresponding};"
    )
    return res, node_corresponding


class MinSpanSolver:
    """Store variables in max and ranked spanning arborescence problems.

    There are four important methods in this class:

        - Append ``branching``.
        - Update ``forest`` if necessary.
        - Update ``e`` and ``d``.
        - Contract a deep cycle into a super node if possible.

    This class is intended for the solver of ranked spanning
    arborescence, :class:`EstRDF.graph.rank.RankedSpanMax`, as well.

    """

    def __init__(
        self,
        m: DiGraphMap,
        branch: List[str],
        cycles: Dict[str, Set[str]],
        lbd: Dict[str, str],
        forest: nx.DiGraph,
        root: str,
    ):
        """Init using current values.

        Args:
            m: the current graph.
            branch: the current branch.
            cycles: all the nodes in the original graph are keys and
                sets of edges are values.
            lbd: the current lbd. Keys are nodes, and edges are values.
            forest: the current facilitating forest.
            root: the specified root node in the graph.
        """
        self.original = deepcopy(m)
        self.original.name = "original"
        nx.freeze(self.original)

        self.m = deepcopy(m)

        self.m._validate(root)
        self.root = root

        self.branch = branch
        self.cycles = cycles
        self.lbd = lbd
        self.forest = forest

        self.d = math.inf
        self.e = None

    @classmethod
    def from_map(cls, m: MultiDiGraphMap, root: str):
        """Init a solver from a multi directed graph with maps.

        Args:
            m: a mapped directed graph.
            root: the specified root node in the graph.

        Returns:
            An initiated solver for min spanning rooted tree.
        """
        branch = []

        nodes = list(m.nodes)
        if root not in nodes:
            logger.error("The root is incorrectly specified.")
        else:
            nodes.remove(root)
        cycles = {node: [] for node in nodes}

        lbd = {}
        forest = nx.DiGraph()

        res = cls(m, branch, cycles, lbd, forest, root)
        logger.info("A solver for max span arborescence has been initiated.")
        return res

    @property
    def _deep_cycle_contained(self) -> DiGraphMap:
        """Check if current branch contains a deep cycle of current m.

        Returns:
            A contained deep cycle. None if the current branching does
            nnt contain any deep cycle of the graph.
        """
        res = None

        branching = self.m.get_subgraph(self.branch)
        cycles = nx.simple_cycles(nx.DiGraph(branching))

        for nodes_cycle in cycles:
            is_deep, edge_keys = self.m.validate_deep_cycle(nodes_cycle)

            if is_deep:
                res = self.m.get_deep_cycle(nodes_cycle, edge_keys)
                break

        if res:
            logger.debug(
                f"A deep cycle {set(res.edge_dict.keys())} is "
                f"contained by branching {self.branch}"
            )
        return res

    def _append_branching(self, v: Optional[str] = None) -> str:
        """Append with the in-edge of an exposed node with max weight.

        Args:
            v: name of the exposed node. Default to be None.

        Returns:
            An edge appended to the current branching.
        """
        if not v:
            v = self.m.first_node_exposed(self.branch, self.root)
            logger.debug(f'Node "{v}" is to be processed.')

        b = self.m.get_in_edge_with_max_weight(v)
        self.branch.append(b)
        logger.info(f"The branching has been appended, becoming {self.branch};")
        return b

    def _update_forest(self, v: str, b: str):
        """Update forest based on an exposed node and the new edge.

        Args:
            v: name of the exposed node.
            b: name of the new edge in the current branching.
        """
        if not self.cycles[v]:
            self.lbd[v] = b
            self.forest.add_node(b)
        else:
            for f in self.cycles[v]:
                self.forest.add_edge(b, f)

    def process(self, v: str, node_corresponding: Optional[str] = None):
        """Execute the first part of MSA algorithm.

        This method is summarised in [gabow1986efficient]_:

            The first stage begins with no edges selected and in general
            maintains a set of selected edges that defines a forest (set
            of trees). As the stage proceeds, cycles of selected edges
            are formed. Each such cycle is contracted to form a new
            super node. At the end of the phase, all the nodes in the
            graph are contracted into a single node.

        There are three steps in this method:

            - Select an edge and append it to ``branching``.
            - Update ``forest`` if necessary.
            - Contract a deep cycle into a super node if possible.

        Note:
            - Keys in ``lbd`` are nodes and values are edges.
            - Edges are considered when checking if the branching
              contains a deep cycle.

        Args:
            v: name of the exposed node.
            node_corresponding: which node in the deep cycle to be kept.
                Default to be None, then the first node will be chosen.
                It is referred to as the node corresponding to the deep
                cycle.
        """
        b = self._append_branching(v)

        self._update_forest(v, b)

        # If branch contains a deep cycle of m.
        u, a_deep_cycle = self._update_with_deep_cycle(node_corresponding)

        if u and a_deep_cycle:
            self.cycles[u] = {
                data["label"] for _, _, data in a_deep_cycle.edges(data=True)
            }

        logger.debug(f'Node "{v}" has been processed.')

    @property
    def first_node_exposed(self) -> str:
        """Get the first exposed node based on current state.

        See
        :func:`EstRDF.graph.directed.MultiDiGraphMap.first_node_exposed`
        for more detail.

        Returns:
            An exposed node.
        """
        res = self.m.first_node_exposed(self.branch, self.root)
        return res

    def _get_path(self, b: str) -> Dict[int, str]:
        """Gather a path according to a given beginning.

        Args:
            b: the beginning of the path.

        Returns:
            Integer-indexed path from 1 to s.
        """
        begin = b
        end = self.lbd[self.original.target_map[b]]

        res_list = nx.shortest_path(self.forest, begin, end)
        logger.info(f"The path is {res_list};")
        res_dict = {i: res_list[i - 1] for i in range(1, len(res_list) + 1)}
        return res_dict

    def _update_branch(self) -> str:
        """Update the branch and return the edge popped from the branch.

        Returns:
            The edge popped from the branch.
        """
        if self.branch:
            b = self.branch.pop()
            seq = self._get_path(b)

            res = set()
            s = len(seq)
            if s > 1:
                for h in range(2, s + 1):
                    children = dict(
                        nx.bfs_successors(self.forest, source=seq[h - 1], depth_limit=1)
                    )[seq[h - 1]]
                    children.remove(seq[h])
                    res.update(children)
                    self.forest.remove_node(seq[h - 1])

                self.branch.extend(res)

            logger.debug(f"The branching has been updated to {self.branch}.")
            logger.debug(f"The forest has been updated to {list(self.forest.nodes)}.")
        else:
            b = None
            logger.info("The branching is already empty.")

        return b

    def recover_msa(self) -> Set[str]:
        """Recover MSA based on branching and forest in the first stage.

        This method (the second stage to find MSA) is summarised in
        [gabow1986efficient]_:

            The second phase of the algorithm consists of expanding the
            cycles formed during the first phase in reverse order of
            their contraction and discarding one edge from each to form
            a spanning tree in the original graph.

        Returns:
            All the edges in the max spanning arborescence.
        """
        v = self.first_node_exposed
        if not v:
            res = set()
            while True:
                b = self._update_branch()
                if b:
                    res.add(b)
                else:
                    break
        else:
            logger.error(f'There is still a node "{v}" exposed.')
            res = None

        return res

    def _seek(self, b: str, msa: DiGraphMap) -> Tuple[str, float]:
        """Find an edge next to a given edge in the MSA.

        Args:
            b: the given edge. It must be found in the MSA.
            msa: min spanning arborescence of the original graph.

        Returns:
            An edge next to the given edge.
        """
        if b in self.m.edge_dict.keys() and b in msa.edge_dict.keys():
            sources, targets, weights = self.m.maps
            # sources_msa, targets_msa = msa.maps
            sources_raw, targets_raw, _ = self.original.maps
            edge_set = set(self.m.edge_dict.keys())
            edge_set.remove(b)

            f_set = set()
            for f in edge_set:
                if targets[f] == targets[b] and not _is_ancestor(
                    nx.DiGraph(msa), targets_raw[b], sources_raw[f]
                ):
                    f_set.add(f)

            if f_set:
                f_weights = {f: weights[f] for f in f_set}
                res = max(f_weights, key=lambda k: f_weights[k])
                delta = weights[b] - weights[res]
            else:
                res = None
                delta = math.inf

            logger.debug(
                f'An edge "{res}" is found next to {b} and ' f"delta is {delta}."
            )
        else:
            logger.error(f'Given edge "{b}" is not in the graph.')
            res = None
            delta = None

        return res, delta

    def _update_with_deep_cycle(self, node_corresponding: str):
        """Update current graph if branching contains a deep cycle.

        Args:
            node_corresponding: which node in the deep cycle to be kept.

        Returns:
            Corresponding node and the deep cycle if any deep cycle is
            found.
        """
        a_deep_cycle = self._deep_cycle_contained

        if a_deep_cycle:
            for edge in a_deep_cycle.edge_dict.keys():
                self.branch.remove(edge)
            logger.debug(f"The branching has been slimmed to {self.branch}.")

            self.m, u = collapse_into_cycle(
                self.m, a_deep_cycle, self.root, node_corresponding=node_corresponding
            )
        else:
            u = None

        return u, a_deep_cycle

    def process_next(
        self,
        a: DiGraphMap,
        v: str,
        y: Optional[Set[str]] = None,
        node_corresponding: Optional[str] = None,
    ):
        """Process an exposed node in NEXT algorithm.

        Comment in [camerini1980ranking]_:

            Most part of this method is the same as ``process``. The
            main difference consisting in the fact that since ``a`` is
            known, the updating of ``forest`` and the successive
            expansions of ``branch`` are no longer required. Therefore
            NEXT can be efficiently implemented by utilizing the
            bookkeeping mechanisms ([tarjan1977finding]_).

        There are three steps:

            - Append ``branching``.
            - Update ``e`` and ``d``.
            - Contract a deep cycle into a super node if possible.

        Args:
            a: min spanning arborescence of the original graph.
            v: name of the exposed node. Default to be None.
            y: a branching of the original graph. Default to be None.
            node_corresponding: which node in the deep cycle to be kept.
                Default to be None, then the first node will be chosen.
                It's referred to as the node corresponding to the deep
                cycle.
        """
        b = self._append_branching(v)

        if not y:
            y = set()

        edges = {edge for edge in a.edge_dict.keys() if edge not in y}
        if b in edges:
            _, delta = self._seek(b, a)
            if delta < self.d:
                self.e = b
                self.d = delta + 0

        self._update_with_deep_cycle(node_corresponding)

        logger.debug(f'Node "{v}" has been processed.')


def _next_sa(
    raw: nx.DiGraph, a: Arborescence, y: Set[str], z: Set[str]
) -> Tuple[str, float]:
    """Find ``e`` and ``d`` based on a given spanning arborescence.

    Args:
        raw: a directed graph with weights and labels.
        a: previously obtained spanning arborescence.
        y: a branching of the original graph.
        z: a set of edges of the original graph, and these edges are not
            contained in the branching.

    Returns:
        ``e`` and ``d``.
    """
    logger.debug(f"Branching {y} and edges subset {z} are passed.")

    n = MultiDiGraphMap.from_nx(raw)
    m = n.constrain_subgraph(y, z)

    if not a.root:
        logger.error("Root of the previous spanning arborescence is not specified.")
    mss = MinSpanSolver.from_map(m, a.root)

    a = DiGraphMap.from_nx(a)

    v = mss.first_node_exposed
    while v:
        mss.process_next(a, v, y)
        v = mss.first_node_exposed

    if mss.d < 0:
        logger.warning('There is a negative "d".')
    return mss.e, mss.d


def _max_sa(
    n_raw: nx.DiGraph, root: str, branch: Set[str], edges: Set[str]
) -> Arborescence:
    """Find the min spanning arborescence of a directed graph.

    As summarised in [gabow1986efficient]_, there are two stages in this
    algorithm:

        - The first stage finds a set of edges containing a minimum
          spanning tree and some additional edges.
        - The second stage removes the extra edges.

    Warning:
        - This is not an efficient implementation, but will be used in
          the generator for ranking spanning arborescences according to
          their weights.
        - All the edges in the graph must have attribute ``weight``.
        - A different attribute cannot be specified as weights.

    Args:
        n_raw: a multi directed graph.
        root: the specified root node in the graph.
        branch: a branching of the original graph.
        edges: a set of edges of the original graph, and these edges are
            not contained in the branching.

    Returns:
        The min spanning rooted tree.
    """
    logger.debug(f"The pass branching is {branch}.")
    logger.debug(f"The pass edges are {edges}.")

    n = MultiDiGraphMap.from_nx(n_raw)
    m = n.constrain_subgraph(branch, edges)

    # MSA
    mss = MinSpanSolver.from_map(m, root)
    v = mss.first_node_exposed
    while v:
        mss.process(v)
        v = mss.first_node_exposed

    edges_recovered = mss.recover_msa()
    res = mss.original.get_subgraph(edges_recovered)

    res = Arborescence(res)

    if any(edge not in res.df_edges["label"].tolist() for edge in branch):
        logger.error("All edges in the branching should be found in the SA.")
    if any(
        edge not in {e for e in n.edge_dict.keys() if e not in edges}
        for edge in res.df_edges["label"]
    ):
        logger.error(
            "All edges in the SA should be found in original edge set "
            "without passed edges"
        )

    return res


def _is_ancestor(g: nx.DiGraph, source: str, target: str) -> bool:
    """Check if ``source`` is an ancestor of ``target`` in a DG.

    Warning:
        ``source`` and ``target`` must be included in ``g``.

    Args:
        g: a given directed graph.
        source: name of the potential ancestor.
        target: name of a node.

    Returns:
        Whether ``source`` is an ancestor of ``target``.

    """
    if source not in g.nodes:
        logger.error(f'Source "{source}" is not in the graph.')
        path = None
    elif target not in g.nodes:
        logger.error(f'Target "{target}" is not in the graph.')
        path = None
    else:
        path = next(nx.all_simple_paths(g, source, target), None)

    if path:
        res = True
    else:
        res = False
    return res


def _is_reachable(g: nx.DiGraph, root: str) -> bool:
    """Check if all nodes are reachable from a given root.

    ``root`` should be included in ``g``.

    Args:
        g: directed graph.
        root: name of the specified root.

    Returns:
        bool: True if all nodes are reachable from a given root.
    """
    if root not in g.nodes:
        logger.error(f'The root "{root}" is not in the graph.')
        res = False
    else:
        res = True
        nodes = {n for n in g.nodes if n != root}
        for node in nodes:
            if not _is_ancestor(g, root, node):
                logger.error(f"Node {node} is not reachable from {root}.")
                res = False
    return res


class DescendSpanningArborescences:
    """
    Generator to descend spanning arborescences by total edge weights.

    A tuple for a spanning arborescence and its rank every time is
    returned in each iteration.

    A list of tuples, ``p_list``, is maintained during the iteration.
    There are two steps in each iteration:

        - Take out the tuple with the max weight and find the max
          spanning arborescence based on the graph constrained by
          parameters in this tuple. The weight of this tuple is the
          weight of the max spanning arborescence.
        - Append two new tuples to the list.

    Attributes:

        root (str): name of the node which is set as root.
        raw (MultiDiGraphMap): the original directed graph.
        msa (Arborescence): the max spanning arborescence.
        rank (int): rank of the current spanning arborescence.
        p_list (List[tuple]): sorted list of tuples storing candidate
            spanning arborescences that might be used in future
            iteration.

    """

    _threshold = 1e-4

    def __init__(self, g: nx.DiGraph, root: str):
        """Init a generator to descend weighted spanning arborescences.
        Args:
            g: a directed graph with weighted edges.
            root: specified root of spanning arborescences.
        """
        self.root = root
        self.raw = MultiDiGraphMap.from_nx(g)
        nx.freeze(self.raw)

        _is_reachable(self.raw, self.root)

        # Check if there is edge directed into the root.
        edges_to_root = set(self.raw.in_edges(self.root))
        if edges_to_root:
            logger.error(f"There are edges, {edges_to_root}, directed into root.")

        self.msa = _max_sa(self.raw, self.root, set(), set())
        logger.success(
            "Min spanning arborescence has weight "
            f'{self.msa.size(weight="weight")}.'
            # f'It has edges {self.msa.df_edges.loc[:, "label"].to_list()} .'
        )

        e, d = _next_sa(self.raw, self.msa, set(), set())
        self.p_list = [
            _ResultRank(self.msa.size(weight="weight") - d, e, self.msa, set(), set())
        ]  # Index will be used later, so a list is required.

        self.rank = 1
        self._last = self.msa.size(weight="weight")
        """float: graph weight of the SA with lower rank."""

    def __iter__(self):  # noqa: D105
        return self

    def __next__(self) -> Tuple[Arborescence, int]:
        """Get a spanning arborescence with higher rank and less weight.

        Raises:
            StopIteration: when there is no more spanning arborescence.

        Returns:
            A spanning arborescence and its rank.
        """
        # Select a _ResultRank with max w.
        idx_max = np.argmax([rr.w for rr in self.p_list])
        pre = self.p_list.pop(idx_max)

        if pre.w == -math.inf:
            logger.warning("All the spanning arborescences have been returned.")
            raise StopIteration()
        else:
            y_prime = pre.y.copy()
            y_prime.add(pre.e)
            z_prime = pre.z.copy()
            z_prime.add(pre.e)

            a_current = _max_sa(self.raw, self.root, pre.y, z_prime)
            self.rank += 1
            logger.success(
                f"SA ranks {self.rank} with weight "
                f'{a_current.size(weight="weight")}.'
                # f'Edges {a_current[j].df_edges.loc[:, "label"].to_list()} .'
            )

            # Check if the total weight is decreased.
            if a_current.size(weight="weight") > self._last:
                logger.error("Increasing total weight.")
            self._last = a_current.size(weight="weight")

            # Check if the total weight is the same as expected.
            if abs(a_current.size(weight="weight") - pre.w) >= self._threshold:
                logger.error(
                    f'Weight of the SA, {a_current.size(weight="weight")}, is '
                    f"different from the expected value, {pre.w}."
                )

            # Check if there is edge directed into the root.
            edges_to_root = set(a_current.in_edges(self.root))
            if edges_to_root:
                logger.error(f"There are edges, {edges_to_root}, directed into root.")

            e, d = _next_sa(self.raw, pre.a, y_prime, pre.z)
            self.p_list.append(
                _ResultRank(
                    pre.a.size(weight="weight") - d,
                    e,
                    pre.a,
                    y_prime,
                    pre.z,
                )
            )

            e, d = _next_sa(self.raw, a_current, pre.y, z_prime)
            self.p_list.append(
                _ResultRank(
                    pre.w - d,
                    e,
                    a_current,
                    pre.y,
                    z_prime,
                )
            )

            return a_current, self.rank
