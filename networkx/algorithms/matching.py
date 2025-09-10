"""Functions for computing and verifying matchings in a graph."""

from itertools import combinations, repeat
from typing import Any, Dict, List, Optional, Tuple, Union
import networkx as nx
from networkx.utils import not_implemented_for
import logging 
__all__ = [
    "is_matching",
    "is_maximal_matching",
    "is_perfect_matching",
    "max_weight_matching",
    "min_weight_matching",
    "maximal_matching",
    "minimal_fraction_max_matching"
]

log = logging.getLogger(__name__)


@not_implemented_for("multigraph")
@not_implemented_for("directed")
@nx._dispatchable
def maximal_matching(G):
    r"""Find a maximal matching in the graph.

    A matching is a subset of edges in which no node occurs more than once.
    A maximal matching cannot add more edges and still be a matching.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    matching : set
        A maximal matching of the graph.

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)])
    >>> sorted(nx.maximal_matching(G))
    [(1, 2), (3, 5)]

    Notes
    -----
    The algorithm greedily selects a maximal matching M of the graph G
    (i.e. no superset of M exists). It runs in $O(|E|)$ time.
    """
    matching = set()
    nodes = set()
    for edge in G.edges():
        # If the edge isn't covered, add it to the matching
        # then remove neighborhood of u and v from consideration.
        u, v = edge
        if u not in nodes and v not in nodes and u != v:
            matching.add(edge)
            nodes.update(edge)
    return matching


def matching_dict_to_set(matching):
    """Converts matching dict format to matching set format

    Converts a dictionary representing a matching (as returned by
    :func:`max_weight_matching`) to a set representing a matching (as
    returned by :func:`maximal_matching`).

    In the definition of maximal matching adopted by NetworkX,
    self-loops are not allowed, so the provided dictionary is expected
    to never have any mapping from a key to itself. However, the
    dictionary is expected to have mirrored key/value pairs, for
    example, key ``u`` with value ``v`` and key ``v`` with value ``u``.

    """
    edges = set()
    for edge in matching.items():
        u, v = edge
        if (v, u) in edges or edge in edges:
            continue
        if u == v:
            raise nx.NetworkXError(f"Selfloops cannot appear in matchings {edge}")
        edges.add(edge)
    return edges


@nx._dispatchable
def is_matching(G, matching):
    """Return True if ``matching`` is a valid matching of ``G``

    A *matching* in a graph is a set of edges in which no two distinct
    edges share a common endpoint. Each node is incident to at most one
    edge in the matching. The edges are said to be independent.

    Parameters
    ----------
    G : NetworkX graph

    matching : dict or set
        A dictionary or set representing a matching. If a dictionary, it
        must have ``matching[u] == v`` and ``matching[v] == u`` for each
        edge ``(u, v)`` in the matching. If a set, it must have elements
        of the form ``(u, v)``, where ``(u, v)`` is an edge in the
        matching.

    Returns
    -------
    bool
        Whether the given set or dictionary represents a valid matching
        in the graph.

    Raises
    ------
    NetworkXError
        If the proposed matching has an edge to a node not in G.
        Or if the matching is not a collection of 2-tuple edges.

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)])
    >>> nx.is_maximal_matching(G, {1: 3, 2: 4})  # using dict to represent matching
    True

    >>> nx.is_matching(G, {(1, 3), (2, 4)})  # using set to represent matching
    True

    """
    if isinstance(matching, dict):
        matching = matching_dict_to_set(matching)

    nodes = set()
    for edge in matching:
        if len(edge) != 2:
            raise nx.NetworkXError(f"matching has non-2-tuple edge {edge}")
        u, v = edge
        if u not in G or v not in G:
            raise nx.NetworkXError(f"matching contains edge {edge} with node not in G")
        if u == v:
            return False
        if not G.has_edge(u, v):
            return False
        if u in nodes or v in nodes:
            return False
        nodes.update(edge)
    return True


@nx._dispatchable
def is_maximal_matching(G, matching):
    """Return True if ``matching`` is a maximal matching of ``G``

    A *maximal matching* in a graph is a matching in which adding any
    edge would cause the set to no longer be a valid matching.

    Parameters
    ----------
    G : NetworkX graph

    matching : dict or set
        A dictionary or set representing a matching. If a dictionary, it
        must have ``matching[u] == v`` and ``matching[v] == u`` for each
        edge ``(u, v)`` in the matching. If a set, it must have elements
        of the form ``(u, v)``, where ``(u, v)`` is an edge in the
        matching.

    Returns
    -------
    bool
        Whether the given set or dictionary represents a valid maximal
        matching in the graph.

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (2, 3), (3, 4), (3, 5)])
    >>> nx.is_maximal_matching(G, {(1, 2), (3, 4)})
    True

    """
    if isinstance(matching, dict):
        matching = matching_dict_to_set(matching)
    # If the given set is not a matching, then it is not a maximal matching.
    edges = set()
    nodes = set()
    for edge in matching:
        if len(edge) != 2:
            raise nx.NetworkXError(f"matching has non-2-tuple edge {edge}")
        u, v = edge
        if u not in G or v not in G:
            raise nx.NetworkXError(f"matching contains edge {edge} with node not in G")
        if u == v:
            return False
        if not G.has_edge(u, v):
            return False
        if u in nodes or v in nodes:
            return False
        nodes.update(edge)
        edges.add(edge)
        edges.add((v, u))
    # A matching is maximal if adding any new edge from G to it
    # causes the resulting set to match some node twice.
    # Be careful to check for adding selfloops
    for u, v in G.edges:
        if (u, v) not in edges:
            # could add edge (u, v) to edges and have a bigger matching
            if u not in nodes and v not in nodes and u != v:
                return False
    return True


