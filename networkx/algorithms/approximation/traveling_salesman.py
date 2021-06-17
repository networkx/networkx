"""
=================================
Travelling Salesman Problem (TSP)
=================================

Implementation of approximate algorithms
for solving and approximating the TSP problem.

Categories of algorithms which are implemented:

- Christofides (provides a 3/2-approximation of TSP)
- Greedy
- Simulated Annealing (SA)
- Threshold Accepting (TA)

The Travelling Salesman Problem tries to find, given the weight
(distance) between all points where a salesman has to visit, the
route so that:

- The total distance (cost) which the salesman travels is minimized.
- The salesman returns to the starting point.
- Note that for a complete graph, the salesman visits each point once.

The function `travelling_salesman_problem` allows for incomplete
graphs by finding all-pairs shortest paths, effectively converting
the problem to a complete graph problem. It calls one of the
approximate methods on that problem and then converts the result
back to the original graph using the previously found shortest paths.

TSP is an NP-hard problem in combinatorial optimization,
important in operations research and theoretical computer science.

http://en.wikipedia.org/wiki/Travelling_salesman_problem
"""
import math
import networkx as nx
import numpy as np
import scipy.optimize as sp

from networkx import NetworkXNoCycle
from networkx.utils import py_random_state, not_implemented_for, pairwise

__all__ = [
    "traveling_salesman_problem",
    "christofides",
    "greedy_tsp",
    "simulated_annealing_tsp",
    "threshold_accepting_tsp",
    "_held_karp",
]


def swap_two_nodes(soln, seed):
    """Swap two nodes in `soln` to give a neighbor solution.

    Parameters
    ----------
    soln : list of nodes
        Current cycle of nodes

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    list
        The solution after move is applied. (A neighbor solution.)

    Notes
    -----
        This function assumes that the incoming list `soln` is a cycle
        (that the first and last element are the same) and also that
        we don't want any move to change the first node in the list
        (and thus not the last node either).

        The input list is changed as well as returned. Make a copy if needed.

    See Also
    --------
        move_one_node
    """
    a, b = seed.sample(range(1, len(soln) - 1), k=2)
    soln[a], soln[b] = soln[b], soln[a]
    return soln


def move_one_node(soln, seed):
    """Move one node to another position to give a neighbor solution.

    The node to move and the position to move to are chosen randomly.
    The first and last nodes are left untouched as soln must be a cycle
    starting at that node.

    Parameters
    ----------
    soln : list of nodes
        Current cycle of nodes

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    list
        The solution after move is applied. (A neighbor solution.)

    Notes
    -----
        This function assumes that the incoming list `soln` is a cycle
        (that the first and last element are the same) and also that
        we don't want any move to change the first node in the list
        (and thus not the last node either).

        The input list is changed as well as returned. Make a copy if needed.

    See Also
    --------
        swap_two_nodes
    """
    a, b = seed.sample(range(1, len(soln) - 1), k=2)
    soln.insert(b, soln.pop(a))
    return soln


@not_implemented_for("directed")
def christofides(G, weight="weight", tree=None):
    """Approximate a solution of the traveling salesman problem

    Compute a 3/2-approximation of the traveling salesman problem
    in a complete undirected graph using Christofides [1]_ algorithm.

    Parameters
    ----------
    G : Graph
        `G` should be a complete weighted undirected graph.
        The distance between all pairs of nodes should be included.

    weight : string, optional (default="weight")
        Edge data key corresponding to the edge weight.
        If any edge does not have this attribute the weight is set to 1.

    tree : NetworkX graph or None (default: None)
        A minimum spanning tree of G. Or, if None, the minimum spanning
        tree is computed using :func:`networkx.minimum_spanning_tree`

    Returns
    -------
    list
        List of nodes in `G` along a cycle with a 3/2-approximation of
        the minimal Hamiltonian cycle.

    References
    ----------
    .. [1] Christofides, Nicos. "Worst-case analysis of a new heuristic for
       the travelling salesman problem." No. RR-388. Carnegie-Mellon Univ
       Pittsburgh Pa Management Sciences Research Group, 1976.
    """
    # Remove selfloops if necessary
    loop_nodes = nx.nodes_with_selfloops(G)
    try:
        node = next(loop_nodes)
    except StopIteration:
        pass
    else:
        G = G.copy()
        G.remove_edge(node, node)
        G.remove_edges_from((n, n) for n in loop_nodes)
    # Check that G is a complete graph
    N = len(G) - 1
    # This check ignores selfloops which is what we want here.
    if any(len(nbrdict) != N for n, nbrdict in G.adj.items()):
        raise nx.NetworkXError("G must be a complete graph.")

    if tree is None:
        tree = nx.minimum_spanning_tree(G, weight=weight)
    L = G.copy()
    L.remove_nodes_from([v for v, degree in tree.degree if not (degree % 2)])
    MG = nx.MultiGraph()
    MG.add_edges_from(tree.edges)
    edges = nx.min_weight_matching(L, maxcardinality=True, weight=weight)
    MG.add_edges_from(edges)
    return _shortcutting(nx.eulerian_circuit(MG))


