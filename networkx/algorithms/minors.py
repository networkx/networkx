# minors.py - functions for computing minors of graphs
#
# Copyright 2015 Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Provides functions for computing minors of a graph."""
from itertools import chain
from itertools import combinations
from itertools import permutations
from itertools import product

__all__ = ['contracted_edge', 'contracted_nodes',
           'identified_nodes', 'quotient_graph']


def peek(iterable):
    """Returns an arbitrary element of ``iterable`` without removing it.

    This is most useful for peeking at an arbitrary element of a set::

        >>> peek({3, 2, 1})
        1
        >>> peek('hello')
        'h'

    """
    return next(iter(iterable))


def equivalence_classes(iterable, relation):
    """Returns the set of equivalence classes of the given ``iterable`` under
    the specified equivalence relation.

    ``relation`` must be a Boolean-valued function that takes two argument. It
    must represent an equivalence relation (that is, the relation induced by
    the function must be reflexive, symmetric, and transitive).

    The return value is a set of sets. It is a partition of the elements of
    ``iterable``; duplicate elements will be ignored so it makes the most sense
    for ``iterable`` to be a :class:`set`.

    """
    # For simplicity of implementation, we initialize the return value as a
    # list of lists, then convert it to a set of sets at the end of the
    # function.
    blocks = []
    # Determine the equivalence class for each element of the iterable.
    for y in iterable:
        # Each element y must be in *exactly one* equivalence class.
        #
        # Each block is guaranteed to be non-empty
        for block in blocks:
            x = peek(block)
            if relation(x, y):
                block.append(y)
                break
        else:
            # If the element y is not part of any known equivalence class, it
            # must be in its own, so we create a new singleton equivalence
            # class for it.
            blocks.append([y])
    return {frozenset(block) for block in blocks}


def quotient_graph(G, node_relation, edge_relation=None, create_using=None):
    """Returns the quotient graph of ``G`` under the specified equivalence
    relation on nodes.

    Parameters
    ----------
    G : NetworkX graph
       The graph for which to return the quotient graph with the specified node
       relation.

    node_relation : Boolean function with two arguments
       This function must represent an equivalence relation on the nodes of
       ``G``. It must take two arguments *u* and *v* and return ``True``
       exactly when *u* and *v* are in the same equivalence class. The
       equivalence classes form the nodes in the returned graph.

    edge_relation : Boolean function with two arguments
       This function must represent an edge relation on the *blocks* of ``G``
       in the partition induced by ``node_relation``. It must take two
       arguments, *B* and *C*, each one a set of nodes, and return ``True``
       exactly when there should be an edge joining block *B* to block *C* in
       the returned graph.

       If ``edge_relation`` is not specified, it is assumed to be the following
       relation. Block *B* is related to block *C* if and only if some node in
       *B* is adjacent to some node in *C*, according to the edge set of ``G``.

    create_using : NetworkX graph
       If specified, this must be an instance of a NetworkX graph class. The
       nodes and edges of the quotient graph will be added to this graph and
       returned. If not specified, the returned graph will have the same type
       as the input graph.

    Returns
    -------
    NetworkX graph
       The quotient graph of ``G`` under the equivalence relation specified by
       ``node_relation``.

    Examples
    --------
    The quotient graph of the complete bipartite graph under the "same
    neighbors" equivalence relation is `K_2`. Under this relation, two nodes
    are equivalent if they are not adjacent but have the same neighbor set::

        >>> import networkx as nx
        >>> G = nx.complete_bipartite_graph(2, 3)
        >>> same_neighbors = lambda u, v: (u not in G[v] and v not in G[u]
        ...                                and G[u] == G[v])
        >>> Q = nx.quotient_graph(G, same_neighbors)
        >>> K2 = nx.complete_graph(2)
        >>> nx.is_isomorphic(Q, K2)
        True

    The quotient graph of a directed graph under the "same strongly connected
    component" equivalence relation is the condensation of the graph (see
    :func:`condensation`). This example comes from the Wikipedia article
    *`Strongly connected component`_*::

        >>> import networkx as nx
        >>> G = nx.DiGraph()
        >>> edges = ['ab', 'be', 'bf', 'bc', 'cg', 'cd', 'dc', 'dh', 'ea',
        ...          'ef', 'fg', 'gf', 'hd', 'hf']
        >>> G.add_edges_from(tuple(x) for x in edges)
        >>> components = list(nx.strongly_connected_components(G))
        >>> sorted(sorted(component) for component in components)
        [['a', 'b', 'e'], ['c', 'd', 'h'], ['f', 'g']]
        >>>
        >>> C = nx.condensation(G, components)
        >>> component_of = C.graph['mapping']
        >>> same_component = lambda u, v: component_of[u] == component_of[v]
        >>> Q = nx.quotient_graph(G, same_component)
        >>> nx.is_isomorphic(C, Q)
        True

    Node identification can be represented as the quotient of a graph under the
    equivalence relation that places the two nodes in one block and each other
    node in its own singleton block::

        >>> import networkx as nx
        >>> K24 = nx.complete_bipartite_graph(2, 4)
        >>> K34 = nx.complete_bipartite_graph(3, 4)
        >>> C = nx.contracted_nodes(K34, 1, 2)
        >>> nodes = {1, 2}
        >>> is_contracted = lambda u, v: u in nodes and v in nodes
        >>> Q = nx.quotient_graph(K34, is_contracted)
        >>> nx.is_isomorphic(Q, C)
        True
        >>> nx.is_isomorphic(Q, K24)
        True

    .. _Strongly connected component: https://en.wikipedia.org/wiki/Strongly_connected_component

    """
    H = type(create_using)() if create_using is not None else type(G)()
    # Compute the blocks of the partition on the nodes of G induced by the
    # equivalence relation R.
    H.add_nodes_from(equivalence_classes(G, node_relation))
    # By default, the edge relation is the relation defined as follows. B is
    # adjacent to C if a node in B is adjacent to a node in C, according to the
    # edge set of G.
    #
    # This is not a particularly efficient implementation of this relation:
    # there are O(n^2) pairs to check and each check may require O(log n) time
    # (to check set membership). This can certainly be parallelized.
    if edge_relation is None:
        edge_relation = lambda b, c: any(v in G[u] for u, v in product(b, c))
    block_pairs = permutations(H, 2) if H.is_directed() else combinations(H, 2)
    H.add_edges_from((b, c) for (b, c) in block_pairs if edge_relation(b, c))
    return H