@nx._dispatchable
def is_perfect_matching(G, matching):
    """Return True if ``matching`` is a perfect matching for ``G``

    A *perfect matching* in a graph is a matching in which exactly one edge
    is incident upon each vertex.

    Parameters
    ----------
    G : NetworkX graph

    matching : dict or set
        A dictionary or set representing a matching. If a dictionary, it
        must have ``matching[u] == v`` and ``matching[v] == u`` for each
        edge ``(u, v)`` in the matching. If a set, it must have elements
        of the form ``(u, v)``, where ``(u, v)`` is an edge in the
        matching.

    Returns
    -------
    bool
        Whether the given set or dictionary represents a valid perfect
        matching in the graph.

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5), (4, 6)])
    >>> my_match = {1: 2, 3: 5, 4: 6}
    >>> nx.is_perfect_matching(G, my_match)
    True

    """
    if isinstance(matching, dict):
        matching = matching_dict_to_set(matching)

    nodes = set()
    for edge in matching:
        if len(edge) != 2:
            raise nx.NetworkXError(f"matching has non-2-tuple edge {edge}")
        u, v = edge
        if u not in G or v not in G:
            raise nx.NetworkXError(f"matching contains edge {edge} with node not in G")
        if u == v:
            return False
        if not G.has_edge(u, v):
            return False
        if u in nodes or v in nodes:
            return False
        nodes.update(edge)
    return len(nodes) == len(G)


@not_implemented_for("multigraph")
@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight")
def min_weight_matching(G, weight="weight"):
    """Compute a minimum-weight maximum-cardinality matching of `G`.

    The minimum-weight maximum-cardinality matching is the matching
    that has the minimum weight among all maximum-cardinality matchings.

    Use the maximum-weight algorithm with edge weights subtracted
    from the maximum weight of all edges.

    A matching is a subset of edges in which no node occurs more than once.
    The weight of a matching is the sum of the weights of its edges.
    A maximal matching cannot add more edges and still be a matching.
    The cardinality of a matching is the number of matched edges.

    This method replaces the edge weights with 1 plus the maximum edge weight
    minus the original edge weight.

    new_weight = (max_weight + 1) - edge_weight

    then runs :func:`max_weight_matching` with the new weights.
    The max weight matching with these new weights corresponds
    to the min weight matching using the original weights.
    Adding 1 to the max edge weight keeps all edge weights positive
    and as integers if they started as integers.

    Read the documentation of `max_weight_matching` for more information.

    Parameters
    ----------
    G : NetworkX graph
      Undirected graph

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.
       If key not found, uses 1 as weight.

    Returns
    -------
    matching : set
        A minimal weight matching of the graph.

    See Also
    --------
    max_weight_matching
    """
    if len(G.edges) == 0:
        return max_weight_matching(G, maxcardinality=True, weight=weight)
    G_edges = G.edges(data=weight, default=1)
    max_weight = 1 + max(w for _, _, w in G_edges)
    InvG = nx.Graph()
    edges = ((u, v, max_weight - w) for u, v, w in G_edges)
    InvG.add_weighted_edges_from(edges, weight=weight)
    return max_weight_matching(InvG, maxcardinality=True, weight=weight)