def _shortcutting(circuit):
    """Remove duplicate nodes in the path"""
    nodes = []
    for u, v in circuit:
        if v in nodes:
            continue
        if not nodes:
            nodes.append(u)
        nodes.append(v)
    nodes.append(nodes[0])
    return nodes


def traveling_salesman_problem(G, weight="weight", nodes=None, cycle=True, method=None):
    """Find the shortest path in `G` connecting specified nodes

    This function allows approximate solution to the traveling salesman
    problem on networks that are not complete graphs and/or where the
    salesman does not need to visit all nodes.

    This function proceeds in two steps. First, it creates a complete
    graph using the all-pairs shortest_paths between nodes in `nodes`.
    Edge weights in the new graph are the lengths of the paths
    between each pair of nodes in the original graph.
    Second, an algorithm (default: `christofides`) is used to approximate
    the minimal Hamiltonian cycle on this new graph. The available
    algorithms are:

     - christofides
     - greedy_tsp
     - simulated_annealing_tsp
     - threshold_accepting_tsp

    Once the Hamiltonian Cycle is found, this function post-processes to
    accommodate the structure of the original graph. If `cycle` is ``False``,
    the biggest weight edge is removed to make a Hamiltonian path.
    Then each edge on the new complete graph used for that analysis is
    replaced by the shortest_path between those nodes on the original graph.

    Parameters
    ----------
    G : NetworkX graph
        Undirected possibly weighted graph

    nodes : collection of nodes (default=G.nodes)
        collection (list, set, etc.) of nodes to visit

    weight : string, optional (default="weight")
        Edge data key corresponding to the edge weight.
        If any edge does not have this attribute the weight is set to 1.

    cycle : bool (default: True)
        Indicates whether a cycle should be returned, or a path.
        Note: the cycle is the approximate minimal cycle.
        The path simply removes the biggest edge in that cycle.

    method : function (default: None)
        A function that returns a cycle on all nodes and approximates
        the solution to the traveling salesman problem on a complete
        graph. The returned cycle is then used to find a corresponding
        solution on `G`. `method` should be callable; take inputs
        `G`, and `weight`; and return a list of nodes along the cycle.

        Provided options include :func:`christofides`, :func:`greedy_tsp`,
        :func:`simulated_annealing_tsp` and :func:`threshold_accepting_tsp`.

        If `method is None`: use :func:`christofides` for undirected `G` and
        :func:`threshold_accepting_tsp` for directed `G`.

        To specify parameters for these provided functions, construct lambda
        functions that state the specific value. `method` must have 2 inputs.
        (See examples).

    Returns
    -------
    list
        List of nodes in `G` along a path with a 3/2-approximation of the minimal
        path through `nodes`.

    Examples
    --------
    >>> tsp = nx.approximation.traveling_salesman_problem
    >>> G = nx.cycle_graph(9)
    >>> G[4][5]["weight"] = 5  # all other weights are 1
    >>> tsp(G, nodes=[3, 6])
    [3, 2, 1, 0, 8, 7, 6, 7, 8, 0, 1, 2, 3]
    >>> path = tsp(G, cycle=False)
    >>> path in ([4, 3, 2, 1, 0, 8, 7, 6, 5], [5, 6, 7, 8, 0, 1, 2, 3, 4])
    True

    Build (curry) your own function to provide parameter values to the methods.

    >>> SA_tsp = nx.approximation.simulated_annealing_tsp
    >>> method = lambda G, wt: SA_tsp(G, "greedy", weight=wt, temp=500)
    >>> path = tsp(G, cycle=False, method=method)
    >>> path in ([4, 3, 2, 1, 0, 8, 7, 6, 5], [5, 6, 7, 8, 0, 1, 2, 3, 4])
    True

    """
    if method is None:
        if G.is_directed():

            def threshold_tsp(G, weight):
                return threshold_accepting_tsp(G, "greedy", weight)

            method = threshold_tsp
        else:
            method = christofides
    if nodes is None:
        nodes = list(G.nodes)

    dist = {}
    path = {}
    for n, (d, p) in nx.all_pairs_dijkstra(G, weight=weight):
        dist[n] = d
        path[n] = p

    GG = nx.Graph()
    for u in nodes:
        for v in nodes:
            if u == v:
                continue
            GG.add_edge(u, v, weight=dist[u][v])
    best_GG = method(GG, weight)

    if not cycle:
        # find and remove the biggest edge
        biggest_edge = None
        length_biggest = float("-inf")
        (u, v) = max(pairwise(best_GG), key=lambda x: dist[x[0]][x[1]])
        pos = best_GG.index(u) + 1
        while best_GG[pos] != v:
            pos = best_GG[pos:].index(u) + 1
        best_GG = best_GG[pos:-1] + best_GG[:pos]

    best_path = []
    for u, v in pairwise(best_GG):
        best_path.extend(path[u][v][:-1])
    best_path.append(v)
    return best_path


