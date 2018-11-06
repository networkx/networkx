#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
****************
ISMAGS Algorithm
****************

Provides a Python implementation of the ISMAGS algorithm. [1]_

It is capable of finding (subgraph) isomorphisms between two graphs, taking the
symmetry of the subgraph into account. In most cases the VF2 algorithm is
faster (at least on small graphs) than this implementation, but in some cases
there is an exponential number of isomorphisms that are symmetrically
equivalent. In that case, the ISMAGS algorithm will provide only one solution
per symmetry group.

In addition, this implementation also provides an interface to find the
largest common induced subgraph [2]_ between any two graphs, again taking
symmetry into account. Given `graph` and `subgraph` the algorithm will remove
nodes from the `subgraph` until `subgraph` is isomorphic to a subgraph of
`graph`. Since only the symmetry of `subgraph` is taken into account it is
worth thinking about how you provide your graphs:

>>> graph1 = nx.path_graph(4)
>>> graph2 = nx.star_graph(3)
>>> ismags = isomorphism.ISMAGS(graph1, graph2)
>>> ismags.is_isomorphic()
False
>>> list(ismags.largest_common_subgraph())
[{1: 0, 0: 1, 2: 2}, {2: 0, 1: 1, 3: 2}]
>>> ismags2 = isomorphism.ISMAGS(graph2, graph1)
>>> list(ismags2.largest_common_subgraph())
[{1: 0, 0: 1, 2: 2},
 {1: 0, 0: 1, 3: 2},
 {2: 0, 0: 1, 1: 2},
 {2: 0, 0: 1, 3: 2},
 {3: 0, 0: 1, 1: 2},
 {3: 0, 0: 1, 2: 2}]

However, when not taking symmetry into account, it doesn't matter:

>>> list(ismags.largest_common_subgraph(symmetry=False))
[{1: 0, 0: 1, 2: 3},
 {1: 0, 2: 1, 0: 3},
 {2: 0, 1: 1, 3: 3},
 {2: 0, 3: 1, 1: 3},
 {1: 0, 0: 2, 2: 3},
 {1: 0, 2: 2, 0: 3},
 {2: 0, 1: 2, 3: 3},
 {2: 0, 3: 2, 1: 3},
 {1: 0, 0: 1, 2: 2},
 {1: 0, 2: 1, 0: 2},
 {2: 0, 1: 1, 3: 2},
 {2: 0, 3: 1, 1: 2}]
>>> list(ismags2.largest_common_subgraph(symmetry=False))
[{1: 0, 0: 1, 2: 3},
 {1: 0, 2: 1, 0: 3},
 {2: 0, 1: 1, 3: 3},
 {2: 0, 3: 1, 1: 3},
 {1: 0, 0: 2, 2: 3},
 {1: 0, 2: 2, 0: 3},
 {2: 0, 1: 2, 3: 3},
 {2: 0, 3: 2, 1: 3},
 {1: 0, 0: 1, 2: 2},
 {1: 0, 2: 1, 0: 2},
 {2: 0, 1: 1, 3: 2},
 {2: 0, 3: 1, 1: 2}]

Notes
-----
 - The current implementation works for undirected graphs only. The algorithm
   in general should work for directed graphs as well though.
 - Node keys for both provided graphs need to be fully orderable as well as
   hashable.
 - Node and edge equality is assumed to be transitive: if A is equal to B, and
   B is equal to C, then A is equal to C.

References
----------
    .. [1] M. Houbraken, S. Demeyer, T. Michoel, P. Audenaert, D. Colle,
       M. Pickavet, "The Index-Based Subgraph Matching Algorithm with General
       Symmetries (ISMAGS): Exploiting Symmetry for Faster Subgraph
       Enumeration", PLoS One 9(5): e97896, 2014.
       https://doi.org/10.1371/journal.pone.0097896
    .. [2] https://en.wikipedia.org/wiki/Maximum_common_induced_subgraph