@not_implemented_for("multigraph")
@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight")
def max_weight_matching(G, maxcardinality=False, weight="weight"):
    """Compute a maximum-weighted matching of G.

    A matching is a subset of edges in which no node occurs more than once.
    The weight of a matching is the sum of the weights of its edges.
    A maximal matching cannot add more edges and still be a matching.
    The cardinality of a matching is the number of matched edges.

    Parameters
    ----------
    G : NetworkX graph
      Undirected graph

    maxcardinality: bool, optional (default=False)
       If maxcardinality is True, compute the maximum-cardinality matching
       with maximum weight among all maximum-cardinality matchings.

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.
       If key not found, uses 1 as weight.


    Returns
    -------
    matching : set
        A maximal matching of the graph.

     Examples
    --------
    >>> G = nx.Graph()
    >>> edges = [(1, 2, 6), (1, 3, 2), (2, 3, 1), (2, 4, 7), (3, 5, 9), (4, 5, 3)]
    >>> G.add_weighted_edges_from(edges)
    >>> sorted(nx.max_weight_matching(G))
    [(2, 4), (5, 3)]

    Notes
    -----
    If G has edges with weight attributes the edge data are used as
    weight values else the weights are assumed to be 1.

    This function takes time O(number_of_nodes ** 3).

    If all edge weights are integers, the algorithm uses only integer
    computations.  If floating point weights are used, the algorithm
    could return a slightly suboptimal matching due to numeric
    precision errors.

    This method is based on the "blossom" method for finding augmenting
    paths and the "primal-dual" method for finding a matching of maximum
    weight, both methods invented by Jack Edmonds [1]_.

    Bipartite graphs can also be matched using the functions present in
    :mod:`networkx.algorithms.bipartite.matching`.

    References
    ----------
    .. [1] "Efficient Algorithms for Finding Maximum Matching in Graphs",
       Zvi Galil, ACM Computing Surveys, 1986.
    """
    #
    # The algorithm is taken from "Efficient Algorithms for Finding Maximum
    # Matching in Graphs" by Zvi Galil, ACM Computing Surveys, 1986.
    # It is based on the "blossom" method for finding augmenting paths and
    # the "primal-dual" method for finding a matching of maximum weight, both
    # methods invented by Jack Edmonds.
    #
    # A C program for maximum weight matching by Ed Rothberg was used
    # extensively to validate this new code.
    #
    # Many terms used in the code comments are explained in the paper
    # by Galil. You will probably need the paper to make sense of this code.
    #

    class NoNode:
        """Dummy value which is different from any node."""

    class Blossom:
        """Representation of a non-trivial blossom or sub-blossom."""

        __slots__ = ["childs", "edges", "mybestedges"]

        # b.childs is an ordered list of b's sub-blossoms, starting with
        # the base and going round the blossom.

        # b.edges is the list of b's connecting edges, such that
        # b.edges[i] = (v, w) where v is a vertex in b.childs[i]
        # and w is a vertex in b.childs[wrap(i+1)].

        # If b is a top-level S-blossom,
        # b.mybestedges is a list of least-slack edges to neighboring
        # S-blossoms, or None if no such list has been computed yet.
        # This is used for efficient computation of delta3.

        # Generate the blossom's leaf vertices.
        def leaves(self):
            stack = [*self.childs]
            while stack:
                t = stack.pop()
                if isinstance(t, Blossom):
                    stack.extend(t.childs)
                else:
                    yield t

    # Get a list of vertices.
    gnodes = list(G)
    if not gnodes:
        return set()  # don't bother with empty graphs

    # Find the maximum edge weight.
    maxweight = 0
    allinteger = True
    for i, j, d in G.edges(data=True):
        wt = d.get(weight, 1)
        if i != j and wt > maxweight:
            maxweight = wt
        allinteger = allinteger and (str(type(wt)).split("'")[1] in ("int", "long"))

    # If v is a matched vertex, mate[v] is its partner vertex.
    # If v is a single vertex, v does not occur as a key in mate.
    # Initially all vertices are single; updated during augmentation.
    mate = {}

    # If b is a top-level blossom,
    # label.get(b) is None if b is unlabeled (free),
    #                 1 if b is an S-blossom,
    #                 2 if b is a T-blossom.
    # The label of a vertex is found by looking at the label of its top-level
    # containing blossom.
    # If v is a vertex inside a T-blossom, label[v] is 2 iff v is reachable
    # from an S-vertex outside the blossom.
    # Labels are assigned during a stage and reset after each augmentation.
    label = {}

    # If b is a labeled top-level blossom,
    # labeledge[b] = (v, w) is the edge through which b obtained its label
    # such that w is a vertex in b, or None if b's base vertex is single.
    # If w is a vertex inside a T-blossom and label[w] == 2,
    # labeledge[w] = (v, w) is an edge through which w is reachable from
    # outside the blossom.
    labeledge = {}

    # If v is a vertex, inblossom[v] is the top-level blossom to which v
    # belongs.
    # If v is a top-level vertex, inblossom[v] == v since v is itself
    # a (trivial) top-level blossom.
    # Initially all vertices are top-level trivial blossoms.
    inblossom = dict(zip(gnodes, gnodes))

    # If b is a sub-blossom,
    # blossomparent[b] is its immediate parent (sub-)blossom.
    # If b is a top-level blossom, blossomparent[b] is None.
    blossomparent = dict(zip(gnodes, repeat(None)))

    # If b is a (sub-)blossom,
    # blossombase[b] is its base VERTEX (i.e. recursive sub-blossom).
    blossombase = dict(zip(gnodes, gnodes))

    # If w is a free vertex (or an unreached vertex inside a T-blossom),
    # bestedge[w] = (v, w) is the least-slack edge from an S-vertex,
    # or None if there is no such edge.
    # If b is a (possibly trivial) top-level S-blossom,
    # bestedge[b] = (v, w) is the least-slack edge to a different S-blossom
    # (v inside b), or None if there is no such edge.
    # This is used for efficient computation of delta2 and delta3.
    bestedge = {}

    # If v is a vertex,
    # dualvar[v] = 2 * u(v) where u(v) is the v's variable in the dual
    # optimization problem (if all edge weights are integers, multiplication
    # by two ensures that all values remain integers throughout the algorithm).
    # Initially, u(v) = maxweight / 2.
    dualvar = dict(zip(gnodes, repeat(maxweight)))

    # If b is a non-trivial blossom,
    # blossomdual[b] = z(b) where z(b) is b's variable in the dual
    # optimization problem.
    blossomdual = {}

    # If (v, w) in allowedge or (w, v) in allowedg, then the edge
    # (v, w) is known to have zero slack in the optimization problem;
    # otherwise the edge may or may not have zero slack.
    allowedge = {}

    # Queue of newly discovered S-vertices.
    queue = []

    # Return 2 * slack of edge (v, w) (does not work inside blossoms).
    def slack(v, w):
        return dualvar[v] + dualvar[w] - 2 * G[v][w].get(weight, 1)

    # Assign label t to the top-level blossom containing vertex w,
    # coming through an edge from vertex v.
    def assignLabel(w, t, v):
        b = inblossom[w]
        assert label.get(w) is None and label.get(b) is None
        label[w] = label[b] = t
        if v is not None:
            labeledge[w] = labeledge[b] = (v, w)
        else:
            labeledge[w] = labeledge[b] = None
        bestedge[w] = bestedge[b] = None
        if t == 1:
            # b became an S-vertex/blossom; add it(s vertices) to the queue.
            if isinstance(b, Blossom):
                queue.extend(b.leaves())
            else:
                queue.append(b)
        elif t == 2:
            # b became a T-vertex/blossom; assign label S to its mate.
            # (If b is a non-trivial blossom, its base is the only vertex
            # with an external mate.)
            base = blossombase[b]
            assignLabel(mate[base], 1, base)

    # Trace back from vertices v and w to discover either a new blossom
    # or an augmenting path. Return the base vertex of the new blossom,
    # or NoNode if an augmenting path was found.
    def scanBlossom(v, w):
        # Trace back from v and w, placing breadcrumbs as we go.
        path = []
        base = NoNode
        while v is not NoNode:
            # Look for a breadcrumb in v's blossom or put a new breadcrumb.
            b = inblossom[v]
            if label[b] & 4:
                base = blossombase[b]
                break
            assert label[b] == 1
            path.append(b)
            label[b] = 5
            # Trace one step back.
            if labeledge[b] is None:
                # The base of blossom b is single; stop tracing this path.
                assert blossombase[b] not in mate
                v = NoNode
            else:
                assert labeledge[b][0] == mate[blossombase[b]]
                v = labeledge[b][0]
                b = inblossom[v]
                assert label[b] == 2
                # b is a T-blossom; trace one more step back.
                v = labeledge[b][0]
            # Swap v and w so that we alternate between both paths.
            if w is not NoNode:
                v, w = w, v
        # Remove breadcrumbs.
        for b in path:
            label[b] = 1
        # Return base vertex, if we found one.
        return base

    # Construct a new blossom with given base, through S-vertices v and w.
    # Label the new blossom as S; set its dual variable to zero;
    # relabel its T-vertices to S and add them to the queue.
    def addBlossom(base, v, w):
        bb = inblossom[base]
        bv = inblossom[v]
        bw = inblossom[w]
        # Create blossom.
        b = Blossom()
        blossombase[b] = base
        blossomparent[b] = None
        blossomparent[bb] = b
        # Make list of sub-blossoms and their interconnecting edge endpoints.
        b.childs = path = []
        b.edges = edgs = [(v, w)]
        # Trace back from v to base.
        while bv != bb:
            # Add bv to the new blossom.
            blossomparent[bv] = b
            path.append(bv)
            edgs.append(labeledge[bv])
            assert label[bv] == 2 or (
                label[bv] == 1 and labeledge[bv][0] == mate[blossombase[bv]]
            )
            # Trace one step back.
            v = labeledge[bv][0]
            bv = inblossom[v]
        # Add base sub-blossom; reverse lists.
        path.append(bb)
        path.reverse()
        edgs.reverse()
        # Trace back from w to base.
        while bw != bb:
            # Add bw to the new blossom.
            blossomparent[bw] = b
            path.append(bw)
            edgs.append((labeledge[bw][1], labeledge[bw][0]))
            assert label[bw] == 2 or (
                label[bw] == 1 and labeledge[bw][0] == mate[blossombase[bw]]
            )
            # Trace one step back.
            w = labeledge[bw][0]
            bw = inblossom[w]
        # Set label to S.
        assert label[bb] == 1
        label[b] = 1
        labeledge[b] = labeledge[bb]
        # Set dual variable to zero.
        blossomdual[b] = 0
        # Relabel vertices.
        for v in b.leaves():
            if label[inblossom[v]] == 2:
                # This T-vertex now turns into an S-vertex because it becomes
                # part of an S-blossom; add it to the queue.
                queue.append(v)
            inblossom[v] = b
        # Compute b.mybestedges.
        bestedgeto = {}
        for bv in path:
            if isinstance(bv, Blossom):
                if bv.mybestedges is not None:
                    # Walk this subblossom's least-slack edges.
                    nblist = bv.mybestedges
                    # The sub-blossom won't need this data again.
                    bv.mybestedges = None
                else:
                    # This subblossom does not have a list of least-slack
                    # edges; get the information from the vertices.
                    nblist = [
                        (v, w) for v in bv.leaves() for w in G.neighbors(v) if v != w
                    ]
            else:
                nblist = [(bv, w) for w in G.neighbors(bv) if bv != w]
            for k in nblist:
                (i, j) = k
                if inblossom[j] == b:
                    i, j = j, i
                bj = inblossom[j]
                if (
                    bj != b
                    and label.get(bj) == 1
                    and ((bj not in bestedgeto) or slack(i, j) < slack(*bestedgeto[bj]))
                ):
                    bestedgeto[bj] = k
            # Forget about least-slack edge of the subblossom.
            bestedge[bv] = None
        b.mybestedges = list(bestedgeto.values())
        # Select bestedge[b].
        mybestedge = None
        bestedge[b] = None
        for k in b.mybestedges:
            kslack = slack(*k)
            if mybestedge is None or kslack < mybestslack:
                mybestedge = k
                mybestslack = kslack
        bestedge[b] = mybestedge

    # Expand the given top-level blossom.
    def expandBlossom(b, endstage):
        # This is an obnoxiously complicated recursive function for the sake of
        # a stack-transformation.  So, we hack around the complexity by using
        # a trampoline pattern.  By yielding the arguments to each recursive
        # call, we keep the actual callstack flat.

        def _recurse(b, endstage):
            # Convert sub-blossoms into top-level blossoms.
            for s in b.childs:
                blossomparent[s] = None
                if isinstance(s, Blossom):
                    if endstage and blossomdual[s] == 0:
                        # Recursively expand this sub-blossom.
                        yield s
                    else:
                        for v in s.leaves():
                            inblossom[v] = s
                else:
                    inblossom[s] = s
            # If we expand a T-blossom during a stage, its sub-blossoms must be
            # relabeled.
            if (not endstage) and label.get(b) == 2:
                # Start at the sub-blossom through which the expanding
                # blossom obtained its label, and relabel sub-blossoms untili
                # we reach the base.
                # Figure out through which sub-blossom the expanding blossom
                # obtained its label initially.
                entrychild = inblossom[labeledge[b][1]]
                # Decide in which direction we will go round the blossom.
                j = b.childs.index(entrychild)
                if j & 1:
                    # Start index is odd; go forward and wrap.
                    j -= len(b.childs)
                    jstep = 1
                else:
                    # Start index is even; go backward.
                    jstep = -1
                # Move along the blossom until we get to the base.
                v, w = labeledge[b]
                while j != 0:
                    # Relabel the T-sub-blossom.
                    if jstep == 1:
                        p, q = b.edges[j]
                    else:
                        q, p = b.edges[j - 1]
                    label[w] = None
                    label[q] = None
                    assignLabel(w, 2, v)
                    # Step to the next S-sub-blossom and note its forward edge.
                    allowedge[(p, q)] = allowedge[(q, p)] = True
                    j += jstep
                    if jstep == 1:
                        v, w = b.edges[j]
                    else:
                        w, v = b.edges[j - 1]
                    # Step to the next T-sub-blossom.
                    allowedge[(v, w)] = allowedge[(w, v)] = True
                    j += jstep
                # Relabel the base T-sub-blossom WITHOUT stepping through to
                # its mate (so don't call assignLabel).
                bw = b.childs[j]
                label[w] = label[bw] = 2
                labeledge[w] = labeledge[bw] = (v, w)
                bestedge[bw] = None
                # Continue along the blossom until we get back to entrychild.
                j += jstep
                while b.childs[j] != entrychild:
                    # Examine the vertices of the sub-blossom to see whether
                    # it is reachable from a neighboring S-vertex outside the
                    # expanding blossom.
                    bv = b.childs[j]
                    if label.get(bv) == 1:
                        # This sub-blossom just got label S through one of its
                        # neighbors; leave it be.
                        j += jstep
                        continue
                    if isinstance(bv, Blossom):
                        for v in bv.leaves():
                            if label.get(v):
                                break
                    else:
                        v = bv
                    # If the sub-blossom contains a reachable vertex, assign
                    # label T to the sub-blossom.
                    if label.get(v):
                        assert label[v] == 2
                        assert inblossom[v] == bv
                        label[v] = None
                        label[mate[blossombase[bv]]] = None
                        assignLabel(v, 2, labeledge[v][0])
                    j += jstep
            # Remove the expanded blossom entirely.
            label.pop(b, None)
            labeledge.pop(b, None)
            bestedge.pop(b, None)
            del blossomparent[b]
            del blossombase[b]
            del blossomdual[b]

        # Now, we apply the trampoline pattern.  We simulate a recursive
        # callstack by maintaining a stack of generators, each yielding a
        # sequence of function arguments.  We grow the stack by appending a call
        # to _recurse on each argument tuple, and shrink the stack whenever a
        # generator is exhausted.
        stack = [_recurse(b, endstage)]
        while stack:
            top = stack[-1]
            for s in top:
                stack.append(_recurse(s, endstage))
                break
            else:
                stack.pop()

    # Swap matched/unmatched edges over an alternating path through blossom b
    # between vertex v and the base vertex. Keep blossom bookkeeping
    # consistent.
    def augmentBlossom(b, v):
        # This is an obnoxiously complicated recursive function for the sake of
        # a stack-transformation.  So, we hack around the complexity by using
        # a trampoline pattern.  By yielding the arguments to each recursive
        # call, we keep the actual callstack flat.

        def _recurse(b, v):
            # Bubble up through the blossom tree from vertex v to an immediate
            # sub-blossom of b.
            t = v
            while blossomparent[t] != b:
                t = blossomparent[t]
            # Recursively deal with the first sub-blossom.
            if isinstance(t, Blossom):
                yield (t, v)
            # Decide in which direction we will go round the blossom.
            i = j = b.childs.index(t)
            if i & 1:
                # Start index is odd; go forward and wrap.
                j -= len(b.childs)
                jstep = 1
            else:
                # Start index is even; go backward.
                jstep = -1
            # Move along the blossom until we get to the base.
            while j != 0:
                # Step to the next sub-blossom and augment it recursively.
                j += jstep
                t = b.childs[j]
                if jstep == 1:
                    w, x = b.edges[j]
                else:
                    x, w = b.edges[j - 1]
                if isinstance(t, Blossom):
                    yield (t, w)
                # Step to the next sub-blossom and augment it recursively.
                j += jstep
                t = b.childs[j]
                if isinstance(t, Blossom):
                    yield (t, x)
                # Match the edge connecting those sub-blossoms.
                mate[w] = x
                mate[x] = w
            # Rotate the list of sub-blossoms to put the new base at the front.
            b.childs = b.childs[i:] + b.childs[:i]
            b.edges = b.edges[i:] + b.edges[:i]
            blossombase[b] = blossombase[b.childs[0]]
            assert blossombase[b] == v

        # Now, we apply the trampoline pattern.  We simulate a recursive
        # callstack by maintaining a stack of generators, each yielding a
        # sequence of function arguments.  We grow the stack by appending a call
        # to _recurse on each argument tuple, and shrink the stack whenever a
        # generator is exhausted.
        stack = [_recurse(b, v)]
        while stack:
            top = stack[-1]
            for args in top:
                stack.append(_recurse(*args))
                break
            else:
                stack.pop()

    # Swap matched/unmatched edges over an alternating path between two
    # single vertices. The augmenting path runs through S-vertices v and w.
    def augmentMatching(v, w):
        for s, j in ((v, w), (w, v)):
            # Match vertex s to vertex j. Then trace back from s
            # until we find a single vertex, swapping matched and unmatched
            # edges as we go.
            while 1:
                bs = inblossom[s]
                assert label[bs] == 1
                assert (labeledge[bs] is None and blossombase[bs] not in mate) or (
                    labeledge[bs][0] == mate[blossombase[bs]]
                )
                # Augment through the S-blossom from s to base.
                if isinstance(bs, Blossom):
                    augmentBlossom(bs, s)
                # Update mate[s]
                mate[s] = j
                # Trace one step back.
                if labeledge[bs] is None:
                    # Reached single vertex; stop.
                    break
                t = labeledge[bs][0]
                bt = inblossom[t]
                assert label[bt] == 2
                # Trace one more step back.
                s, j = labeledge[bt]
                # Augment through the T-blossom from j to base.
                assert blossombase[bt] == t
                if isinstance(bt, Blossom):
                    augmentBlossom(bt, j)
                # Update mate[j]
                mate[j] = s

    # Verify that the optimum solution has been reached.
    def verifyOptimum():
        if maxcardinality:
            # Vertices may have negative dual;
            # find a constant non-negative number to add to all vertex duals.
            vdualoffset = max(0, -min(dualvar.values()))
        else:
            vdualoffset = 0
        # 0. all dual variables are non-negative
        assert min(dualvar.values()) + vdualoffset >= 0
        assert len(blossomdual) == 0 or min(blossomdual.values()) >= 0
        # 0. all edges have non-negative slack and
        # 1. all matched edges have zero slack;
        for i, j, d in G.edges(data=True):
            wt = d.get(weight, 1)
            if i == j:
                continue  # ignore self-loops
            s = dualvar[i] + dualvar[j] - 2 * wt
            iblossoms = [i]
            jblossoms = [j]
            while blossomparent[iblossoms[-1]] is not None:
                iblossoms.append(blossomparent[iblossoms[-1]])
            while blossomparent[jblossoms[-1]] is not None:
                jblossoms.append(blossomparent[jblossoms[-1]])
            iblossoms.reverse()
            jblossoms.reverse()
            for bi, bj in zip(iblossoms, jblossoms):
                if bi != bj:
                    break
                s += 2 * blossomdual[bi]
            assert s >= 0
            if mate.get(i) == j or mate.get(j) == i:
                assert mate[i] == j and mate[j] == i
                assert s == 0
        # 2. all single vertices have zero dual value;
        for v in gnodes:
            assert (v in mate) or dualvar[v] + vdualoffset == 0
        # 3. all blossoms with positive dual value are full.
        for b in blossomdual:
            if blossomdual[b] > 0:
                assert len(b.edges) % 2 == 1
                for i, j in b.edges[1::2]:
                    assert mate[i] == j and mate[j] == i
        # Ok.

    # Main loop: continue until no further improvement is possible.
    while 1:
        # Each iteration of this loop is a "stage".
        # A stage finds an augmenting path and uses that to improve
        # the matching.

        # Remove labels from top-level blossoms/vertices.
        label.clear()
        labeledge.clear()

        # Forget all about least-slack edges.
        bestedge.clear()
        for b in blossomdual:
            b.mybestedges = None

        # Loss of labeling means that we can not be sure that currently
        # allowable edges remain allowable throughout this stage.
        allowedge.clear()

        # Make queue empty.
        queue[:] = []

        # Label single blossoms/vertices with S and put them in the queue.
        for v in gnodes:
            if (v not in mate) and label.get(inblossom[v]) is None:
                assignLabel(v, 1, None)

        # Loop until we succeed in augmenting the matching.
        augmented = 0
        while 1:
            # Each iteration of this loop is a "substage".
            # A substage tries to find an augmenting path;
            # if found, the path is used to improve the matching and
            # the stage ends. If there is no augmenting path, the
            # primal-dual method is used to pump some slack out of
            # the dual variables.

            # Continue labeling until all vertices which are reachable
            # through an alternating path have got a label.
            while queue and not augmented:
                # Take an S vertex from the queue.
                v = queue.pop()
                assert label[inblossom[v]] == 1

                # Scan its neighbors:
                for w in G.neighbors(v):
                    if w == v:
                        continue  # ignore self-loops
                    # w is a neighbor to v
                    bv = inblossom[v]
                    bw = inblossom[w]
                    if bv == bw:
                        # this edge is internal to a blossom; ignore it
                        continue
                    if (v, w) not in allowedge:
                        kslack = slack(v, w)
                        if kslack <= 0:
                            # edge k has zero slack => it is allowable
                            allowedge[(v, w)] = allowedge[(w, v)] = True
                    if (v, w) in allowedge:
                        if label.get(bw) is None:
                            # (C1) w is a free vertex;
                            # label w with T and label its mate with S (R12).
                            assignLabel(w, 2, v)
                        elif label.get(bw) == 1:
                            # (C2) w is an S-vertex (not in the same blossom);
                            # follow back-links to discover either an
                            # augmenting path or a new blossom.
                            base = scanBlossom(v, w)
                            if base is not NoNode:
                                # Found a new blossom; add it to the blossom
                                # bookkeeping and turn it into an S-blossom.
                                addBlossom(base, v, w)
                            else:
                                # Found an augmenting path; augment the
                                # matching and end this stage.
                                augmentMatching(v, w)
                                augmented = 1
                                break
                        elif label.get(w) is None:
                            # w is inside a T-blossom, but w itself has not
                            # yet been reached from outside the blossom;
                            # mark it as reached (we need this to relabel
                            # during T-blossom expansion).
                            assert label[bw] == 2
                            label[w] = 2
                            labeledge[w] = (v, w)
                    elif label.get(bw) == 1:
                        # keep track of the least-slack non-allowable edge to
                        # a different S-blossom.
                        if bestedge.get(bv) is None or kslack < slack(*bestedge[bv]):
                            bestedge[bv] = (v, w)
                    elif label.get(w) is None:
                        # w is a free vertex (or an unreached vertex inside
                        # a T-blossom) but we can not reach it yet;
                        # keep track of the least-slack edge that reaches w.
                        if bestedge.get(w) is None or kslack < slack(*bestedge[w]):
                            bestedge[w] = (v, w)

            if augmented:
                break

            # There is no augmenting path under these constraints;
            # compute delta and reduce slack in the optimization problem.
            # (Note that our vertex dual variables, edge slacks and delta's
            # are pre-multiplied by two.)
            deltatype = -1
            delta = deltaedge = deltablossom = None

            # Compute delta1: the minimum value of any vertex dual.
            if not maxcardinality:
                deltatype = 1
                delta = min(dualvar.values())

            # Compute delta2: the minimum slack on any edge between
            # an S-vertex and a free vertex.
            for v in G.nodes():
                if label.get(inblossom[v]) is None and bestedge.get(v) is not None:
                    d = slack(*bestedge[v])
                    if deltatype == -1 or d < delta:
                        delta = d
                        deltatype = 2
                        deltaedge = bestedge[v]

            # Compute delta3: half the minimum slack on any edge between
            # a pair of S-blossoms.
            for b in blossomparent:
                if (
                    blossomparent[b] is None
                    and label.get(b) == 1
                    and bestedge.get(b) is not None
                ):
                    kslack = slack(*bestedge[b])
                    if allinteger:
                        assert (kslack % 2) == 0
                        d = kslack // 2
                    else:
                        d = kslack / 2.0
                    if deltatype == -1 or d < delta:
                        delta = d
                        deltatype = 3
                        deltaedge = bestedge[b]

            # Compute delta4: minimum z variable of any T-blossom.
            for b in blossomdual:
                if (
                    blossomparent[b] is None
                    and label.get(b) == 2
                    and (deltatype == -1 or blossomdual[b] < delta)
                ):
                    delta = blossomdual[b]
                    deltatype = 4
                    deltablossom = b

            if deltatype == -1:
                # No further improvement possible; max-cardinality optimum
                # reached. Do a final delta update to make the optimum
                # verifiable.
                assert maxcardinality
                deltatype = 1
                delta = max(0, min(dualvar.values()))

            # Update dual variables according to delta.
            for v in gnodes:
                if label.get(inblossom[v]) == 1:
                    # S-vertex: 2*u = 2*u - 2*delta
                    dualvar[v] -= delta
                elif label.get(inblossom[v]) == 2:
                    # T-vertex: 2*u = 2*u + 2*delta
                    dualvar[v] += delta
            for b in blossomdual:
                if blossomparent[b] is None:
                    if label.get(b) == 1:
                        # top-level S-blossom: z = z + 2*delta
                        blossomdual[b] += delta
                    elif label.get(b) == 2:
                        # top-level T-blossom: z = z - 2*delta
                        blossomdual[b] -= delta

            # Take action at the point where minimum delta occurred.
            if deltatype == 1:
                # No further improvement possible; optimum reached.
                break
            elif deltatype == 2:
                # Use the least-slack edge to continue the search.
                (v, w) = deltaedge
                assert label[inblossom[v]] == 1
                allowedge[(v, w)] = allowedge[(w, v)] = True
                queue.append(v)
            elif deltatype == 3:
                # Use the least-slack edge to continue the search.
                (v, w) = deltaedge
                allowedge[(v, w)] = allowedge[(w, v)] = True
                assert label[inblossom[v]] == 1
                queue.append(v)
            elif deltatype == 4:
                # Expand the least-z blossom.
                expandBlossom(deltablossom, False)

            # End of a this substage.

        # Paranoia check that the matching is symmetric.
        for v in mate:
            assert mate[mate[v]] == v

        # Stop when no more augmenting path can be found.
        if not augmented:
            break

        # End of a stage; expand all S-blossoms which have zero dual.
        for b in list(blossomdual.keys()):
            if b not in blossomdual:
                continue  # already expanded
            if blossomparent[b] is None and label.get(b) == 1 and blossomdual[b] == 0:
                expandBlossom(b, True)

    # Verify that we reached the optimum solution (only for integer weights).
    if allinteger:
        verifyOptimum()

    return matching_dict_to_set(mate)