def asadpour_tsp(G, weight="weight"):
    """
    Returns an approximate solution to the traveling salesman problem.

    This approximate solution is one of the best known approximations for
    the asymmetric traveling salesman problem developed by Asadpour et al,
    [1]_. The algorithm first solves the Held-Karp relaxation to find a
    lower bound for the weight of the cycle. Next, it constructs an
    exponential distribution of undirected spanning trees where the
    probability of an edge being in the tree corresponds to the weight of
    that edge using a maximum entropy rounding scheme. Next we sample that
    distribution $2 \\log n$ times and save the minimum sampled tree once
    the direction of the arcs is added back to the edges. Finally,
    we argument then short circuit that graph to find the approximate tour
    for the salesman.

    Parameters
    ----------
    G : nx.DiGraph
        The graph should be a complete weighted directed graph.
        The distance between all paris of nodes should be included.

    weight : string, optional (default="weight")
        Edge data key corresponding to the edge weight.
        If any edge does not have this attribute the weight is set to 1.

    Returns
    -------
        cycle : list of nodes Returns the cycle (list of nodes) that a salesman
            can follow to minimize the total weight of the trip.

    Raises
    ------
    NetworkXError
        If `G` is not complete, the algorithm raises an exception.

    References
    ----------
    .. [1] A. Asadpour, M. X. Goemans, A. Madry, S. O. Gharan, and A. Saberi,
       An o(log n/log log n)-approximation algorithm for the asymmetric
       traveling salesman problem, Operations research, 65 (2017),
       pp. 1043–1061
    """
    pass