def contracted_nodes(G, u, v, self_loops=True):
    """Returns the graph that results from contracting ``u`` and ``v``.

    Node contraction identifies the two nodes as a single node incident to any
    edge that was incident to the original two nodes.

    Parameters
    ----------
    G : NetworkX graph
       The graph whose nodes will be contracted.

    u, v : nodes
       Must be nodes in ``G``.

    self_loops : Boolean
       If this is ``True``, any edges joining ``u`` and ``v`` in ``G`` become
       self-loops on the new node in the returned graph.

    Returns
    -------
    Networkx graph
       A new graph object of the same type as ``G`` (leaving ``G`` unmodified)
       with ``u`` and ``v`` identified in a single node. The right node ``v``
       will be merged into the node ``u``, so only ``u`` will appear in the
       returned graph.

    Examples
    --------
    Contracting two nonadjacent nodes of the cycle graph on four nodes `C_4`
    yields the path graph (ignoring parallel edges)::

        >>> import networkx as nx
        >>> G = nx.cycle_graph(4)
        >>> M = nx.contracted_nodes(G, 1, 3)
        >>> P3 = nx.path_graph(3)
        >>> nx.is_isomorphic(M, P3)
        True

    See also
    --------
    contracted_edge
    quotient_graph

    Notes
    -----
    This function is also available as ``identified_nodes``.
    """
    H = G.copy()
    if H.is_directed():
        in_edges = ((w, u, d) for w, x, d in G.in_edges(v, data=True)
                    if self_loops or w != u)
        out_edges = ((u, w, d) for x, w, d in G.out_edges(v, data=True)
                     if self_loops or w != u)
        new_edges = chain(in_edges, out_edges)
    else:
        new_edges = ((u, w, d) for x, w, d in G.edges(v, data=True)
                     if self_loops or w != u)
    v_data = H.node[v]
    H.remove_node(v)
    H.add_edges_from(new_edges)
    if 'contraction' in H.node[u]:
        H.node[u]['contraction'][v] = v_data
    else:
        H.node[u]['contraction'] = {v: v_data}
    return H

identified_nodes = contracted_nodes


def contracted_edge(G, edge, self_loops=True):
    """Returns the graph that results from contracting the specified edge.

    Edge contraction identifies the two endpoints of the edge as a single node
    incident to any edge that was incident to the original two nodes. A graph
    that results from edge contraction is called a *minor* of the original
    graph.

    Parameters
    ----------
    G : NetworkX graph
       The graph whose edge will be contracted.

    edge : tuple
       Must be a pair of nodes in ``G``.

    self_loops : Boolean
       If this is ``True``, any edges (including ``edge``) joining the
       endpoints of ``edge`` in ``G`` become self-loops on the new node in the
       returned graph.

    Returns
    -------
    Networkx graph
       A new graph object of the same type as ``G`` (leaving ``G`` unmodified)
       with endpoints of ``edge`` identified in a single node. The right node
       of ``edge`` will be merged into the left one, so only the left one will
       appear in the returned graph.

    Raises
    ------
    ValueError
       If ``edge`` is not an edge in ``G``.

    Examples
    --------
    Attempting to contract two nonadjacent nodes yields an error::

        >>> import networkx as nx
        >>> G = nx.cycle_graph(4)
        >>> nx.contracted_edge(G, (1, 3))
        Traceback (most recent call last):
          ...
        ValueError: Edge (1, 3) does not exist in graph G; cannot contract it

    Contracting two adjacent nodes in the cycle graph on *n* nodes yields the
    cycle graph on *n - 1* nodes::

        >>> import networkx as nx
        >>> C5 = nx.cycle_graph(5)
        >>> C4 = nx.cycle_graph(4)
        >>> M = nx.contracted_edge(C5, (0, 1), self_loops=False)
        >>> nx.is_isomorphic(M, C4)
        True

    See also
    --------
    contracted_nodes
    quotient_graph

    """
    if not G.has_edge(*edge):
        raise ValueError('Edge {0} does not exist in graph G; cannot contract'
                         ' it'.format(edge))
    return contracted_nodes(G, *edge, self_loops=self_loops)
