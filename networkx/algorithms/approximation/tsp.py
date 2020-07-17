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

Travelling Salesman Problem tries to find, given the weight
(distance) between all points where salesman has to visit, the
route so that:
- Total distance (cost) which salesman travels to be minimized.
- Salesman has to return to the point where he stated.
- Salesman has to visit each point only once apart fom source point.

It is an NP-hard problem in combinatorial optimization,
important in operations research and theoretical computer science.

http://en.wikipedia.org/wiki/Travelling_salesman_problem
"""
import math
import networkx as nx
from networkx.utils import py_random_state

__all__ = ["greedy_tsp", "simulated_annealing_tsp", "threshold_accepting_tsp"]


def greedy_tsp(G, source, weight="weight"):
    """Return a low cost cycle starting at `source` and its cost.

    This approximates a solution to the traveling salesman problem.
    It finds a cycle of all the nodes that a salesman can visit in order
    to visit many nodes while minimizing total distance.
    It uses a simple greedy algorithm.
    In essence, this function returns a large cycle given a source point
    for which the total cost of the cycle is minimized.

    Parameters
    ----------
    G: Graph
        The Graph should be a complete weighted undirected graph.
        The distance between all pairs of nodes should be included.

    source : node
        Starting node

    weight: string, optional (default='weight')
        Edge data key corresponding to the edge weight

    Returns
    -------
    cycle : list, cost : float
        Returns the route (list of nodes) that a salesman
        can follow to minimize total cost, and the total
        cost of the algorithm's solution.

    Raises
    ------
    NetworkXError
        If G is either not complete or not weighted,
        the algorithm raises an exception.

    Examples
    --------
    >>> from networkx.algorithms import approximation as approx
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from([('A', 'B', 3),
    ...                           ('A', 'C', 17), ('A', 'D', 14), ('B', 'A', 3),
    ...                           ('B', 'C', 12), ('B', 'D', 16), ('C', 'A', 13),
    ...                           ('C', 'B', 12), ('C', 'D', 4), ('D', 'A', 14),
    ...                           ('D', 'B', 15), ('D', 'C', 2)])
    >>> cycle, cost = approx.greedy_tsp(G, 'D')
    >>> cycle
    ['D', 'C', 'B', 'A', 'D']
    >>> cost
    31

    Notes
    -----
    This implementation of a greedy algorithm is based on the following:
    - The algorithm adds a node to the solution at every iteration.
    - The algorithm selects a node not already in the cycle whose connection
    to the previous node adds the least cost to the cycle.

    A greedy algorithm does not always give the best solution.
    However, it can construct a first feasible solution which can
    be passed as a parameter to an iterative improvement algorithm such
    as Simulated Annealing, or Threshold Accepting.

    Time complexity:
    It has a running time O(|E||V|^2)   ??This requires a complete graph. |E|==|V^2|
    """
    if any(v not in G[u] for u in G for v in G if u != v):
        raise nx.NetworkXError("Not a complete graph. All node pairs must have edges.")
    if not nx.is_weighted(G, weight=weight):
        raise nx.NetworkXError("Given graph is not weighted.")

    if G.number_of_nodes() == 2:
        neighbor = list(G.neighbors(source))[0]
        return (
            [source, neighbor, source],
            G[source][neighbor][weight] + G[neighbor][source][weight],
        )

    nodeset = set(G)
    nodeset.remove(source)
    cycle = [source]
    cost = 0
    while nodeset:
        next_visitor = min(nodeset, key=lambda v: G[source][v][weight])
        cycle.append(next_visitor)
        cost += G[source][next_visitor][weight]
        nodeset.remove(next_visitor)
        source = next_visitor
    cycle.append(cycle[0])
    cost += G[cycle[-2]][cycle[0]][weight]
    return cycle, cost


@py_random_state(9)
def simulated_annealing_tsp(
    G,
    source,
    temp=100,
    move="1-1",
    tolerance=10,
    iterations=100,
    alpha=0.01,
    cycle=None,
    weight="weight",
    seed=None,
):
    """Returns an approximate solution to the traveling salesman problem.

    This function uses simulated annealing to approximate the minimal cost
    cycle through the nodes. Starting from a suboptimal solution, simulated
    annealing perturbs that solution, occasionally accepting changes the make
    the solution worse to escape from a locally optimal solution. The chance
    of accepting such changes decrease over the iterations to encourage
    an optimal result.  In summary, the function returns a cycle starting
    at `source` for which the total cost is minimized. It also returns the cost.

    The chance of accepting a proposed change is related to a parameter called
    the temperature (annealing has a physical analogue of steel hardening
    as it cools). As the temperature is reduced, the chance of moves that
    increase cost goes down.

    Parameters
    ----------
    G: Graph
        The Graph should be a complete weighted undirected graph.
        The distance between all pairs of nodes should be included.

    source : node
        Starting node

    temp : int, optional (default=100)
        The algorithm's temperature parameter. It represents the initial
        value of temperature

    move : string, optional (default='1-1')
        Move to be applied in a solution to generate a
        new (neighbor) solution. The algorithm checks if this
        neighbor solution is better than the best solution so far.
        Two moves are available:
        - 1-1 exchange which transposes the position
        of two elements of the current solution.
        For example if we apply 1-1 exchange in the solution
        A = [3, 2, 1, 4, 3]
        we can get the following by the transposition of 1 and 4 elements.
        A' = [3, 2, 4, 1, 3]
        - 1-0 exchange which moves an element of solution
        in a new position.
        For example if we apply 1-0 exchange in the solution
        A = [3, 2, 1, 4, 3]
        we can transfer the fourth element to the second position.
        A' = [3, 4, 2, 1, 3]

    tolerance : int, optional (default=10)
        The stopping condition for number of consecutive iterations of
        the outer loop for which the best cost solution has not decreased.

    iterations : int, optional (default=100)
        The stopping condition for the total number of iterations
        of the inner loop.

    alpha : float between (0, 1), optional (default=0.01)
        Percentage of temperature decrease in each iteration
        of outer loop

    cycle : list, optional (default=compute using greedy algorithm)
        The initial solution (a cycle all nodes).

    weight: string, optional (default='weight')
        Edge data key corresponding to the edge weight

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    cycle : list, cost : float
        Returns the route (list of nodes) that salesman
        has to follow to minimize total cost, and total
        cost of algorithm's solution.

    Raises
    ------
    NetworkXError
        If G is either not complete or not weighted,
        the algorithm raises an exception.

    Examples
    --------
    >>> from networkx.algorithms import approximation as approx
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from({('A', 'B', 3),
    ...                           ('A', 'C', 17), ('A', 'D', 14), ('B', 'A', 3),
    ...                           ('B', 'C', 12), ('B', 'D', 16), ('C', 'A', 13),
    ...                           ('C', 'B', 12), ('C', 'D', 4), ('D', 'A', 14),
    ...                           ('D', 'B', 15), ('D', 'C', 2)})
    >>> cycle, cost = approx.simulated_annealing_tsp(G, 'D')
    >>> cycle
    ['D', 'C', 'B', 'A', 'D']
    >>> cost
    31
    >>> incycle = ['D', 'B', 'A', 'C', 'D']
    >>> cycle, cost = approx.simulated_annealing_tsp(G, 'D', cycle=incycle)
    >>> cycle
    ['D', 'C', 'B', 'A', 'D']
    >>> cost
    31

    Notes
    -----
    Simulated Annealing is a metaheuristic local search algorithm.
    The main characteristic of this algorithm is that it accepts
    even solutions which lead to the increase of the cost in order
    to escape from low quality local optimal solutions.

    This algorithm needs an initial solution. If not provided, it is
    constructed by a simple greedy algorithm. At every iteration, the
    algorithm selects thoughtfully a neighbor solution.
    Consider c(x) cost of current solution and c(x') cost of
    neighbor solution.
    If c(x') - c(x) <= 0 then neighbor solution becomes current
    solution for the next iteration. Otherwise, algorithm accepts
    the neighbor solution with probability p = exp - ([c(x') - c(x)] / temp).
    Otherwise the current solution is retained.

    Temp is a parameter of the algorithm and represents temperature.

    Time complexity:
    For N_i iterations of the inner loop and N_o iterations of the
    outer loop, this algorithm has running time O(|E||V|^2 + N_i * N_o * |V|)
    when a greedy algorithm is used to construct an initial solution.
    Otherwise it has a running time O(N_i * N_o * |V|).

    For more information and how algorithm is inspired see:
    http://en.wikipedia.org/wiki/Simulated_annealing
    """
    if cycle is None:
        # Construct an initial solution using a greedy algorithm.
        cycle, cost = greedy_tsp(G, source, weight=weight)
        if G.number_of_nodes() == 2:
            return cycle, cost
    else:
        # Find the cost of initial solution and make the essential checks for graph.
        if any(v not in G[u] for u in G for v in G if u != v):
            raise nx.NetworkXError(
                "Not a complete graph. All node pairs must have edges."
            )
        if not nx.is_weighted(G, weight=weight):
            raise nx.NetworkXError("Given graph is not weighted.")

        if G.number_of_nodes() == 2:
            neighbor = list(G.neighbors(source))[0]
            return (
                [source, neighbor, source],
                G[source][neighbor][weight] + G[neighbor][source][weight],
            )

        cost = sum(G[u][v][weight] for u, v in zip(cycle, cycle[1:]))

    count = 0
    best_cycle = cycle[:]
    best_cost = cost
    while count <= tolerance and temp > 0:
        count += 1
        for i in range(iterations):
            adj_sol = _apply_move(cycle, move, seed)
            adj_cost = sum(G[u][v][weight] for u, v in zip(adj_sol, adj_sol[1:]))
            delta = adj_cost - cost
            if delta <= 0:
                # Set current solution the adjacent solution.
                cycle = adj_sol
                cost = adj_cost

                if cost < best_cost:
                    count = 0
                    best_cycle = cycle[:]
                    best_cost = cost
            else:
                # Accept even a worse solution with probability p.
                p = math.exp(-delta / temp)
                if p >= seed.random():
                    cycle = adj_sol
                    cost = adj_cost
        temp -= temp * alpha

    return best_cycle, best_cost


@py_random_state(9)
def threshold_accepting_tsp(
    G,
    source,
    threshold=1,
    move="1-1",
    tolerance=10,
    iterations=100,
    alpha=0.1,
    cycle=None,
    weight="weight",
    seed=None,
):
    """Returns an approximate solution to the traveling salesman problem.

    This function uses threshold accepting methods to approximate the minimal cost
    cycle through the nodes. Starting from a suboptimal solution, threshold
    accepting methods perturb that solution, accepting any changes that make
    the solution no worse than increasing by a threshold amount. Improvements
    in cost are accepted, but so are changes leading to small increases in cost.
    This allows the solution to leave suboptimal local minima in solution space.
    The threshold is decreased slowly as iterations proceed helping to ensure
    an optimum. In summary, the function returns a cycle starting at `source`
    for which the total cost is minimized. It also returns the cost.

    Parameters
    ----------
    G: Graph
        The Graph should be a complete weighted undirected graph.
        The distance between all pairs of nodes should be included.

    source : node
        Starting node

    threshold : int, optional (default=1)
        The algorithm's threshold parameter. It represents the initial
        threshold's value

    move : string, optional (default='1-1')
        Move to be applied in a solution to generate a
        new (neighbor) solution. The algorithm checks if this
        neighbor solution is better than the best solution so far.
        Two moves are available:
        - 1-1 exchange which transposes the position
        of two elements of the current solution.
        For example if we apply 1-1 exchange in the solution
        A = [3, 2, 1, 4, 3]
        we can get the following by the transposition of 1 and 4 elements.
        A' = [3, 2, 4, 1, 3]
        - 1-0 exchange which moves an element of solution
        in a new position.
        For example if we apply 1-0 exchange in the solution
        A = [3, 2, 1, 4, 3]
        we can transfer the fourth element to the second position.
        A' = [3, 4, 2, 1, 3]

    tolerance : int, optional (default=10)
        The stopping condition for number of consecutive iterations of
        the outer loop for which the best cost solution has not decreased.

    iterations : int, optional (default=100)
        The stopping condition for the total number of iterations
        of the inner loop.

    alpha : float between (0, 1), optional (default=0.1)
        Percentage of threshold decrease when there is at
        least one acceptance of a neighbor solution.
        If no inner loop moves are accepted the threshold remains unchanged.

    cycle : list, optional (default=compute using greedy algorithm)
        The initial solution (a cycle all nodes).

    weight: string, optional (default='weight')
        Edge data key corresponding to the edge weight

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    cycle : list, cost : float
        Returns the route (list of nodes) that salesman
        has to follow to minimize total cost, and total
        cost of algorithm's solution.

    Raises
    ------
    NetworkXError
        If graph is not either complete or weighed,
        algorithm raises an exception.

    Examples
    --------
    >>> from networkx.algorithms import approximation as approx
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from({('A', 'B', 3),
    ...                           ('A', 'C', 17), ('A', 'D', 14), ('B', 'A', 3),
    ...                           ('B', 'C', 12), ('B', 'D', 16), ('C', 'A', 13),
    ...                           ('C', 'B', 12), ('C', 'D', 4), ('D', 'A', 14),
    ...                           ('D', 'B', 15), ('D', 'C', 2)})
    >>> cycle, cost = approx.threshold_accepting_tsp(G, 'D')
    >>> cycle
    ['D', 'C', 'B', 'A', 'D']
    >>> cost
    31
    >>> cycle, cost = approx.threshold_accepting_tsp(G, 'D',
    ... cycle=['D', 'B', 'A', 'C', 'D'])
    >>> cycle
    ['D', 'C', 'B', 'A', 'D']
    >>> cost
    31

    Notes
    -----
    Threshold Accepting is a metaheuristic local search algorithm.
    The main characteristic of this algorithm is that it accepts
    even solutions which lead to the increase of the cost in order
    to escape from low quality local optimal solutions.

    This algorithm needs an initial solution. This solution can be
    constructed by a simple greedy algorithm. At every iteration, it
    selects thoughtfully a neighbor solution.
    Consider c(x) cost of current solution and c(x') cost of
    neighbor solution.
    If c(x') - c(x) <= threshold then neighbor solution becomes current
    solution for the next iteration, where threshold is named threshold.

    In comparison to Simulated Annealing algorithm, Threshold
    Accepting algorithm does not accept very low quality solutions.
    (due to the presence of the threshold value.) In case of
    Simulated Annealing, even a very low quality solution can
    be accepting with probability p.

    Time complexity:
    It has a running time 0(|E||V|^2 + m * n * |V|) when a greedy
    algorithm is used to construct an initial solution, otherwise
    it has a running time O(m * n * |V|) where m and n are the number
    of iterations of outer and inner loop respectively.

    For more information and how algorithm is inspired see:
    http://en.wikipedia.org/wiki/Threshold_accepting

    See Also
    --------
    simulated_annealing_tsp()

    """
    if cycle is None:
        # Construct an initial solution using a greedy algorithm.
        cycle, cost = greedy_tsp(G, source, weight=weight)
        if G.number_of_nodes() == 2:
            return cycle, cost
    else:
        # Find the cost of initial solution and make the essential checks for graph.
        if any(v not in G[u] for u in G for v in G if u != v):
            raise nx.NetworkXError(
                "Not a complete graph. All node pairs must have edges."
            )
        if not nx.is_weighted(G, weight=weight):
            raise nx.NetworkXError("Given graph is not weighted.")

        if G.number_of_nodes() == 2:
            neighbor = list(G.neighbors(source))[0]
            return (
                [source, neighbor, source],
                G[source][neighbor][weight] + G[neighbor][source][weight],
            )

        cost = sum(G[u][v][weight] for u, v in zip(cycle, cycle[1:]))

    count = 0
    best_cycle = cycle[:]
    best_cost = cost
    while count <= tolerance:
        count += 1
        accepted = False
        for i in range(iterations):
            adj_sol = _apply_move(cycle, move, seed)
            adj_cost = sum(G[u][v][weight] for u, v in zip(cycle, cycle[1:]))
            delta = adj_cost - cost
            if delta <= threshold:
                accepted = True

                # Set current solution the adjacent solution.
                cycle = adj_sol
                cost = adj_cost

                if cost < best_cost:
                    count = 0
                    best_cycle = cycle[:]
                    best_cost = cost
        if accepted:
            threshold -= threshold * alpha

    return best_cycle, best_cost


def _apply_move(soln, move, seed):
    """
    Apply a move to a solution to generate a neighbor solution.

    Parameters
    ----------
    soln : list of nodes
        Current solution (list of nodes)

    move : string
        Move to be applied

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    The solution after move is applied. (A neighbor solution.)
    """
    a = seed.randint(1, len(soln) - 2)
    listb = list(range(1, a)) + list(range(a + 1, len(soln) - 1))
    b = seed.choice(listb)
    if move == "1-1":
        soln[a], soln[b] = soln[b], soln[a]
    elif move == "1-0":
        soln.insert(b, soln.pop(a))
    return soln