def _held_karp(G, weight="weight"):
    """
    Solves the Held-Karp relaxation of the input complete digraph and scales
    the output solution for use in the Asadpour [1]_ ASTP algorithm.

    The Held-Karp relaxation defines the lower bound for solutions to the
    ATSP, although it does return a fractional solution. This is used in the
    Asadpour algorithm as an initial solution which is later rounded to a
    integral tree within the spanning tree polytopes. This function solves
    the relaxation with the branch and bound method in [2]_.

    Parameters
    ----------
    G : nx.DiGraph
        The graph should be a complete weighted directed graph.
        The distance between all paris of nodes should be included.

    weight : string, optional (default="weight")
        Edge data key corresponding to the edge weight.
        If any edge does not have this attribute the weight is set to 1.

    Returns
    -------
    OPT : float
        The cost for the optimal solution to the Held-Karp relaxation
    z_star : numpy array
        A symmetrized and scaled version of the optimal solution to the
        Held-Karp relaxation for use in the Asadpour algorithm

    References
    ----------
    .. [1] A. Asadpour, M. X. Goemans, A. Madry, S. O. Gharan, and A. Saberi,
       An o(log n/log log n)-approximation algorithm for the asymmetric
       traveling salesman problem, Operations research, 65 (2017),
       pp. 1043–1061

    .. [2] M. Held, R. M. Karp, The traveling-salesman problem and minimum
           spanning trees, Operations Research, 1970-11-01, Vol. 18 (6),
           pp.1138-1162
    """

    def k_pi():
        """
        Find the set of minimum 1-Arborescences for G at point pi.

        Returns
        -------
        Set
            The set of minimum 1-Trees
        """
        # Create a copy of G without vertex 1
        G_1 = G.copy()
        # node is node '1' in the Held and Karp paper
        G_1.remove_node(node)
        minimum_arborescence_weight = math.inf
        minimum_1_arborescence_weight = math.inf
        minimum_1_arborescences = set()
        for arborescence in nx.ArborescenceIterator(G_1):
            if minimum_arborescence_weight == math.inf:
                minimum_arborescence_weight = arborescence.size(weight)
            elif arborescence.size(weight) > minimum_arborescence_weight:
                # We are done with minimum arborescences
                break
            arborescence.add_node(node)
            # We can pick the minimum weight in-edge for the vertex with a cycle
            min_in_edge_weight = math.inf
            min_in_edge = None
            for u, v, d in G.in_edges(node, data=True):
                edge_weight = d[weight]
                if edge_weight < min_in_edge_weight:
                    min_in_edge_weight = edge_weight
                    min_in_edge = (u, v)
            arborescence.add_edge(
                min_in_edge[0], min_in_edge[1], weight=min_in_edge_weight
            )
            # We have to pick the root node of the arborescence for the out edge
            # of the first vertex as that is the only node without an edge
            # directed into it.
            for n in arborescence:
                if arborescence.in_degree(n) == 0:
                    # root found
                    arborescence.add_edge(node, n, weight=G[node][n][weight])
                    break
            # We now have a 1-arborescence
            if arborescence.size(weight) < minimum_1_arborescence_weight:
                minimum_1_arborescence_weight = arborescence.size(weight)
            minimum_1_arborescences.add(arborescence)
        # Not every minimum spanning arborescence will produce a minimum
        # 1-arborescence, depending on the cheapest root to connect to.
        # Once we have this set, we need to delete all of the non-minimum
        # 1-arborescences from it.
        for one_arborescence in list(minimum_1_arborescences):
            if one_arborescence.size(weight) > minimum_1_arborescence_weight:
                minimum_1_arborescences.discard(one_arborescence)

        return minimum_1_arborescences

    def direction_of_ascent(d=None):
        """
        Find the direction of ascent at point pi.

        See [1]_ for more information.

        Parameters
        ----------
        d : dict
            A mapping from the nodes of n to their values for the direction of
            ascent

        Returns
        -------
        np.array
            A numpy array representing the direction in which the objective
            function is increasing the fastest.

        References
        ----------
        .. [1] M. Held, R. M. Karp, The traveling-salesman problem and minimum
           spanning trees, Operations Research, 1970-11-01, Vol. 18 (6),
           pp.1138-1162
        """
        # 1. Set d equal to the zero n-vector.
        if d is None:
            d = {}
            for n in G:
                d[n] = 0
            del n
        # 2. Find a 1-Aborescence T^k such that k is in K(pi, d).
        minimum_1_arborescences = k_pi()
        while True:
            # Reduce K(pi) to K(pi, d)
            # Find the arborescence in K(pi) which increases the lest in
            # direction d
            min_k_d_weight = math.inf
            min_k_d = None
            for arborescence in minimum_1_arborescences:
                weighted_cost = 0
                v_k_0 = 0
                for n in G:
                    weighted_cost += d[n] * (arborescence.degree(n) - 2)
                    if arborescence.degree(n) - 2 == 0:
                        v_k_0 += 1
                if weighted_cost < min_k_d_weight:
                    min_k_d_weight = weighted_cost
                    min_k_d = arborescence
                if v_k_0 == len(G):
                    min_k_d_weight = weighted_cost
                    min_k_d = arborescence
            # 3. If sum of d_i * v_{i, k} is greater than zero, terminate
            if min_k_d_weight > 0:
                return d, min_k_d
            # 4. d_i = d_i + v_{i, k}
            for n in G:
                if n is node:
                    continue
                d[n] += min_k_d.degree(n) - 2
            # Check that we do not need to terminate because the direction
            # of ascent does not exist. This is done with linear
            # programming.
            c = np.full(len(minimum_1_arborescences), -1)
            a_eq = np.empty((len(G) + 1, len(minimum_1_arborescences)))
            b_eq = np.zeros(len(G) + 1)
            b_eq[len(G)] = 1
            arb_count = 0
            for arborescence in minimum_1_arborescences:
                n_count = len(G) - 1
                for n in arborescence:
                    a_eq[n_count][arb_count] = arborescence.degree(n) - 2
                    n_count -= 1
                a_eq[len(G)][arb_count] = 1
                arb_count += 1
            program_result = sp.linprog(c, A_eq=a_eq, b_eq=b_eq)
            bool_result = program_result.x >= 0
            if program_result.status == 0 and np.sum(bool_result) == len(
                minimum_1_arborescences
            ):
                # There is no direction of ascent
                return None, min_k_d

            # 5. GO TO 2

    def find_epsilon(k, d):
        """
        Given the direction of ascent at pi, find the maximum distance we can go
        in that direction.

        Parameters
        ----------
        k : nx.DiGraph
        d : dict

        Returns
        -------
        float
            The distance we can travel in direction d
        """
        epsilon = {}
        for u_e, v_e, d_e in G.edges(data=True):
            if (u_e, v_e) in k.edges:
                continue
            k.add_edge(u_e, v_e, weight=d_e[weight])
            c = nx.find_cycle(k, v_e, orientation="ignore")
            # All edges in c could be substitutes for edge e, but I have not
            # been able to figure out how to check if it is a substitute
            # without doing so explicitly
            for u_c, v_c, _ in c:
                # delete the edge in the cycle and check if we still have
                # a 1-arborescence
                if (u_c, v_c) == (u_e, v_e):
                    continue
                k.remove_edge(u_c, v_c)
                if (
                    max(d for n, d in k.in_degree()) <= 1
                    and len(G) == k.number_of_edges()
                    and nx.is_weakly_connected(k)
                ):
                    # (u_e, v_e) is a substitute for (u_c, v_c)
                    if d[u_c] == d[u_e] or G[u_c][v_c][weight] == d_e[weight]:
                        k.add_edge(u_c, v_c, weight=G[u_c][v_c][weight])
                        continue
                    epsilon[(u_c, v_c, u_e, v_e)] = (
                        G[u_c][v_c][weight] - d_e[weight]
                    ) / (d[u_e] - d[u_c])
                    epsilon_c = G[u_c][v_c][weight] + epsilon[(u_c, v_c, u_e, v_e)] * (
                        d[u_c]
                    )
                    epsilon_e = d_e[weight] + epsilon[(u_c, v_c, u_e, v_e)] * (d[u_e])
                    if epsilon[(u_c, v_c, u_e, v_e)] < 0:
                        del epsilon[(u_c, v_c, u_e, v_e)]
                k.add_edge(u_c, v_c, weight=G[u_c][v_c][weight])
            k.remove_edge(u_e, v_e)
        min_epsilon = min(epsilon.items(), key=lambda x: x[1])

        return min_epsilon[1]

    # I HAVE to know that the elements in pi correspond to the correct elements
    # in the direction of ascent, even if the node labels are not integers.
    # Thus, I will use dictionaries to made that mapping.
    pi_dict = {}
    for n in G:
        pi_dict[n] = 0
    del n
    node = next(G.__iter__())
    original_edge_weights = {}
    for u, v, d in G.edges(data=True):
        original_edge_weights[(u, v)] = d[weight]
    dir_ascent, k_d = direction_of_ascent()
    while dir_ascent is not None:
        max_distance = find_epsilon(k_d, dir_ascent)
        for n, v in dir_ascent.items():
            pi_dict[n] += max_distance * v
        for u, v, d in G.edges(data=True):
            d[weight] = original_edge_weights[(u, v)] + pi_dict[u]
        dir_ascent, k_d = direction_of_ascent()

    return k_d


