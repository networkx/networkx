# schultz.py - functions related to the c index of a graph
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
# Authors: Jangwon Yie(kleinaberoho10@gmail.com)

"""Functions related to the Schultz index of a graph."""
import networkx as nx
from networkx.utils import not_implemented_for
from .shortest_paths import shortest_path_length as spl

__all__ = ['schultz_index_first', 'schultz_index_second']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def schultz_index_first(g: nx.Graph):
    """Returns the Schultz index (of the first kind)[1] of the given graph.
    Let G be a undirected graph and V be its node set. For any (unordered) pair {x,y},
    s_1({x,y}) = d(x,y) * (d(x) + d(y)). Then the Schultz index (of the first kind)
    is the sum of s_1({x,y}) for all (unordered) pairs {x,y}.

    Parameters
    ----------
    g : NetworkX graph

    Returns
    -------
    int
        The first kind of Schultz index of the graph `g`.

    Reference
    ----------
    [1] H. P. Schultz, Topological organic chemistry. 1.
    Graph theory and topological indices of alkanes, J. Chem. Inf. Comput. Sci. 29
    (1989), 239–257

    Examples
    --------
    The first kind of Schultz index of the (unweighted) complete graph on *n* nodes
    equals the number of pairs of the *n* nodes times 2 * (n - 1),
    since each pair of nodes is at distance one and the sum of degree of two
    vertices is 2 * (n - 1).

        >>> import networkx as nx
        >>> from networkx.algorithms.schultz import *
        >>> n = 10
        >>> G = nx.complete_graph(n)
        >>> nx.schultz_index_first(G) == n * (n - 1) * (n - 1)
        True

    Graphs that are disconnected

        >>> G = nx.empty_graph(2)
        >>> nx.schultz_index_first(G)
        inf

    """
    if not nx.is_connected(g):
        return float('inf')

    dist_and_degrees = __list__dist_and_degree(g)

    return sum([dd[0] * (dd[1] + dd[2]) for dd in dist_and_degrees])


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def schultz_index_second(g: nx.Graph):
    """Returns the Schultz index (of the second kind)[1] of the given graph.
    Let G be a undirected graph and V be its node set. For any (unordered) pair {x,y},
    s_2({x,y}) = d(x,y) * d(x) * d(y). Then the Schultz index (of the second kind)
    is the sum of s_2({x,y}) for all (unordered) pairs {x,y}.

    Parameters
    ----------
    g : NetworkX graph
    Returns
    -------
    int
        The second kind of Schultz index of the graph `g`. It is nowadays known as
        the Gutman index.

    Reference
    ----------

    [1] I. Gutman, Selected properties of the Schultz molecular topological index,
     J. Chem. Inf. Comput. Sci. 34 (1994), 1087–1089.

    Examples
    --------
    The second kind of Schultz index of the (unweighted) complete graph on *n* nodes
    equals the number of pairs of the *n* nodes times (n - 1) * (n - 1),
    since each pair of nodes is at distance one and the product of degree of two
    vertices is (n - 1) * (n - 1).

        >>> import networkx as nx
        >>> from networkx.algorithms.schultz import *
        >>> n = 10
        >>> G = nx.complete_graph(n)
        >>> nx.schultz_index_second(G) == n * (n - 1) * (n - 1) * (n - 1) / 2
        True

    Graphs that are disconnected

        >>> G = nx.empty_graph(2)
        >>> nx.schultz_index_second(G)
        inf

    """
    if not nx.is_connected(g):
        return float('inf')

    dist_and_degrees = __list__dist_and_degree(g)
    return sum([dd[0] * dd[1] * dd[2] for dd in dist_and_degrees])


def __list__dist_and_degree(g):
    dist_pairs = dict(spl(g))

    nodes = list(g.nodes)
    l = list()
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            d_ij = dist_pairs[nodes[i]][nodes[j]]
            l.append((d_ij, g.degree[nodes[i]], g.degree[nodes[j]]))

    return l
