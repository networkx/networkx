# -*- encoding: utf-8 -*-
#
# structuralholes.py - functions for computing measures of structural holes
#
# Copyright 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for computing measures of structural holes."""
from __future__ import division

import itertools
import math

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['aggregate_constraint', 'constraint', 'effective_size',
           'efficiency', 'hierarchy', 'local_constraint']


def all_neighbors(G, n):
    """Returns an iterator over all in- and out-neighbors of node `n` in
    the graph `G`.

    If `G` is an undirected graph, this simply returns an iterator over
    the neighbors of `n`.

    """
    if G.is_directed():
        return itertools.chain(G.predecessors(n), G.successors(n))
    return G.neighbors(n)


@not_implemented_for('multigraph')
def mutual_weight(G, u, v, weight='weight'):
    """Returns the sum of the weights of the edge from `u` to `v` and
    the edge from `v` to `u` in `G`.

    `weight` is the edge data key that represents the edge weight. If
    the specified key is not in the edge data for an edge, that edge is
    assumed to have weight 1.

    Pre-conditions: `u` and `v` must both be in `G`.

    """
    return (G[u][v].get(weight, 1) if v in G[u] else 0
            + G[v][u].get(weight, 1) if u in G[v] else 0)


def normalized_mutual_weight(G, u, v, normalization=sum):
    """Returns normalized mutual weight of the edges from `u` to `v`
    with respect to the mutual weights of the neighbors of `u` in `G`.

    `normalization` specifies how the normalization factor is
    computed. It must be a function that takes a single argument and
    returns a number. The argument will be an iterable of mutual weights
    of pairs ``(u, w)``, where ``w`` ranges over each (in- and
    out-)neighbor of ``u``. Commons values for `normalization` are
    ``sum`` and ``max``.

    """
    scale = normalization(mutual_weight(G, u, w) for w in all_neighbors(G, u))
    return 0 if scale == 0 else mutual_weight(G, u, v) / scale


# def ego_density(G, v):
#     """Returns the density of the ego graph of ``v``.

#     This function ignores edge weights.

#     Parameters
#     ----------
#     G : NetworkX graph

#     v : node
#         The node whose ego density will be returned. This must be a node in
#         the graph ``G``.

#     Returns
#     -------
#     float
#         The ego density of ``v`` in ``G``.

#     See also
#     --------
#     density
#     ego_graph

#     Examples
#     --------
#     Compute the ego density as a percentage by multiplying the density by one
#     hundred::

#         >>> from networkx import complete_graph, ego_density
#         >>> G = complete_graph(5)
#         >>> density = ego_density(G, 0)
#         >>> density * 100
#         100

#     """
#     # TODO Is there a definition that makes sense for weighted graphs?
#     return nx.density(nx.ego_graph(G, v, center=False, undirected=True))


def effective_size(G, v):
    """Returns the effective size of ``v`` in the graph ``G``.

    The *effective size* of a node is the difference between the degree
    of the node and the average degree in the subgraph induced by its
    neighbors [1]_.

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``v``. Directed graphs are treated like
        undirected graphs when computing neighbors of ``v``.
    v : node
        A node in the graph ``G``.

    Returns
    -------
    float
        The effective size of the node ``v`` in the graph ``G``.

    Notes
    -----
    This function ignores edge weights.

    See also
    --------
    efficiency

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Harvard University Press, 2009.

    """
    ndeg = G.degree(v)
    E = nx.ego_graph(G, v, center=False, undirected=True)
    return ndeg - sum(d for v, d in E.degree()) / (ndeg - 1)


# TODO This name will clash with the global/local/nodal efficiency in
# pull request #1521.
def efficiency(G, v):
    """Returns the efficiency of ``v`` in the graph ``G``.

    The *efficiency* of a node is the effective size of the node
    normalized by the degree of that node [1]_. For the definition of
    effective size, see :func:`effective_size`.

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``v``. Directed graphs are treated like
        undirected graphs when computing neighbors of ``v``.
    v : node
        A node in the graph ``G``.

    Returns
    -------
    float
        The efficiency of the node ``v`` in the graph ``G``.

    Notes
    -----
    This function ignores edge weights.

    See also
    --------
    efficiency

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Harvard University Press, 2009.

    """
    return effective_size(G, v) / G.degree(v)


def constraint(G, v):
    r"""Returns the constraint on the node ``v`` in the graph ``G``.

    The *constraint* is a measure of the extent to which a node *v* is
    invested in those nodes that are themselves invested in the
    neighbors of *v*. Formally, the *constraint on v*, denoted `c(v)`,
    is defined by

    .. math::

       c(v) = \sum_{w \in N(v) \setminus \{v\}} \ell(v, w)

    where `N(v)` is the subset of the neighbors of `v` that are both
    predecessors and successors of `v` and `\ell(v, w)` is the local
    constraint on `v` with respect to `w` [1]_. For the definition of local
    constraint, see :func:`local_constraint`.

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``v``. This can be either directed or undirected.
    v : node
        A node in the graph ``G``.

    Returns
    -------
    float
        The constraint on the node ``v`` in the graph ``G``.

    Notes
    -----
    This function takes edge weights into account, assuming they are
    stored under the edge data key ``'weight'``.

    See also
    --------
    local_constraint

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Harvard University Press, 2009.

    """
    if G.is_directed():
        neighbors = set(G.successors(v)) & set(G.predecessors(v))
    else:
        neighbors = G.neighbors(v)
    return sum(local_constraint(G, v, n) for n in neighbors)