def _spanning_tree_distribution(z_star):
    """
    Solves the Maximum Entropy Convex Program in the Asadpour algorithm [1]_
    using the approach in section 7 to build an exponential distribution of
    undirected spanning trees.

    This algorithm ensures that the probability of any edge in a spanning
    tree is proportional to the sum of the probabilities of the tress
    containing that edge over the sum of the probabilities of all spanning
    trees of the graph.

    Parameters
    ----------
    z_star : numpy array
        The output of `_held_karp()`, a scaled version of the Held-Karp
        solution.

    Returns
    -------
    gamma : numpy array
        The probability distribution which approximately preserves the marginal
        probabilities of `z_star`.
    """
    pass


def _sample_spanning_tree(G, gamma):
    """
    Sample one spanning tree from the distribution defined by `gamma`,
    roughly using algorithm A8 in [1]_ .

    We 'shuffle' the edges in the graph, and then probabilistically
    determine weather to add the edge conditioned on all of the previous
    edges which where added to the tree. Probabilities are calculated using
    Kirchhoff's Matrix Tree Theorem and a weighted Laplacian matrix.

    Parameters
    ----------
    G : nx.Graph
        An undirected version of the original graph.

    gamma : numpy array
        The probabilities associated with each of the edges in the undirected
        graph `G`.

    Returns
    -------
    nx.Graph
        A spanning tree using the distribution defined by `gamma`.

    References
    ----------
    .. [1] V. Kulkarni, Generating random combinatorial objects, Journal of
       algorithms, 11 (1990), pp. 185–207
    """
    pass


def greedy_tsp(G, weight="weight", source=None):
    """Return a low cost cycle starting at `source` and its cost.

    This approximates a solution to the traveling salesman problem.
    It finds a cycle of all the nodes that a salesman can visit in order
    to visit many nodes while minimizing total distance.
    It uses a simple greedy algorithm.
    In essence, this function returns a large cycle given a source point
    for which the total cost of the cycle is minimized.

    Parameters
    ----------
    G : Graph
        The Graph should be a complete weighted undirected graph.
        The distance between all pairs of nodes should be included.

    weight : string, optional (default="weight")
        Edge data key corresponding to the edge weight.
        If any edge does not have this attribute the weight is set to 1.

    source : node, optional (default: first node in list(G))
        Starting node.  If None, defaults to ``next(iter(G))``

    Returns
    -------
    cycle : list of nodes
        Returns the cycle (list of nodes) that a salesman
        can follow to minimize total weight of the trip.

    Raises
    ------
    NetworkXError
        If `G` is not complete, the algorithm raises an exception.

    Examples
    --------
    >>> from networkx.algorithms import approximation as approx
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from({
    ...     ("A", "B", 3), ("A", "C", 17), ("A", "D", 14), ("B", "A", 3),
    ...     ("B", "C", 12), ("B", "D", 16), ("C", "A", 13),("C", "B", 12),
    ...     ("C", "D", 4), ("D", "A", 14), ("D", "B", 15), ("D", "C", 2)
    ... })
    >>> cycle = approx.greedy_tsp(G, source="D")
    >>> cost = sum(G[n][nbr]["weight"] for n, nbr in nx.utils.pairwise(cycle))
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

    Time complexity: It has a running time $O(|V|^2)$
    """
    # Check that G is a complete graph
    N = len(G) - 1
    # This check ignores selfloops which is what we want here.
    if any(len(nbrdict) - (n in nbrdict) != N for n, nbrdict in G.adj.items()):
        raise nx.NetworkXError("G must be a complete graph.")

    if source is None:
        source = nx.utils.arbitrary_element(G)

    if G.number_of_nodes() == 2:
        neighbor = next(G.neighbors(source))
        return [source, neighbor, source]

    nodeset = set(G)
    nodeset.remove(source)
    cycle = [source]
    next_node = source
    while nodeset:
        nbrdict = G[next_node]
        next_node = min(nodeset, key=lambda n: nbrdict[n].get(weight, 1))
        cycle.append(next_node)
        nodeset.remove(next_node)
    cycle.append(cycle[0])
    return cycle


