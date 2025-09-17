"""
ISMAGS Algorithm
================

Provides a Python implementation of the ISMAGS algorithm. [1]_

It is capable of finding (subgraph) isomorphisms between two graphs, taking the
symmetry of the subgraph into account. In most cases the VF2 algorithm is
faster (at least on small graphs) than this implementation, but in some cases
there is an exponential number of isomorphisms that are symmetrically
equivalent. In that case, the ISMAGS algorithm will provide only one solution
per symmetry group.

>>> petersen = nx.petersen_graph()
>>> ismags = nx.isomorphism.ISMAGS(petersen, petersen)
>>> isomorphisms = list(ismags.isomorphisms_iter(symmetry=False))
>>> len(isomorphisms)
120
>>> isomorphisms = list(ismags.isomorphisms_iter(symmetry=True))
>>> answer = [{0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}]
>>> answer == isomorphisms
True

In addition, this implementation also provides an interface to find the
largest common induced subgraph [2]_ between any two graphs, again taking
symmetry into account. Given `graph` and `subgraph` the algorithm will remove
nodes from the `subgraph` until `subgraph` is isomorphic to a subgraph of
`graph`. Since only the symmetry of `subgraph` is taken into account it is
worth thinking about how you provide your graphs:

>>> graph1 = nx.path_graph(4)
>>> graph2 = nx.star_graph(3)
>>> ismags = nx.isomorphism.ISMAGS(graph1, graph2)
>>> ismags.is_isomorphic()
False
>>> largest_common_subgraph = list(ismags.largest_common_subgraph())
>>> answer = [{1: 0, 0: 1, 2: 2}, {2: 0, 1: 1, 3: 2}]
>>> answer == largest_common_subgraph
True
>>> ismags2 = nx.isomorphism.ISMAGS(graph2, graph1)
>>> largest_common_subgraph = list(ismags2.largest_common_subgraph())
>>> answer = [
...     {1: 0, 0: 1, 2: 2},
...     {1: 0, 0: 1, 3: 2},
...     {2: 0, 0: 1, 1: 2},
...     {2: 0, 0: 1, 3: 2},
...     {3: 0, 0: 1, 1: 2},
...     {3: 0, 0: 1, 2: 2},
... ]
>>> answer == largest_common_subgraph
True

However, when not taking symmetry into account, it doesn't matter:

>>> largest_common_subgraph = list(ismags.largest_common_subgraph(symmetry=False))
>>> answer = [
...     {1: 0, 0: 1, 2: 2},
...     {1: 0, 2: 1, 0: 2},
...     {2: 0, 1: 1, 3: 2},
...     {2: 0, 3: 1, 1: 2},
...     {1: 0, 0: 1, 2: 3},
...     {1: 0, 2: 1, 0: 3},
...     {2: 0, 1: 1, 3: 3},
...     {2: 0, 3: 1, 1: 3},
...     {1: 0, 0: 2, 2: 3},
...     {1: 0, 2: 2, 0: 3},
...     {2: 0, 1: 2, 3: 3},
...     {2: 0, 3: 2, 1: 3},
... ]
>>> answer == largest_common_subgraph
True
>>> largest_common_subgraph = list(ismags2.largest_common_subgraph(symmetry=False))
>>> answer = [
...     {1: 0, 0: 1, 2: 2},
...     {1: 0, 0: 1, 3: 2},
...     {2: 0, 0: 1, 1: 2},
...     {2: 0, 0: 1, 3: 2},
...     {3: 0, 0: 1, 1: 2},
...     {3: 0, 0: 1, 2: 2},
...     {1: 1, 0: 2, 2: 3},
...     {1: 1, 0: 2, 3: 3},
...     {2: 1, 0: 2, 1: 3},
...     {2: 1, 0: 2, 3: 3},
...     {3: 1, 0: 2, 1: 3},
...     {3: 1, 0: 2, 2: 3},
... ]
>>> answer == largest_common_subgraph
True

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

__all__ = ["ISMAGS"]

import itertools
from collections import Counter, defaultdict
from functools import reduce, wraps

import networkx as nx

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
            message = "The function does not works on multidimensional arrays."
            raise NotImplementedError(message) from None

    iterator = iter(iterable)
    first = next(iterator, None)
    return all(item == first for item in iterator)


def make_partition(items, test):
    """
    Partition items into sets based on the outcome of ``test(item1, item2)``.
    Pairs of items for which `test` returns `True` end up in the same set.

    Parameters
    ----------
    items : collections.abc.Iterable[collections.abc.Hashable]
        Items to partition
    test : collections.abc.Callable[collections.abc.Hashable, collections.abc.Hashable]
        A function that will be called with 2 arguments, taken from items.
        Should return `True` if those 2 items need to end up in the same
        part, and `False` otherwise.

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
    partition = []
    for item in items:
        for part in partition:
            p_item = next(iter(part))
            if test(item, p_item):
                part.add(item)
                break
        else:  # No break
            partition.append({item})
    return partition


