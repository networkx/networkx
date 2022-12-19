import PiecewiseConstantValuation as pc
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


def allocation_graph1():
    g1 = nx.Graph()
    g1.add_nodes_from([1, 2, 3])
    g1.add_edges_from([(1, 2), (1, 3), (2, 3)])
    g1[1][2]['weight'] = 10
    g1[1][3]['weight'] = 30
    g1[3][2]['weight'] = 25
    g2 = nx.Graph()
    g2.add_nodes_from([2, 3, 4, 5, 6])
    g2.add_edges_from([(2, 3), (2, 4), (4, 6), (4, 5), (5, 6)])
    g2[3][2]['weight'] = 5 / 3
    g2[2][4]['weight'] = 18
    g2[4][5]['weight'] = 5
    g2[4][6]['weight'] = 5
    g2[5][6]['weight'] = 5
    return g1, g2


def allocation_graph2():
    g1 = nx.Graph()
    g1.add_nodes_from([2, 3, 4, 5])
    g1.add_edges_from([(2, 5), (5, 4), (4, 3)])
    g1[2][5]['weight'] = 6
    g1[5][4]['weight'] = 10
    g1[4][3]['weight'] = 6
    g2 = nx.Graph()
    g2.add_nodes_from([1, 2, 3, 4])
    g2.add_edges_from([(4, 3), (2, 3), (2, 1)])
    g2[4][3]['weight'] = 2
    g2[3][2]['weight'] = 6
    g2[2][1]['weight'] = 6
    return g1, g2


def allocation_graph3():
    g1 = nx.Graph()
    g1.add_nodes_from([1, 2, 3, 4])
    g1.add_edges_from([(1, 2), (2, 3), (3, 4)])
    g1[1][2]['weight'] = 30
    g1[2][3]['weight'] = 2
    g1[3][4]['weight'] = 6
    g2 = nx.Graph()
    g2.add_nodes_from([2, 4, 5, 6])
    g2.add_edges_from([(4, 5), (2, 5), (5, 6)])
    g2[4][5]['weight'] = 5
    g2[2][5]['weight'] = 2
    g2[5][6]['weight'] = 15
    return g1, g2


def get_proportional_allocation(v1, v2, graph):
    """
    This algorithm obtains a connected allocation of the graph or "cake".
    ----------
    graph : NetworkX graph
        almost bridgeless graph
    v1, v2 : list of PiecewiseConstantValuation. Each item in the list represents the value of each agent to an edge.

    Returns
    -------
    A connected proportional allocation, represented by a graph for each agent.

     References
    ----------
    Based on an article by Xiaohui Bei and Warut Suksompong
    https://arxiv.org/pdf/1910.14129.pdf#subsection.4.5 - 2019

    Programmer : Eran Katz
    >>> g1, g2 = allocation_graph1()
    >>> get_proportional_allocation([pc.PiecewiseConstantValuation([10,20]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([5,10,15]), \
    pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([5,10])], [pc.PiecewiseConstantValuation([5,10]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5]), \
    pc.PiecewiseConstantValuation([4,6,8]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5])], graph_example1())
    g1 , g2
    >>> g1, g2 = allocation_graph2()
    >>> get_proportional_allocation([pc.PiecewiseConstantValuation([1,2,3]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([2,4,6]), pc.PiecewiseConstantValuation([5,10]), pc.PiecewiseConstantValuation([1])] \
    , [pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([2,4]), pc.PiecewiseConstantValuation([2,4]), pc.PiecewiseConstantValuation([6])], graph_example2())
    g1 , g2
    >>> g1, g2 = allocation_graph3()
    >>> get_proportional_allocation([pc.PiecewiseConstantValuation([5,10,15]), pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([1,2,3]), \
    pc.PiecewiseConstantValuation([5,10]), pc.PiecewiseConstantValuation([3]), pc.PiecewiseConstantValuation([20])], [pc.PiecewiseConstantValuation([5,10]), pc.PiecewiseConstantValuation([1]), pc.PiecewiseConstantValuation([2,4]), \
    pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([5,10])], graph_example3())
    g1, g2
    """
    pass