@py_random_state(9)
def simulated_annealing_tsp(
    G,
    init_cycle,
    weight="weight",
    source=None,
    temp=100,
    move="1-1",
    max_iterations=10,
    N_inner=100,
    alpha=0.01,
    seed=None,
):
    """Returns an approximate solution to the traveling salesman problem.

    This function uses simulated annealing to approximate the minimal cost
    cycle through the nodes. Starting from a suboptimal solution, simulated
    annealing perturbs that solution, occasionally accepting changes that make
    the solution worse to escape from a locally optimal solution. The chance
    of accepting such changes decreases over the iterations to encourage
    an optimal result.  In summary, the function returns a cycle starting
    at `source` for which the total cost is minimized. It also returns the cost.

    The chance of accepting a proposed change is related to a parameter called
    the temperature (annealing has a physical analogue of steel hardening
    as it cools). As the temperature is reduced, the chance of moves that
    increase cost goes down.

    Parameters
    ----------
    G : Graph
        `G` should be a complete weighted undirected graph.
        The distance between all pairs of nodes should be included.

    init_cycle : list of all nodes or "greedy"
        The initial solution (a cycle through all nodes).
        Usually you should use `greedy_tsp(G, weight)`.
        But you can start with `list(G)` or the final result
        of `simulated_annealing_tsp` when doing `threshold_accepting_tsp`.

        This argument is required. A shortcut if you don't want to think
        about it is to use the string "greedy" which calls `greedy_tsp`.

    weight : string, optional (default="weight")
        Edge data key corresponding to the edge weight.
        If any edge does not have this attribute the weight is set to 1.

    source : node, optional (default: first node in list(G))
        Starting node.  If None, defaults to ``next(iter(G))``

    temp : int, optional (default=100)
        The algorithm's temperature parameter. It represents the initial
        value of temperature

    move : "1-1" or "1-0" or function, optional (default="1-1")
        Indicator of what move to use when finding new trial solutions.
        Strings indicate two special built-in moves:

        - "1-1": 1-1 exchange which transposes the position
          of two elements of the current solution.
          The function called is :func:`swap_two_nodes`.
          For example if we apply 1-1 exchange in the solution
          ``A = [3, 2, 1, 4, 3]``
          we can get the following by the transposition of 1 and 4 elements:
          ``A' = [3, 2, 4, 1, 3]``
        - "1-0": 1-0 exchange which moves an node in the solution
          to a new position.
          The function called is :func:`move_one_node`.
          For example if we apply 1-0 exchange in the solution
          ``A = [3, 2, 1, 4, 3]``
          we can transfer the fourth element to the second position:
          ``A' = [3, 4, 2, 1, 3]``

        You may provide your own functions to enact a move from
        one solution to a neighbor solution. The function must take
        the solution as input along with a `seed` input to control
        random number generation (see the `seed` input here).
        Your function should maintain the solution as a cycle with
        equal first and last node and all others appearing once.
        Your function should return the new solution.

    max_iterations : int, optional (default=10)
        Declared done when this number of consecutive iterations of
        the outer loop occurs without any change in the best cost solution.

    N_inner : int, optional (default=100)
        The number of iterations of the inner loop.

    alpha : float between (0, 1), optional (default=0.01)
        Percentage of temperature decrease in each iteration
        of outer loop

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    cycle : list of nodes
        Returns the cycle (list of nodes) that a salesman
        can follow to minimize total weight of the trip.

    Raises
    ------
    NetworkXError
        If `G` is not complete the algorithm raises an exception.

    Examples
    --------
    >>> from networkx.algorithms import approximation as approx
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from({
    ...     ("A", "B", 3), ("A", "C", 17), ("A", "D", 14), ("B", "A", 3),
    ...     ("B", "C", 12), ("B", "D", 16), ("C", "A", 13),("C", "B", 12),
    ...     ("C", "D", 4), ("D", "A", 14), ("D", "B", 15), ("D", "C", 2)
    ... })
    >>> cycle = approx.simulated_annealing_tsp(G, "greedy", source="D")
    >>> cost = sum(G[n][nbr]["weight"] for n, nbr in nx.utils.pairwise(cycle))
    >>> cycle
    ['D', 'C', 'B', 'A', 'D']
    >>> cost
    31
    >>> incycle = ["D", "B", "A", "C", "D"]
    >>> cycle = approx.simulated_annealing_tsp(G, incycle, source="D")
    >>> cost = sum(G[n][nbr]["weight"] for n, nbr in nx.utils.pairwise(cycle))
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
    Consider $c(x)$ cost of current solution and $c(x')$ cost of a
    neighbor solution.
    If $c(x') - c(x) <= 0$ then the neighbor solution becomes the current
    solution for the next iteration. Otherwise, the algorithm accepts
    the neighbor solution with probability $p = exp - ([c(x') - c(x)] / temp)$.
    Otherwise the current solution is retained.

    `temp` is a parameter of the algorithm and represents temperature.

    Time complexity:
    For $N_i$ iterations of the inner loop and $N_o$ iterations of the
    outer loop, this algorithm has running time $O(N_i * N_o * |V|)$.

    For more information and how the algorithm is inspired see:
    http://en.wikipedia.org/wiki/Simulated_annealing
    """
    if move == "1-1":
        move = swap_two_nodes
    elif move == "1-0":
        move = move_one_node
    if init_cycle == "greedy":
        # Construct an initial solution using a greedy algorithm.
        cycle = greedy_tsp(G, weight=weight, source=source)
        if G.number_of_nodes() == 2:
            return cycle

    else:
        cycle = list(init_cycle)
        if source is None:
            source = cycle[0]
        elif source != cycle[0]:
            raise nx.NetworkXError("source must be first node in init_cycle")
        if cycle[0] != cycle[-1]:
            raise nx.NetworkXError("init_cycle must be a cycle. (return to start)")

        if len(cycle) - 1 != len(G) or len(set(G.nbunch_iter(cycle))) != len(G):
            raise nx.NetworkXError("init_cycle should be a cycle over all nodes in G.")

        # Check that G is a complete graph
        N = len(G) - 1
        # This check ignores selfloops which is what we want here.
        if any(len(nbrdict) - (n in nbrdict) != N for n, nbrdict in G.adj.items()):
            raise nx.NetworkXError("G must be a complete graph.")

        if G.number_of_nodes() == 2:
            neighbor = next(G.neighbors(source))
            return [source, neighbor, source]

    # Find the cost of initial solution
    cost = sum(G[u][v].get(weight, 1) for u, v in pairwise(cycle))

    count = 0
    best_cycle = cycle.copy()
    best_cost = cost
    while count <= max_iterations and temp > 0:
        count += 1
        for i in range(N_inner):
            adj_sol = move(cycle, seed)
            adj_cost = sum(G[u][v].get(weight, 1) for u, v in pairwise(adj_sol))
            delta = adj_cost - cost
            if delta <= 0:
                # Set current solution the adjacent solution.
                cycle = adj_sol
                cost = adj_cost

                if cost < best_cost:
                    count = 0
                    best_cycle = cycle.copy()
                    best_cost = cost
            else:
                # Accept even a worse solution with probability p.
                p = math.exp(-delta / temp)
                if p >= seed.random():
                    cycle = adj_sol
                    cost = adj_cost
        temp -= temp * alpha

    return best_cycle


