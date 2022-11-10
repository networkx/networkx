import numpy as np
from scipy.optimize import linprog

import networkx as nx


def maximum_weight_fractional_matching(G: nx.Graph):
    """Returns the maximum-weight fractional matching of the wighted graph `G`.

    A fractional graph is a graph in which every edge has a fraction [0,1]
    such that the sum of fractions of edges adjacent to each vertex is at most 1.
    A matching is a set of edges that do not share any nodes.
    Define fw(e) for each edge e to be the multiplication of its weight and fraction.
    A maximum-weight fractional matching is one with the maximum fw(e) sum of all e in E(G).

    A fractional matching of maximum weight in a graph can be found by linear programming.

    *If the edges are not weighted - the weight of each edge is 1.

    Parameters
    ----------
    G : NetworkX graph
      Undirected weighted graph

    Returns
    -------
    F : dictionary

       The fractions are returned as a dictionary, `frac`, such that
         ``frac[e] == f`` for edge `e` with fraction `f` (rounded to 3 decimals).

    Examples
    --------
    In the weighted graph, G = (V,E).
        >>> G = nx.Graph()
        >>> G.add_nodes_from(["a1", "a2"])
        >>> G.add_edge("a1", "a2", weight=3)
        >>> F = maximum_weight_fractional_matching(G)
        >>> print(F=={('a1', 'a2'): 1.0})
        True
        >>> F[('a1','a2')]
        1.0

    explanation:                                               weight = 3
                    G =                                     a1-----------a2

                                                              frac = 1.0
                    maximum_weight_fractional_matching(G) = a1-----------a2

    The returned value is {('a1', 'a2'): 1.0}.
    There is only one edge, so it gets the maximaum value.

    another example:
        >>> G = nx.Graph()
        >>> G.add_nodes_from(["a1", "a2", "a3"])
        >>> G.add_weighted_edges_from([("a1", "a2", 1), ("a1", "a3", 2), ("a2", "a3", 3)])
        >>> F = maximum_weight_fractional_matching(G)
        >>> print(F=={('a1', 'a2'): 0.5, ('a1', 'a3'): 0.5, ('a2', 'a3'): 0.5})
        True
        >>> F[('a2','a3')]
        0.5

    explanation:                                                weight = 1
                    G =                                     a1------------a2
                                                              \\          \\
                                                    weight = 2  \\       \\ weight = 3
                                                                  \\    \\
                                                                    \\ \\
                                                                     a3

                                                               frac = 0.5
                    maximum_weight_fractional_matching(G) = a1------------a2
                                                              \\          \\
                                                     frac = 0.5 \\       \\ frac = 0.5
                                                                  \\    \\
                                                                    \\ \\
                                                                     a3

    The returned value is {('a1', 'a2'): 0.5, ('a1', 'a3'): 0.5, ('a2', 'a3'): 0.5}.
    We want to find Max(x,y,z) S.T
    a1: x +2y<=1
    a2: x+3z<=1
    a3: 2y+3z<=1
    and
    x,y,z<=1
    we can solve it using the linprog function:
    linprog(c, A_ub, b_ub, bounds, method='highs')
    linprog solve the same problem, but it finds the Min(x,y,z) so if we want Max(x,y,z)
    we can change our inqualities to be:
    Min(x,y,z)
    S.T
    a1: x +2y>=-1
    a2: x+3z>=-1
    a3: 2y+3z>=-1
    set bounds = (-1, 0)
    and then take the result as ABS, like that - |Min(x,y,z)|
    than we will get the solution for our original problem = {('a1', 'a2'): 0.5, ('a1', 'a3'): 0.5, ('a2', 'a3'): 0.5}

    Raises
    ------


    Notes
    -----


    See Also
    --------
    linprog

    References
    ----------
    https://en.wikipedia.org/wiki/Fractional_matching
    """

    if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
        return dict()
    num_nodes = len(G.nodes)
    num_edges = len(G.edges)
    c = [G.edges[edge].get("weight", 1) for edge in G.edges]
    b = [1] * num_nodes
    bounds = (-1, 0)
    index_node = {node: i for i, node in enumerate(G.nodes)}
    index_edge = {edge: i for i, edge in enumerate(G.edges)}
    A = np.zeros([num_nodes, num_edges], dtype=int)
    for edge in G.edges:
        i_edge = index_edge[edge]
        i_node1, i_node2 = index_node[edge[0]], index_node[edge[1]]
        A[i_node1, i_edge] = -1
        A[i_node2, i_edge] = -1
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
    return dict(zip(G.edges, np.abs(np.round(res.x, 3))))
