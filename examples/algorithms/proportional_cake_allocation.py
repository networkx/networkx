import PiecewiseConstantValuation as pc
import networkx as nx
from networkx.algorithms.approximation import contiguous_oriented_labeling as col
import matplotlib.pyplot as plt
import networkx.algorithms.isomorphism as iso



def graph_example1():
    """
    Notice that this graph is almost bridgeless, if we add edge (3,6) for example  this graph will be bridgeless
    """
    g = nx.Graph()
    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (4, 6), (4, 5), (5, 6)])
    # nx.draw(g)
    # plt.show()
    return g


def graph_example2():
    """
    Notice that this graph is almost bridgeless, if we add edge (1,5) for example  this graph will be bridgeless
    """
    g = nx.Graph()
    g.add_nodes_from([1, 2, 3, 4, 5])
    g.add_edges_from([(1, 2), (2, 3), (2, 5), (5, 4), (4, 3)])
    # nx.draw(g)
    # plt.show()
    return g


def graph_example3():
    """
    Notice that this graph is almost bridgeless, if we add edge (1,6) for example this graph will be bridgeless
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
    g1.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4)])
    g1[1][2]["weight"] = 5
    g1[1][3]["weight"] = 30
    g1[3][2]["weight"] = 10
    g1[2][4]["weight"] = 10
    g2 = nx.Graph()
    g2.add_nodes_from([2, 4, 5, 6])
    g2.add_edges_from([(2, 4), (4, 6), (4, 5), (5, 6)])
    g2[2][4]["weight"] = 18
    g2[4][5]["weight"] = 5
    g2[4][6]["weight"] = 10
    g2[5][6]["weight"] = 5
    return g1, g2


def allocation_graph2():
    g1 = nx.Graph()
    g1.add_nodes_from([1, 2, 5, 4])
    g1.add_edges_from([(1, 2), (2, 5), (5, 4)])
    g1[1][2]["weight"] = 1
    g1[2][5]["weight"] = 10
    g1[5][4]["weight"] = 10
    g2 = nx.Graph()
    g2.add_nodes_from([2, 3, 4])
    g2.add_edges_from([(4, 3), (2, 3)])
    g2[3][4]["weight"] = 6
    g2[2][3]["weight"] = 6
    return g1, g2


def allocation_graph3():
    g1 = nx.Graph()
    g1.add_nodes_from([1, 2])
    g1.add_edges_from([(1, 2)])
    g1[1][2]["weight"] = 30
    g2 = nx.Graph()
    g2.add_nodes_from([2, 3, 4, 5, 6])
    g2.add_edges_from([(2, 3), (2, 5), (3, 4), (4, 5), (5, 6)])
    g2[2][3]["weight"] = 1
    g2[2][5]["weight"] = 2
    g2[3][4]["weight"] = 6
    g2[5][4]["weight"] = 5
    g2[5][6]["weight"] = 15
    return g1, g2


def total_valuation(v):
    """
    This function returns the total valuation of an agent for the entire graph
    >>> total_valuation([pc.PiecewiseConstantValuation([10,20]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([5]), \
    pc.PiecewiseConstantValuation([10 ,20]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([5,10])])
    110
    >>> total_valuation([pc.PiecewiseConstantValuation([1]), pc.PiecewiseConstantValuation([1, 2, 3, 4]), \
    pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([2, 4]),pc.PiecewiseConstantValuation([5, 10])])
    42
    >>> total_valuation([pc.PiecewiseConstantValuation([5, 10, 15]), pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([2]),pc.PiecewiseConstantValuation([1, 2]), \
    pc.PiecewiseConstantValuation([3]), pc.PiecewiseConstantValuation([20])])
    60
    """
    s = 0
    for i in v:
        s += i.total_value()
    return s


def get_valuations_until_i(ordered_edges, vals_to_edges, edge, half):
    """
    This function valuates the cake until a certain point.
    """
    cake_alloc = nx.Graph()
    edge_weight = 0
    s = 0
    j = ordered_edges.index(edge)
    for i in range(j + 1):
        len = vals_to_edges[ordered_edges[i]][
            0
        ].cake_length()  # length of a single assignment of an edge
        for l in range(len):  # iterate over the piece
            if s == half:
                return (
                    s,
                    cake_alloc,
                    l / len,
                )  # if its exactly half we return the allocation and if we didnt take the whole edge assignment we return the part we stopped at
            cake_alloc.add_edge(ordered_edges[i][0], ordered_edges[i][1])
            s += vals_to_edges[ordered_edges[i]][0].eval(l, l + 1)
            edge_weight += vals_to_edges[ordered_edges[i]][0].eval(l, l + 1)
            cake_alloc[ordered_edges[i][0]][ordered_edges[i][1]]["weight"] = edge_weight
        edge_weight = 0
    return s, cake_alloc, 1


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
    >>> g3, g4 = get_proportional_allocation([pc.PiecewiseConstantValuation([10,20]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([5]), \
    pc.PiecewiseConstantValuation([10 ,20]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([5,10])], [pc.PiecewiseConstantValuation([5,10]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5]), \
    pc.PiecewiseConstantValuation([4,6,8,10]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([10])], graph_example1())
    >>> em = iso.numerical_edge_match('weight', 1)
    >>> iso.is_isomorphic(g1, g3, edge_match=em) and iso.is_isomorphic(g2, g4, edge_match=em)
    True
    >>> g1, g2 = allocation_graph2()
    >>> g3, g4 = get_proportional_allocation([pc.PiecewiseConstantValuation([1]), pc.PiecewiseConstantValuation([1, 2, 3, 4]), \
    pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([2, 4]),pc.PiecewiseConstantValuation([5, 10])],[pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([5]), \
    pc.PiecewiseConstantValuation([5]),pc.PiecewiseConstantValuation([2, 4]), pc.PiecewiseConstantValuation([2, 4])], graph_example2())
    >>> em = iso.numerical_edge_match('weight', 1)
    >>> iso.is_isomorphic(g1, g3, edge_match=em) and iso.is_isomorphic(g2, g4, edge_match=em)
    True
    >>> g1, g2 = allocation_graph3()
    >>> g3, g4 = get_proportional_allocation([pc.PiecewiseConstantValuation([5, 10, 15]), pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([2]),pc.PiecewiseConstantValuation([1, 2]), \
    pc.PiecewiseConstantValuation([3]), pc.PiecewiseConstantValuation([20])],[pc.PiecewiseConstantValuation([5, 10]), pc.PiecewiseConstantValuation([1]), pc.PiecewiseConstantValuation([2, 4]), \
     pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([5, 10])],graph_example3())
    >>> em = iso.numerical_edge_match('weight', 1)
    >>> iso.is_isomorphic(g1, g3, edge_match=em) and iso.is_isomorphic(g2, g4, edge_match=em)
    True
    """
    ordered_edges, oriented_edges = col.get_contiguous_oriented_labeling(
        graph
    )  # get the orientation of the edges and the order
    g = nx.DiGraph(oriented_edges)  # build a directed graph from them
    vals_to_edges = dict()  # all the values the agents gave to each edge
    i = 0
    edge_weight = 0
    for val in zip(
        v1, v2
    ):  # each value to each edge will be a tuple. First index value of 1st agent. Second to 2nd agent
        vals_to_edges[ordered_edges[i]] = val
        i += 1
    sum_v1 = total_valuation(v1)
    sum_v2 = total_valuation(v2)
    remainder_sum_v2 = 0
    alloc2 = nx.Graph()
    alloc1 = tuple()
    for (
        e
    ) in (
        ordered_edges
    ):  # according to the algorithm, the knife goes from i- to i+ in increasing order of the labels.
        for path in nx.all_simple_paths(
            g, source=ordered_edges[0][0], target=e[1]
        ):  # compute an ordered directed path
            alloc1 = get_valuations_until_i(
                ordered_edges, vals_to_edges, (path[-2], path[-1]), sum_v1 / 2
            )  # get the total value of it and then check if its half
            if alloc1[0] == sum_v1 / 2:
                u = path[-2]
                v = path[-1]
                part = alloc1[2]
                for edge in g.edges:
                    if edge not in alloc1[1].edges:
                        alloc2.add_edge(edge[0], edge[1])
                        remainder_sum_v2 += vals_to_edges[edge][1].total_value()
                        alloc2[edge[0]][edge[1]]["weight"] = vals_to_edges[edge][
                            1
                        ].total_value()
                if (
                    part != 1
                ):  # if part != 1 it means we need to add a fraction of an edge and not the entirety of it
                    len = vals_to_edges[(u, v)][1].cake_length()
                    for l in range(int(len * part), len):
                        edge_weight += vals_to_edges[(u, v)][1].eval(l, l + 1)
                        remainder_sum_v2 += vals_to_edges[(u, v)][1].eval(l, l + 1)
                    alloc2.add_edge(u, v)
                    alloc2[u][v]["weight"] = edge_weight
                if remainder_sum_v2 >= sum_v2 / 2:
                    return alloc1[1], alloc2
                else:
                    return (
                        alloc1[1],
                        nx.Graph(),
                    )  # return empty graph if we the rest is not sufficent to 2nd agent
    return alloc1, alloc2


# graph1, graph2 = get_proportional_allocation(
#     [pc.PiecewiseConstantValuation([5, 10, 15]), pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([2]),
#      pc.PiecewiseConstantValuation([1, 2]), pc.PiecewiseConstantValuation([3]), pc.PiecewiseConstantValuation([20])],
#     [pc.PiecewiseConstantValuation([5, 10]), pc.PiecewiseConstantValuation([1]), pc.PiecewiseConstantValuation([2, 4]),
#      pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([5, 10])],
#     graph_example3())
#
# for edge in graph1.edges:
#     print(edge, graph1.get_edge_data(edge[0], edge[1]))
# print("----------")
# for edge in graph2.edges:
#     print(edge, graph2.get_edge_data(edge[0], edge[1]))
