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
import math
from operator import itemgetter
from random import choice, randint, random
import networkx as nx

__all__ = ['greedy_tsp', 'simulated_annealing_tsp']


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
        Returns the route (list of nodes) that salesman
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
    ['D', 'C', 'B', 'A', 'D']
    >>> sol[1]
    31.0

    Notes
    -----
    Implementation of greedy algorithm is based on the following:
    - Algorithm adds a node to the solution at every
    iteration.
    - Algorithm selects a node whose connection with the previous node
    adds the minimum cost to incomplete solution at every iteration.

    A greedy algorithm does not give always the best solution.
    However, it can construct a first feasible solution which can
    be passed as parameter in iterative improvement algorithm such
    as Simulated Annealing, Threshold Accepting.
    """
    if not _is_completed(G):
        raise nx.NetworkXError('Given graph is not completed.')
    if not nx.is_weighted(G, weight=weight):
        raise nx.NetworkXError('Given graph is not weighted.')
    nodelist = G.nodes()
    nodelist.remove(source)
    sol = [source]
    cost = 0.0
    while len(nodelist) > 0:
        next_visitor, dist = _select_next(G, source, nodelist, weight)
        sol.append(next_visitor)
        cost += dist
        nodelist.remove(next_visitor)
        source = next_visitor
    sol.append(sol[0])
    cost += G.edge[sol[-2]][sol[0]][weight]
    return sol, cost


def _is_completed(G):
    """
    Function to test if a graph is completed.

    :param G: A networkX Graph
    :return: True if graph is completed; False otherwise.
    """
    return all(G.has_edge(u, v) for u in G.nodes() for v in G.nodes() if u != v)


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
    visitors = [(node, G.edge[source][node][weight])
                for node in nodes]
    return sorted(visitors, key=itemgetter(1))[0]


def simulated_annealing_tsp(G, source, temp=100, move='1-1', outer_iter=10,
                            inner_iter=100, a=0.01, sol=None, weight='weight'):
    """Finds the route that salesman has to visit in order
    to minimize total distance and total distance using a
    simulated annealing algorithm.

    In essence, function returns a cycle given a source point
    which total cost of cycle is minimized.

    Parameters
    ----------
    G: A complete weighted graph.

    source : node
        Starting node

    temp : int, optional (default=100)
        An algorithm's parameter. It represents the initial
        temperature of algorithm

    move : string, optional (default='1-1')
        Move to be applied in a solution to generate a
        neighbor solution.

    outer_iter : int, optional (default=10)
        Number of consecutive iterations of outer loop
        that cost of best solution is not decreased

    inner_iter : int, optional (default=100)
        Number of times that inner loop is being executed.

    a : float between (0, 1), optional (default=0.01)
        Percentage of temperature decrease in each iteration
        of outer loop

    sol : list, optional (default=None)
        Initial solution contains the sequence that nodes
        must be visited.

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
        Returns the route (list of nodes) that salesman
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
    >>> sol = nx.simulated_annealing_tsp(G, 'D')
    >>> sol[0]
    ['D', 'C', 'B', 'A', 'D']
    >>> sol[1]
    31.0
    >>> sol = nx.simulated_annealing_tsp(G, 'D', sol=['D', 'B', 'A', 'C', 'D'])
    >>> sol[0]
    ['D', 'C', 'B', 'A', 'D']
    >>> sol[1]
    31.0

    Notes
    -----
    Simulated Annealing is a metaheuristic local search algorithm.
    The main characteristic of this algorithm is that it accepts
    even solutions which lead to the increase of the cost in order
    to escape from low quality local optimal solutions.

    This algorithm needs an initial solution. This solution can be
    constructed by a simple greedy algorithm. At every iteration, it
    selects thoughtfully a neighbor solution.
    Consider c(x) cost of current solution and c(x') cost of
    neighbor solution.
    If c(x') - c(x) <= 0 then neighbor solution becomes current
    solution for the next iteration. Otherwise, algorithm accepts
    neighbor solution to become current solution for the next iteration
    with probability p = exp - ([c(x') - c(x)] / temp).

    Temp is parameter of algorithm and represents temperature in every
    iteration.

    For more information and how algorithm is inspired see:
    http://en.wikipedia.org/wiki/Simulated_annealing
    """
    if sol is None:
        # Construct an initial solution using a greedy algorithm.
        sol, cost = greedy_tsp(G, source, weight=weight)

    else:
        # Calculate the cost of initial solution and make the essential checks for graph.
        if not _is_completed(G):
            raise nx.NetworkXError('Given graph is not completed.')
        if not nx.is_weighted(G, weight=weight):
            raise nx.NetworkXError('Given graph is not weighted.')
        cost = _calculate_cost(G, sol, weight=weight)

    count = 0
    best_sol = list(sol)
    best_cost = cost
    while count <= outer_iter and temp > 0:
        count += 1
        for i in range(0, inner_iter):
            adj_sol = _apply_move(sol, move)
            adj_cost = _calculate_cost(G, adj_sol, weight=weight)
            delta = adj_cost - cost
            if delta <= 0:

                # Set current solution the adjacent solution.
                sol = list(adj_sol)
                cost = adj_cost

                if cost < best_cost:
                    count = 0
                    best_sol = list(sol)
                    best_cost = cost
            else:

                # Accept even a worse solution with probability p.
                p = math.exp(- (delta / temp))
                if p >= random():
                    sol = list(adj_sol)
                    cost = adj_cost

        temp -= temp * a

    return best_sol, best_cost


def _apply_move(sol, move):
    """
    Apply a move to a solution to generate a neighbor solution.

    :param sol: Current solution (list of nodes)
    :param move: Move to be applied
    :return: A neighbor solution
    """
    a = randint(1, len(sol) - 2)
    listb = range(1, a) + range(a + 1, len(sol) - 2)
    b = choice(listb)
    if move == '1-1':
        sol[a], sol[b] = sol[b], sol[a]
    elif move == '1-0':
        sol.insert(b, sol.pop(a))
    return sol


def _calculate_cost(G, sol, weight='weight'):
    """
    Calculate cost (distance) of a solution (list of nodes)

    For example, if we have the following solution:
    ['D', 'A', 'C', 'D']
    Cost of solution is calculated as follows:
    weight('D', 'A') + weight('A', 'C') + weight('C', 'D')

    :param G: A NetoworkX graph
    :param sol: List of nodes. Sequence that nodes must be visited.
    :param weight: Edge data key corresponding to the edge weight
    :return: float, cost (dist) of solution
    """
    return sum(G.edge[sol[i]][sol[i + 1]][weight] for i in range(0, len(sol) - 1))
