"""
Algorithm for computing a :math:s -club cluster graph (an undirected graph where
all connected components have diameter at most :math:s) from a given graph :math:G.

Given a positive integer :math:d, and an undirected simple graph :math:G,
produce a d-club graph :math:G_d that is an induced subgraph
of :math:G. Note that :math:G_d is not unique to :math:G.

*d-fragmentation* is the process of removing a minimum number of edges from a
graph :math:G such that the resultant graph is a *d-club* cluster graph. See [1]_ for a formal
definition of a *d-club*.

This implementation is for simple undirected forests and
is based on the linear time algorithm presented in [2]_.


Examples
--------

>>>
>>> # A forest F with two trees.
... F = nx.Graph()
>>> F.add_edges_from(
...     [
...         ("a", "b"),
...         ("a", "c"),
...         ("c", "d"),
...         ("b", "e"),
...         ("b", "f"),
...         ("f", "g"),
...         ("f", "h"),
...         ("f", "i"),
...         ("j", "k"),
...         ("j", "m"),
...         ("k", "l"),
...         ("m", "n"),
...         ("m", "o"),
...         ("m", "q"),
...         ("q", "p"),
...         ("q", "r"),
...     ]
... )
>>>
>>> d = 2
>>> # A set of edges of minimum cardinality
>>> # that must be deleted to obtain a maximum 2-club from F.
>>> edge_cut = nx.d_fragmented(F, d)
>>> edge_cut_list = list(edge_cut)
>>> sz = len(edge_cut_list)
>>> sz
4
>>> # Since a 2-club cluster subgraph is not unique
>>> # the actual edge_cut may vary but the size of all
>>> # minimum edge_cuts should be `sz`.

>>> d = 3
>>> # A set of edges of minimum cardinality
>>> # that must be deleted to obtain a maximum 3-club from F.
>>> edge_cut = nx.d_fragmented(F, d)
>>> edge_cut_list = list(edge_cut)
>>> sz = len(edge_cut_list)
>>> sz
2
>>> # Since a 3-club cluster subgraph is not unique
>>> # the actual edge_cut may vary but the size of all
>>> # minimum edge_cuts should be `sz`.
>>> d = 4
>>> # A set of edges of minimum cardinality
>>> # that must be deleted to obtain a maximum 4-club from F.
>>> edge_cut = nx.d_fragmented(F, d)
>>> edge_cut_list = list(edge_cut)
>>> sz = len(edge_cut_list)
>>> sz
2
>>> # Since a 4-club cluster subgraph is not unique
>>> # the actual edge_cut may vary but the size of all
>>> # minimum edge_cuts should be `sz`.
>>>
>>> d = 5
>>> # A set of edges of minimum cardinality
>>> # that must be deleted to obtain a maximum 5-club from F.
>>> # Note that since the diameter of both the components is 5,
>>> # it is already a 5-club cluster graph.
>>> # Hence no edges need to be removed from F.
>>>
>>> edge_cut = nx.d_fragmented(F, d)
>>> edge_cut_list = list(edge_cut)
>>> sz = len(edge_cut_list)
>>> sz
0


References
----------

..  [1] Schafer, A. (2009). Diploma Thesis. Friedrich Schiller University Jena Faculty of Mathematics and Computer Science. [Exact Algorithms for s-Club Finding and Related Problems](https://pure.mpg.de/rest/items/item_1587743_4/component/file_1587742/content)

..  [2] Oellerman, O., Patel, A. (2020). The s-club deletion problem on various graph families. (Work in Progress). University of Winnipeg, Canada.

"""


from typing import Dict, Generator

import networkx as nx
from networkx.utils import not_implemented_for
from networkx.algorithms.tree import recognition
from networkx.algorithms.components import connected
from operator import itemgetter


__all__ = ["d_fragmented"]


@not_implemented_for("directed", "multigraph")
def d_fragmented(G: nx.Graph, d: int) -> Generator:
    """
    Given a simple undirected graph G, compute a
    d-club cluster graph.

    Parameters
    ----------
    G: A networkX graph instance.
        Any simple undirected graph.
    d: A non-negative int.
        The club-size of a cluster graph.

    Raises
    ------
    NetworkXNotImplemented
        The case where G is not a Forest is not
        supported.


    Yields
    -------
    edge: Tuple
        Tuples that represent undirected edges
        between nodes of G.


    Notes
    ______

    Runs in O(|V(G)|) if
    G is a Forest (a collection of
    pair-wise disconnected trees).
    This algorithm is provided in
    [1]_.

    If more results are known, it is encouraged to add to this file
    the support for more cases.

    References
    ----------
    .. [1] Oellerman, O., Patel, A.,
        The s-club deletion problem on various graph families,
        University of Winnipeg, Canada, 2020.

    """
    if d < 0:
        raise ValueError("Note d cannot be negative.")
    elif d == 0:
        yield from G.edges
    elif recognition.is_forest(G):
        for comp in connected.connected_components(G):
            h = G.subgraph(comp)
            yield from iter(_d_fragment_tree(h, d))

    else:
        # TODO: Implement d-fragmentation for arbitrary graphs

        no_good_algorithm_known = """
            If d >= 1, then no fast algorithms of d-fragmentation are known for graphs that are not forests.
            In fact, the problem of extracting a maximum d-club cluster graph from an arbitrary graph
            for d >= 2 is known to be NP-Complete.

            The current implementation only supports forests for d >= 1.
            If you know one, please consider adding it to NetworkX by following:

            https://github.com/networkx/networkx/blob/master/CONTRIBUTING.rst
        """
        raise nx.exception.NetworkXNotImplemented(no_good_algorithm_known)