@not_implemented_for("multigraph")
@not_implemented_for("directed")
@nx._dispatchable
def minimal_fraction_max_matching(G: nx.Graph):
    """Find a maximum fractional matching in the graph with the minimum 0.5 edges.

    A fractional matching is a generalization of a matching where each edge
    can have a value of 0, 1/2, or 1. The sum of edge values incident to any
    vertex cannot exceed 1.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    initial_matching : dict, optional (default=None)
        A dictionary mapping edge tuples (u,v) to values (0, 0.5, or 1).
        If not provided, an empty matching is used.

    Returns
    -------
    matching : dict
        A dictionary mapping edge tuples (u,v) to values (0, 0.5, or 1)
        representing the maximum fractional matching.

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1,3),(2,3)])
    >>> minimal_fraction_max_matching(G)
    {(1, 2): 0.5, (1, 3): 0.5, (2, 3): 0.5}
    >>> G =  nx.Graph([(1, 2), (1,3),(2,3),(3,4)])
    >>> minimal_fraction_max_matching(G)
    {(1, 2): 1, (3, 4): 1}
    >>> G = nx.Graph([(1, 2), (1,3),(2,4),(3,5),(4,5),(5,6),(6,7)])
    >>> minimal_fraction_max_matching(G)
    {(1, 2): 0.5, (1, 3): 0.5, (2, 4): 0.5, (3, 5): 0.5, (4, 5): 0.5, (6, 7): 1}

    Notes
    -----
    Based on the algorithm described in:
    "Konig-Egervary graphs, 2-bicritical graphs and fractional matchings"
    by Jean-Marie Bourjolly and William R. Pulleyblank
    Proggramer: Roi Sibony
    Date: 20.05.2024
    """
    solver = FractionalMatchingSolver(G)
    log.debug("#"*20 + " Starting the solver for minimal_fractoin_max_matching " + "#"*20)
    log.info("Starting fractional matching solver.")
    log.debug("Initial Graph" ":%s", G.edges(data=True))
    return solver.solve() 