def local_constraint(G, u, v):
    r"""Returns the local constraint on the node ``u`` with respect to
    the node ``v`` in the graph ``G``.

    Formally, the *local constraint on u with respect to v*, denoted
    `\ell(v)`, is defined by

    .. math::

       ell(u, v) = \left(p(u, v) + \sum_{w \in N(v)} p(u, w) p(w, v)\right)^2,

    where `N(v)` is the set of neighbors of `v` and `p(x, y)` is the
    normalized mutual weight of the (directed or undirected) edges
    joining `x` and `y`, for each vertex `x` and `y` [1]_. The *mutual
    weight* of `x` and `y` is the sum of the weights of edges joining
    them (edge weights are assumed to be one if the graph is
    unweighted).

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``u`` and ``v``. This can be either
        directed or undirected.

    u : node
        A node in the graph ``G``.

    v : node
        A node in the graph ``G``.

    Returns
    -------
    float
        The constraint of the node ``v`` in the graph ``G``.

    Notes
    -----
    This function takes edge weights into account, assuming they are
    stored under the edge data key ``'weight'``.

    See also
    --------
    constraint

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Harvard University Press, 2009.

    """
    nmw = normalized_mutual_weight
    weight = nmw(G, u, v)
    r = sum(nmw(G, u, w) * nmw(G, w, v) for w in all_neighbors(G, u))
    return (weight + r) ** 2


def aggregate_constraint(G, v, organizational_measure=None):
    r"""Returns the hierarchy value of the node ``v`` in the graph ``G``.

    Formally, the *aggregate constraint* of `v`, denoted `a(v)`, is defined
    by

    .. math::

       a(v) = \sum_{w \in N(v)} \ell(v, w) * M(w),

    where `N(v)` is the set of neighbors of `v` and `M(w)`, the
    organizational measure of node `w`, is a `[0, 1]`-valued
    function. Informally, the organizational measure of a node is an
    indication of how "replaceable" the node is by any other element of
    its neighbor subgraph.

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``v``. This can be either directed or
        undirected.

    v : node
        A node in the graph ``G``.

    organizational_measure : function
        A parameter that indicates how "replaceable" any node is within
        its neighbor subgraph. If specified, this must be a function
        that takes two inputs, a graph and a node (any node) in the
        graph, and produces a single output, a number between zero and
        one, inclusive. If no function is specified, it is the constant
        function of value one.

    Returns
    -------
    float
        The aggregate constraint on the node ``v`` in the graph ``G``.

    Notes
    -----
    This function takes edge weights into account, assuming they are
    stored under the edge data key ``'weight'``.

    See also
    --------
    constraint
    local_constraint

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Harvard University Press, 2009.

    """
    if organizational_measure is None:
        organizational_measure = lambda G, w: 1
    return sum(local_constraint(G, v, w) * organizational_measure(G, w)
               for w in all_neighbors(G, v))


def hierarchy(G, v):
    r"""Returns the hierarchy value of the node ``v`` in the graph ``G``.

    Formally, the *hierarchy value* of `v`, denoted `h(v)`, is defined
    by

    .. math::

       h(v) = \frac{\sum_{w \in N(v) \setminus \{v\}} s(v, w) \log s(v, w))}
                   {\deg(v) \log \deg(v)},

    where

    .. math::

       s(v, w) = \frac{\ell(v, w) \deg(v)}{a(v)},

    the set `N(v)` is the set of neighbors of `v`, the value `\ell(v,
    w)` is the local constraint on `v` with respect to `w`, the value
    `\deg(v)` is the degree of `v` in the graph, and `a(v)` is the
    aggregate constraint on `v` [1]_. For the definitions of these
    functions, see :func:`local_constraint` and
    :func:`aggregate_constraint`.

    In the special case that the degree of ``v`` is one, the hierarchy
    value is defined to be one.

    The constraint functions take edge weights into account if the graph
    is weighted, otherwise edges are assumed to have weight one.

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``u`` and ``v``. This can be either
        directed or undirected.

    v : node
        A node in the graph ``G``.

    Returns
    -------
    float
        The hierarchy value of the node ``v`` in the graph ``G``.

    Raises
    ------
    :exc:`NetworkXError`
        If the degree of ``v`` is zero.

    Notes
    -----
    This function takes edge weights into account, assuming they are
    stored under the edge data key ``'weight'``.

    See also
    --------
    aggregate_constraint
    local_constraint

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Harvard University Press, 2009.

    """
    degv = G.degree(v)
    if degv == 0:
        msg = 'hierarchy not defined for degree zero node {}'.format(v)
        raise nx.NetworkXError(msg)
    # If we allowed the computation to continue with degree one, we
    # would get a division by zero error when attempting to divide by
    # the logarithm of the degree.
    if degv == 1:
        return 1
    v_constraint = aggregate_constraint(G, v)
    sl_constraint = 0
    numerator = 0
    for w in all_neighbors(G, v):
        sl_constraint = degv * local_constraint(G, v, w) / v_constraint
        numerator += sl_constraint * math.log(sl_constraint)
    return numerator / (degv * math.log(degv))
