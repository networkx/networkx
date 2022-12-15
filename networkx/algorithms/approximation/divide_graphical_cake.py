import networkx as nx
import matplotlib.pyplot as plt


def graph_example1():
    """
    Notice that this graph is almost bridgeless, if we add edge (3,6) this graph will be bridgeless
    """
    g = nx.Graph()
    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (4, 6), (4, 5), (5, 6)])
    # nx.draw(g)
    # plt.show()
    return g


def graph_example2():
    """
    Notice that this graph is almost bridgeless, if we add edge (1,5) this graph will be bridgeless
    """
    g = nx.Graph()
    g.add_nodes_from([1, 2, 3, 4, 5])
    g.add_edges_from([(1, 2), (2, 3), (2, 5), (5, 4), (4, 3)])
    # nx.draw(g)
    # plt.show()
    return g


def graph_example3():
    """
    Notice that this graph is almost bridgeless, if we add edge (1,6) this graph will be bridgeless
    """
    g = nx.Graph()
    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2), (2, 3), (2, 5), (5, 4), (4, 3), (5, 6)])
    # nx.draw(g)
    # plt.show()
    return g


def get_contiguous_oriented_labeling(graph):
    """
    This algorithm admits a contiguous oriented labeling in an almost bridgeless graph
    Parameters
    ----------
    graph : NetworkX graph
        almost bridgeless graph

    Returns
    -------
    a contiguous oriented labeling.
    First value is a list of each edge ordered by its labeling.
    Second value is a dictionary of each vertex and its oriantations.

    Notes
    -------
    A bridge of a graph is an edge that is not contained in any cycle.
    A graph is said to be bridgeless if it contains no bridges.
    A graph is said to be almost bridgeless if we can add an edge so that the resulting
    graph is bridgeless.
    An oriented labeling of a graph with m edges is a labeling of the edges with
    numbers 1, 2, . . . ,m, using each number exactly once, together with a labeling of one endpoint of
    each edge i with i− and the other endpoint with i+ (so each vertex receives a number of labels
    equal to the number of edges adjacent to it). An oriented labeling is said to be contiguous if:
    • For each 2 ≤ i ≤ m, the edges labeled 1, 2, . . . , i − 1 form a connected subgraph, and the
    vertex labeled i− belongs to one of these edges.
    • For each 1 ≤ i ≤ m − 1, the edges labeled i + 1, i + 2, . . . ,m form a connected subgraph, and
    the vertex labeled i+ belongs to one of these edges.

     References
    ----------
    Based on an article by Xiaohui Bei and Warut Suksompong
    https://arxiv.org/pdf/1910.14129.pdf#subsection.4.1 - 2019

    Programmer : Eran Katz

    Example 1:
    >>> get_contiguous_oriented_labeling(graph_example1())
    [(3,1), (1,2), (3,2), (2,4), (4,5), (5,6), (4,6)],
    {1: [-1,-2], 2: [2,3,-4], 3: [-1,-3], 4: [4,-5,-7], 5: [5,-6], 6: [6,7]}
    Example 2:
    >>> get_contiguous_oriented_labeling(graph_example2())
    [(2,5), (4,5), (3,4), (2,3), (1,2)],
    {1: [5], 2: [1,4,-5], 3: [3,-4], 4: [2, -3], 5: [-1, -2]}
    Example 3:
    >>> get_contiguous_oriented_labeling(graph_example3())
     [(1, 2), (2,3), (3,4), (4,5), (2,5), (5,6)],
    {1: [-1], 2: [1,-2,-5], 3: [2,-3], 4: [3,-4], 5: [4,5,-6], 6: [6]}

    """
    return {}, {}