class FractionalMatchingSolver:
    """Class for finding a maximum fractional matching in a graph."""
    
    def __init__(self, G: nx.Graph):
        """Initialize with a graph and optional initial matching."""
        self.G = G
        # Initialize the matching if not provided
        self.x = {} 
        
        # Ensure symmetric representation (if (u,v):val then also (v,u):val)
        for (u, v), val in list(self.x.items()):
            self.x[(v, u)] = val
            
        # These will be initialized in each solve iteration
        self.labels = {}
        self.preds = {}
    
    def solve(self) -> Dict[Tuple[Any, Any], float]:
        """Find a maximum fractional matching."""
        # Main loop: keeps trying to augment the matching until no further improvement
        while True:
            # Step 1: Initialize labels and predecessors
            self._initialize_labels()
            
            # Continue until we can't augment anymore
            augmented = False
            
            while not augmented:
                # Step 2: Scan edges to find potential augmentation
                result = self._edge_scan()

                log.info("Edge scan result: %s", result)
                # If no augmenting structure found, we're done with this phase
                if result is None:
                    log.debug("#"*20 + " Finished the current iteration " + "#"*20)
                    break
                    
                u, v = result
                # Step 3: Check the labels of the vertices
                # Handle based on the type of augmenting structure found
                if self.labels.get(v) == "+":
                    # Found an augmenting path/cycle of type 1 or 3
                    log.info("V is labeled '+', performing type 1/3 augmentation.")
                    self._augment(u, v)
                    augmented = True
                else:
                    # step 4
                    # Found a potential type 2 augmentation or need to label more nodes
                    log.info("V is unlabeled, checking for type 2 augmentation or labeling.")
                    if self._label_or_augment(u, v):
                        log.info("Type 2 augmentation possible, augmenting.")
                        self._augment(u, v)
                        augmented = True
            # If we couldn't augment in this phase, we're done
            if not augmented:
                break
        
        # Return only one direction of edges to match NetworkX convention
        result = {}
        for (u, v), val in self.x.items():
            if val > 0 and u < v:  # Only keep one direction and non-zero edges
                result[(u, v)] = val
        log.info("Final matching: %s", result)  
        return result
    
    def _initialize_labels(self) -> None:
        """
        Step 1 (Initialization).
        Label every unsaturated node "+" and every saturated node None.
        Initialize all predecessor pointers to None.
        """
        self.labels = {}
        self.preds = {v: None for v in self.G.nodes}   
        log.debug("Initializing labels and predecessors.")
        # Calculate saturation for each node
        node_values = {}
        for (u, v), val in self.x.items():
            node_values[u] = node_values.get(u, 0) + val
        
        # Label unsaturated nodes with "+"
        for node in self.G:
            saturation = node_values.get(node, 0)
            if saturation < 1:
                self.labels[node] = "+"
            else:
                self.labels[node] = None
            if node not in self.preds:
                self.preds[node] = None
        log.debug("Labels initialized: %s \n finshed the initilization", self.labels)

    def _edge_scan(self) -> Optional[Tuple[Any, Any]]:
        """
        Step 2 (Edge scan).
        Scan every edge [u,v] with u labelled "+". 
        - If v is "-", termination condition reached (matching is max).
        - Otherwise return a pair (u,v) to indicate where to go next:
            • if v is "+", caller should perform the type-1/3 augment; 
            • if v is None, caller should do label_or_augment.
        """
        log.debug("Scanning edges for potential augmenting structures.")
        # Scan all edges where one endpoint is labeled "+"
        for u in self.G:
            if self.labels.get(u) == "+":
                for v in self.G.neighbors(u):
                    # Check if this edge can be used for augmentation
                    
                    # Case 1: v is labeled "-" - terminates search
                    if self.labels.get(v) == "-":
                        continue
                        
                    # Case 2: v is labeled "+" - type 1/3 augmentation possible
                    if self.labels.get(v) == "+":
                        return (u, v)
                        
                    # Case 3: v is unlabeled - potential type 2 augmentation
                    if self.labels.get(v) is None:
                        # Only consider edges with x-value < 1
                        edge_val = self.x.get((u, v), 0)
                        if edge_val < 1:
                            return (u, v)
        
        # No augmenting structure found
        return None
    # Helper function to build the cycle
    def _build_cycle(self,path_u: list[Any], path_v: list[Any]) -> list[Any]:
        """
        Return the ordered list of vertices that form the simple cycle
        u → ... → v → u (edge v-u closes it).
        Both paths run from the vertex to the common root,
        so they always share at least that root.
        """
        set_u = set(path_u)
        # first common vertex when climbing from v towards the root
        lca = next(node for node in path_v if node in set_u)

        idx_u = path_u.index(lca)   # where LCA sits inside path_u
        idx_v = path_v.index(lca)   #               inside path_v

        # u ... lca   +   lca-1 ... v   (second part reversed)
        cycle = path_u[:idx_u + 1] + list(reversed(path_v[:idx_v]))
        return cycle            # starts with u, ends with v

    def _augment(self, u: Any, v: Any) -> None:
        """
        Step 3 (Augment).
        Trace back from u and v via preds to their respective unsaturated roots,
        classify it as type 1 or type 3, flip x-values along the cycle/path,
        then clear all labels and preds so we can re-initialize.
        """
        log.debug("Augmenting matching between vertices %s and %s", u, v)
        # Construct paths from u and v back to their roots
        path_u = [u]
        path_v = [v]
        
        # Trace path from u to its root
        current = u
        while self.preds[current] is not None:
            current = self.preds[current]
            path_u.append(current)
        
        # Trace path from v to its root
        current = v
        while self.preds[current] is not None:
            current = self.preds[current]
            path_v.append(current)
        
        # Check if this is type 1 (different roots) or type 3 (same root)
        if path_u[-1] != path_v[-1]:
            # Type 1: augmenting path between two different roots
            # Flip x-values along the path
            # Path from u's root to u
            log.info("Type 1 augmentation: flipping edges along path from u to its root.")
            path_u.reverse()
            for i in range(len(path_u) - 1):
                a, b = path_u[i], path_u[i+1]
                log.debug("Flipping edge (%s, %s)", a, b)
                self.x[(a, b)] = 1 - self.x.get((a, b), 0)
                self.x[(b, a)] = self.x[(a, b)]
            
            # Edge connecting u and v
            self.x[(u, v)] = 1 - self.x.get((u, v), 0)
            self.x[(v, u)] = self.x[(u, v)]
            
            # Path from v to v's root
            for i in range(len(path_v) - 1):
                a, b = path_v[i], path_v[i+1]
                self.x[(a, b)] = 1 - self.x.get((a, b), 0)
                self.x[(b, a)] = self.x[(a, b)]
        else:
            # Type 3: augmenting cycle with a common root
            # Form the cycle by joining the paths
            log.info("Type 3 augmentation: found common root, building cycle.")
            cycle = self._build_cycle(path_u, path_v)
            log.debug("Type 3 augmentation: found cycle %s", cycle)
            if not cycle:
                log.info("No cycle found through vertices:", path_u)
            # Flip x-values around the cycle
            for i in range(len(cycle)):
                a = cycle[i]
                b = cycle[(i + 1) % len(cycle)] 
                log.debug("Flipping edge (%s, %s)", a, b)
                self.x[(a, b)] = 0.5 if self.x.get((a, b), 0) != 0.5 else 0
                self.x[(b, a)] = self.x[(a, b)]
            
            path_v = path_v[::-1]
            # I need i and i+1 to turn on the corresponding edge to 1 depending on if odd or even index
            for i in range(len(path_v) - 1):
                a, b = path_v[i], path_v[i+1]
                log.debug("Final step of the augmentation for the path\nFlipping edge (%s, %s)", a, b)
                self.x[(a, b)] = 1 - self.x.get((a, b), 0)
                self.x[(b, a)] = self.x[(a, b)]

    
    def _label_or_augment(self, u: Any, v: Any) -> None:
        """
        Step 4 (Label or augment).
        If v is saturated but has an incident edge j with x[j]==1, then
          • set label[v] = "-", label[w] = "+" for that neighbor w,
          • set preds[w] = v, preds[v] = u,
          • return to edge_scan.
        Otherwise v lies on a 1/2-cycle: do the type-2 augmentation on that cycle,
        then clear labels/preds for a fresh start.
        """
        # Check if v has a neighbor w with edge value 1
        for w in self.G.neighbors(v):
            if self.x.get((v, w), 0) == 1:
                log.info("We are in the labeling part of the algorithm.")
                log.info("Found saturated neighbor w with edge value 1: %s", w)
                log.debug("Setting labels and predecessors for v=%s, w=%s", v, w)
                # Set labels and predecessors
                self.labels[v] = "-"
                self.labels[w] = "+"
                self.preds[v] = u
                self.preds[w] = v
                return False #return to step 2 (edge scan)
            
        # If we get here, v must be on a 1/2-cycle (type 2 augmentation)
        # Find the 1/2 -cycle by tracing from v
        cycle = [v]
        visited = {v}
        log.info("No saturated neighbor found, looking for 1/2-cycle starting from v: %s", v)
        while True:
            # Find the next node in the cycle (connected by a 1/2 edge)
            current = cycle[-1]
            next_node_found = False
            log.debug("Looking for next node in 1/2-cycle from current: %s", current)
            for next_node in self.G.neighbors(current):
                if self.x.get((current, next_node), 0) == 0.5 and next_node not in visited:
                    cycle.append(next_node)
                    visited.add(next_node)
                    next_node_found = True
                    break
            
            if not next_node_found:
                # Check if we've found a cycle
                for next_node in self.G.neighbors(current):
                    if next_node == cycle[0] and self.x.get((current, next_node), 0) == 0.5:
                        # Found the cycle, now perform the type 2 augmentation
                        for i in range(len(cycle)):
                            a = cycle[i]
                            b = cycle[(i + 1) % len(cycle)]
                            # Change 0.5 edges to 0 or 1 alternately
                            new_val = 0 if i % 2 == 0 else 1
                            log.debug("Augmenting edge (%s, %s) to value %s", a, b, new_val)
                            self.x[(a, b)] = new_val
                            self.x[(b, a)] = new_val
                        return True
                # If we get here, no cycle was found - this shouldn't happen in theory
                log.error("No cycle found in type-2 augmentation step. This should not happen.")
                return False