def node_to_part_ID_dict(partition):
    """
    Creates a dictionary that maps each item in each part to the index of
    the part to which it belongs.

    Parameters
    ----------
    partition: collections.abc.Sequence[collections.abc.Iterable]
        As returned by :func:`make_partition`.

    Returns
    -------
    dict
    """
    return {node: ID for ID, part in enumerate(partition) for node in part}


def color_degree_by_node(G, n_colors, e_colors):
    """Returns a dict by node to counts of edge and node color for that node.

    This returns a dict by node to a 2-tuple of node color and degree by
    (edge color and nbr color). E.g. ``{0: (1, {(0, 2): 5})}`` means that
    node ``0`` has node type 1 and has 5 edges of type 0 that go to nodes of type 2.
    Thus, this is a measure of degree (edge count) by color of edge and color
    of the node on the other side of that edge.

    For directed graphs the degree counts is a 2-tuple of (in, out) degree counts.

    Ideally, if edge_match is None, this could get simplified to just the node
    color on the other end of the edge. Similarly if node_match is None then only
    edge color is tracked. And if both are None, we simply count the number of edges.
    """
    if not G.is_directed():
        if len(n_colors) < len(G):
            for n, nbrs in G.adjacency():
                if n not in n_colors:
                    n_colors[n] = None
                    for v in nbrs:
                        e_colors[n, v] = None
        # undirected colored degree
        return {
            u: (n_colors[u], Counter((e_colors[u, v], n_colors[v]) for v in nbrs))
            for u, nbrs in G.adjacency()
        }
    # directed colored out and in degree
    return {
        u: (
            n_colors[u],
            Counter((e_colors[u, v], n_colors[v]) for v in nbrs),
            Counter((e_colors[v, u], n_colors[v]) for v in G._pred[u]),
        )
        for u, nbrs in G.adjacency()
    }


class EdgeLookup:
    """Class to handle getitem for undirected edges"""
    def __init__(self, edge_dict):
        self.edge_dict = edge_dict

    def __getitem__(self, edge):
        if edge in self.edge_dict:
            return self.edge_dict[edge]
        return self.edge_dict[edge[::-1]]

    def items(self):
        return self.edge_dict.items()