@py_random_state(9)
def threshold_accepting_tsp(
    G,
    init_cycle,
    weight="weight",
    source=None,
    threshold=1,
    move="1-1",
    max_iterations=10,
    N_inner=100,
    alpha=0.1,
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
    for which the total cost is minimized.

    Parameters
    ----------
    G : Graph
        `G` should be a complete weighted undirected graph.
        The distance between all pairs of nodes should be included.

    weight : string, optional (default="weight")
        Edge data key corresponding to the edge weight.
        If any edge does not have this attribute the weight is set to 1.

    source : node, optional (default: first node in list(G))
        Starting node.  If None, defaults to ``next(iter(G))``

    threshold : int, optional (default=1)
        The algorithm's threshold parameter. It represents the initial
        threshold's value

    move : "1-1" or "1-0" or function, optional (default="1-1")
        Indicator of what move to use when finding new trial solutions.
        Strings indicate two special built-in moves:
        - "1-1": 1-1 exchange which transposes the position
          of two elements of the current solution.
          The function called is :func:`swap_two_nodes`.
          For example if we apply 1-1 exchange in the solution
          ``A = [3, 2, 1, 4, 3]``
          we can get the following by the transposition of 1 and 4 elements:
          ``A' = [3, 2, 4, 1, 3]``
        - "1-0": 1-0 exchange which moves an node in the solution
          to a new position.
          The function called is :func:`move_one_node`.
          For example if we apply 1-0 exchange in the solution
          ``A = [3, 2, 1, 4, 3]``
          we can transfer the fourth element to the second position:
          ``A' = [3, 4, 2, 1, 3]``

        You may provide your own functions to enact a move from
        one solution to a neighbor solution. The function must take
        the solution as input along with a `seed` input to control
        random number generation (see the `seed` input here).
        Your function should maintain the solution as a cycle with
        equal first and last node and all others appearing once.
        Your function should return the new solution.

    max_iterations : int, optional (default=10)
        Declared done when this number of consecutive iterations of
        the outer loop occurs without any change in the best cost solution.

    N_inner : int, optional (default=100)
        The number of iterations of the inner loop.

    alpha : float between (0, 1), optional (default=0.1)
        Percentage of threshold decrease when there is at
        least one acceptance of a neighbor solution.
        If no inner loop moves are accepted the threshold remains unchanged.

    cycle : list, optional (default=compute using greedy algorithm)
        The initial solution (a cycle all nodes).

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    cycle : list of nodes
        Returns the cycle (list of nodes) that a salesman
        can follow to minimize total weight of the trip.

    Raises
    ------
    NetworkXError
        If `G` is not complete the algorithm raises an exception.

    Examples
    --------
    >>> from networkx.algorithms import approximation as approx
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from({
    ...     ("A", "B", 3), ("A", "C", 17), ("A", "D", 14), ("B", "A", 3),
    ...     ("B", "C", 12), ("B", "D", 16), ("C", "A", 13),("C", "B", 12),
    ...     ("C", "D", 4), ("D", "A", 14), ("D", "B", 15), ("D", "C", 2)
    ... })
    >>> cycle = approx.threshold_accepting_tsp(G, "greedy", source="D")
    >>> cost = sum(G[n][nbr]["weight"] for n, nbr in nx.utils.pairwise(cycle))
    >>> cycle
    ['D', 'C', 'B', 'A', 'D']
    >>> cost
    31
    >>> incycle = ["D", "B", "A", "C", "D"]
    >>> cycle = approx.threshold_accepting_tsp(G, incycle, source="D")
    >>> cost = sum(G[n][nbr]["weight"] for n, nbr in nx.utils.pairwise(cycle))
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
    Consider $c(x)$ cost of current solution and $c(x')$ cost of
    neighbor solution.
    If $c(x') - c(x) <= threshold$ then the neighbor solution becomes the current
    solution for the next iteration, where the threshold is named threshold.

    In comparison to the Simulated Annealing algorithm, the Threshold
    Accepting algorithm does not accept very low quality solutions
    (due to the presence of the threshold value). In the case of
    Simulated Annealing, even a very low quality solution can
    be accepted with probability $p$.

    Time complexity:
    It has a running time $O(m * n * |V|)$ where $m$ and $n$ are the number
    of times the outer and inner loop run respectively.

    For more information and how algorithm is inspired see:
    https://doi.org/10.1016/0021-9991(90)90201-B

    See Also
    --------
    simulated_annealing_tsp

    """
    if move == "1-1":
        move = swap_two_nodes
    elif move == "1-0":
        move = move_one_node
    if init_cycle == "greedy":
        # Construct an initial solution using a greedy algorithm.
        cycle = greedy_tsp(G, weight=weight, source=source)
        if G.number_of_nodes() == 2:
            return cycle

    else:
        cycle = list(init_cycle)
        if source is None:
            source = cycle[0]
        elif source != cycle[0]:
            raise nx.NetworkXError("source must be first node in init_cycle")
        if cycle[0] != cycle[-1]:
            raise nx.NetworkXError("init_cycle must be a cycle. (return to start)")

        if len(cycle) - 1 != len(G) or len(set(G.nbunch_iter(cycle))) != len(G):
            raise nx.NetworkXError("init_cycle is not all and only nodes.")

        # Check that G is a complete graph
        N = len(G) - 1
        # This check ignores selfloops which is what we want here.
        if any(len(nbrdict) - (n in nbrdict) != N for n, nbrdict in G.adj.items()):
            raise nx.NetworkXError("G must be a complete graph.")

        if G.number_of_nodes() == 2:
            neighbor = list(G.neighbors(source))[0]
            return [source, neighbor, source]

    # Find the cost of initial solution
    cost = sum(G[u][v].get(weight, 1) for u, v in pairwise(cycle))

    count = 0
    best_cycle = cycle.copy()
    best_cost = cost
    while count <= max_iterations:
        count += 1
        accepted = False
        for i in range(N_inner):
            adj_sol = move(cycle, seed)
            adj_cost = sum(G[u][v].get(weight, 1) for u, v in pairwise(adj_sol))
            delta = adj_cost - cost
            if delta <= threshold:
                accepted = True

                # Set current solution the adjacent solution.
                cycle = adj_sol
                cost = adj_cost

                if cost < best_cost:
                    count = 0
                    best_cycle = cycle.copy()
                    best_cost = cost
        if accepted:
            threshold -= threshold * alpha

    return best_cycle
