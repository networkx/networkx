# -*- encoding: utf-8 -*-
#
# coding.py - functions for encoding and decoding trees as sequences
#
# Copyright 2015-2019 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for encoding and decoding trees.

Since a tree is a highly restricted form of graph, it can be represented
concisely in several ways. This module includes functions for encoding
and decoding trees in the form of nested tuples and Prüfer
sequences. The former requires a rooted tree, whereas the latter can be
applied to unrooted trees. Furthermore, there is a bijection from Prüfer
sequences to labeled trees.

"""
from itertools import chain

import networkx as nx
from networkx.utils import not_implemented_for

__author__ = """\n""".join(['Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>',
                            'Pascal Ortiz <pascal.ortiz@gmail.com>'])

__all__ = ['from_nested_tuple', 'from_prufer_sequence', 'NotATree',
           'to_nested_tuple', 'to_prufer_sequence']


class NotATree(nx.NetworkXException):
    """Raised when a function expects a tree (that is, a connected
    undirected graph with no cycles) but gets a non-tree graph as input
    instead.

    """


@not_implemented_for('directed')
def to_nested_tuple(T, root, canonical_form=False):
    """Returns a nested tuple representation of the given tree.

    The nested tuple representation of a tree is defined
    recursively. The tree with one node and no edges is represented by
    the empty tuple, ``()``. A tree with ``k`` subtrees is represented
    by a tuple of length ``k`` in which each element is the nested tuple
    representation of a subtree.

    Parameters
    ----------
    T : NetworkX graph
        An undirected graph object representing a tree.

    root : node
        The node in ``T`` to interpret as the root of the tree.

    canonical_form : bool
        If ``True``, each tuple is sorted so that the function returns
        a canonical form for rooted trees. This means "lighter" subtrees
        will appear as nested tuples before "heavier" subtrees. In this
        way, each isomorphic rooted tree has the same nested tuple
        representation.

    Returns
    -------
    tuple
        A nested tuple representation of the tree.

    Notes
    -----
    This function is *not* the inverse of :func:`from_nested_tuple`; the
    only guarantee is that the rooted trees are isomorphic.

    See also
    --------
    from_nested_tuple
    to_prufer_sequence

    Examples
    --------
    The tree need not be a balanced binary tree::

        >>> T = nx.Graph()
        >>> T.add_edges_from([(0, 1), (0, 2), (0, 3)])
        >>> T.add_edges_from([(1, 4), (1, 5)])
        >>> T.add_edges_from([(3, 6), (3, 7)])
        >>> root = 0
        >>> nx.to_nested_tuple(T, root)
        (((), ()), (), ((), ()))

    Continuing the above example, if ``canonical_form`` is ``True``, the
    nested tuples will be sorted::

        >>> nx.to_nested_tuple(T, root, canonical_form=True)
        ((), ((), ()), ((), ()))

    Even the path graph can be interpreted as a tree::

        >>> T = nx.path_graph(4)
        >>> root = 0
        >>> nx.to_nested_tuple(T, root)
        ((((),),),)

    """

    def _make_tuple(T, root, _parent):
        """Recursively compute the nested tuple representation of the
        given rooted tree.

        ``_parent`` is the parent node of ``root`` in the supertree in
        which ``T`` is a subtree, or ``None`` if ``root`` is the root of
        the supertree. This argument is used to determine which
        neighbors of ``root`` are children and which is the parent.

        """
        # Get the neighbors of `root` that are not the parent node. We
        # are guaranteed that `root` is always in `T` by construction.
        children = set(T[root]) - {_parent}
        if len(children) == 0:
            return ()
        nested = (_make_tuple(T, v, root) for v in children)
        if canonical_form:
            nested = sorted(nested)
        return tuple(nested)

    # Do some sanity checks on the input.
    if not nx.is_tree(T):
        raise nx.NotATree('provided graph is not a tree')
    if root not in T:
        raise nx.NodeNotFound('Graph {} contains no node {}'.format(T, root))

    return _make_tuple(T, root, None)


def from_nested_tuple(sequence, sensible_relabeling=False):
    """Returns the rooted tree corresponding to the given nested tuple.

    The nested tuple representation of a tree is defined
    recursively. The tree with one node and no edges is represented by
    the empty tuple, ``()``. A tree with ``k`` subtrees is represented
    by a tuple of length ``k`` in which each element is the nested tuple
    representation of a subtree.

    Parameters
    ----------
    sequence : tuple
        A nested tuple representing a rooted tree.

    sensible_relabeling : bool
        Whether to relabel the nodes of the tree so that nodes are
        labeled in increasing order according to their breadth-first
        search order from the root node.

    Returns
    -------
    NetworkX graph
        The tree corresponding to the given nested tuple, whose root
        node is node 0. If ``sensible_labeling`` is ``True``, nodes will
        be labeled in breadth-first search order starting from the root
        node.

    Notes
    -----
    This function is *not* the inverse of :func:`to_nested_tuple`; the
    only guarantee is that the rooted trees are isomorphic.

    See also
    --------
    to_nested_tuple
    from_prufer_sequence

    Examples
    --------
    Sensible relabeling ensures that the nodes are labeled from the root
    starting at 0::

        >>> balanced = (((), ()), ((), ()))
        >>> T = nx.from_nested_tuple(balanced, sensible_relabeling=True)
        >>> edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        >>> all((u, v) in T.edges() or (v, u) in T.edges() for (u, v) in edges)
        True

    """

    def _make_tree(sequence):
        """Recursively creates a tree from the given sequence of nested
        tuples.

        This function employs the :func:`~networkx.tree.join` function
        to recursively join subtrees into a larger tree.

        """
        # The empty sequence represents the empty tree, which is the
        # (unique) graph with a single node. We mark the single node
        # with an attribute that indicates that it is the root of the
        # graph.
        if len(sequence) == 0:
            return nx.empty_graph(1)
        # For a nonempty sequence, get the subtrees for each child
        # sequence and join all the subtrees at their roots. After
        # joining the subtrees, the root is node 0.
        return nx.tree.join([(_make_tree(child), 0) for child in sequence])

    # Make the tree and remove the `is_root` node attribute added by the
    # helper function.
    T = _make_tree(sequence)
    if sensible_relabeling:
        # Relabel the nodes according to their breadth-first search
        # order, starting from the root node (that is, the node 0).
        bfs_nodes = chain([0], (v for u, v in nx.bfs_edges(T, 0)))
        labels = {v: i for i, v in enumerate(bfs_nodes)}
        # We would like to use `copy=False`, but `relabel_nodes` doesn't
        # allow a relabel mapping that can't be topologically sorted.
        T = nx.relabel_nodes(T, labels)
    return T


@not_implemented_for('directed')
def to_prufer_sequence(T):
    r"""Returns the Prüfer sequence of the given tree.

    A *Prüfer sequence* is a list of *n* - 2 numbers between 0 and
    *n* - 1, inclusive. The tree corresponding to a given Prüfer
    sequence can be recovered by repeatedly joining a node in the
    sequence with a node with the smallest potential degree according to
    the sequence.

    Parameters
    ----------
    T : NetworkX graph
        An undirected graph object representing a tree.

    Returns
    -------
    list
        The Prüfer sequence of the given tree.

    Raises
    ------
    NetworkXPointlessConcept
        If the number of nodes in `T` is less than two.

    NotATree
        If `T` is not a tree.

    KeyError
        If the set of nodes in `T` is not {0, …, *n* - 1}.

    Notes
    -----
    There is a bijection from labeled trees to Prüfer sequences. This
    function is the inverse of the :func:`from_prufer_sequence`
    function.

    Sometimes Prüfer sequences use nodes labeled from 1 to *n* instead
    of from 0 to *n* - 1. This function requires nodes to be labeled in
    the latter form. You can use :func:`~networkx.relabel_nodes` to
    relabel the nodes of your tree to the appropriate format.

    This implementation is from [1]_ and has linear time complexity.

    References
    ----------
    .. [1] Micikevicius Paulius, Caminiti Saverio and Deo Narsingh.
           "Linear-time algorithms for encoding trees as sequences of node labels"
           *Congressus Numerantium* 183 (2006): 66-75.
           <http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.70.5052&rank=1>

    See also
    --------
    to_nested_tuple
    from_prufer_sequence

    Examples
    --------
    There is a bijection between Prüfer sequences and labeled trees, so
    this function is the inverse of the :func:`from_prufer_sequence`
    function:

    >>> edges = [(0, 3), (1, 3), (2, 3), (3, 4), (4, 5)]
    >>> tree = nx.Graph(edges)
    >>> sequence = nx.to_prufer_sequence(tree)
    >>> sequence
    [3, 3, 3, 4]
    >>> tree2 = nx.from_prufer_sequence(sequence)
    >>> list(tree2.edges()) == edges
    True

    """
    # Perform some sanity checks on the input.
    n = len(T)
    if n < 2:
        msg = 'Prüfer sequence undefined for trees with fewer than two nodes'
        raise nx.NetworkXPointlessConcept(msg)
    if not nx.is_tree(T):
        raise nx.NotATree('provided graph is not a tree')
    if set(T) != set(range(n)):
        raise KeyError('tree must have node labels {0, ..., n - 1}')

    n = T.number_of_nodes()
    in_tree = [True] * n
    degree = [T.degree(i) for i in range(n)]
    cnt = 0
    result = []
    for i in range(n):
        index = i
        while degree[index] == 1 and index <= i:
            in_tree[index] = False
            for k in T[index]:
                degree[k] -= 1
            for parent in T[index]:
                if in_tree[parent]:
                    break
            result.append(parent)
            cnt += 1
            if cnt == n - 2:
                return result
            index = parent


def from_prufer_sequence(sequence):
    r"""Returns the tree corresponding to the given Prüfer sequence.

    A *Prüfer sequence* is a list of *n* - 2 numbers between 0 and
    *n* - 1, inclusive. The tree corresponding to a given Prüfer
    sequence can be recovered by repeatedly joining a node in the
    sequence with a node with the smallest potential degree according to
    the sequence.

    Parameters
    ----------
    sequence : list
        A Prüfer sequence, which is a list of *n* - 2 integers between
        zero and *n* - 1, inclusive.

    Returns
    -------
    NetworkX graph
        The tree corresponding to the given Prüfer sequence.

    Notes
    -----
    There is a bijection from labeled trees to Prüfer sequences. This
    function is the inverse of the :func:`from_prufer_sequence` function.

    Sometimes Prüfer sequences use nodes labeled from 1 to *n* instead
    of from 0 to *n* - 1. This function requires nodes to be labeled in
    the latter form. You can use :func:`networkx.relabel_nodes` to
    relabel the nodes of your tree to the appropriate format.

    This implementation is from [1]_ and has linear time complexity.

    References
    ----------
    .. [1] Micikevicius Paulius, Caminiti Saverio and Deo Narsingh.
           "Linear-time algorithms for encoding trees as sequences of node labels"
           *Congressus Numerantium* 183 (2006): 66-75.
           <http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.70.5052&rank=1>

    See also
    --------
    from_nested_tuple
    to_prufer_sequence

    Examples
    --------
    There is a bijection between Prüfer sequences and labeled trees, so
    this function is the inverse of the :func:`to_prufer_sequence`
    function:

    >>> edges = [(0, 3), (1, 3), (2, 3), (3, 4), (4, 5)]
    >>> tree = nx.Graph(edges)
    >>> sequence = nx.to_prufer_sequence(tree)
    >>> sequence
    [3, 3, 3, 4]
    >>> tree2 = nx.from_prufer_sequence(sequence)
    >>> list(tree2.edges()) == edges
    True

    """
    n = len(sequence) + 2
    T = nx.empty_graph(n)
    if n == 2:
        T.add_edge(0, 1)
        return T
    not_in = [True] * n
    mult = [0] * n
    for i in sequence:
        not_in[i] = False
        mult[i] += 1
    k = 0
    for j in range(n):
        u = j
        while k < n - 2 and u <= j and not_in[u]:
            v = sequence[k]
            T.add_edge(u, v)
            k += 1
            mult[v] -= 1
            if mult[v] == 0:
                not_in[v] = True
            u = v
        if k == n - 2:
            for u in range(j + 1, n):
                if not_in[u] and u != v:
                    break
            T.add_edge(u, v)
            return T
