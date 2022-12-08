import doctest
import networkx as nx
"""REUT HADAD & TAL SOMECH"""

"""
This is an implementation for two different algorithms described on "MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS,
WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS" article.
The article points on two algorithms that solves kidney exchange problems, which can be modelled as cycle packing
problems in a directed graph, involving cycles of length 2, 3, or even longer.
In the article we focus on the maximal exchange of circles of size 2 and 3 vertices, we demonstrate an approximation
algorithm and an exact algorithm for this problem.
"""
"""article title: MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS,WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS
authors:Biro, P. and Manlove, D.F. and Rizzi, R.
year:(2009)
link:http://eprints.gla.ac.uk/25732/
"""


def APXalgorithm(graph: nx.DiGraph, k: int) -> list:
    """
    "Algorithm 1 - APX-complete algorithm for kidney exchange programs" by Biro, P. and Manlove, D.F. and Rizzi, R.
    :param graph:a networkx graph representing the said graph
    :param k: k to which the k-way exchange works in the algorithm
    :return: a list of matching k-way exchange for kidney exchange program
    Algorithm - the algorithm finds maximum weight k-way exchanges using reduction from graph to hyper-graph
    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_node(1)
    >>> Digraph.add_node(2)
    >>> Digraph.add_node(3)
    >>> Digraph.add_node(4)
    >>> Digraph.add_node(5)
    >>> Digraph.add_node(6)
    >>> Digraph.add_node(7)
    >>> Digraph.add_node(8)
    >>> Digraph.add_edge(1,8,weight=2)
    >>> Digraph.add_edge(8,1,weight=4)
    >>> Digraph.add_edge(2,1,weight=5)
    >>> Digraph.add_edge(1,3,weight=4)
    >>> Digraph.add_edge(3,8,weight=2)
    >>> Digraph.add_edge(8,2,weight=3)
    >>> Digraph.add_edge(8,5,weight=4)
    >>> Digraph.add_edge(5,7,weight=3)
    >>> Digraph.add_edge(7,6,weight=2)
    >>> Digraph.add_edge(6,5,weight=4)
    >>> print(APXalgorithm(Digraph,3))
    [[5,6,7],[1,8,2]]||[[5,6,7],[1,3,8]]
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_node(1)
    >>> Digraph.add_node(2)
    >>> Digraph.add_node(3)
    >>> Digraph.add_node(4)
    >>> Digraph.add_edge(2,1,weight=3)
    >>> Digraph.add_edge(1,3,weight=1)
    >>> Digraph.add_edge(3,2,weight=2)
    >>> Digraph.add_edge(3,4,weight=5)
    >>> Digraph.add_edge(4,3,weight=9)
    >>> print(APXalgorithm(Digraph))
    [3,4]
    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_node(1)
    >>> Digraph.add_node(2)
    >>> Digraph.add_node(3)
    >>> Digraph.add_node(4)
    >>> Digraph.add_node(5)
    >>> Digraph.add_node(6)
    >>> Digraph.add_node(7)
    >>> Digraph.add_node(8)
    >>> Digraph.add_edge(8,1,weight=4)
    >>> Digraph.add_edge(2,1,weight=5)
    >>> Digraph.add_edge(1,3,weight=4)
    >>> Digraph.add_edge(3,8,weight=2)
    >>> Digraph.add_edge(8,2,weight=3)
    >>> Digraph.add_edge(8,5,weight=4)
    >>> Digraph.add_edge(5,7,weight=3)
    >>> Digraph.add_edge(7,6,weight=2)
    >>> Digraph.add_edge(6,5,weight=4)
    >>> print(APXalgorithm(Digraph,2))
    []
    """
    f = 5
    return [f]


def ExactAlgorithm(graph: nx.Graph, k: int) -> list:
    """
    "Algorithm 2 - Exact algorithm for kidney exchange programs" by Biro, P. and Manlove, D.F. and Rizzi, R.
    :param graph:a networkx graph representing the said graph
    :param k: k to which the k-way exchange works in the algorithm
    :return: a list of matching k-way exchange for kidney exchange program
    Algorithm - the algorithm finds maximum weight k-way exchanges using reduction from directed graph to non directed
    graph
    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_node(1)
    >>> Digraph.add_node(2)
    >>> Digraph.add_node(3)
    >>> Digraph.add_node(4)
    >>> Digraph.add_node(5)
    >>> Digraph.add_node(6)
    >>> Digraph.add_node(7)
    >>> Digraph.add_node(8)
    >>> Digraph.add_edge(1,8,weight=2)
    >>> Digraph.add_edge(8,1,weight=4)
    >>> Digraph.add_edge(2,1,weight=5)
    >>> Digraph.add_edge(1,3,weight=4)
    >>> Digraph.add_edge(3,8,weight=2)
    >>> Digraph.add_edge(8,2,weight=3)
    >>> Digraph.add_edge(8,5,weight=4)
    >>> Digraph.add_edge(5,7,weight=3)
    >>> Digraph.add_edge(7,6,weight=2)
    >>> Digraph.add_edge(6,5,weight=4)
    >>> print(APXalgorithm(Digraph,3))
    [[5,6,7],[1,8,2]]||[[5,6,7],[1,3,8]]
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_node(1)
    >>> Digraph.add_node(2)
    >>> Digraph.add_node(3)
    >>> Digraph.add_node(4)
    >>> Digraph.add_edge(2,1,weight=3)
    >>> Digraph.add_edge(1,3,weight=1)
    >>> Digraph.add_edge(3,2,weight=2)
    >>> Digraph.add_edge(3,4,weight=5)
    >>> Digraph.add_edge(4,3,weight=9)
    >>> print(APXalgorithm(Digraph))
    [3,4]
    >>> graphEX3 = nx.DiGraph()
    >>> graphEX3.add_node(10)
    >>> graphEX3.add_node(11)
    >>> graphEX3.add_node(12)
    >>> graphEX3.add_node(13)
    >>> graphEX3.add_node(14)
    >>> graphEX3.add_node(15)
    >>> graphEX3.add_node(16)
    >>> graphEX3.add_edge(10,11,weight=10)
    >>> graphEX3.add_edge(11,12,weight=5)
    >>> graphEX3.add_edge(12,13,weight=6)
    >>> graphEX3.add_edge(13,10,weight=4)
    >>> graphEX3.add_edge(11,14,weight=2)
    >>> graphEX3.add_edge(14,16,weight=3)
    >>> graphEX3.add_edge(16,15,weight=8)
    >>> graphEX3.add_edge(15,14,weight=6)
    >>> print(ExactAlgorithm(graphEX3, 2))
    []
    """
    f = 5
    return [f]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print_hi('PyCharm')
    doctest.testmod()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
