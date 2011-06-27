"""
    Module to simplify the specification of user-defined equality functions for
    node and edge attributes during isomorphism checks.

    During the construction of an isomorphism, the algorithm considers two
    candidate nodes n1 in G1 and n2 in G2.  The graphs G1 and G2 are then
    compared with respect to properties involving n1 and n2, and if the outcome
    is good, then the candidate nodes are considered isomorphic. NetworkX
    provides a simple mechanism for users to extend the comparisons to include
    node and edge attributes.

    Node attributes are handled by the `node_match` keyword. When considering
    n1 and n2, the algorithm passes their node attribute dictionaries to
    `node_match`, and if it returns `False`, then n1 and n2 cannot be
    considered to be isomorphic.

    Edge attributes are handled by the `edge_match` keyword. When considering
    n1 and n2, the algorithm must verify that outgoing edges from n1 are
    commensurate with the outgoing edges for n2. If the graph is directed,
    then a similar check is also performed for incoming edges.

    Focusing only on outgoing edges, we consider pairs of nodes (n1, v1) from
    G1 and (n2, v2) from G2. For graphs and digraphs, there is only one edge
    between (n1, v1) and only one edge between (n2, v2). Those edge attribute
    dictionaries are passed to `edge_match`, and if it returns `False`, then
    n1 and n2 cannot be considered isomorphic. For multigraphs and
    multidigraphs, there can be multiple edges between (n1, v1) and also
    multiple edges between (n2, v2).  Now, there must exist an isomorphism
    from "all the edges between (n1, v1)" to "all the edges between (n2, v2)".
    So, all of the edge attribute dictionaries are passed to `edge_match`, and
    it must determine if there is an isomorphism between the two sets of edges.
"""

import networkx as nx

from . import isomorphvf2 as vf2

__all__ = ['GraphMatcher',
           'DiGraphMatcher',
           'MultiGraphMatcher',
           'MultiDiGraphMatcher',
           'close',
           'attrcompare_factory',
           'multi_attrcompare_factory_setlike'
          ]

def close(x, y, rtol=1.0000000000000001e-05, atol=1e-08):
    """Returns True if x and y are sufficiently close.

    Parameters
    ----------
    rtol : float
        The relative error tolerance.
    atol : float
        The absolute error tolerance.

    """
    # assumes finite weights
    return abs(x-y) <= atol + rtol * abs(y)

def attrcompare_factory(attrs):
    """Returns a customized attribute comparison function.

    For each attribute, the comparison functions are logically ANDed together.
    The comparison function is suitable as a `node_match` function or as an
    `edge_match` function for non-multi graphs and non-multi digraphs.

    Parameters
    ----------
    attrs : dict
        A dictionary keyed by attributes. The values should be 2-tuples of the
        form: (operator, default) where `operator` is the operator that should
        be used to compare the attribute values and `default` is the deafult
        value to use if an attribute does not exist in the dictionary.

    Returns
    -------
    match : callable
        A customized match function that can be used in (di)graph matchers.

    Examples
    --------
    >>> from networkx.algorithms.isomorphism.vf2userfunc import close
    >>> from operator import eq
    >>> attrs = { 'color': (eq, ''),
    ...           'size':  (close, 10),
    ...           'shape': (eq, 'circle') }
    ...
    >>> match = attrcompare_factory(attrs)
    >>> # g1 and g2 can be any graph or digraph, multi or not
    >>> gm = nx.is_isomorphic(g1, g2, node_match=match)
    >>> # g1 and g2 can be any non-multi graph or non-multi digraph
    >>> gm = nx.is_isomorphic(g1, g2, edge_match=match)

    """
    # We perform the logical AND of the operators.
    def match(attrs_g1, attrs_g2):
        for attr, (op, default) in attrs.items():
            v1 = attrs_g1.get(attr, default)
            v2 = attrs_g2.get(attr, default)
            if not op(v1, v2):
                return False
        else:
            return True

    return match

def multi_attrcompare_factory_setlike(attrs):
    """Returns a customized attribute comparison function for multi(di)graphs.

    For each attribute in `attrs`, a set of tuples is built from all the edges
    in each dictionary of dictionary of edge attributes. The comparison
    function is suitable as an `edge_match` function for multigraphs and
    multidigraphs.

    Parameters
    ----------
    attrs : dict
        A dictionary keyed by attributes. The values should be the default
        attribute values to use when an edge does not have the attribute
        specified.  The values of each edge attribute are assumed to be
        hashable and comparable via the == operator.

    Returns
    -------
    match : callable
        A customized match function that can be used in multi(di)graph matchers.

    Examples
    --------
    >>> from networkx.algorithms.isomorphism.vf2userfunc import close
    >>> from operator import eq
    >>> attrs = { 'color': '',
    ...           'linewidth': 10,
    ...           'shape': 'circle' }
    ...
    >>> match = multi_attrcompare_factory_setlike(attrs)
    >>> # g1 and g2 are multigraphs or multidigraphs
    >>> gm = nx.is_isomorphic(g1, g2, edge_match=match)

    """
    def match(attrs_g1, attrs_g2):
        data1 = set([])
        for eattrs in attrs_g1.values():
            x = tuple( eattrs.get(attr, d) for attr, d in attrs.items() )
            data1.add(x)
        data2 = set([])
        for eattrs in attrs_g2.values():
            x = tuple( eattrs.get(attr, d) for attr, d in attrs.items() )
            data2.add(x)

        return data1 == data2

    return match