def _is_leaf(G: nx.Graph, node):
    """
    Return True if node is a leaf,
    False otherwise.
    """

    return len(list(G.neighbors(node))) == 1


def _get_node_with_highest_degree(G: nx.Graph):
    """
    Get a random node from the vertex
    set of the graph.
    """
    if len(list(G.nodes)) == 0:
        raise ValueError("Empty graph has no nodes.")
    heaviest_node = max(list(G.nodes), key=lambda x: G.degree[x])
    return heaviest_node


def _d_fragment_tree_helper(G: nx.Graph, parent, node, sub_ecc: Dict, d: int, edge_set):
    """
    A helper for recursive computation
    of a d-club cluster graph from G.

    Parameters
    ----------
    G: networkX.graph()
        A Tree.
    parent: node
        Some vertex of G. It could be a sentinel as well if node is the root.
    node: node
        Some vertex of G. This cannot be sentinel.
    sub_ecc: dict
        A dictionary of computed eccentricities
        for subtrees rooted at some vertex.
    d: int
        A positive int.
    edge_set: Set
        A set that collects the edges that
        form an edge cut.

    Returns
    -------
    sub_ecc, edge_set: Tuple
        A tuple (sub_ecc, edge_set) where `sub_ecc`
        is a populated dictionary of computed
        eccentricities for subtrees rooted at some vertex
        and `edge_set` is a minimum edge cut.
    """
    if _is_leaf(G, node):
        sub_ecc[node] = 0
    else:
        for n in G.neighbors(node):
            if n != parent:
                _d_fragment_tree_helper(G, node, n, sub_ecc, d, edge_set)

        ecc_values = []

        for c in G.neighbors(node):
            if c in sub_ecc and c != parent:
                ecc_values.append((c, sub_ecc[c]))

        values = sorted(ecc_values, key=itemgetter(1), reverse=True)

        if len(values) == 1:
            child, child_ecc = values[0]

            if child_ecc >= d:
                edge_set |= {(child, node)}
                sub_ecc[node] = 0
            else:
                sub_ecc[node] = sub_ecc[child] + 1
        else:
            no_more = False

            for _counter in range(len(values) - 1):
                _first = values[_counter]
                _second = values[_counter + 1]

                child_first, ecc_first = _first
                child_second, ecc_second = _second

                if ecc_first + ecc_second + 2 >= d + 1:
                    edge_set |= {(child_first, node)}
                else:
                    sub_ecc[node] = sub_ecc[child_first] + 1
                    no_more = True
                    break

            if not no_more:
                child_last, ecc_last = values[-1]
                if ecc_last >= d:
                    edge_set |= {(child_last, node)}
                    sub_ecc[node] = 0
                else:
                    sub_ecc[node] = sub_ecc[child_last] + 1
    return sub_ecc, edge_set


def _d_fragment_tree(G: nx.Graph, d: int):
    """
    Compute the minimum edge cut
    that transforms G into a
    d-club cluster graph.

    Parameters
    ----------
    G: A networkX graph.
        A tree.
    d: A non-negative int
        The club-size for a cluster graph of G.

    Returns
    -------

    """

    class Sentinel:
        """
        A sentinel node that is different
        from every other node in a graph.
        """

        def __eq__(self, other):
            return False

        pass

    if len(list(G.edges)) == 0:
        return set()

    node = _get_node_with_highest_degree(G)
    sub_ecc = dict()
    parent = Sentinel()
    edge_set = set()
    ecc, edges = _d_fragment_tree_helper(G, parent, node, sub_ecc, d, edge_set)
    return edges


# Leaving the following function commented
# so that if more d-fragmentation algorithms are added
# in future, then they can be tested locally.

# def tester():
#     adjacency = {
#         0: {1, 6},
#         1: {0, 3},
#         2: {3},
#         3: {1, 2},
#         4: {7},
#         5: {7},
#         6: {0, 7},
#         7: {4, 5, 6}
#     }
#
#     def get_edges_from_adjacency(adj):
#         return [(u, v) for u, nbrs in adj.items() for v in nbrs]
#
#     g = nx.Graph()
#     g.update(edges=get_edges_from_adjacency(adjacency), nodes=adjacency)
#
#     # print(_is_forest(G))
#     for edg in d_fragmented(g, 2):
#         print(edg)
#         pass