"""

__author__ = 'P C Kroon (p.c.kroon@rug.nl)'
__all__ = ['ISMAGS']

from collections import defaultdict
from functools import reduce, wraps
import itertools


def are_all_equal(iterable):
    """
    Returns ``True`` if and only if all elements in `iterable` are equal; and
    ``False`` otherwise.

    Parameters
    ----------
    iterable: collections.abc.Iterable
        The container whose elements will be checked.

    Returns
    -------
    bool
        ``True`` iff all elements in `iterable` compare equal, ``False``
        otherwise.
    """
    try:
        shape = iterable.shape
    except AttributeError:
        pass
    else:
        if len(shape) > 1:
            message = 'The function does not works on multidimension arrays.'
            raise NotImplementedError(message) from None

    iterator = iter(iterable)
    first = next(iterator, None)
    return all(item == first for item in iterator)


def make_partitions(items, test):
    """
    Partitions items into sets based on the outcome of ``test(item1, item2)``.
    Pairs of items for which `test` returns `True` end up in the same set.

    Parameters
    ----------
    items : collections.abc.Iterable[collections.abc.Hashable]
        Items to partition
    test : collections.abc.Callable[collections.abc.Hashable, collections.abc.Hashable]
        A function that will be called with 2 arguments, taken from items.
        Should return `True` if those 2 items need to end up in the same
        partition, and `False` otherwise.

    Returns
    -------
    list[set]
        A list of sets, with each set containing part of the items in `items`,
        such that ``all(test(*pair) for pair in  itertools.combinations(set, 2))
        == True``

    Notes
    -----
    The function `test` is assumed to be transitive: if ``test(a, b)`` and
    ``test(b, c)`` return ``True``, then ``test(a, c)`` must also be ``True``.
    """
    partitions = []
    for item in items:
        for partition in partitions:
            p_item = next(iter(partition))
            if test(item, p_item):
                partition.add(item)
                break
        else:  # No break
            partitions.append(set((item,)))
    return partitions


def partition_to_color(partitions):
    """
    Creates a dictionary with for every item in partition for every partition
    in partitions the index of partition in partitions.

    Parameters
    ----------
    partitions: collections.abc.Sequence[collections.abc.Iterable]
        As returned by :func:`make_partitions`.

    Returns
    -------
    dict
    """
    colors = dict()
    for color, keys in enumerate(partitions):
        for key in keys:
            colors[key] = color
    return colors


def intersect(collection_of_sets):
    """
    Given an collection of sets, returns the intersection of those sets.

    Parameters
    ----------
    collection_of_sets: collections.abc.Collection[set]
        A collection of sets.

    Returns
    -------
    set
        An intersection of all sets in `collection_of_sets`. Will have the same
        type as the item initially taken from `collection_of_sets`.
    """
    collection_of_sets = list(collection_of_sets)
    first = collection_of_sets.pop()
    out = reduce(set.intersection, collection_of_sets, set(first))
    return type(first)(out)


class ISMAGS:
    """
    Implements the ISMAGS subgraph matching algorith. [1]_ ISMAGS stands for
    "Index-based Subgraph Matching Algorithm with General Symmetries". As the
    name implies, it is symmetry aware and will only generate non-symmetric
    isomorphisms.

    Notes
    -----
    The implementation imposes additional conditions compared to the VF2
    algorithm on the graphs provided and the comparison functions
    (:attr:`node_equality` and :attr:`edge_equality`):

     - Node keys in both graphs must be orderable as well as hashable.
     - Equality must be transitive: if A is equal to B, and B is equal to C,
       then A must be equal to C.

    Attributes
    ----------
    graph: networkx.Graph
    subgraph: networkx.Graph
    node_equality: collections.abc.Callable
        The function called to see if two nodes should be considered equal.
        It's signature looks like this:
        ``f(graph1: networkx.Graph, node1, graph2: networkx.Graph, node2) -> bool``.
        `node1` is a node in `graph1`, and `node2` a node in `graph2`.
        Constructed from the argument `node_match`.
    edge_equality: collections.abc.Callable
        The function called to see if two edges should be considered equal.
        It's signature looks like this:
        ``f(graph1: networkx.Graph, edge1, graph2: networkx.Graph, edge2) -> bool``.
        `edge1` is an edge in `graph1`, and `edge2` an edge in `graph2`.
        Constructed from the argument `edge_match`.

    References
    ----------
    .. [1] M. Houbraken, S. Demeyer, T. Michoel, P. Audenaert, D. Colle,
       M. Pickavet, "The Index-Based Subgraph Matching Algorithm with General
       Symmetries (ISMAGS): Exploiting Symmetry for Faster Subgraph
       Enumeration", PLoS One 9(5): e97896, 2014.
       https://doi.org/10.1371/journal.pone.0097896
    """
    def __init__(self, graph, subgraph, node_match=None, edge_match=None):
        """
        Parameters
        ----------
        graph: networkx.Graph
        subgraph: networkx.Graph
        node_match: collections.abc.Callable
            Function used to determine whether two nodes are equivalent. It's
            signature should look like ``f(n1: dict, n2: dict) -> bool``, with
            `n1` and `n2` node property dicts. See also
            :func:`~networkx.algorithms.isomorphism.categorical_node_match` and
            friends.
        edge_match: collections.abc.Callable
            Function used to determine whether two edges are equivalent. It's
            signature should look like ``f(e1: dict, e2: dict) -> bool``, with
            `e1` and `e2` edge property dicts. See also
            :func:`~networkx.algorithms.isomorphism.categorical_edge_match` and
            friends.
        """
        # TODO: graph and subgraph setter methods that invalidate the caches.
        # TODO: allow for precomputed partitions and colors
        self.graph = graph
        self.subgraph = subgraph

        self._sgn_partitions_ = None
        self._sge_partitions_ = None

        self._sgn_colors_ = None
        self._sge_colors_ = None

        self._gn_partitions_ = None
        self._ge_partitions_ = None

        self._gn_colors_ = None
        self._ge_colors_ = None

        self._node_compat_ = None
        self._edge_compat_ = None

        self._symmetry_cache = {}

        if node_match is None:
            self.node_equality = self._node_match_maker(lambda n1, n2: True)
            self._sgn_partitions_ = [set(self.subgraph.nodes)]
            self._gn_partitions_ = [set(self.graph.nodes)]
            self._node_compat_ = {0: 0}
        else:
            self.node_equality = self._node_match_maker(node_match)
        if edge_match is None:
            self.edge_equality = self._edge_match_maker(lambda e1, e2: True)
            self._sge_partitions_ = [set(self.subgraph.edges)]
            self._ge_partitions_ = [set(self.graph.edges)]
            self._edge_compat_ = {0: 0}
        else:
            self.edge_equality = self._edge_match_maker(edge_match)

    @property
    def _sgn_partitions(self):
        if self._sgn_partitions_ is None:
            def nodematch(node1, node2):
                return self.node_equality(self.subgraph, node1, self.subgraph, node2)
            self._sgn_partitions_ = make_partitions(self.subgraph.nodes, nodematch)
        return self._sgn_partitions_

    @property
    def _sge_partitions(self):
        if self._sge_partitions_ is None:
            def edgematch(edge1, edge2):
                return self.edge_equality(self.subgraph, edge1, self.subgraph, edge2)
            self._sge_partitions_ = make_partitions(self.subgraph.edges, edgematch)
        return self._sge_partitions_

    @property
    def _gn_partitions(self):
        if self._gn_partitions_ is None:
            def nodematch(node1, node2):
                return self.node_equality(self.graph, node1, self.graph, node2)
            self._gn_partitions_ = make_partitions(self.graph.nodes, nodematch)
        return self._gn_partitions_

    @property
    def _ge_partitions(self):
        if self._ge_partitions_ is None:
            def edgematch(edge1, edge2):
                return self.edge_equality(self.graph, edge1, self.graph, edge2)
            self._ge_partitions_ = make_partitions(self.graph.edges, edgematch)
        return self._ge_partitions_

    @property
    def _sgn_colors(self):
        if self._sgn_colors_ is None:
            self._sgn_colors_ = partition_to_color(self._sgn_partitions)
        return self._sgn_colors_

    @property
    def _sge_colors(self):
        if self._sge_colors_ is None:
            self._sge_colors_ = partition_to_color(self._sge_partitions)
        return self._sge_colors_

    @property
    def _gn_colors(self):
        if self._gn_colors_ is None:
            self._gn_colors_ = partition_to_color(self._gn_partitions)
        return self._gn_colors_

    @property
    def _ge_colors(self):
        if self._ge_colors_ is None:
            self._ge_colors_ = partition_to_color(self._ge_partitions)
        return self._ge_colors_

    @property
    def _node_compatibility(self):
        if self._node_compat_ is not None:
            return self._node_compat_
        self._node_compat_ = {}
        for sgn_part_color, gn_part_color in itertools.product(range(len(self._sgn_partitions)),
                                                               range(len(self._gn_partitions))):
            sgn = next(iter(self._sgn_partitions[sgn_part_color]))
            gn = next(iter(self._gn_partitions[gn_part_color]))
            if self.node_equality(self.subgraph, sgn, self.graph, gn):
                self._node_compat_[sgn_part_color] = gn_part_color
        return self._node_compat_

    @property
    def _edge_compatibility(self):
        if self._edge_compat_ is not None:
            return self._edge_compat_
        self._edge_compat_ = {}
        for sge_part_color, ge_part_color in itertools.product(range(len(self._sge_partitions)),
                                                               range(len(self._ge_partitions))):
            sge = next(iter(self._sge_partitions[sge_part_color]))
            ge = next(iter(self._ge_partitions[ge_part_color]))
            if self.edge_equality(self.subgraph, sge, self.graph, ge):
                self._edge_compat_[sge_part_color] = ge_part_color
        return self._edge_compat_

    @staticmethod
    def _node_match_maker(cmp):
        @wraps(cmp)
        def comparer(graph1, node1, graph2, node2):
            return cmp(graph1.nodes[node1], graph2.nodes[node2])
        return comparer

    @staticmethod
    def _edge_match_maker(cmp):
        @wraps(cmp)
        def comparer(graph1, edge1, graph2, edge2):
            return cmp(graph1.edges[edge1], graph2.edges[edge2])
        return comparer

    def find_subgraphs(self, symmetry=True):
        """
        Find all subgraph isomorphisms between :attr:`subgraph` <=
        :attr:`graph`.

        Parameters
        ----------
        symmetry: bool
            Whether symmetry should be taken into account. If False, found
            isomorphisms may be symmetrically equivalent.

        Yields
        ------
        dict
            The found isomorphism mappings of {graph_node: subgraph_node}.
        """
        # The networkx VF2 algorithm is slightly funny in when it yields an
        # empty dict and when not.
        if not self.subgraph:
            yield {}
            return
        elif not self.graph:
            return
        elif len(self.graph) < len(self.subgraph):
            return

        if symmetry:
            _, cosets = self.analyze_symmetry(self.subgraph,
                                              self._sgn_partitions,
                                              self._sge_colors)
            constraints = self._make_constraints(cosets)
        else:
            constraints = []

        candidates = self._find_nodecolor_candidates()

        if any(candidates.values()):
            start_sgn = min(candidates, key=lambda n: min(candidates[n], key=len))
            candidates[start_sgn] = (intersect(candidates[start_sgn]),)
            yield from self._map_nodes(start_sgn, candidates, constraints)
        else:
            return

    def largest_common_subgraph(self, symmetry=True):
        """
        Find the largest common induced subgraphs between :attr:`subgraph` and
        :attr:`graph`.

        Parameters
        ----------
        symmetry: bool
            Whether symmetry should be taken into account. If False, found
            largest common subgraphs may be symmetrically equivalent.

        Yields
        ------
        dict
            The found isomorphism mappings of {graph_node: subgraph_node}.
        """
        # The networkx VF2 algorithm is slightly funny in when it yields an
        # empty dict and when not.
        if not self.subgraph:
            yield {}
            return
        elif not self.graph:
            return

        if symmetry:
            _, cosets = self.analyze_symmetry(self.subgraph,
                                              self._sgn_partitions,
                                              self._sge_colors)
            constraints = self._make_constraints(cosets)
        else:
            constraints = []

        candidates = self._find_nodecolor_candidates()

        if any(candidates.values()):
            yield from self._largest_common_subgraph(candidates, constraints)
        else:
            return

    def analyze_symmetry(self, graph, node_partitions, edge_colors):
        """
        Find a minimal set of permutations and corresponding co-sets that
        describe the symmetry of :attr:`subgraph`.

        Returns
        -------
        tuple[set[frozenset], dict]
            The found permutations and co-sets. Permutations is a set of
            frozenset of pairs of node keys which can be exchanged without
            changing :attr:`subgraph`. The co-sets is a dictionary of node key:
            set of node keys. Every key, value describes which values can be
            interchanged while keeping all nodes less than the key the same.
        """
        key = hash((tuple(graph.nodes), tuple(graph.edges),
                    tuple(map(tuple, node_partitions)), tuple(edge_colors.items())))
        if key in self._symmetry_cache:
            return self._symmetry_cache[key]
        node_partitions = self._refine_node_partitions(graph,
                                                       node_partitions,
                                                       edge_colors)
        permutations, cosets = self._process_opp(graph,
                                                 node_partitions,
                                                 node_partitions,
                                                 edge_colors)
        self._symmetry_cache[key] = permutations, cosets
        return permutations, cosets

    def is_isomorphic(self, symmetry=False):
        """
        Returns True if :attr:`graph` is isomorphic to :attr:`subgraph` and
        False otherwise.

        Returns
        -------
        bool
        """
        return len(self.subgraph) == len(self.graph) and self.subgraph_is_isomorphic(symmetry)

    def subgraph_is_isomorphic(self, symmetry=False):
        """
        Returns True if a subgraph of :attr:`graph` is isomorphic to
        :attr:`subgraph` and False otherwise.

        Returns
        -------
        bool
        """
        # symmetry=False, since we only need to know whether there is any
        # example; figuring out all symmetry elements probably costs more time
        # than it gains.
        isom = next(self.find_subgraphs(symmetry=symmetry), None)
        return isom is not None

    def isomorphisms_iter(self, symmetry=True):
        if len(self.graph) == len(self.subgraph):
            yield from self.subgraph_isomorphisms_iter()

    def subgraph_isomorphisms_iter(self, symmetry=True):
        return self.find_subgraphs(symmetry)

    def _find_nodecolor_candidates(self):
        """
        Per node in subgraph find all nodes in graph that have the same color.
        """
        candidates = defaultdict(set)
        for sgn in self.subgraph.nodes:
            sgn_color = self._sgn_colors[sgn]
            if sgn_color in self._node_compatibility:
                gn_color = self._node_compatibility[sgn_color]
                candidates[sgn].add(frozenset(self._gn_partitions[gn_color]))
            else:
                candidates[sgn].add(frozenset())
        candidates = dict(candidates)
        for sgn, options in candidates.items():
            candidates[sgn] = frozenset(options)
        return candidates

    @staticmethod
    def _make_constraints(cosets):
        """
        Turn cosets into constraints.
        """
        constraints = []
        for node_i, node_ts in cosets.items():
            for node_t in node_ts:
                if node_i != node_t:
                    # Node i must be smaller then node t.
                    constraints.append((node_i, node_t))
        return constraints

    @staticmethod
    def _find_node_edge_color(graph, node_colors, edge_colors):
        """
        For every node in graph, come up with a color that combines 1) the
        color of the node, and 2) the number of edges of a color to each type
        of node.
        """
        counts = defaultdict(lambda: defaultdict(int))
        for node1, node2 in graph.edges:
            if (node1, node2) in edge_colors:
                # FIXME directed graphs
                ecolor = edge_colors[node1, node2]
            else:
                ecolor = edge_colors[node2, node1]
            # Count per node how many edges it has of what color to nodes of
            # what color
            counts[node1][ecolor, node_colors[node2]] += 1
            counts[node2][ecolor, node_colors[node1]] += 1

        node_edge_colors = dict()
        for node in graph.nodes:
            node_edge_colors[node] = node_colors[node], set(counts[node].items())

        return node_edge_colors

    @classmethod
    def _refine_node_partitions(cls, graph, node_partitions, edge_colors):
        """
        Given a partition of nodes in graph, make the partitions smaller such
        that all nodes in a partition have 1) the same color, and 2) the same
        number of edges to specific other partitions.
        """
        def equal_color(node1, node2):
            return node_edge_colors[node1] == node_edge_colors[node2]

        while True:
            node_colors = partition_to_color(node_partitions)
            node_edge_colors = cls._find_node_edge_color(graph, node_colors, edge_colors)
            to_refine = any(not are_all_equal(node_edge_colors[node] for node in nodes)
                            for nodes in node_partitions)
            if not to_refine:
                break
            # Preserve the original order of the partitions where valid
            node_partitions = make_partitions((n for p in node_partitions for n in p), equal_color)
        return node_partitions

    def _edges_of_same_color(self, sgn1, sgn2):
        """
        Returns all edges in :attr:`graph` that have the same colour as the
        edge between sgn1 and sgn2 in :attr:`subgraph`.
        """
        if (sgn1, sgn2) in self._sge_colors:
            # FIXME directed graphs
            sge_color = self._sge_colors[sgn1, sgn2]
        else:
            sge_color = self._sge_colors[sgn2, sgn1]
        if sge_color in self._edge_compatibility:
            ge_color = self._edge_compatibility[sge_color]
            g_edges = self._ge_partitions[ge_color]
        else:
            g_edges = []
        return g_edges

    def _map_nodes(self, sgn, candidates, constraints, mapping=None, to_be_mapped=None):
        """
        Find all subgraph isomorphisms honoring constraints.
        """
        if mapping is None:
            mapping = {}
        else:
            mapping = mapping.copy()
        if to_be_mapped is None:
            to_be_mapped = set(self.subgraph.nodes)

        # Note, we modify candidates here. Doesn't seem to affect results, but
        # remember this.
        #candidates = candidates.copy()
        sgn_candidates = intersect(candidates[sgn])
        candidates[sgn] = frozenset([sgn_candidates])
        for gn in sgn_candidates:
            # We're going to try to map sgn to gn.

            # First, let's see if that would violate a constraint.
            # It's probably better to integrate the constraints infinding the
            # candidates below, *and* somehow propagating them. That *should*
            # reduce the search space. Of course it won't matter for asymmetric
            # subgraphs.
            violation = False
            for constraint in constraints:
                low, high = constraint
                # gn violates upper bound
                too_high = low == sgn and high in mapping and gn > mapping[high]
                # gn violates lower bound
                too_low = high == sgn and low in mapping and gn < mapping[low]
                if too_high or too_low:
                    violation = True
                    break
            if violation or (gn in mapping.values()) or (sgn not in to_be_mapped):
                # This either violates a constraint, or gn is already mapped to
                # something
                # Don't measure coverage for this line.
                # See https://github.com/nedbat/coveragepy/issues/198
                continue  # pragma: no cover

            # REDUCTION and COMBINATION
            mapping[sgn] = gn
            # BASECASE
            if to_be_mapped == set(mapping.keys()):
                yield {v: k for k, v in mapping.items()}
                continue

            new_candidates = candidates.copy()
            sgn_neighbours = self.subgraph[sgn]
            not_gn_neighbours = set(self.graph.nodes) - set(self.graph[gn])
            for sgn2 in self.subgraph:
                if sgn2 not in sgn_neighbours:
                    gn2_options = not_gn_neighbours
                else:
                    # Get all edges to gn of the right color:
                    g_edges = self._edges_of_same_color(sgn, sgn2)
                    # FIXME directed graphs
                    # And all nodes involved in those which are connected to gn
                    gn2_options = {n for e in g_edges for n in e if gn in e}
                # Node color compatibility should be taken care of by the
                # initial candidate lists made by find_subgraphs

                # Add gn2_options to the right collection. Since new_candidates
                # is a dict of frozensets of frozensets of node indices it's
                # a bit clunky. We can't do .add, and + also doesn't work. We
                # could do |, but I deem union to be clearer.
                new_candidates[sgn2] = new_candidates[sgn2].union([frozenset(gn2_options)])
            # The next node is the one that is unmapped and has fewest
            # candidates
            # Pylint disables because it's a one-shot function.
            next_sgn = min(to_be_mapped - set(mapping.keys()),
                           key=lambda n: min(new_candidates[n], key=len))  # pylint: disable=cell-var-from-loop
            yield from self._map_nodes(next_sgn,
                                       new_candidates,
                                       constraints,
                                       mapping=mapping,
                                       to_be_mapped=to_be_mapped)
            # Unmap sgn-gn. Strictly not necessary since it'd get overwritten
            # when making a new mapping for sgn.
            #del mapping[sgn]

    def _largest_common_subgraph(self, candidates, constraints,
                                 to_be_mapped=None):
        """
        Find all largest common subgraphs honoring constraints.
        """
        if to_be_mapped is None:
            to_be_mapped = {frozenset(self.subgraph.nodes)}

        # The LCS problem is basically a repeated subgraph isomorphism problem
        # with smaller and smaller subgraphs. We store the nodes that are
        # "part of" the subgraph in to_be_mapped, and we make it a little
        # smaller every iteration.

        # pylint disable becuase it's guarded against by default value
        current_size = len(next(iter(to_be_mapped), []))  # pylint: disable=stop-iteration-return

        found_iso = False
        if current_size <= len(self.graph):
            # There's no point in trying to find isomorphisms of
            # graph >= subgraph if subgraph has more nodes than graph.

            for nodes in to_be_mapped:
                # Find the isomorphism between subgraph[to_be_mapped] <= graph
                next_sgn = min(nodes, key=lambda n: min(candidates[n], key=len))
                isomorphs = self._map_nodes(next_sgn, candidates, constraints,
                                            to_be_mapped=nodes)

                # This is effectively `yield from isomorphs`, except that we look
                # whether an item was yielded.
                try:
                    item = next(isomorphs)
                except StopIteration:
                    pass
                else:
                    yield item
                    yield from isomorphs
                    found_iso = True

        # BASECASE
        if found_iso or current_size == 1:
            # Shrinking has no point because either 1) we end up with a smaller
            # common subgraph (and we want the largest), or 2) there'll be no
            # more subgraph.
            return

        left_to_be_mapped = set()
        for nodes in to_be_mapped:
            for sgn in nodes:
                # We're going to remove sgn from to_be_mapped, but subject to
                # symmetry constraints. We know that for every constraint we
                # have those subgraph nodes are equal. So whenever we would
                # remove the lower part of a constraint, remove the higher
                # instead. This is all dealth with by _remove_node. And because
                # left_to_be_mapped is a set, we don't do double work.

                # And finally, make the subgraph one node smaller.
                # REDUCTION
                new_nodes = self._remove_node(sgn, nodes, constraints)
                left_to_be_mapped.add(new_nodes)
        # COMBINATION
        yield from self._largest_common_subgraph(candidates, constraints,
                                                 to_be_mapped=left_to_be_mapped)

    @staticmethod
    def _remove_node(node, nodes, constraints):
        """
        Returns a new set where node has been removed from nodes, subject to
        symmetry constraints. We know, that for every constraint we have
        those subgraph nodes are equal. So whenever we would remove the
        lower part of a constraint, remove the higher instead.
        """
        while True:
            for low, high in constraints:
                if low == node and high in nodes:
                    node = high
                    break
            else:  # no break, couldn't find node in constraints
                break
        return frozenset(nodes - {node})

    @staticmethod
    def _find_permutations(top_partitions, bottom_partitions):
        """
        Return the pairs of top/bottom partitions where the partitions are
        different. Ensures that all partitions in both top and bottom
        partitions have size 1.
        """
        # Find permutations
        permutations = set()
        for top, bot in zip(top_partitions, bottom_partitions):
            # top and bot have only one element
            if len(top) != 1 or len(bot) != 1:
                raise IndexError("Not all nodes are coupled. This is"
                                 " impossible: {}, {}".format(top_partitions,
                                                              bottom_partitions))
            if top != bot:
                permutations.add(frozenset((next(iter(top)), next(iter(bot)))))
        return permutations

    @staticmethod
    def _update_orbits(orbits, permutations):
        """
        Update orbits based on permutations. Orbits is modified in place.
        For every pair of items in permutations their respective orbits are
        merged.
        """
        for permutation in permutations:
            node, node2 = permutation
            # Find the orbits that contain node and node2, and replace the
            # orbit containing node with the union
            first = second = None
            for idx, orbit in enumerate(orbits):
                if first is not None and second is not None:
                    break
                if node in orbit:
                    first = idx
                if node2 in orbit:
                    second = idx
            if first != second:
                orbits[first].update(orbits[second])
                del orbits[second]

    @staticmethod
    def _find_coupled_nodes(top_partitions, bottom_partitions):
        """
        Find all nodes in top and bottom partitions that are coupled. These
        are nodes that are in their own partition in both top and bottom.
        """
        coupled = {}
        for top, bot in zip(top_partitions, bottom_partitions):
            if len(top) == len(bot) == 1:
                coupled[next(iter(top))] = next(iter(bot))
        return coupled

    def _couple_nodes(self, top_partitions, bottom_partitions, pair_idx,
                      t_node, b_node, graph, edge_colors):
        """
        Generate new partitions from top and bottom_partitions where t_node is
        coupled to b_node. pair_idx is the index of the partitions where t_ and
        b_node can be found.
        """
        t_partition = top_partitions[pair_idx]
        b_partition = bottom_partitions[pair_idx]
        assert t_node in t_partition and b_node in b_partition
        # Couple node to node2. This means they get their own partition
        new_top_partitions = [top.copy() for top in top_partitions]
        new_bottom_partitions = [bot.copy() for bot in bottom_partitions]
        new_t_groups = {t_node}, t_partition - {t_node}
        new_b_groups = {b_node}, b_partition - {b_node}
        # Replace the old partitions with the coupled ones
        del new_top_partitions[pair_idx]
        del new_bottom_partitions[pair_idx]
        new_top_partitions[pair_idx:pair_idx] = new_t_groups
        new_bottom_partitions[pair_idx:pair_idx] = new_b_groups

        new_top_partitions = self._refine_node_partitions(graph,
                                                          new_top_partitions,
                                                          edge_colors)
        new_bottom_partitions = self._refine_node_partitions(graph,
                                                             new_bottom_partitions,
                                                             edge_colors)
        # We collect the nodes that are coupled so we can use it as a
        # sanity check.
        coupled = self._find_coupled_nodes(new_top_partitions, new_bottom_partitions)
        # Sort the partitions by size. This works by the grace that sort
        # is stable. We do this so we can deal with partitions like this:
        # [{4}, {5, 6}, {0}, {1}, {3}, {2}] [{0, 4}, {5}, {6}, {1}, {3}, {2}]
        # We need to do this, because _refine_node_partitions doesn't (can't?)
        # keep the order sane and produces the example partitions above.
        new_top_partitions = sorted(new_top_partitions, key=len)
        new_bottom_partitions = sorted(new_bottom_partitions, key=len)
        new_coupled = self._find_coupled_nodes(new_top_partitions, new_bottom_partitions)
        # Make sure coupled <= new_coupled. This means that everything
        # that was coupled still is. There may be more items coupled now
        # though, and that's fine.
        assert all(new_coupled[k] == v for k, v in coupled.items())
        return new_top_partitions, new_bottom_partitions

    def _process_opp(self, graph, top_partitions, bottom_partitions,
                     edge_colors, orbits=None, cosets=None):
        """
        Processes ordered pair partitions as per the reference paper. Finds and
        returns all permutations and cosets that leave the graph unchanged.
        """
        if orbits is None:
            orbits = [{node} for node in graph.nodes]
        else:
            # Note that we don't copy orbits when we are given one. This means
            # we leak information between the recursive branches. This is
            # intentional!
            orbits = orbits
        if cosets is None:
            cosets = {}
        else:
            cosets = cosets.copy()

        assert all(len(t_p) == len(b_p) for t_p, b_p in zip(top_partitions, bottom_partitions))

        # BASECASE
        if all(len(top) == 1 for top in top_partitions):
            # All nodes are mapped
            permutations = self._find_permutations(top_partitions, bottom_partitions)
            self._update_orbits(orbits, permutations)
            if permutations:
                return [permutations], cosets
            else:
                return [], cosets

        permutations = []
        unmapped_nodes = {(node, idx)
                          for idx, t_partition in enumerate(top_partitions)
                          for node in t_partition if len(t_partition) > 1}
        node, pair_idx = min(unmapped_nodes)
        b_partition = bottom_partitions[pair_idx]

        for node2 in sorted(b_partition):
            if len(b_partition) == 1:
                # Can never result in symmetry
                continue
            if node != node2 and any(node in orbit and node2 in orbit for orbit in orbits):
                # Orbit prune branch
                continue
            # REDUCTION
            # Couple node to node2
            partitions = self._couple_nodes(top_partitions, bottom_partitions,
                                            pair_idx, node, node2, graph,
                                            edge_colors)
            new_top_partitions, new_bottom_partitions = partitions

            new_perms, new_cosets = self._process_opp(graph,
                                                      new_top_partitions,
                                                      new_bottom_partitions,
                                                      edge_colors,
                                                      orbits,
                                                      cosets)
            # COMBINATION
            permutations += new_perms
            cosets.update(new_cosets)

        mapped = {k for top, bottom in zip(top_partitions, bottom_partitions)
                  for k in top if len(top) == 1 and top == bottom}
        ks = {k for k in graph.nodes if k < node}
        # Have all nodes with ID < node been mapped?
        find_coset = ks <= mapped
        if find_coset:
            # Find the orbit that contains node
            for orbit in orbits:
                if node in orbit:
                    cosets[node] = orbit.copy()
        return permutations, cosets