class ISMAGS:
    """
    Implements the ISMAGS subgraph matching algorithm. [1]_ ISMAGS stands for
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

    def __init__(self, graph, subgraph, node_match=None, edge_match=None, cache=None):
        """
        Parameters
        ----------
        graph: networkx.Graph
        subgraph: networkx.Graph
        node_match: collections.abc.Callable or None
            Function used to determine whether two nodes are equivalent. Its
            signature should look like ``f(n1: dict, n2: dict) -> bool``, with
            `n1` and `n2` node property dicts. See also
            :func:`~networkx.algorithms.isomorphism.categorical_node_match` and
            friends.
            If `None`, all nodes are considered equal.
        edge_match: collections.abc.Callable or None
            Function used to determine whether two edges are equivalent. Its
            signature should look like ``f(e1: dict, e2: dict) -> bool``, with
            `e1` and `e2` edge property dicts. See also
            :func:`~networkx.algorithms.isomorphism.categorical_edge_match` and
            friends.
            If `None`, all edges are considered equal.
        cache: collections.abc.Mapping
            A cache used for caching graph symmetries.
        """
        if graph.is_directed() != subgraph.is_directed():
            raise ValueError("Directed and undirected graphs cannot be compared.")

        # TODO: allow for precomputed partitions and colors
        self.graph = graph
        self.subgraph = subgraph
        self._symmetry_cache = cache
        # Naming conventions are taken from the original paper.
        # For your sanity:
        #   sg: subgraph
        #   g: graph
        #   e: edge(s)
        #   n: node(s)
        # So: sgn means "subgraph nodes".
        node_parts = self.create_aligned_partition(
            node_match, self.subgraph.nodes, self.graph.nodes
        )
        self._sgn_partition, self._gn_partition, self.N_node_colors = node_parts
        self._sgn_colors = node_to_part_ID_dict(self._sgn_partition)
        self._gn_colors = node_to_part_ID_dict(self._gn_partition)

        edge_partitions = self.create_aligned_partition(
            edge_match, self.subgraph.edges(), self.graph.edges()
        )
        self._sge_partition, self._ge_partition, self.N_edge_colors = edge_partitions
        if self.graph.is_directed():
            self._sge_colors = node_to_part_ID_dict(self._sge_partition)
            self._ge_colors = node_to_part_ID_dict(self._ge_partition)
        else:  # allow lookups (u, v) or (v, u)
            self._sge_colors = EdgeLookup(node_to_part_ID_dict(self._sge_partition))
            self._ge_colors = EdgeLookup(node_to_part_ID_dict(self._ge_partition))

    def create_aligned_partition(self, match, sg_things, g_things):
        """Partitions of `things` based on function `match`
        Returns: sg_partition, g_partition, number_of_matched_parts

        The first `number_of_matched_parts` parts in each partition
        match in order, e.g. 2nd part matches other's 2nd part.
        Warning: nodes in parts after that have no matching nodes in the other graph.
        For morphisms those nodes can't appear in the mapping.
        """
        if match is None:
            sg_partition = [set(sg_things)]
            g_partition = [set(g_things)]
            return sg_partition, g_partition, 1

        # Use match to create a partition
        sg_multiedge = isinstance(sg_things, nx.classes.reportviews.OutEdgeDataView)
        g_multiedge = isinstance(g_things, nx.classes.reportviews.OutEdgeDataView)
        if not sg_multiedge:
            def sg_match(thing1, thing2):
                return match(sg_things[thing1], sg_things[thing2])

        else:  # multiedges (note nodes of multigraphs use simple case above)
            def sg_match(thing1, thing2):
                (u1, v1), (u2, v2) = thing1, thing2
                return match(self.subgraph[u1][v1], self.subgraph[u2][v2])

        if not g_multiedge:
            def g_match(thing1, thing2):
                return match(g_things[thing1], g_things[thing2])

        else:  # multiedges (note nodes of multigraphs use simple case above)
            def g_match(thing1, thing2):
                (u1, v1), (u2, v2) = thing1, thing2
                return match(self.graph[u1][v1], self.graph[u2][v2])

        sg_partition = make_partition(sg_things, sg_match)
        g_partition = make_partition(g_things, g_match)

        # Align order of g_partition to match that of sg_partition
        sgc_to_gc = {}
        gc_to_sgc = {}
        sN, N = len(sg_partition), len(g_partition)
        for sgc, gc in itertools.product(range(sN), range(N)):
            sgt = next(iter(sg_partition[sgc]))
            gt = next(iter(g_partition[gc]))
            sgt_ = sg_things[sgt] if not sg_multiedge else self.subgraph[sgt[0]][sgt[1]]
            gt_ = g_things[gt] if not g_multiedge else self.graph[gt[0]][gt[1]]
            if match(sgt_, gt_):
                assert sgc not in sgc_to_gc  # 2 sg parts match same g part
                assert gc not in gc_to_sgc  # 2 g parts match same sg part
                sgc_to_gc[sgc] = gc
                gc_to_sgc[gc] = sgc
        ## return two lists and the number of partitions that match.
        new_order = [
            (sg_partition[sgc], g_partition[gc]) for sgc, gc in sgc_to_gc.items()
        ]
        Ncolors = len(new_order)
        if Ncolors:
            new_sg_p, new_g_p = [list(x) for x in zip(*new_order)]
        else:
            new_sg_p, new_g_p = [], []
        if Ncolors < sN:
            extra = [sg_partition[c] for c in range(sN) if c not in sgc_to_gc]
            new_sg_p = list(new_sg_p) + extra
            new_g_p = list(new_g_p) + [set()] * len(extra)
        if Ncolors < N:
            extra = [g_partition[c] for c in range(N) if c not in gc_to_sgc]
            new_g_p = list(new_g_p) + extra
            new_sg_p = list(new_sg_p) + [set()] * len(extra)

        return new_sg_p, new_g_p, Ncolors

    def find_isomorphisms(self, symmetry=True):
        """Find all subgraph isomorphisms between subgraph and graph

        Finds isomorphisms where :attr:`subgraph` <= :attr:`graph`.

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
        elif len(self._sgn_partition) > self.N_node_colors:
            return
        elif len(self._sge_partition) > self.N_edge_colors:
            return

        if symmetry:
            # only find node symmetry for subgraph colors that match to graph colors
            cosets = self.analyze_subgraph_symmetry()
            constraints = self._make_constraints(cosets)
        else:
            constraints = []

        cand_sets = self._get_node_color_candidate_sets()
        cand_sets = {node: cands for node, cands in cand_sets.items() if cands}
        la_candidates = self._get_color_degree_candidates()
        for sgn, la_cands in la_candidates.items():
            cand_sets[sgn].add(frozenset(la_cands))

        if any(cand_sets.values()):
            # Choose start node based on a heuristic for the min # of candidates
            # Heuristic here is length of smallest frozenset in candidates' set
            # of frozensets for that node. Using the smallest length avoids
            # avoids computing the intersection of the frosensets for each node.
            start_sgn = min(cand_sets, key=lambda n: min(len(x) for x in cand_sets[n]))
            cand_sets[start_sgn] = (frozenset.intersection(*cand_sets[start_sgn]),)
            yield from self._map_nodes(start_sgn, cand_sets, constraints)
        return

    def _get_color_degree_candidates(self):
        """
        Returns a mapping of {subgraph node: set of graph nodes} for
        which the graph nodes are feasible mapping candidate_sets for the
        subgraph node, as determined by looking ahead one edge.
        """
        g_deg = color_degree_by_node(self.graph, self._gn_colors, self._ge_colors)
        sg_deg = color_degree_by_node(self.subgraph, self._sgn_colors, self._sge_colors)

        color_degree_candidates = defaultdict(set)
        for sgn, (_, *needed_counts) in sg_deg.items():
            for gn, (_, *g_counts) in g_deg.items():
                if all(
                    all(
                        sg_cnt <= g_counts[idx][color]
                        for color, sg_cnt in counts.items()
                    )
                    for idx, counts in enumerate(needed_counts)
                ):
                    color_degree_candidates[sgn].add(gn)
        return color_degree_candidates

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
            cosets = self.analyze_subgraph_symmetry()
            constraints = self._make_constraints(cosets)
        else:
            constraints = []

        candidate_sets = self._get_node_color_candidate_sets()

        if any(candidate_sets.values()):
            relevant_parts = self._sgn_partition[:self.N_node_colors]
            to_be_mapped = {frozenset(n for p in relevant_parts for n in p)}
            yield from self._largest_common_subgraph(
                candidate_sets, constraints, to_be_mapped
            )
        else:
            return

    def analyze_subgraph_symmetry(self):
        """
        Find a minimal set of permutations and corresponding co-sets that
        describe the symmetry of ``self.subgraph``, given the node and edge
        equalities given by `node_partition` and `edge_colors`, respectively.

        Returns
        -------
        dict[collections.abc.Hashable, set[collections.abc.Hashable]]
            The found co-sets. The co-sets is a dictionary of
            ``{node key: set of node keys}``.
            Every key-value pair describes which ``values`` can be interchanged
            without changing nodes less than ``key``.
        """
        node_partition, edge_colors = self._sgn_partition, self._sge_colors

        if self._symmetry_cache is not None:
            key = hash(
                (
                    tuple(self.subgraph.nodes),
                    tuple(self.subgraph.edges),
                    tuple(map(tuple, node_partition)),
                    tuple(edge_colors.items()),
                    self.subgraph.is_directed(),
                )
            )
            if key in self._symmetry_cache:
                return self._symmetry_cache[key]
        node_partition = next(
            self._refine_node_partition(self.subgraph, node_partition, edge_colors)
        )
        cosets = self._process_ordered_pair_partitions(
            self.subgraph, node_partition, node_partition, edge_colors
        )
        if self._symmetry_cache is not None:
            self._symmetry_cache[key] = cosets
        return cosets

    def is_isomorphic(self, symmetry=False):
        """
        Returns True if :attr:`graph` is isomorphic to :attr:`subgraph` and
        False otherwise.

        Returns
        -------
        bool
        """
        return len(self.subgraph) == len(self.graph) and self.subgraph_is_isomorphic(
            symmetry
        )

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
        isom = next(self.subgraph_isomorphisms_iter(symmetry=symmetry), None)
        return isom is not None

    def isomorphisms_iter(self, symmetry=True):
        """
        Does the same as :meth:`find_isomorphisms` if :attr:`graph` and
        :attr:`subgraph` have the same number of nodes.
        """
        if len(self.graph) == len(self.subgraph):
            yield from self.subgraph_isomorphisms_iter(symmetry=symmetry)

    def subgraph_isomorphisms_iter(self, symmetry=True):
        """Alternative name for :meth:`find_isomorphisms`."""
        return self.find_isomorphisms(symmetry)

    def _get_node_color_candidate_sets(self):
        """
        Per node in subgraph find all nodes in graph that have the same color.
        Stored as a dict-of-set-of-frozenset. The dict is keyed by node to a
        collection of frozensets of graph nodes. Each of these frozensets are
        a restriction. The node can be mapped only to nodes in the frosenset.
        Thus it must be mapped to nodes in the intersection of all these sets.
        We store the sets to delay taking the intersection of them. This helps
        for two reasons: Firstly any duplicate restriction sets can be ignored;
        Secondly, some nodes will not need the intersection to be constructed.
        Note: a dict-of-list-of-set would store duplicate sets in the list and
        we want to avoid that. But I wonder if checking hash/equality when `add`ing
        removes the benefit of avoiding computing intersections.
        """
        candidate_sets = defaultdict(set)
        for sgn in self.subgraph.nodes:
            sgn_color = self._sgn_colors[sgn]
            if sgn_color >= self.N_node_colors:  # color has no candidates
                candidate_sets[sgn]  # creates empty set entry in defaultdict
            else:
                candidate_sets[sgn].add(frozenset(self._gn_partition[sgn_color]))
        return dict(candidate_sets)

    @staticmethod
    def _make_constraints(cosets):
        """
        Turn cosets into constraints.
        """
        constraints = []
        for node_i, node_ts in cosets.items():
            for node_t in node_ts:
                if node_i != node_t:
                    # node_i <= node_t in ordering of nodes
                    constraints.append((node_i, node_t))
        return constraints

    @staticmethod
    def _get_permutations_by_length(items):
        """
        Get all permutations of items, but only permute items with the same
        length.

        >>> found = list(ISMAGS._get_permutations_by_length([[1], [2], [3, 4], [4, 5]]))
        >>> answer = [
        ...     (([1], [2]), ([3, 4], [4, 5])),
        ...     (([1], [2]), ([4, 5], [3, 4])),
        ...     (([2], [1]), ([3, 4], [4, 5])),
        ...     (([2], [1]), ([4, 5], [3, 4])),
        ... ]
        >>> found == answer
        True
        """
        by_len = defaultdict(list)
        for item in items:
            by_len[len(item)].append(item)

        yield from itertools.product(
            *(itertools.permutations(by_len[l]) for l in sorted(by_len))
        )

    @classmethod
    def _refine_node_partition(cls, graph, partition, edge_colors, branch=False):
        def equal_color(node1, node2):
            return color_degree[node1] == color_degree[node2]

        yields = 0
        possible_partitions = [partition]
        while possible_partitions:
            partition = possible_partitions.pop()
            node_colors = node_to_part_ID_dict(partition)
            color_degree = color_degree_by_node(graph, node_colors, edge_colors)
            if all(are_all_equal(color_degree[n] for n in p) for p in partition):
                yield partition
                if branch:
                    continue
                return

            more_partitions = [[]]
            for part in partition:
                if are_all_equal(color_degree[node] for node in part):
                    for n_p in more_partitions:
                        n_p.append(part)
                else:
                    refined = make_partition(part, equal_color)
                    R = len(refined)
                    if not branch or R == 1 or R == len({len(r) for r in refined}):
                        for n_p in more_partitions:
                            n_p.extend(sorted(refined, key=len))
                    else:
                        # This is where tracking partitions by len breaks.
                        # There are multiple new cells in refined with the
                        # same length, and their order matters. So we hit
                        # it with a big hammer and simply add all orderings.
                        new_partitions = []
                        perms = cls._get_permutations_by_length(refined)
                        for n_p in more_partitions:
                            for permutation in perms:
                                new_partitions.append(n_p + list(permutation[0]))
                        more_partitions = new_partitions
            possible_partitions.extend(more_partitions[::-1])


    def _map_nodes(self, sgn, candidate_sets, constraints, mapping=None, to_be_mapped=None):
        """
        Find all subgraph isomorphisms honoring constraints.
        The collection `candidate_sets` is stored as a dict-of-set-of-frozenset.
        The dict is keyed by node to a collection of candidate frozensets. Any
        viable candidate must nelong to all the frozensets in the collection.
        So each frozenset added to the collection is a restriction on the candidates.

        According to the paper, we store the collection of sets rather than their
        intersection to delay computing many intersections with the hope of avoiding
        them completely. having the middle collection be a set also means that
        duplicate restrictions on candidates are ignored, avoided another intersection.
        """
        # shortcuts for speed
        subgraph = self.subgraph
        graph = self.graph
        self_ge_partition = self._ge_partition
        self_sge_colors = self._sge_colors
        is_directed = subgraph.is_directed()
        gn_ID_to_node = list(graph)
        gn_node_to_ID = {n: id for id, n in enumerate(graph)}

        mapping = {}
        rev_mapping = {}
        if to_be_mapped is None:
            to_be_mapped = self.subgraph._adj.keys()

        # Note that we don't copy candidates here. This means we leak
        # information between the recursive branches. This is intentional!
        # Specifically, we modify candidates here. That's OK because we substitute
        # the set of frozensets with a set containing the frozenset intersection.
        # So, it doesn't change the membership rule or the length rule for sorting.
        # Membership: any candidate must be an element of each of the frozensets.
        # Length: length of the intersection set. Use heuristic min(len of frozensets).
        # This intersection improves future length heuristics which can only occur
        # after this recursive call finishes. But it means future additional
        # restriction frozensets that duplicate previous ones are not ignored.
        sgn_candidates = frozenset.intersection(*candidate_sets[sgn])
        candidate_sets[sgn] = {sgn_candidates}
        queue = [(sgn, candidate_sets, iter(sgn_candidates))]
        its = jts = kts = 0
        while queue:  # DFS over all possible mappings
            sgn, candidate_sets, sgn_cand_iter = queue[-1]

            for gn in sgn_cand_iter:
                # We're going to try to map sgn to gn.
                if gn in rev_mapping:
                    continue  # pragma: no cover

                # REDUCTION and COMBINATION
                if sgn in mapping:
                    old_gn = mapping[sgn]
                    del rev_mapping[old_gn]
                mapping[sgn] = gn
                rev_mapping[gn] = sgn
                # BASECASE
                if len(mapping) == len(to_be_mapped):
                    yield rev_mapping.copy()
                    del mapping[sgn]
                    del rev_mapping[gn]
                    continue
                left_to_map = to_be_mapped - mapping.keys()

                # Now we copy the candidates dict. But it is not a deepcopy.
                # The dict-of-sets-of-frozensets point to the same sets of frozensets.
                # Be careful to not change the sets of frozensets below.
                # Shallow copy. allows chg for new sgns
                new_candidates = candidate_sets.copy()

                # update the candidate_sets for unmapped sgn based on sgn mapped
                if not is_directed:
                    sgn_nbrs = subgraph._adj[sgn]
                    not_gn_nbrs = graph._adj.keys() - graph._adj[gn].keys()
                    for sgn2 in left_to_map:
                        # edge color must match when sgn2 connected to sgn
                        if sgn2 not in sgn_nbrs:
                            gn2_options = not_gn_nbrs
                        else:
                            g_edges = self_ge_partition[self_sge_colors[sgn, sgn2]]
                            gn2_options = {n for e in g_edges if gn in e for n in e}
                        # Node color compatibility should be taken care of by the
                        # initial candidate lists made by find_subgraphs

                        # Add gn2_options to the right collection. Since new_candidates
                        # is a dict-of-sets-of-frozensets of node indices it's
                        # a bit clunky. We can't do .add without changing the original,
                        # and + also doesn't work. Could do |, but union is clearer?
                        new_candidates[sgn2] = new_candidates[sgn2].union(
                            [frozenset(gn2_options)]
                        )
                else:  # directed
                    sgn_nbrs = subgraph._adj[sgn].keys()
                    sgn_preds = subgraph._pred[sgn].keys()
                    not_gn_nbrs = graph._adj.keys() - graph._adj[gn].keys() - graph._pred[gn].keys()
                    for sgn2 in left_to_map:
                        # edge color must match when sgn2 connected to sgn
                        if sgn2 not in sgn_nbrs:
                            if sgn2 not in sgn_preds:
                                gn2_options = not_gn_nbrs
                            else:  # sgn2 in sgn_preds
                                g_edges = self_ge_partition[self_sge_colors[sgn2, sgn]]
                                gn2_options = {e[0] for e in g_edges if gn == e[1]}
                        else:
                            if sgn2 not in sgn_preds:
                                g_edges = self_ge_partition[self_sge_colors[sgn, sgn2]]
                                gn2_options = {e[1] for e in g_edges if gn == e[0]}
                            else:
                                # gn2 must have correct color in both directions
                                g_edges = self_ge_partition[self_sge_colors[sgn, sgn2]]
                                gn2_options = {e[1] for e in g_edges if gn == e[0]}
                                g_edges = self_ge_partition[self_sge_colors[sgn2, sgn]]
                                gn2_options &= {e[0] for e in g_edges if gn == e[1]}
                        new_candidates[sgn2] = new_candidates[sgn2].union(
                            [frozenset(gn2_options)]
                        )

                for sgn2 in left_to_map:
                    # symmetry must match. constraints mean gn2>gn iff sgn2>sgn
                    if (sgn, sgn2) in constraints:
                        gn2_options = set(gn_ID_to_node[gn_node_to_ID[gn] + 1:])
                        # gn2_options = {gn2 for gn2 in self.graph if gn2 > gn}
                    elif (sgn2, sgn) in constraints:
                        gn2_options = set(gn_ID_to_node[:gn_node_to_ID[gn]])
                        # gn2_options = {gn2 for gn2 in self.graph if gn2 < gn}
                    else:
                        continue  # pragma: no cover
                    # same gn2_options comment here. Use union.
                    new_candidates[sgn2] = new_candidates[sgn2].union(
                        [frozenset(gn2_options)]
                    )

                # The next node is the one that is unmapped and has fewest candidates
                # Use the heuristic of the min size of the frosensets rather than
                # intersection of all frozensets to delay computing intersections.
                new_sgn = min(
                    left_to_map, key=lambda n: min(len(x) for x in new_candidates[n])
                )
                new_sgn_candidates = frozenset.intersection(*new_candidates[new_sgn])
                if not new_sgn_candidates:
                    continue
                new_candidates[new_sgn] = {new_sgn_candidates}
                queue.append((new_sgn, new_candidates, iter(new_sgn_candidates)))
                break
            else:  # all gn candidates tried for sgn.
                queue.pop()
                if sgn in mapping:
                    assert rev_mapping[mapping[sgn]] == sgn
                    del rev_mapping[mapping[sgn]]
                    del mapping[sgn]

    def _largest_common_subgraph(self, candidates, constraints, to_be_mapped=None):
        """
        Find all largest common subgraphs honoring constraints.
        """
        # to_be_mapped is a set of frozensets of subgraph nodes
        if to_be_mapped is None:
            to_be_mapped = {frozenset(self.subgraph.nodes)}

        # The LCS problem is basically a repeated subgraph isomorphism problem
        # with smaller and smaller subgraphs. We store the nodes that are
        # "part of" the subgraph in to_be_mapped, and we make it a little
        # smaller every iteration.

        current_size = len(next(iter(to_be_mapped), []))

        found_iso = False
        if current_size <= len(self.graph):
            # There's no point in trying to find isomorphisms of
            # graph >= subgraph if subgraph has more nodes than graph.

            # Try the isomorphism first with the nodes with lowest ID. So sort
            # them. Those are more likely to be part of the final correspondence.
            # In theory, this makes finding the first answer(s) faster.
            for nodes in sorted(to_be_mapped, key=sorted):
                # Find the isomorphism between subgraph[to_be_mapped] <= graph
                next_sgn = min(nodes, key=lambda n: min(len(x) for x in candidates[n]))
                isomorphs = self._map_nodes(
                    next_sgn, candidates, constraints, to_be_mapped=nodes
                )

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
        yield from self._largest_common_subgraph(
            candidates, constraints, to_be_mapped=left_to_be_mapped
        )

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
                return frozenset(nodes - {node})

    @staticmethod
    def _find_permutations(top_partition, bottom_partition):
        """
        Return the pairs of top/bottom parts where the parts are
        different. Ensures that all parts in both top and bottom
        partitions have size 1.
        """
        # Find permutations
        permutations = set()
        for top, bot in zip(top_partition, bottom_partition):
            # top and bot have only one element
            if len(top) > 1 or len(bot) > 1:
                raise IndexError(
                    "Not all nodes are coupled. This is"
                    f" impossible: {top_partition}, {bottom_partition}"
                )
            if top != bot:
                permutations.add(frozenset((next(iter(top)), next(iter(bot)))))
        return permutations

    def _couple_nodes(
        self,
        top_partition,
        bottom_partition,
        part_idx,
        t_node,
        b_node,
        graph,
        edge_colors,
    ):
        """
        Generate new partitions from top and bottom_partitions where t_node is
        coupled to b_node. part_idx is the index of the parts where t_ and
        b_node can be found.
        """
        t_part = top_partition[part_idx]
        b_part = bottom_partition[part_idx]
        assert t_node in t_part and b_node in b_part
        # Couple node to node2. This means they get their own part
        new_top = [top.copy() for top in top_partition]
        new_bot = [bot.copy() for bot in bottom_partition]
        new_t_groups = {t_node}, t_part - {t_node}
        new_b_groups = {b_node}, b_part - {b_node}
        # Replace the old partitions with the coupled ones
        del new_top[part_idx]
        del new_bot[part_idx]
        new_top[part_idx:part_idx] = new_t_groups
        new_bot[part_idx:part_idx] = new_b_groups

        new_top = next(self._refine_node_partition(graph, new_top, edge_colors))
        # refine in all branches of possible refinements (to find symmetries)
        bots = self._refine_node_partition(graph, new_bot, edge_colors, branch=True)
        for bot in bots:
            yield list(new_top), bot

    def _process_ordered_pair_partitions(
        self,
        graph,
        top_partition,
        bottom_partition,
        edge_colors,
    ):
        if all(len(top) <= 1 for top in top_partition):
            return {}

        node_to_ID = {n: i for i, n in enumerate(graph)}
        orbit_id = {node: orbit_i for orbit_i, node in enumerate(graph.nodes)}
        orbits = [{node} for node in graph.nodes]
        cosets = {}

        # find smallest node and its partition index
        unmapped_nodes = (
            (node_to_ID[node], node, idx)
            for idx, t_part in enumerate(top_partition)
            for node in t_part
            if len(t_part) > 1
        )
        _, node, part_i = min(unmapped_nodes)  # needs sortable nodes
        b_part = bottom_partition[part_i]
        node2_iter = iter(sorted(b_part))

        queue = [(top_partition, bottom_partition, node, part_i, node2_iter)]

        while queue:
            tops, bottoms, node, part_i, node2_iter = queue[-1]

            if len(bottoms[part_i]) > 1:
                for node2 in node2_iter:
                    if node != node2 and orbit_id[node] == orbit_id[node2]:
                        # Orbit prune branch
                        continue
                    # REDUCTION   Couple node to node2
                    partitions = self._couple_nodes(
                        tops,
                        bottoms,
                        part_i,
                        node,
                        node2,
                        graph,
                        edge_colors,
                    )
                    partitions=list(partitions)
                    new_q = []
                    for opp in partitions:
                        if all(len(top) <= 1 for top in opp[0]):
                            # all nodes are mapped
                            permutations = self._find_permutations(*opp)
                            for permutation in permutations:
                                orb1, orb2 = (orbit_id[n] for n in permutation)
                                if orb1 != orb2:
                                    orbit_set2 = orbits[orb2]
                                    orbits[orb1].update(orbit_set2)
                                    orbits[orb2] = set()
                                    orbit_id.update((n, orb1) for n in orbit_set2)
                            continue

                        ## Prep to load into queue
                        unmapped_nodes = {
                            (node_to_ID[node], node, i)
                            for i, top in enumerate(opp[0])
                            for node in top
                            if len(top) > 1
                        }
                        if unmapped_nodes:
                            _, n, part_i = min(unmapped_nodes)
                            b_part = opp[1][part_i]
                            node2_iter = iter(sorted(b_part))
                            new_q.append((*opp, n, part_i, node2_iter))
                    queue.extend(new_q[::-1])
                    break
                else:  # no more node2 options
                    queue.pop()
                    if node not in cosets:
                        mapped = {
                            k
                            for top, bottom in zip(tops, bottoms)
                            for k in top
                            if len(top) == 1 and top == bottom
                        }
                        IDless = {n for n in graph if node_to_ID[n] < node_to_ID[node]}
                        # Have all nodes with ID < node been mapped?
                        if IDless <= mapped:
                            orb = orbit_id[node]
                            cosets[node] = orbits[orb].copy()
        return cosets
