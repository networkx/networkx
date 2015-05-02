"""
================================
Travelling Salesman Problem (TSP)
================================

Implementation of heuristic and metaheuristic algorithms
for solving and approximating the TSP problem.

Categories of algorithms which are implemented:
- Greedy
- Simulated Annealing (SA)
- Threshold Accepting (TA)
- Tabu Search
- Ant Colony Optimization (ACO)

Travelling Salesman Problem tries to find, given the weight
(distance) between all points where salesman has to visit, the
route so that:
- Total distance (cost) which salesman travels to be minimized.
- Salesman has to return to the point where he stated.
- Salesman has to visit each point only once apart fom source
point.

It is an NP-hard problem in combinatorial optimization,
important in operations research and theoretical computer science.

http://en.wikipedia.org/wiki/Travelling_salesman_problem
"""
import networkx as nx
from operator import itemgetter

__all__ = ['greedy_tsp']


def greedy_tsp(G, source, weight='weight'):
    """Finds the route that salesman has to visit in order
    to minimize total distance and total distance using a
    simple greedy algorithm.

    In essence, function returns a cycle given a source point
    which total cost of cycle is minimized.

    Parameters
    ----------
    G: A complete weighted graph.

    source : node
        Starting node

    weight: string, optional (default='weight')
        Edge data key corresponding to the edge weight

    Raises
    ------
    NetworkXError
        If graph is not either complete or weighed,
        algorithm raises an exception.

    Returns
    -------
    sol : list, cost : float
        Returns the route (list of edges) that salesman
        has to follow to minimize total cost, and total
        cost of algorithm's solution.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from({('A', 'B', 3),
    >>>                           ('A', 'C', 17), ('A', 'D', 14), ('B', 'A', 3),
    >>>                           ('B', 'C', 12), ('B', 'D', 16), ('C', 'A', 13),
    >>>                           ('C', 'B', 12), ('C', 'D', 4), ('D', 'A', 14),
    >>>                           ('D', 'B', 15), ('D', 'C', 2)})
    >>> sol = nx.greedy_tsp(G, 'D')
    >>> sol[0]
    [('D', 'C'), ('C', 'B'), ('B', 'A')]
    >>> sol[1]
    17.0

    Notes
    -----
    Implementation of greedy algorithm is based on the following:
    - Algorithm adds a couple of nodes to the solution at every
    iteration.
    - Algorithm selects the couple of nodes which adds the minimum
    cost to incomplete solution at every iteration.

    A greedy algorithm does not give always the best solution.
    However, it can construct a first feasible solution which can
    be passed as parameter in iterative improvement algorithm such
    as Simulated Annealing, Threshold Accepting.
    """
    g = G.copy()
    if not _is_completed(g):
        raise nx.NetworkXError('Given graph is not completed.')
    if not nx.is_weighted(g, weight=weight):
        raise nx.NetworkXError('Given graph is not weighted.')
    nodelist = g.nodes()
    nodelist.remove(source)
    sol = []
    cost = 0.0
    while len(nodelist) > 0:
        source, next_visitor, dist = _select_next(g, source, nodelist, weight)
        sol.append((source, next_visitor))
        cost += dist
        nodelist.remove(next_visitor)
        source = next_visitor
    return sol, cost


def _is_completed(G):
    """
    Function to test if a graph is completed.

    :param G: A networkX Graph
    :return: True if graph is completed; False otherwise.
    """
    _remove_self_loops(G)
    V = G.number_of_nodes()
    E = G.number_of_edges()
    return E == V * (V - 1)


def _remove_self_loops(G):
    """
    Remove self loops on the graph.

    :param G: A networkX Graph.
    """
    for node in G.nodes():
        if G.has_edge(node, node):
            G.remove_edge(node, node)


def _select_next(G, source, nodes, weight='weight'):
    """
    Function which selects the next node where salesman has to
    visit.

    Node whose connection with the source node given as parameter
    has the minimum weight amongst others.

    :param G: G: A networkX Graph.
    :param source: Node, source node.
    :param nodes: List of nodes which have not been visited yet.
    :param weight: Edge data key corresponding to the edge weight.
    :return: Tuple, edge of source node and next node to visit.
    """
    visitors = [(source, node, G.edge[source][node][weight])
                for node in nodes]
    return sorted(visitors, key=itemgetter(2))[0]