def _semantic_feasibility(self, G1_node, G2_node):
    """
    Returns True if mapping G1_node to G2_node is semantically feasible.

    """
    # Make sure the nodes match
    if self.node_match is not None:
        nm = self.node_match(self.G1.node[G1_node], self.G2.node[G2_node])
        if not nm:
            return False

    # Make sure the edges match
    if self.edge_match is not None:

        # Cached lookups
        G1_adj = self.G1_adj
        G2_adj = self.G2_adj
        core_1 = self.core_1
        edge_match = self.edge_match

        for neighbor in G1_adj[G1_node]:
            # G1_node is not in core_1, so we must handle R_self separately
            if neighbor is G1_node:
                if not edge_match(G1_adj[G1_node][G1_node],
                                  G2_adj[G2_node][G2_node]):
                    return False
            elif neighbor in core_1:
                if not edge_match(G1_adj[G1_node][neighbor],
                                  G2_adj[G2_node][core_1[neighbor]]):
                    return False
        # syntactic check has already verified that neighbors are symmetric

    return True


class GraphMatcher(vf2.GraphMatcher):
    """
    VF2 isomorphism checker for undirected graphs.

    """
    def __init__(self, G1, G2, node_match=None, edge_match=None):
        """
        Parameters
        ----------
        G1, G2 : graph
            The graphs to be tested.

        node_match : callable
            A function that returns True iff node `n1` in `G1` and `n2` in `G2`
            should be considered equal during the isomorphism test. The
            function will be called like:

               node_match(G1.node[n1], G2.node[n2])

            That is, the function will receive the node attribute dictionaries
            of the nodes under consideration. If `None`, then no attributes are
            considered when testing for an isomorphism.

        edge_match : callable
            A function that returns True iff the edge attribute dictionary for
            the pair of nodes (u1, v1) in G1 and (u2, v2) in G2 should be
            considered equal during the isomorphism test. The function will be
            called like:

               edge_match(G1[u1][v1], G2[u2][v2])

            That is, the function will receive the edge attribute dictionaries
            of the edges under consideration. If `None`, then no attributes are
            considered when testing for an isomorphism.

        """
        vf2.GraphMatcher.__init__(self, G1, G2)

        self.node_match = node_match
        self.edge_match = edge_match

        # These will be modified during checks to minimize code repeat.
        self.G1_adj = self.G1.adj
        self.G2_adj = self.G2.adj

    semantic_feasibility = _semantic_feasibility


class DiGraphMatcher(vf2.DiGraphMatcher):
    """
    VF2 isomorphism checker for directed graphs.

    """
    def __init__(self, G1, G2, node_match=None, edge_match=None):
        """
        Parameters
        ----------
        G1, G2 : graph
            The graphs to be tested.

        node_match : callable
            A function that returns True iff node `n1` in `G1` and `n2` in `G2`
            should be considered equal during the isomorphism test. The
            function will be called like:

               node_match(G1.node[n1], G2.node[n2])

            That is, the function will receive the node attribute dictionaries
            of the nodes under consideration. If `None`, then no attributes are
            considered when testing for an isomorphism.

        edge_match : callable
            A function that returns True iff the edge attribute dictionary for
            the pair of nodes (u1, v1) in G1 and (u2, v2) in G2 should be
            considered equal during the isomorphism test. The function will be
            called like:

               edge_match(G1[u1][v1], G2[u2][v2])

            That is, the function will receive the edge attribute dictionaries
            of the edges under consideration. If `None`, then no attributes are
            considered when testing for an isomorphism.

        """
        vf2.DiGraphMatcher.__init__(self, G1, G2)

        self.node_match = node_match
        self.edge_match = edge_match

        # These will be modified during checks to minimize code repeat.
        self.G1_adj = self.G1.adj
        self.G2_adj = self.G2.adj


    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if mapping G1_node to G2_node is semantically feasible."""

        # Test node_match and also test edge_match on successors
        feasible = _semantic_feasibility(self, G1_node, G2_node)
        if not feasible:
            return False

        # Test edge_match on predecessors
        self.G1_adj = self.G1.pred
        self.G2_adj = self.G2.pred
        feasible = _semantic_feasibility(self, G1_node, G2_node)
        self.G1_adj = self.G1.adj
        self.G2_adj = self.G2.adj

        return feasible

## The "semantics" of `edge_match` are different for multi(di)graphs, but
## the implementation is the same.  So, technically we do not need to
## provide "multi" versions, but we do so to match NetworkX's base classes.

class MultiGraphMatcher(GraphMatcher):
    """
    VF2 isomorphism checker for undirected multigraphs.

    """
    pass

class MultiDiGraphMatcher(DiGraphMatcher):
    """
    VF2 isomorphism checker for directed multigraphs.

    """
    pass

